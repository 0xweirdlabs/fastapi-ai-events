from enum import StrEnum
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AlarmCategory(StrEnum):
    NETWORK = "network"
    SECURITY = "security"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    DATABASE = "database"
    SERVICE = "service"
    STORAGE = "storage"
    KUBERNETES = "kubernetes"
    HOST = "host"


class Severity(StrEnum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    WARNING = "warning"
    INDETERMINATE = "indeterminate"
    CLEARED = "cleared"


class AlarmState(StrEnum):
    RAISED = "raised"
    ACKNOWLEDGED = "acknowledged"
    ESCALATED = "escalated"
    SUPPRESSED = "suppressed"
    IN_MAINTENANCE = "in_maintenance"
    CLEARED = "cleared"


class ManagedObjectIdentifier(BaseModel):
    key: str
    value: str


class ManagedObject(BaseModel):
    label: str
    type: str
    identifiers: list[ManagedObjectIdentifier] = Field(default_factory=list)
    ci_id: str | None = None


class AlarmCreate(BaseModel):
    alarm_category: AlarmCategory
    perceived_severity: Severity
    alarm_state: AlarmState = AlarmState.RAISED
    alarm_raised_time: datetime
    managed_object: ManagedObject
    parent_alarm_id: str | None = None


VALID_TRANSITIONS: dict[AlarmState, set[AlarmState]] = {
    AlarmState.RAISED: {AlarmState.ACKNOWLEDGED, AlarmState.ESCALATED, AlarmState.SUPPRESSED, AlarmState.IN_MAINTENANCE, AlarmState.CLEARED},
    AlarmState.ACKNOWLEDGED: {AlarmState.ESCALATED, AlarmState.CLEARED},
    AlarmState.ESCALATED: {AlarmState.ACKNOWLEDGED, AlarmState.CLEARED},
    AlarmState.SUPPRESSED: {AlarmState.RAISED, AlarmState.CLEARED},
    AlarmState.IN_MAINTENANCE: {AlarmState.RAISED},
    AlarmState.CLEARED: set(),
}


class Alarm(BaseModel):
    id: str = Field(default_factory=lambda: f"alm_{uuid.uuid4().hex[:8]}")
    alarm_category: AlarmCategory
    perceived_severity: Severity
    alarm_state: AlarmState
    alarm_raised_time: datetime
    updated_at: datetime = Field(default_factory=_now)
    managed_object: ManagedObject
    parent_alarm_id: str | None = None
