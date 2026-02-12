"""
Event-Activity Network (EAN)
Phase 1: Deterministic structural model only

Based on:
- Schöbel, Public Transportation, Chapter 6
"""

from dataclasses import dataclass
from typing import Dict, List


# =========================
# Core Data Structures
# =========================

@dataclass
class Event:
    """An event represents an arrival or departure at a station."""
    event_id: int
    station: str
    event_type: str  # 'arrival' or 'departure'
    planned_time: float


@dataclass
class Activity:
    """An activity connects two events with a minimum duration."""
    activity_id: int
    activity_type: str  # 'drive', 'wait', 'transfer'
    from_event: int
    to_event: int
    min_duration: float


# =========================
# Event-Activity Network
# =========================

class EventActivityNetwork:
    """Deterministic Event-Activity Network (EAN)."""

    def __init__(self):
        self.events: Dict[int, Event] = {}
        self.activities: Dict[int, Activity] = {}

        self._event_counter = 0
        self._activity_counter = 0

    # ---------
    # Add nodes
    # ---------

    def add_event(self, station: str, event_type: str, planned_time: float) -> int:
        event_id = self._event_counter
        self.events[event_id] = Event(
            event_id=event_id,
            station=station,
            event_type=event_type,
            planned_time=planned_time,
        )
        self._event_counter += 1
        return event_id

    # ---------
    # Add edges
    # ---------

    def add_activity(
        self,
        activity_type: str,
        from_event: int,
        to_event: int,
        min_duration: float,
    ) -> int:
        activity_id = self._activity_counter
        self.activities[activity_id] = Activity(
            activity_id=activity_id,
            activity_type=activity_type,
            from_event=from_event,
            to_event=to_event,
            min_duration=min_duration,
        )
        self._activity_counter += 1
        return activity_id

    # ---------
    # Queries
    # ---------

    def get_outgoing_activities(self, event_id: int) -> List[Activity]:
        return [a for a in self.activities.values() if a.from_event == event_id]

    def get_incoming_activities(self, event_id: int) -> List[Activity]:
        return [a for a in self.activities.values() if a.to_event == event_id]

    # ---------
    # Debug / inspection
    # ---------

    def summary(self) -> None:
        print("Event-Activity Network Summary")
        print(f"Number of events: {len(self.events)}")
        print(f"Number of activities: {len(self.activities)}")
