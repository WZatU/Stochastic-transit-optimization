"""
Event-Activity Network (EAN) implementation for transit simulation.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum


class EventType(Enum):
    """Type of transit event."""
    ARRIVAL = "arrival"
    DEPARTURE = "departure"


class ActivityType(Enum):
    """Type of activity connecting events."""
    TRAVEL = "travel"  # Travel between stations
    DWELL = "dwell"    # Dwell time at a station
    TRANSFER = "transfer"  # Transfer between lines


@dataclass
class Event:
    """
    Represents a transit event (arrival or departure).
    
    Attributes:
        id: Unique identifier for the event
        event_type: Type of event (arrival/departure)
        station: Station where event occurs
        line: Transit line
        scheduled_time: Planned time for the event
        actual_time: Actual time (scheduled + delay)
        delay: Delay in minutes
    """
    id: int
    event_type: EventType
    station: str
    line: str
    scheduled_time: float
    actual_time: float = None
    delay: float = 0.0
    
    def __post_init__(self):
        if self.actual_time is None:
            self.actual_time = self.scheduled_time


@dataclass
class Activity:
    """
    Represents an activity connecting two events.
    
    Attributes:
        id: Unique identifier for the activity
        activity_type: Type of activity
        source_event: Source event ID
        target_event: Target event ID
        min_duration: Minimum duration (lower bound)
        max_duration: Maximum duration (upper bound, for wait activities)
    """
    id: int
    activity_type: ActivityType
    source_event: int
    target_event: int
    min_duration: float
    max_duration: float = None


class EAN:
    """
    Event-Activity Network representation.
    
    The EAN models a transit network as a directed graph where:
    - Nodes represent events (arrivals/departures)
    - Edges represent activities (travel, dwell, transfer)
    """
    
    def __init__(self):
        self.events: Dict[int, Event] = {}
        self.activities: Dict[int, Activity] = {}
        self.event_counter = 0
        self.activity_counter = 0
    
    def add_event(self, event_type: EventType, station: str, line: str, 
                  scheduled_time: float) -> int:
        """Add an event to the network."""
        event_id = self.event_counter
        self.event_counter += 1
        
        event = Event(
            id=event_id,
            event_type=event_type,
            station=station,
            line=line,
            scheduled_time=scheduled_time
        )
        self.events[event_id] = event
        return event_id
    
    def add_activity(self, activity_type: ActivityType, source_event: int,
                     target_event: int, min_duration: float, 
                     max_duration: float = None) -> int:
        """Add an activity to the network."""
        activity_id = self.activity_counter
        self.activity_counter += 1
        
        activity = Activity(
            id=activity_id,
            activity_type=activity_type,
            source_event=source_event,
            target_event=target_event,
            min_duration=min_duration,
            max_duration=max_duration
        )
        self.activities[activity_id] = activity
        return activity_id
    
    def get_outgoing_activities(self, event_id: int) -> List[Activity]:
        """Get all activities starting from an event."""
        return [a for a in self.activities.values() if a.source_event == event_id]
    
    def get_incoming_activities(self, event_id: int) -> List[Activity]:
        """Get all activities ending at an event."""
        return [a for a in self.activities.values() if a.target_event == event_id]
    
    def reset_delays(self):
        """Reset all delays to zero."""
        for event in self.events.values():
            event.delay = 0.0
            event.actual_time = event.scheduled_time
