from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Event:
    event_id: int
    station: str
    event_type: str  # arrival or departure
    planned_time: float


@dataclass(frozen=True)
class Activity:
    activity_id: int
    activity_type: str  # drive, wait, transfer
    from_event: int
    to_event: int
    min_duration: float
    controllable: bool = False


class EventActivityNetwork:
    def __init__(self) -> None:
        self.events: Dict[int, Event] = {}
        self.activities: Dict[int, Activity] = {}
        self._event_counter = 0
        self._activity_counter = 0

    def add_event(self, station: str, event_type: str, planned_time: float) -> int:
        if event_type not in {"arrival", "departure"}:
            raise ValueError(f"invalid event_type={event_type}")
        event_id = self._event_counter
        self.events[event_id] = Event(
            event_id=event_id,
            station=station,
            event_type=event_type,
            planned_time=planned_time,
        )
        self._event_counter += 1
        return event_id

    def add_activity(
        self,
        activity_type: str,
        from_event: int,
        to_event: int,
        min_duration: float,
        controllable: bool = False,
    ) -> int:
        if activity_type not in {"drive", "wait", "transfer"}:
            raise ValueError(f"invalid activity_type={activity_type}")
        if from_event not in self.events or to_event not in self.events:
            raise ValueError("activity endpoints must exist")
        activity_id = self._activity_counter
        self.activities[activity_id] = Activity(
            activity_id=activity_id,
            activity_type=activity_type,
            from_event=from_event,
            to_event=to_event,
            min_duration=float(min_duration),
            controllable=controllable,
        )
        self._activity_counter += 1
        return activity_id

    def outgoing(self, event_id: int) -> List[Activity]:
        return [a for a in self.activities.values() if a.from_event == event_id]

    def incoming(self, event_id: int) -> List[Activity]:
        return [a for a in self.activities.values() if a.to_event == event_id]

    def station_departures(self, station: str) -> List[int]:
        return [
            eid
            for eid, e in self.events.items()
            if e.station == station and e.event_type == "departure"
        ]

    def station_arrivals(self, station: str) -> List[int]:
        return [
            eid
            for eid, e in self.events.items()
            if e.station == station and e.event_type == "arrival"
        ]
