from src.network import EventActivityNetwork
from src.simulation import compute_earliest_times
from src.metrics import compute_activity_slack, critical_activities


def main():
    # 1. Create network
    ean = EventActivityNetwork()

    # 2. Add events (arrival / departure)
    e_dep_A = ean.add_event("A", "departure", 0.0)
    e_arr_B = ean.add_event("B", "arrival", 10.0)
    e_dep_B = ean.add_event("B", "departure", 12.0)
    e_arr_C = ean.add_event("C", "arrival", 25.0)

    # 3. Add activities
    ean.add_activity("drive", e_dep_A, e_arr_B, min_duration=10.0)
    ean.add_activity("wait", e_arr_B, e_dep_B, min_duration=2.0)
    ean.add_activity("drive", e_dep_B, e_arr_C, min_duration=13.0)

    # 4. Inspect structure (Phase 1 check)
    print("=== EVENTS ===")
    for e in ean.events.values():
        print(e)

    print("\n=== ACTIVITIES ===")
    for a in ean.activities.values():
        print(a)

    print("\n=== OUTGOING from B arrival ===")
    for a in ean.get_outgoing_activities(e_arr_B):
        print(a)

    # 5. Phase 2: compute earliest feasible times
    print("\n=== Phase 2: Earliest feasible times (source A departure +5) ===")

   
    times = compute_earliest_times(
        ean,
        source_event=e_dep_A,
        source_delay=5.0
    )

    for eid in sorted(times):
        e = ean.events[eid]
        print(
            f"Event {eid}: {e.station} {e.event_type} | "
            f"planned={e.planned_time} -> realized={times[eid]}"
        )
    
    print("\n=== Phase 2.5: Activity slacks ===")
    slacks = compute_activity_slack(ean, times)
    for aid in sorted(slacks):
        act = ean.activities[aid]
        print(
            f"Activity {aid} ({act.activity_type} {act.from_event}->{act.to_event}): "
            f"min_dur={act.min_duration} slack={slacks[aid]}"
        )

    crit = critical_activities(slacks)
    print(f"\nCritical activities: {crit}")
   

if __name__ == "__main__":
    main()
