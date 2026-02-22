from src.demo_network import build_demo_network
from src.optimization import solve_tdm_b
from src.propagation import activity_slack, compute_earliest_times, compute_realized_times
from src.simulation import run_monte_carlo


def _scenarios_by_name(result: dict) -> dict:
    return {item["scenario"]: item for item in result["scenarios"]}


def test_policy_ranking_is_reasonable() -> None:
    out = run_monte_carlo(n=120, dist="exp", seed=7)
    s = _scenarios_by_name(out)

    assert s["rule_based"]["avg_delay"] <= s["no_management"]["avg_delay"]
    assert s["lp_based"]["avg_delay"] <= s["rule_based"]["avg_delay"]

    assert s["rule_based"]["miss_rate"] <= s["no_management"]["miss_rate"]
    assert s["lp_based"]["miss_rate"] <= s["rule_based"]["miss_rate"]


def test_invalid_monte_carlo_runs() -> None:
    try:
        run_monte_carlo(n=0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_phase2_compatibility_api() -> None:
    ean, _, _ = build_demo_network()
    source_event = 0
    x = compute_earliest_times(ean, source_event=source_event, source_delay=5.0)
    assert x[source_event] == ean.events[source_event].planned_time + 5.0


def test_optimization_decisions_cover_all_transfers() -> None:
    ean, _, transfer_ids = build_demo_network()
    pre_control = compute_realized_times(ean, arrival_source_delay={}, inactive_activities=set())
    loads = {aid: 10.0 for aid in transfer_ids}

    out = solve_tdm_b(
        ean,
        transfer_ids=transfer_ids,
        pre_control_times=pre_control,
        transfer_load=loads,
        penalty_t=12.0,
    )
    assert set(out.wait_decisions.keys()) == set(transfer_ids)
    assert all(v in {0, 1} for v in out.wait_decisions.values())


def test_activity_slack_nonnegative_on_planned_timetable() -> None:
    ean, _, _ = build_demo_network()
    slacks = activity_slack(ean)
    assert all(value >= 0 for value in slacks.values())
