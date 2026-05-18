from fastapi.testclient import TestClient
from weirdlabs.main import app
from weirdlabs.store import InMemoryAlarmStore, get_alarm_store


def make_client(store: InMemoryAlarmStore) -> TestClient:
    app.dependency_overrides[get_alarm_store] = lambda: store
    return TestClient(app)


def make_network_alarm() -> dict:
    return {
        "alarm_category": "network",
        "perceived_severity": "critical",
        "alarm_state": "raised",
        "alarm_raised_time": "2024-01-01T00:00:00Z",
        "managed_object": {
            "label": "router-ams-01",
            "type": "network",
            "identifiers": [{"key": "hostname", "value": "router-ams-01"}],
        },
    }


def test_list_alarms_returns_empty_list():
    client = make_client(InMemoryAlarmStore())

    response = client.get("/alarms")

    assert response.status_code == 200
    data = response.json()
    assert data["alarms"] == []
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 20
    assert data["pagination"]["total"] == 0


def test_list_alarms_returns_seeded_alarm_with_tmf_field_names():
    from weirdlabs.models.alarm import Alarm

    store = InMemoryAlarmStore()
    store.add_alarm(Alarm(**make_network_alarm()))
    client = make_client(store)

    response = client.get("/alarms")

    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total"] == 1
    alarm = data["alarms"][0]
    assert alarm["alarm_category"] == "network"
    assert alarm["perceived_severity"] == "critical"
    assert alarm["alarm_state"] == "raised"
    assert alarm["alarm_raised_time"] == "2024-01-01T00:00:00Z"
    assert alarm["managed_object"]["label"] == "router-ams-01"


def test_agent_list_alarms_returns_compact_field_names():
    from weirdlabs.models.alarm import Alarm

    store = InMemoryAlarmStore()
    store.add_alarm(Alarm(**make_network_alarm()))
    client = make_client(store)

    response = client.get("/agent/alarms")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    alarm = data["alarms"][0]
    assert alarm["cat"] == "network"
    assert alarm["sev"] == "critical"
    assert alarm["st"] == "raised"
    assert alarm["ts"] == "2024-01-01T00:00:00Z"
    assert alarm["obj"]["lbl"] == "router-ams-01"
    assert "alarm_category" not in alarm
    assert "perceived_severity" not in alarm


def test_filter_alarms_by_category():
    from weirdlabs.models.alarm import Alarm

    store = InMemoryAlarmStore()
    store.add_alarm(Alarm(**make_network_alarm()))
    store.add_alarm(Alarm(**{**make_network_alarm(), "alarm_category": "host"}))
    client = make_client(store)

    response = client.get("/alarms?category=network")

    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total"] == 1
    assert data["alarms"][0]["alarm_category"] == "network"


def test_filter_alarms_by_severity():
    from weirdlabs.models.alarm import Alarm

    store = InMemoryAlarmStore()
    store.add_alarm(Alarm(**make_network_alarm()))
    store.add_alarm(Alarm(**{**make_network_alarm(), "perceived_severity": "minor"}))
    client = make_client(store)

    response = client.get("/alarms?severity=critical")

    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["total"] == 1
    assert data["alarms"][0]["perceived_severity"] == "critical"


# --- POST /alarms ---

def test_create_alarm_returns_201_with_assigned_id():
    client = make_client(InMemoryAlarmStore())

    response = client.post("/alarms", json=make_network_alarm())

    assert response.status_code == 201
    data = response.json()
    assert data["alarm_category"] == "network"
    assert data["perceived_severity"] == "critical"
    assert data["id"].startswith("alm_")


def test_created_alarm_appears_in_list():
    client = make_client(InMemoryAlarmStore())
    client.post("/alarms", json=make_network_alarm())

    response = client.get("/alarms")

    assert response.json()["pagination"]["total"] == 1


def test_create_alarm_defaults_state_to_raised():
    client = make_client(InMemoryAlarmStore())
    body = {k: v for k, v in make_network_alarm().items() if k != "alarm_state"}

    response = client.post("/alarms", json=body)

    assert response.status_code == 201
    assert response.json()["alarm_state"] == "raised"


def test_create_alarm_rejects_invalid_category():
    client = make_client(InMemoryAlarmStore())
    body = {**make_network_alarm(), "alarm_category": "not_a_category"}

    response = client.post("/alarms", json=body)

    assert response.status_code == 422
