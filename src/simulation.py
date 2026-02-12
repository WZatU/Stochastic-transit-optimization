from collections import deque
from typing import Dict

from src.network import EventActivityNetwork


def compute_earliest_times(
    ean: EventActivityNetwork,
    source_event: int,
    source_delay: float = 0.0,
) -> Dict[int, float]:
    """
    Phase 2: Compute earliest feasible event times under EAN constraints.

    Initialization:
        x[i] = planned_time[i] for all events i
        x[source] += source_delay

    For each activity a = (i -> j):
        x[j] >= x[i] + min_duration[a]

    Returns:
        dict: event_id -> earliest feasible time
    """
    x = {eid: e.planned_time for eid, e in ean.events.items()}
    x[source_event] = x[source_event] + source_delay

    q = deque([source_event])
    in_q = {source_event}

    while q:
        i = q.popleft()
        in_q.discard(i)

        for act in ean.get_outgoing_activities(i):
            j = act.to_event
            candidate = x[i] + act.min_duration

            if candidate > x[j]:
                x[j] = candidate
                if j not in in_q:
                    q.append(j)
                    in_q.add(j)

    return x
