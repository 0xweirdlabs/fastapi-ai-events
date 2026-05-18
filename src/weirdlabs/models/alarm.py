from enum import StrEnum
from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator
import uuid
from .extensions import AlarmExtension


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


def _validate_extension_category(alarm_category: str, extension: Any) -> None:
    if extension is not None and extension.category != alarm_category:
        raise ValueError(
            f"Extension category '{extension.category}' does not match alarm_category '{alarm_category}'"
        )


class AlarmCreate(BaseModel):
    alarm_category: AlarmCategory
    perceived_severity: Severity
    alarm_state: AlarmState = AlarmState.RAISED
    alarm_raised_time: datetime
    managed_object: ManagedObject
    parent_alarm_id: str | None = None
    extension: AlarmExtension | None = None

    @model_validator(mode="after")
    def extension_matches_category(self) -> "AlarmCreate":
        _validate_extension_category(self.alarm_category, self.extension)
        return self


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
    extension: AlarmExtension | None = None

    @model_validator(mode="after")
    def extension_matches_category(self) -> "Alarm":
        _validate_extension_category(self.alarm_category, self.extension)
        return self
