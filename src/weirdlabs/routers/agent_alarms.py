from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from ..models.alarm import Alarm, AlarmCategory, Severity
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
        )


class AgentAlarmListResponse(BaseModel):
    alarms: list[AgentAlarm]
    cursor: str | None = None
    total: int


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
