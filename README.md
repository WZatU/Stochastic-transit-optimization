# Stochastic Transit Optimization

A minimal stochastic transit simulation using Event-Activity Networks (EAN) and a linear delay management model (TDM-B).

## Overview

This project implements a stochastic transit delay simulation system that:
- Models transit networks using Event-Activity Networks (EAN)
- Applies LP-based delay management (TDM-B) for wait-depart decisions
- Evaluates performance using Monte Carlo simulation
- Propagates delays at the event level through the network

## Features

### Event-Activity Network (EAN)
- **Events**: Arrival and departure events at stations
- **Activities**: Travel, dwell, and transfer connections between events
- Directed graph representation of transit operations

### TDM-B Delay Management
- Linear programming formulation for optimal wait-depart decisions
- Minimizes total delay propagation across the network
- Handles transfer connections with conditional constraints
- Alternative simple propagation method for comparison

### Monte Carlo Simulation
- Random delay generation with configurable distributions
- Multiple scenario evaluation
- Statistical analysis (mean, std, percentiles)
- Performance metrics for delay propagation

## Scope

✅ **In Scope:**
- Small networks (≤5 stations)
- Event-level delay propagation
- Monte Carlo evaluation
- LP-based wait-depart decisions

❌ **Non-Goals:**
- Real city data integration
- GUI system
- Large-scale optimization

## Installation

```bash
pip install -r requirements.txt
```

**Requirements:**
- Python 3.7+
- numpy >= 1.20.0
- scipy >= 1.8.0
- pulp >= 2.7.0

## Usage

### Quick Start

Run the example simulation:

```bash
python example.py
```

This demonstrates a simple 5-station, 2-line network with transfer connections.

### Creating a Custom Network

```python
from ean import EAN, EventType, ActivityType
from delay_management import DelayManagementModel
from monte_carlo import MonteCarloSimulation

# Create network
ean = EAN()

# Add events
dep1 = ean.add_event(EventType.DEPARTURE, "Station1", "Line1", 0.0)
arr2 = ean.add_event(EventType.ARRIVAL, "Station2", "Line1", 10.0)

# Add activities
ean.add_activity(ActivityType.TRAVEL, dep1, arr2, 10.0)

# Create delay management model
tdm = DelayManagementModel(ean)

# Run Monte Carlo simulation
mc_sim = MonteCarloSimulation(ean, tdm)
stats = mc_sim.run_simulation(
    num_scenarios=100,
    delay_generator=lambda s: {0: np.random.exponential(3.0)}
)
mc_sim.print_statistics(stats)
```

## Architecture

### Modules

- **ean.py**: Event-Activity Network implementation
  - `Event`: Transit event (arrival/departure)
  - `Activity`: Connection between events
  - `EAN`: Network graph structure

- **delay_management.py**: TDM-B delay management model
  - `DelayManagementModel`: LP-based delay propagation
  - Wait-depart decision optimization

- **monte_carlo.py**: Stochastic simulation
  - `MonteCarloSimulation`: Multi-scenario evaluation
  - Statistical analysis and reporting

- **example.py**: Demonstration script
  - Sample 5-station network
  - Multiple delay scenarios
  - Performance comparison

## Example Network

The included example creates a network with:

```
Line A: Station1 -> Station2 -> Station3 -> Station4 -> Station5
Line B: Station1 -> Station3 -> Station5

Transfers: Available at Station3 (between Line A and Line B)
```

## Model Details

### Event-Activity Network
- Nodes represent transit events (arrivals/departures)
- Edges represent activities:
  - **Travel**: Movement between stations
  - **Dwell**: Waiting time at a station
  - **Transfer**: Passenger connections between lines

### TDM-B Delay Management
The LP formulation minimizes total delay:

```
minimize: Σ (delay_i) for all events i

subject to:
- Fixed activities: delay_j ≥ delay_i + (scheduled_time_i + duration - scheduled_time_j)
- Transfer activities: conditional on wait decision (binary variable)
- Source delays: delay_i ≥ source_delay_i
```

### Monte Carlo Evaluation
For each scenario:
1. Generate random source delays (e.g., exponential distribution)
2. Propagate delays using TDM-B
3. Record resulting delays at all events
4. Compute statistics across all scenarios

## License

MIT License - see LICENSE file for details.