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


def make_network_alarm_with_extension() -> dict:
    return {
        **make_network_alarm(),
        "extension": {
            "category": "network",
            "interface": "GigabitEthernet0/1",
            "topology_element": "interface",
            "protocol": "BGP",
        },
    }


# --- extensions ---

def test_post_alarm_with_network_extension_stores_and_returns_it():
    client = make_client(InMemoryAlarmStore())

    response = client.post("/alarms", json=make_network_alarm_with_extension())

    assert response.status_code == 201
    ext = response.json()["extension"]
    assert ext["interface"] == "GigabitEthernet0/1"
    assert ext["topology_element"] == "interface"
    assert ext["protocol"] == "BGP"


def test_get_alarms_returns_extension_with_verbose_keys():
    client = make_client(InMemoryAlarmStore())
    client.post("/alarms", json=make_network_alarm_with_extension())

    data = client.get("/alarms").json()

    ext = data["alarms"][0]["extension"]
    assert "interface" in ext
    assert "topology_element" in ext


def test_agent_alarms_returns_compact_extension_keys():
    client = make_client(InMemoryAlarmStore())
    client.post("/alarms", json=make_network_alarm_with_extension())

    data = client.get("/agent/alarms").json()

    ext = data["alarms"][0]["ext"]
    assert ext["iface"] == "GigabitEthernet0/1"
    assert ext["topo"] == "interface"
    assert "interface" not in ext


def test_extension_category_mismatch_returns_422():
    client = make_client(InMemoryAlarmStore())
    body = {
        **make_network_alarm(),
        "extension": {
            "category": "host",
            "metric": "cpu_load",
            "current_value": 95.0,
            "threshold": 90.0,
            "unit": "%",
        },
    }

    response = client.post("/alarms", json=body)

    assert response.status_code == 422


def test_post_host_alarm_with_extension():
    client = make_client(InMemoryAlarmStore())
    body = {
        **make_network_alarm(),
        "alarm_category": "host",
        "extension": {
            "category": "host",
            "metric": "disk_usage",
            "current_value": 98.5,
            "threshold": 90.0,
            "unit": "%",
        },
    }

    response = client.post("/alarms", json=body)

    assert response.status_code == 201
    ext = response.json()["extension"]
    assert ext["metric"] == "disk_usage"
    assert ext["current_value"] == 98.5


def test_post_database_alarm_with_impacted_services():
    client = make_client(InMemoryAlarmStore())
    body = {
        **make_network_alarm(),
        "alarm_category": "database",
        "extension": {
            "category": "database",
            "impacted_services": [
                {"id": "svc_001", "label": "Billing Dashboard"},
                {"id": "svc_002", "label": "Customer Portal"},
            ],
        },
    }

    response = client.post("/alarms", json=body)

    assert response.status_code == 201
    svcs = response.json()["extension"]["impacted_services"]
    assert len(svcs) == 2
    assert svcs[0]["label"] == "Billing Dashboard"


def test_post_security_cve_alarm_with_scores():
    client = make_client(InMemoryAlarmStore())
    body = {
        **make_network_alarm(),
        "alarm_category": "security",
        "extension": {
            "category": "security",
            "security_type": "cve",
            "cve_id": "CVE-2024-12345",
            "affected_software": "openssl",
            "affected_version": "3.0.1",
            "scores": [
                {"method": "cvss", "value": 9.8, "scale": "0-10"},
            ],
        },
    }

    response = client.post("/alarms", json=body)

    assert response.status_code == 201
    ext = response.json()["extension"]
    assert ext["cve_id"] == "CVE-2024-12345"
    assert ext["scores"][0]["method"] == "cvss"


# --- filters ---

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


# --- PATCH /alarms/{id}/state ---

def test_valid_state_transition_returns_updated_alarm():
    client = make_client(InMemoryAlarmStore())
    created = client.post("/alarms", json=make_network_alarm()).json()
    alarm_id = created["id"]

    response = client.patch(f"/alarms/{alarm_id}/state", json={"state": "acknowledged"})

    assert response.status_code == 200
    assert response.json()["alarm_state"] == "acknowledged"
    assert response.json()["id"] == alarm_id


def test_invalid_state_transition_returns_422():
    client = make_client(InMemoryAlarmStore())
    alarm_id = client.post("/alarms", json=make_network_alarm()).json()["id"]

    response = client.patch(f"/alarms/{alarm_id}/state", json={"state": "raised"})

    assert response.status_code == 422


def test_transitioning_cleared_alarm_returns_422():
    client = make_client(InMemoryAlarmStore())
    alarm_id = client.post("/alarms", json=make_network_alarm()).json()["id"]
    client.patch(f"/alarms/{alarm_id}/state", json={"state": "cleared"})

    response = client.patch(f"/alarms/{alarm_id}/state", json={"state": "acknowledged"})

    assert response.status_code == 422


def test_transition_unknown_alarm_returns_404():
    client = make_client(InMemoryAlarmStore())

    response = client.patch("/alarms/alm_unknown/state", json={"state": "acknowledged"})

    assert response.status_code == 404


def test_updated_at_changes_after_transition():
    client = make_client(InMemoryAlarmStore())
    created = client.post("/alarms", json=make_network_alarm()).json()
    original_updated_at = created["updated_at"]

    updated = client.patch(f"/alarms/{created['id']}/state", json={"state": "acknowledged"}).json()

    assert updated["updated_at"] != original_updated_at


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
