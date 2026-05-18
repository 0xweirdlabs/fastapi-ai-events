from datetime import datetime, timezone
from .models.alarm import Alarm, AlarmCreate, AlarmCategory, AlarmState, Severity


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

    def list_correlated(self, parent_id: str) -> list[Alarm]:
        return [a for a in self._alarms if a.parent_alarm_id == parent_id]

    def list_many(
        self,
        categories: list[AlarmCategory] | None = None,
        severities: list[Severity] | None = None,
        states: list[AlarmState] | None = None,
        limit: int = 50,
    ) -> list[Alarm]:
        results = self._alarms
        if categories:
            results = [a for a in results if a.alarm_category in categories]
        if severities:
            results = [a for a in results if a.perceived_severity in severities]
        if states:
            results = [a for a in results if a.alarm_state in states]
        return results[:limit]

    def list_since(
        self,
        since: datetime,
        cursor: datetime | None = None,
        limit: int = 50,
    ) -> tuple[list[Alarm], datetime | None]:
        cutoff = cursor if cursor is not None else since
        results = sorted(
            [a for a in self._alarms if a.updated_at > cutoff],
            key=lambda a: a.updated_at,
        )
        has_more = len(results) > limit
        page = results[:limit]
        next_cursor = page[-1].updated_at if has_more else None
        return page, next_cursor

    def transition_state(self, alarm_id: str, new_state: AlarmState) -> Alarm:
        alarm = self.get_by_id(alarm_id)
        if alarm is None:
            raise KeyError(alarm_id)
        alarm.alarm_state = new_state
        alarm.updated_at = datetime.now(timezone.utc)
        return alarm


def get_alarm_store() -> InMemoryAlarmStore:
    return InMemoryAlarmStore()
