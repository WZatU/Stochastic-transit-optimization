"""
Monte Carlo simulation for stochastic transit delay evaluation.
"""

import numpy as np
from typing import Dict, Callable, List
from ean import EAN
from delay_management import DelayManagementModel


class MonteCarloSimulation:
    """
    Monte Carlo simulation for evaluating stochastic delays in transit networks.
    
    Runs multiple scenarios with random delay realizations and computes
    statistics on delay propagation.
    """
    
    def __init__(self, ean: EAN, delay_model: DelayManagementModel):
        """
        Initialize Monte Carlo simulation.
        
        Args:
            ean: Event-Activity Network
            delay_model: Delay management model (TDM-B)
        """
        self.ean = ean
        self.delay_model = delay_model
    
    def run_simulation(
        self, 
        num_scenarios: int,
        delay_generator: Callable[[int], Dict[int, float]],
        use_lp: bool = True
    ) -> Dict:
        """
        Run Monte Carlo simulation.
        
        Args:
            num_scenarios: Number of scenarios to simulate
            delay_generator: Function that generates random source delays
            use_lp: Whether to use LP-based delay management (True) or simple propagation
        
        Returns:
            Dictionary containing simulation statistics
        """
        all_delays = []
        total_delays = []
        max_delays = []
        
        for scenario in range(num_scenarios):
            # Reset network
            self.ean.reset_delays()
            
            # Generate random source delays
            source_delays = delay_generator(scenario)
            
            # Propagate delays
            if use_lp:
                result_delays = self.delay_model.propagate_delays(source_delays)
            else:
                result_delays = self.delay_model.simple_propagate_delays(source_delays)
            
            # Collect statistics
            all_delays.append(result_delays)
            total_delays.append(sum(result_delays.values()))
            max_delays.append(max(result_delays.values()))
        
        # Compute aggregate statistics
        statistics = self._compute_statistics(all_delays, total_delays, max_delays)
        
        return statistics
    
    def _compute_statistics(
        self, 
        all_delays: List[Dict[int, float]],
        total_delays: List[float],
        max_delays: List[float]
    ) -> Dict:
        """Compute aggregate statistics from simulation results."""
        
        # Per-event statistics
        event_delays = {event_id: [] for event_id in self.ean.events}
        for scenario_delays in all_delays:
            for event_id, delay in scenario_delays.items():
                event_delays[event_id].append(delay)
        
        event_stats = {}
        for event_id, delays in event_delays.items():
            event_stats[event_id] = {
                'mean': np.mean(delays),
                'std': np.std(delays),
                'min': np.min(delays),
                'max': np.max(delays),
                'median': np.median(delays),
                'percentile_95': np.percentile(delays, 95)
            }
        
        # Global statistics
        statistics = {
            'num_scenarios': len(all_delays),
            'total_delay': {
                'mean': np.mean(total_delays),
                'std': np.std(total_delays),
                'min': np.min(total_delays),
                'max': np.max(total_delays)
            },
            'max_delay': {
                'mean': np.mean(max_delays),
                'std': np.std(max_delays),
                'min': np.min(max_delays),
                'max': np.max(max_delays)
            },
            'event_statistics': event_stats
        }
        
        return statistics
    
    def print_statistics(self, statistics: Dict):
        """Print simulation statistics in a readable format."""
        print(f"\n{'='*60}")
        print(f"Monte Carlo Simulation Results ({statistics['num_scenarios']} scenarios)")
        print(f"{'='*60}\n")
        
        print("Global Statistics:")
        print(f"  Total Delay Across Network:")
        print(f"    Mean: {statistics['total_delay']['mean']:.2f} min")
        print(f"    Std:  {statistics['total_delay']['std']:.2f} min")
        print(f"    Min:  {statistics['total_delay']['min']:.2f} min")
        print(f"    Max:  {statistics['total_delay']['max']:.2f} min")
        
        print(f"\n  Maximum Single Event Delay:")
        print(f"    Mean: {statistics['max_delay']['mean']:.2f} min")
        print(f"    Std:  {statistics['max_delay']['std']:.2f} min")
        print(f"    Min:  {statistics['max_delay']['min']:.2f} min")
        print(f"    Max:  {statistics['max_delay']['max']:.2f} min")
        
        print(f"\nPer-Event Statistics:")
        for event_id, stats in statistics['event_statistics'].items():
            event = self.ean.events[event_id]
            print(f"  Event {event_id} ({event.event_type.value} at {event.station}):")
            print(f"    Mean: {stats['mean']:.2f} min, "
                  f"Std: {stats['std']:.2f} min, "
                  f"95th percentile: {stats['percentile_95']:.2f} min")
        
        print(f"\n{'='*60}\n")
