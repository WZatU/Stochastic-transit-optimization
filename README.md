# Stochastic Transit Simulation & Optimization (Mini Demo)

This project implements a small Event-Activity Network (EAN) with stochastic source delays and compares three policies:

- `no_management` (always depart / break transfer)
- `rule_based` (threshold-based wait/depart)
- `lp_based` (TDM-B optimization)

## Run

```bash
python3 run_experiment.py --runs 300 --dist exp
```

Output is written to:

- `docs/results.json`

Open `docs/index.html` to view the static report page.

## GitHub Pages

Set GitHub Pages to serve from `/docs` on your default branch.

## Interview Talking Points

- Why EAN is the delay propagation backbone.
- How Monte Carlo quantifies expected passenger impact under uncertainty.
- Why LP-based decisions outperform static rules in high-delay tails.
- Engineering tradeoff: exact MIP via PuLP vs fallback enumeration on tiny instances.
