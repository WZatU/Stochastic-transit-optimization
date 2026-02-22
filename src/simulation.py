from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

from src.delays import sample_arrival_delays
from src.demo_network import ODMatrix, build_demo_network
from src.ean import EventActivityNetwork
from src.optimization import solve_tdm_b
from src.propagation import compute_realized_times
from src.routing import assign_flows


@dataclass
class PolicyOutcome:
    name: str
    total_passenger_delay: float
    miss_rate: float
    door_to_door: float


def _baseline_planned_travel(
    ean: EventActivityNetwork,
    od: ODMatrix,
) -> Tuple[Dict[Tuple[str, str], float], Dict[int, float], float]:
    planned_times = {eid: e.planned_time for eid, e in ean.events.items()}
    loads, travel, _ = assign_flows(ean, od, planned_times)

    transfer_demand = 0.0
    for aid, load in loads.items():
        if ean.activities[aid].controllable:
            transfer_demand += load

    return travel, loads, transfer_demand


def _evaluate_policy(
    ean: EventActivityNetwork,
    od: ODMatrix,
    planned_travel: Dict[Tuple[str, str], float],
    transfer_ids: List[int],
    transfer_base_load: Dict[int, float],
    transfer_total_demand: float,
    sampled_delay: Dict[int, float],
    decision: Dict[int, int],
    unserved_penalty: float,
) -> PolicyOutcome:
    inactive = {aid for aid in transfer_ids if decision.get(aid, 1) == 0}
    realized = compute_realized_times(ean, sampled_delay, inactive_activities=inactive)
    _, travel, _ = assign_flows(
        ean,
        od,
        realized,
        inactive_activities=inactive,
        unserved_penalty=unserved_penalty,
    )

    total_delay = 0.0
    total_d2d = 0.0
    total_pax = sum(od.values())
    for pair, demand in od.items():
        base = planned_travel[pair]
        cur = travel[pair]
        total_delay += demand * max(0.0, cur - base)
        total_d2d += demand * cur

    broken = sum(transfer_base_load.get(aid, 0.0) for aid in inactive)
    miss_rate = 0.0 if transfer_total_demand <= 0 else broken / transfer_total_demand
    avg_d2d = total_d2d / total_pax if total_pax > 0 else 0.0

    return PolicyOutcome(
        name="",
        total_passenger_delay=total_delay,
        miss_rate=miss_rate,
        door_to_door=avg_d2d,
    )


def run_monte_carlo(
    n: int = 300,
    dist: str = "exp",
    seed: int = 7,
    penalty_t: float = 12.0,
    rule_threshold: float = 3.0,
    unserved_penalty: float = 60.0,
) -> dict:
    if n <= 0:
        raise ValueError("n must be positive")

    ean, od, transfer_ids = build_demo_network()
    planned_travel, base_loads, transfer_total = _baseline_planned_travel(ean, od)
    transfer_load = {aid: base_loads.get(aid, 0.0) for aid in transfer_ids}

    rng = random.Random(seed)

    agg = {
        "no_management": {"delay": 0.0, "miss": 0.0, "d2d": 0.0},
        "rule_based": {"delay": 0.0, "miss": 0.0, "d2d": 0.0},
        "lp_based": {"delay": 0.0, "miss": 0.0, "d2d": 0.0},
    }

    solver_backend = "unknown"

    for _ in range(n):
        sampled = sample_arrival_delays(ean, dist=dist, rng=rng)

        pre_control = compute_realized_times(ean, sampled, inactive_activities=set())

        no_decision = {aid: 0 for aid in transfer_ids}
        rule_decision = {}
        for aid in transfer_ids:
            a = ean.activities[aid]
            incoming_delay = max(
                0.0, pre_control[a.from_event] - ean.events[a.from_event].planned_time
            )
            rule_decision[aid] = 1 if incoming_delay <= rule_threshold else 0

        lp = solve_tdm_b(
            ean,
            transfer_ids=transfer_ids,
            pre_control_times=pre_control,
            transfer_load=transfer_load,
            penalty_t=penalty_t,
        )
        solver_backend = lp.backend

        out_no = _evaluate_policy(
            ean,
            od,
            planned_travel,
            transfer_ids,
            transfer_load,
            transfer_total,
            sampled,
            no_decision,
            unserved_penalty,
        )
        out_rule = _evaluate_policy(
            ean,
            od,
            planned_travel,
            transfer_ids,
            transfer_load,
            transfer_total,
            sampled,
            rule_decision,
            unserved_penalty,
        )
        out_lp = _evaluate_policy(
            ean,
            od,
            planned_travel,
            transfer_ids,
            transfer_load,
            transfer_total,
            sampled,
            lp.wait_decisions,
            unserved_penalty,
        )

        agg["no_management"]["delay"] += out_no.total_passenger_delay
        agg["no_management"]["miss"] += out_no.miss_rate
        agg["no_management"]["d2d"] += out_no.door_to_door

        agg["rule_based"]["delay"] += out_rule.total_passenger_delay
        agg["rule_based"]["miss"] += out_rule.miss_rate
        agg["rule_based"]["d2d"] += out_rule.door_to_door

        agg["lp_based"]["delay"] += out_lp.total_passenger_delay
        agg["lp_based"]["miss"] += out_lp.miss_rate
        agg["lp_based"]["d2d"] += out_lp.door_to_door

    scenarios = []
    for key in ["no_management", "rule_based", "lp_based"]:
        scenarios.append(
            {
                "scenario": key,
                "avg_delay": round(agg[key]["delay"] / n, 3),
                "miss_rate": round(agg[key]["miss"] / n, 3),
                "avg_door_to_door": round(agg[key]["d2d"] / n, 3),
            }
        )

    return {
        "meta": {
            "runs": n,
            "distribution": dist,
            "solver_backend": solver_backend,
            "penalty_t": penalty_t,
            "seed": seed,
        },
        "scenarios": scenarios,
    }
