from typing import Dict, List

from src.network import EventActivityNetwork


def compute_activity_slack(
    ean: EventActivityNetwork,
    times: Dict[int, float],
) -> Dict[int, float]:
    """
    Phase 2.5: Slack per activity.

    slack(a) = (times[to] - times[from]) - min_duration
    """
    slacks: Dict[int, float] = {}
    for aid, act in ean.activities.items():
        slacks[aid] = (times[act.to_event] - times[act.from_event]) - act.min_duration
    return slacks


def critical_activities(slacks: Dict[int, float], eps: float = 1e-9) -> List[int]:
    """
    Activity is critical if slack <= eps (numerical tolerance).
    """
    return [aid for aid, s in slacks.items() if s <= eps]
