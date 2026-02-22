from __future__ import annotations

import random
from typing import Dict

from src.ean import EventActivityNetwork


def sample_arrival_delays(
    ean: EventActivityNetwork,
    dist: str,
    rng: random.Random,
    exp_lambda: float = 0.25,
    normal_mu: float = 2.0,
    normal_sigma: float = 1.2,
) -> Dict[int, float]:
    """Sample independent delays for arrival events only."""
    delays: Dict[int, float] = {}
    for eid, event in ean.events.items():
        if event.event_type != "arrival":
            continue
        if dist == "exp":
            delays[eid] = rng.expovariate(exp_lambda)
        elif dist == "normal":
            delays[eid] = max(0.0, rng.gauss(normal_mu, normal_sigma))
        else:
            raise ValueError("dist must be exp or normal")
    return delays
