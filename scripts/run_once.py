#!/usr/bin/env python3
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.ean import EventActivityNetwork
from src.metrics import compute_activity_slack, critical_activities
from src.propagation import compute_earliest_times


def main() -> None:
    ean = EventActivityNetwork()

    e_dep_a = ean.add_event("A", "departure", 0.0)
    e_arr_b = ean.add_event("B", "arrival", 10.0)
    e_dep_b = ean.add_event("B", "departure", 12.0)
    e_arr_c = ean.add_event("C", "arrival", 25.0)

    ean.add_activity("drive", e_dep_a, e_arr_b, min_duration=10.0)
    ean.add_activity("wait", e_arr_b, e_dep_b, min_duration=2.0)
    ean.add_activity("drive", e_dep_b, e_arr_c, min_duration=13.0)

    print("=== EVENTS ===")
    for event in ean.events.values():
        print(event)

    print("\n=== ACTIVITIES ===")
    for activity in ean.activities.values():
        print(activity)

    print("\n=== OUTGOING from B arrival ===")
    for activity in ean.outgoing(e_arr_b):
        print(activity)

    print("\n=== Phase 2: Earliest feasible times (source A departure +5) ===")
    times = compute_earliest_times(ean, source_event=e_dep_a, source_delay=5.0)

    for eid in sorted(times):
        event = ean.events[eid]
        print(
            f"Event {eid}: {event.station} {event.event_type} | "
            f"planned={event.planned_time} -> realized={times[eid]}"
        )

    print("\n=== Phase 2.5: Activity slacks ===")
    slacks = compute_activity_slack(ean, times)
    for aid in sorted(slacks):
        activity = ean.activities[aid]
        print(
            f"Activity {aid} ({activity.activity_type} {activity.from_event}->{activity.to_event}): "
            f"min_dur={activity.min_duration} slack={slacks[aid]}"
        )

    critical = critical_activities(slacks)
    print(f"\nCritical activities: {critical}")


if __name__ == "__main__":
    main()
