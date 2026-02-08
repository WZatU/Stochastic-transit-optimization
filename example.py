"""
Example usage of the stochastic transit optimization system.

This script demonstrates:
- Creating a simple Event-Activity Network (EAN)
- Running delay management with TDM-B
- Monte Carlo evaluation of stochastic delays
"""

import numpy as np
from ean import EAN, EventType, ActivityType
from delay_management import DelayManagementModel
from monte_carlo import MonteCarloSimulation


def create_simple_network() -> EAN:
    """
    Create a simple transit network with 5 stations and 2 lines.
    
    Network topology:
        Line A: Station1 -> Station2 -> Station3 -> Station4 -> Station5
        Line B: Station1 -> Station3 -> Station5
    
    Transfers available at: Station1, Station3, Station5
    """
    ean = EAN()
    
    # Line A events (scheduled times in minutes from start)
    # Station 1
    a1_dep = ean.add_event(EventType.DEPARTURE, "Station1", "LineA", 0.0)
    
    # Station 2
    a2_arr = ean.add_event(EventType.ARRIVAL, "Station2", "LineA", 10.0)
    a2_dep = ean.add_event(EventType.DEPARTURE, "Station2", "LineA", 12.0)
    
    # Station 3
    a3_arr = ean.add_event(EventType.ARRIVAL, "Station3", "LineA", 22.0)
    a3_dep = ean.add_event(EventType.DEPARTURE, "Station3", "LineA", 24.0)
    
    # Station 4
    a4_arr = ean.add_event(EventType.ARRIVAL, "Station4", "LineA", 34.0)
    a4_dep = ean.add_event(EventType.DEPARTURE, "Station4", "LineA", 36.0)
    
    # Station 5
    a5_arr = ean.add_event(EventType.ARRIVAL, "Station5", "LineA", 46.0)
    
    # Line B events
    # Station 1
    b1_dep = ean.add_event(EventType.DEPARTURE, "Station1", "LineB", 5.0)
    
    # Station 3
    b3_arr = ean.add_event(EventType.ARRIVAL, "Station3", "LineB", 20.0)
    b3_dep = ean.add_event(EventType.DEPARTURE, "Station3", "LineB", 23.0)
    
    # Station 5
    b5_arr = ean.add_event(EventType.ARRIVAL, "Station5", "LineB", 40.0)
    
    # Add travel activities for Line A
    ean.add_activity(ActivityType.TRAVEL, a1_dep, a2_arr, 10.0)
    ean.add_activity(ActivityType.DWELL, a2_arr, a2_dep, 2.0)
    ean.add_activity(ActivityType.TRAVEL, a2_dep, a3_arr, 10.0)
    ean.add_activity(ActivityType.DWELL, a3_arr, a3_dep, 2.0)
    ean.add_activity(ActivityType.TRAVEL, a3_dep, a4_arr, 10.0)
    ean.add_activity(ActivityType.DWELL, a4_arr, a4_dep, 2.0)
    ean.add_activity(ActivityType.TRAVEL, a4_dep, a5_arr, 10.0)
    
    # Add travel activities for Line B
    ean.add_activity(ActivityType.TRAVEL, b1_dep, b3_arr, 15.0)
    ean.add_activity(ActivityType.DWELL, b3_arr, b3_dep, 3.0)
    ean.add_activity(ActivityType.TRAVEL, b3_dep, b5_arr, 17.0)
    
    # Add transfer activities
    # Transfer from Line B to Line A at Station 3
    ean.add_activity(ActivityType.TRANSFER, b3_arr, a3_dep, 3.0, 10.0)
    
    # Transfer from Line A to Line B at Station 3 (backwards connection)
    ean.add_activity(ActivityType.TRANSFER, a3_arr, b3_dep, 1.0, 5.0)
    
    return ean


def delay_generator_exponential(scenario: int) -> dict:
    """
    Generate random source delays using exponential distribution.
    
    Simulates delays at the first departure of Line A with mean 3 minutes.
    """
    np.random.seed(scenario)
    
    # Only apply source delay to first event of Line A (event 0)
    source_delay = np.random.exponential(scale=3.0)
    
    return {0: source_delay}


def delay_generator_normal(scenario: int) -> dict:
    """
    Generate random source delays using normal distribution.
    
    Simulates delays at multiple events.
    """
    np.random.seed(scenario)
    
    delays = {}
    # Add delays to first events of both lines
    delays[0] = max(0, np.random.normal(loc=2.0, scale=1.5))  # Line A
    delays[7] = max(0, np.random.normal(loc=1.5, scale=1.0))  # Line B
    
    return delays


def main():
    """Main demonstration of the stochastic transit optimization system."""
    
    print("="*60)
    print("Stochastic Transit Optimization - Example")
    print("="*60)
    
    # Create the network
    print("\n1. Creating Event-Activity Network (EAN)...")
    ean = create_simple_network()
    print(f"   Created network with {len(ean.events)} events and {len(ean.activities)} activities")
    print(f"   Stations: 5 (Station1 through Station5)")
    print(f"   Lines: 2 (LineA and LineB)")
    
    # Show network structure
    print("\n2. Network Structure:")
    print("   Line A: Station1(0) -> Station2(10) -> Station3(22) -> Station4(34) -> Station5(46)")
    print("   Line B: Station1(5) -> Station3(20) -> Station5(40)")
    print("   Transfers: Available at Station3")
    
    # Create delay management model
    print("\n3. Creating TDM-B Delay Management Model...")
    tdm = DelayManagementModel(ean, weight_factor=1.0)
    print("   LP-based wait-depart decision model initialized")
    
    # Run Monte Carlo simulation
    print("\n4. Running Monte Carlo Simulation...")
    mc_sim = MonteCarloSimulation(ean, tdm)
    
    print("\n   Scenario 1: Exponential delays (mean=3 min) at Line A start")
    stats_exp = mc_sim.run_simulation(
        num_scenarios=100,
        delay_generator=delay_generator_exponential,
        use_lp=True
    )
    mc_sim.print_statistics(stats_exp)
    
    print("\n   Scenario 2: Normal delays at both line starts")
    stats_norm = mc_sim.run_simulation(
        num_scenarios=100,
        delay_generator=delay_generator_normal,
        use_lp=True
    )
    mc_sim.print_statistics(stats_norm)
    
    # Compare LP vs simple propagation
    print("\n5. Comparison: LP-based vs Simple Delay Propagation")
    print("\n   Using LP-based delay management:")
    stats_lp = mc_sim.run_simulation(
        num_scenarios=50,
        delay_generator=delay_generator_exponential,
        use_lp=True
    )
    print(f"   Average total delay: {stats_lp['total_delay']['mean']:.2f} min")
    
    print("\n   Using simple delay propagation:")
    stats_simple = mc_sim.run_simulation(
        num_scenarios=50,
        delay_generator=delay_generator_exponential,
        use_lp=False
    )
    print(f"   Average total delay: {stats_simple['total_delay']['mean']:.2f} min")
    
    improvement = stats_simple['total_delay']['mean'] - stats_lp['total_delay']['mean']
    print(f"\n   Delay reduction with LP: {improvement:.2f} min ({improvement/stats_simple['total_delay']['mean']*100:.1f}%)")
    
    print("\n" + "="*60)
    print("Simulation Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
