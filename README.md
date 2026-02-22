# Stochastic Transit Simulation & Optimization (Mini Demo)

This project implements your PRD as a reproducible mini pipeline:

- Event-Activity Network (EAN) as the delay propagation backbone
- Stochastic source delays on arrival events
- Algorithm-1-style OD flow assignment via shortest path re-routing
- Three strategies for delay management:
  - `no_management`
  - `rule_based`
  - `lp_based` (TDM-B)
- Monte Carlo evaluation and static report for GitHub Pages (`/docs`)

## Project Structure

- `src/ean.py`: EAN data model
- `src/demo_network.py`: fixed demo PTN+EAN (<=8 stations)
- `src/delays.py`: stochastic delay sampling
- `src/propagation.py`: timetable feasibility propagation
- `src/routing.py`: shortest-path passenger assignment
- `src/optimization.py`: TDM-B solver (PuLP, fallback enumeration)
- `src/simulation.py`: Monte Carlo experiment orchestrator
- `run_experiment.py`: CLI to generate `docs/results.json`
- `docs/index.html`: static dashboard
- `docs/interview_notes.md`: interview script

## Quick Start

```bash
python3 -m pip install -r requirements.txt
python3 run_experiment.py --runs 300 --dist exp --seed 7
```

Output:

- `docs/results.json`

Then open report via a local server:

```bash
cd docs
python3 -m http.server 8000
```

Visit `http://localhost:8000`.

## CLI Options

```bash
python3 run_experiment.py \
  --runs 500 \
  --dist normal \
  --seed 11 \
  --penalty-t 12 \
  --rule-threshold 3 \
  --out docs/results.json
```

## Tests

```bash
python3 -m pytest -q
```

## GitHub Pages

1. Push repo to GitHub.
2. In GitHub repo settings, open **Pages**.
3. Set source to **Deploy from a branch**.
4. Select your default branch and `/docs` folder.

## Interview Talking Points (3 minutes)

1. Problem: stochastic delays in a small transit network and operational wait/depart decisions.
2. Modeling: EAN captures all delay propagation constraints.
3. Optimization: TDM-B balances propagated delay vs missed-connection penalties.
4. Evaluation: Monte Carlo expected delay, miss rate, and door-to-door time.
5. Engineering: reproducible seed, modular solver fallback, static web report.
