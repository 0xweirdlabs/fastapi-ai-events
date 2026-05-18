from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from ..models.alarm import Alarm, AlarmCreate, AlarmCategory, AlarmState, Severity, VALID_TRANSITIONS
from ..store import InMemoryAlarmStore, get_alarm_store

router = APIRouter(prefix="/alarms", tags=["alarms"])


class Pagination(BaseModel):
    page: int
    page_size: int
    total: int


class AlarmListResponse(BaseModel):
    alarms: list[Alarm]
    pagination: Pagination


class StateTransitionRequest(BaseModel):
    state: AlarmState


@router.patch("/{alarm_id}/state", response_model=Alarm)
def transition_alarm_state(
    alarm_id: str,
    body: StateTransitionRequest,
    store: InMemoryAlarmStore = Depends(get_alarm_store),
) -> Alarm:
    alarm = store.get_by_id(alarm_id)
    if alarm is None:
        raise HTTPException(status_code=404, detail=f"Alarm {alarm_id} not found")
    if body.state not in VALID_TRANSITIONS[alarm.alarm_state]:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot transition from '{alarm.alarm_state}' to '{body.state}'",
        )
    return store.transition_state(alarm_id, body.state)


@router.post("", response_model=Alarm, status_code=201)
def create_alarm(
    payload: AlarmCreate,
    store: InMemoryAlarmStore = Depends(get_alarm_store),
) -> Alarm:
    return store.create_alarm(payload)


@router.get("", response_model=AlarmListResponse)
def list_alarms(
    category: AlarmCategory | None = Query(None),
    severity: Severity | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    store: InMemoryAlarmStore = Depends(get_alarm_store),
) -> AlarmListResponse:
    alarms = store.list_alarms(category=category, severity=severity)
    total = len(alarms)
    start = (page - 1) * page_size
    return AlarmListResponse(
        alarms=alarms[start : start + page_size],
        pagination=Pagination(page=page, page_size=page_size, total=total),
    )
