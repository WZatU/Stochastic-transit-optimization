from __future__ import annotations

from typing import Dict, Iterable, Set

from src.ean import EventActivityNetwork


def compute_realized_times(
    ean: EventActivityNetwork,
    arrival_source_delay: Dict[int, float],
    inactive_activities: Set[int] | None = None,
) -> Dict[int, float]:
    """
    Feasibility propagation under x[j] >= x[i] + l_ij.

    arrival_source_delay applies only on arrival events:
    x[i] initialized as planned_time + delay(i).
    """
    if inactive_activities is None:
        inactive_activities = set()

    x = {
        eid: e.planned_time + arrival_source_delay.get(eid, 0.0)
        for eid, e in ean.events.items()
    }

    # Bellman-Ford style relaxation; acyclic timetable means it converges quickly.
    n = len(ean.events)
    for _ in range(n):
        changed = False
        for aid, a in ean.activities.items():
            if aid in inactive_activities:
                continue
            candidate = x[a.from_event] + a.min_duration
            if candidate > x[a.to_event]:
                x[a.to_event] = candidate
                changed = True
        if not changed:
            break

    return x


def activity_slack(ean: EventActivityNetwork) -> Dict[int, float]:
    slacks: Dict[int, float] = {}
    for aid, a in ean.activities.items():
        from_t = ean.events[a.from_event].planned_time
        to_t = ean.events[a.to_event].planned_time
        slacks[aid] = (to_t - from_t) - a.min_duration
    return slacks


def controllable_activities(ean: EventActivityNetwork) -> Iterable[int]:
    return [aid for aid, a in ean.activities.items() if a.controllable]
