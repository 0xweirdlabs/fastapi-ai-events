from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


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


class Alarm(BaseModel):
    id: str = Field(default_factory=lambda: f"alm_{uuid.uuid4().hex[:8]}")
    alarm_category: AlarmCategory
    perceived_severity: Severity
    alarm_state: AlarmState
    alarm_raised_time: datetime
    managed_object: ManagedObject
    parent_alarm_id: str | None = None
