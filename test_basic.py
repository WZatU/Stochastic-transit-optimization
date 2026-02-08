"""
Basic tests for the stochastic transit optimization system.
"""

import numpy as np
from ean import EAN, EventType, ActivityType
from delay_management import DelayManagementModel
from monte_carlo import MonteCarloSimulation


def test_ean_creation():
    """Test basic EAN creation and structure."""
    print("Testing EAN creation...")
    ean = EAN()
    
    # Add events
    e1 = ean.add_event(EventType.DEPARTURE, "Station1", "Line1", 0.0)
    e2 = ean.add_event(EventType.ARRIVAL, "Station2", "Line1", 10.0)
    
    assert len(ean.events) == 2
    assert ean.events[e1].station == "Station1"
    assert ean.events[e2].scheduled_time == 10.0
    
    # Add activity
    a1 = ean.add_activity(ActivityType.TRAVEL, e1, e2, 10.0)
    
    assert len(ean.activities) == 1
    assert ean.activities[a1].min_duration == 10.0
    
    # Test outgoing/incoming
    outgoing = ean.get_outgoing_activities(e1)
    assert len(outgoing) == 1
    
    incoming = ean.get_incoming_activities(e2)
    assert len(incoming) == 1
    
    print("✓ EAN creation test passed")


def test_simple_delay_propagation():
    """Test simple delay propagation without LP."""
    print("Testing simple delay propagation...")
    ean = EAN()
    
    # Create simple chain: e1 -> e2 -> e3
    e1 = ean.add_event(EventType.DEPARTURE, "Station1", "Line1", 0.0)
    e2 = ean.add_event(EventType.ARRIVAL, "Station2", "Line1", 10.0)
    e3 = ean.add_event(EventType.DEPARTURE, "Station2", "Line1", 12.0)
    
    ean.add_activity(ActivityType.TRAVEL, e1, e2, 10.0)
    ean.add_activity(ActivityType.DWELL, e2, e3, 2.0)
    
    # Apply delay at e1
    tdm = DelayManagementModel(ean)
    delays = tdm.simple_propagate_delays({e1: 5.0})
    
    assert delays[e1] == 5.0
    assert delays[e2] == 5.0
    assert delays[e3] == 5.0
    
    print("✓ Simple delay propagation test passed")


def test_lp_delay_management():
    """Test LP-based delay management."""
    print("Testing LP-based delay management...")
    ean = EAN()
    
    # Create a simple network with transfer
    e1 = ean.add_event(EventType.DEPARTURE, "Station1", "Line1", 0.0)
    e2 = ean.add_event(EventType.ARRIVAL, "Station2", "Line1", 10.0)
    e3 = ean.add_event(EventType.DEPARTURE, "Station2", "Line2", 12.0)
    
    ean.add_activity(ActivityType.TRAVEL, e1, e2, 10.0)
    ean.add_activity(ActivityType.TRANSFER, e2, e3, 2.0, 5.0)
    
    # Apply delay
    tdm = DelayManagementModel(ean)
    delays = tdm.propagate_delays({e1: 3.0})
    
    assert delays[e1] == 3.0
    assert delays[e2] == 3.0
    # Transfer delay depends on LP decision
    assert delays[e3] >= 0.0
    
    print("✓ LP-based delay management test passed")


def test_monte_carlo_simulation():
    """Test Monte Carlo simulation."""
    print("Testing Monte Carlo simulation...")
    ean = EAN()
    
    # Simple network
    e1 = ean.add_event(EventType.DEPARTURE, "Station1", "Line1", 0.0)
    e2 = ean.add_event(EventType.ARRIVAL, "Station2", "Line1", 10.0)
    ean.add_activity(ActivityType.TRAVEL, e1, e2, 10.0)
    
    tdm = DelayManagementModel(ean)
    mc_sim = MonteCarloSimulation(ean, tdm)
    
    # Run simulation with fixed delays
    def fixed_delay_gen(scenario):
        return {e1: 2.0}
    
    stats = mc_sim.run_simulation(
        num_scenarios=10,
        delay_generator=fixed_delay_gen,
        use_lp=False
    )
    
    assert stats['num_scenarios'] == 10
    assert 'total_delay' in stats
    assert 'event_statistics' in stats
    
    # With fixed delay of 2.0, mean should be close to 4.0 (2 events * 2.0)
    assert abs(stats['total_delay']['mean'] - 4.0) < 0.1
    
    print("✓ Monte Carlo simulation test passed")


def test_reset_delays():
    """Test delay reset functionality."""
    print("Testing delay reset...")
    ean = EAN()
    
    e1 = ean.add_event(EventType.DEPARTURE, "Station1", "Line1", 0.0)
    e2 = ean.add_event(EventType.ARRIVAL, "Station2", "Line1", 10.0)
    
    # Set delays manually
    ean.events[e1].delay = 5.0
    ean.events[e1].actual_time = 5.0
    ean.events[e2].delay = 5.0
    ean.events[e2].actual_time = 15.0
    
    # Reset
    ean.reset_delays()
    
    assert ean.events[e1].delay == 0.0
    assert ean.events[e1].actual_time == 0.0
    assert ean.events[e2].delay == 0.0
    assert ean.events[e2].actual_time == 10.0
    
    print("✓ Delay reset test passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("Running Basic Tests")
    print("="*60 + "\n")
    
    test_ean_creation()
    test_simple_delay_propagation()
    test_lp_delay_management()
    test_monte_carlo_simulation()
    test_reset_delays()
    
    print("\n" + "="*60)
    print("All Tests Passed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
