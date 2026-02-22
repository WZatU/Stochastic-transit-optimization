from src.simulation import run_monte_carlo


def test_monte_carlo_smoke() -> None:
    out = run_monte_carlo(n=10, dist="exp", seed=1)
    assert "scenarios" in out
    assert len(out["scenarios"]) == 3
    for item in out["scenarios"]:
        assert item["avg_delay"] >= 0
        assert 0 <= item["miss_rate"] <= 1
        assert item["avg_door_to_door"] >= 0
