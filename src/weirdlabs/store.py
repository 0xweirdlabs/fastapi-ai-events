from datetime import datetime, timezone
from .models.alarm import Alarm, AlarmCreate, AlarmCategory, Severity, AlarmState


class InMemoryAlarmStore:
    def __init__(self) -> None:
        self._alarms: list[Alarm] = []

    def list_alarms(
        self,
        category: AlarmCategory | None = None,
        severity: Severity | None = None,
    ) -> list[Alarm]:
        alarms = self._alarms
        if category:
            alarms = [a for a in alarms if a.alarm_category == category]
        if severity:
            alarms = [a for a in alarms if a.perceived_severity == severity]
        return alarms

    def add_alarm(self, alarm: Alarm) -> None:
        self._alarms.append(alarm)

    def create_alarm(self, payload: AlarmCreate) -> Alarm:
        alarm = Alarm(**payload.model_dump())
        self._alarms.append(alarm)
        return alarm

    def get_by_id(self, alarm_id: str) -> Alarm | None:
        return next((a for a in self._alarms if a.id == alarm_id), None)

    def transition_state(self, alarm_id: str, new_state: AlarmState) -> Alarm:
        alarm = self.get_by_id(alarm_id)
        if alarm is None:
            raise KeyError(alarm_id)
        alarm.alarm_state = new_state
        alarm.updated_at = datetime.now(timezone.utc)
        return alarm


def get_alarm_store() -> InMemoryAlarmStore:
    return InMemoryAlarmStore()
