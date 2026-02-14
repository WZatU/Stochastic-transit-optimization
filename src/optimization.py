from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Dict, List

from src.ean import EventActivityNetwork
from src.propagation import activity_slack

try:
    import pulp
except Exception:  # pragma: no cover
    pulp = None


@dataclass
class TdmBResult:
    wait_decisions: Dict[int, int]  # transfer activity id -> 0/1
    objective: float
    backend: str


def _build_lp_with_pulp(
    transfer_ids: List[int],
    incoming_delay: Dict[int, float],
    transfer_load: Dict[int, float],
    slack: Dict[int, float],
    penalty_t: float,
) -> TdmBResult:
    model = pulp.LpProblem("tdm_b", pulp.LpMinimize)
    z = {aid: pulp.LpVariable(f"z_{aid}", lowBound=0, upBound=1, cat="Binary") for aid in transfer_ids}
    q = {aid: pulp.LpVariable(f"q_{aid}", lowBound=0) for aid in transfer_ids}

    big_m = max(60.0, max(incoming_delay.values() or [0.0]) + 60.0)

    for aid in transfer_ids:
        model += q[aid] >= incoming_delay[aid] - slack[aid] - big_m * (1 - z[aid])

    model += pulp.lpSum(
        transfer_load[aid] * q[aid] + penalty_t * transfer_load[aid] * (1 - z[aid])
        for aid in transfer_ids
    )

    model.solve(pulp.PULP_CBC_CMD(msg=False))

    decisions = {aid: int(round(z[aid].value())) for aid in transfer_ids}
    objective = float(pulp.value(model.objective))
    return TdmBResult(wait_decisions=decisions, objective=objective, backend="pulp")


def _solve_by_enumeration(
    transfer_ids: List[int],
    incoming_delay: Dict[int, float],
    transfer_load: Dict[int, float],
    slack: Dict[int, float],
    penalty_t: float,
) -> TdmBResult:
    best_obj = float("inf")
    best = None

    for bits in itertools.product([0, 1], repeat=len(transfer_ids)):
        z = dict(zip(transfer_ids, bits))
        obj = 0.0
        for aid in transfer_ids:
            q = max(0.0, incoming_delay[aid] - slack[aid]) if z[aid] == 1 else 0.0
            obj += transfer_load[aid] * q + penalty_t * transfer_load[aid] * (1 - z[aid])
        if obj < best_obj:
            best_obj = obj
            best = z

    return TdmBResult(wait_decisions=best or {}, objective=best_obj, backend="enumeration")


def solve_tdm_b(
    ean: EventActivityNetwork,
    transfer_ids: List[int],
    pre_control_times: Dict[int, float],
    transfer_load: Dict[int, float],
    penalty_t: float,
) -> TdmBResult:
    slack = activity_slack(ean)
    incoming_delay = {}
    for aid in transfer_ids:
        a = ean.activities[aid]
        planned = ean.events[a.from_event].planned_time
        incoming_delay[aid] = max(0.0, pre_control_times[a.from_event] - planned)

    if pulp is not None:
        return _build_lp_with_pulp(transfer_ids, incoming_delay, transfer_load, slack, penalty_t)

    return _solve_by_enumeration(transfer_ids, incoming_delay, transfer_load, slack, penalty_t)
