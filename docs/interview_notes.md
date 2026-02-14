# Interview Notes (3 minutes)

## 1) Problem
I built a mini stochastic transit simulator to compare delay-management decisions in a small bus network.

## 2) Method
I modeled timetable operations as an Event-Activity Network (EAN) and injected random source delays on arrival events.
For each Monte Carlo run, I compared three policies:
- always depart (break transfers),
- threshold rule,
- LP-based TDM-B optimization.

## 3) Optimization
The TDM-B objective balances two costs:
- propagated delay if we wait,
- missed-connection penalty if we depart.
I solved it with PuLP when available and kept an exact enumeration fallback for tiny instances.

## 4) Evaluation
I measured:
- expected total passenger delay,
- missed connection rate,
- average door-to-door time.

## 5) Result
On this demo network, LP-based policy reduced passenger delay and missed-connection rate versus no-management and simple rule-based baseline.

## 6) Engineering choices
- clear modular layers (network, propagation, routing, optimization, simulation)
- reproducible runs with seed
- static GitHub Pages report from JSON output
