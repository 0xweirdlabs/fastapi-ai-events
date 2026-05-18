from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from ..models.alarm import Alarm, AlarmCategory, AlarmState, Severity
from ..store import InMemoryAlarmStore, get_alarm_store

router = APIRouter(prefix="/agent/alarms", tags=["agent"])


class AgentManagedObject(BaseModel):
    lbl: str
    typ: str


class AgentAlarm(BaseModel):
    id: str
    cat: str
    sev: str
    st: str
    ts: str
    obj: AgentManagedObject
    par: str | None = None
    ext: dict | None = None

    @classmethod
    def from_alarm(cls, alarm: Alarm) -> "AgentAlarm":
        return cls(
            id=alarm.id,
            cat=alarm.alarm_category,
            sev=alarm.perceived_severity,
            st=alarm.alarm_state,
            ts=alarm.alarm_raised_time.isoformat().replace("+00:00", "Z"),
            obj=AgentManagedObject(
                lbl=alarm.managed_object.label,
                typ=alarm.managed_object.type,
            ),
            par=alarm.parent_alarm_id,
            ext=alarm.extension.to_compact_dict() if alarm.extension else None,
        )


class AgentAlarmListResponse(BaseModel):
    alarms: list[AgentAlarm]
    cursor: str | None = None
    total: int


class AgentDeltaResponse(BaseModel):
    alarms: list[AgentAlarm]
    cursor: str | None = None
    total: int


class BatchQueryRequest(BaseModel):
    severity: list[Severity] | None = None
    category: list[AlarmCategory] | None = None
    state: list[AlarmState] | None = None
    limit: int = Field(default=50, ge=1, le=500)


@router.post("/get-many", response_model=AgentAlarmListResponse)
def agent_get_many(
    body: BatchQueryRequest,
    store: InMemoryAlarmStore = Depends(get_alarm_store),
) -> AgentAlarmListResponse:
    alarms = store.list_many(
        categories=body.category,
        severities=body.severity,
        states=body.state,
        limit=body.limit,
    )
    return AgentAlarmListResponse(
        alarms=[AgentAlarm.from_alarm(a) for a in alarms],
        cursor=None,
        total=len(alarms),
    )


@router.get("/delta", response_model=AgentDeltaResponse)
def agent_delta(
    since: datetime = Query(...),
    cursor: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    store: InMemoryAlarmStore = Depends(get_alarm_store),
) -> AgentDeltaResponse:
    alarms, next_cursor = store.list_since(since=since, cursor=cursor, limit=limit)
    return AgentDeltaResponse(
        alarms=[AgentAlarm.from_alarm(a) for a in alarms],
        cursor=next_cursor.isoformat() if next_cursor else None,
        total=len(alarms),
    )


@router.get("", response_model=AgentAlarmListResponse)
def agent_list_alarms(
    category: AlarmCategory | None = Query(None),
    severity: Severity | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    store: InMemoryAlarmStore = Depends(get_alarm_store),
) -> AgentAlarmListResponse:
    alarms = store.list_alarms(category=category, severity=severity)
    return AgentAlarmListResponse(
        alarms=[AgentAlarm.from_alarm(a) for a in alarms[:limit]],
        cursor=None,
        total=len(alarms),
    )
