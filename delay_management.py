"""
TDM-B (Train Delay Management Model - Basic) implementation.

This module implements a linear programming-based delay management model
for deciding whether trains should wait for delayed connections or depart.
"""

from typing import Dict, List
import pulp
from ean import EAN, ActivityType


class DelayManagementModel:
    """
    TDM-B: Train Delay Management Model (Basic).
    
    Uses linear programming to determine optimal wait-depart decisions
    that minimize total delay propagation in the network.
    """
    
    def __init__(self, ean: EAN, weight_factor: float = 1.0):
        """
        Initialize the delay management model.
        
        Args:
            ean: Event-Activity Network
            weight_factor: Weight for delay penalties (default 1.0)
        """
        self.ean = ean
        self.weight_factor = weight_factor
    
    def propagate_delays(self, source_delays: Dict[int, float]) -> Dict[int, float]:
        """
        Propagate delays through the network using LP-based decisions.
        
        Args:
            source_delays: Dictionary mapping event IDs to initial delays
        
        Returns:
            Dictionary mapping all event IDs to their final delays
        """
        # Create LP problem
        prob = pulp.LpProblem("Delay_Management", pulp.LpMinimize)
        
        # Decision variables: delay for each event
        delay_vars = {}
        for event_id in self.ean.events:
            delay_vars[event_id] = pulp.LpVariable(
                f"delay_{event_id}", 
                lowBound=source_delays.get(event_id, 0.0)
            )
        
        # Wait-depart decision variables for transfer activities
        wait_vars = {}
        for activity in self.ean.activities.values():
            if activity.activity_type == ActivityType.TRANSFER:
                wait_vars[activity.id] = pulp.LpVariable(
                    f"wait_{activity.id}",
                    cat='Binary'
                )
        
        # Objective: minimize total weighted delay
        total_delay = pulp.lpSum([
            self.weight_factor * delay_vars[event_id] 
            for event_id in self.ean.events
        ])
        prob += total_delay
        
        # Constraints
        for activity in self.ean.activities.values():
            source = activity.source_event
            target = activity.target_event
            
            if activity.activity_type in [ActivityType.TRAVEL, ActivityType.DWELL]:
                # Fixed activities: must respect minimum duration
                prob += (
                    delay_vars[target] >= 
                    delay_vars[source] + 
                    (self.ean.events[source].scheduled_time + activity.min_duration - 
                     self.ean.events[target].scheduled_time)
                )
            
            elif activity.activity_type == ActivityType.TRANSFER:
                # Transfer activities: conditional on wait decision
                # If we wait (wait_var = 1), transfer is maintained
                # If we don't wait (wait_var = 0), transfer may be broken
                M = 1000  # Big-M for constraint formulation
                
                # If waiting: respect minimum transfer time
                prob += (
                    delay_vars[target] >= 
                    delay_vars[source] + 
                    (self.ean.events[source].scheduled_time + activity.min_duration - 
                     self.ean.events[target].scheduled_time) -
                    M * (1 - wait_vars[activity.id])
                )
                
                # If not waiting: can depart with only source delay impact
                if activity.max_duration is not None:
                    prob += (
                        delay_vars[target] <= 
                        delay_vars[source] + 
                        (self.ean.events[source].scheduled_time + activity.max_duration - 
                         self.ean.events[target].scheduled_time) +
                        M * wait_vars[activity.id]
                    )
        
        # Solve the LP
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        
        # Extract solution
        delays = {}
        for event_id in self.ean.events:
            delays[event_id] = delay_vars[event_id].varValue
            if delays[event_id] is None:
                delays[event_id] = source_delays.get(event_id, 0.0)
        
        # Update EAN with computed delays
        for event_id, delay in delays.items():
            self.ean.events[event_id].delay = delay
            self.ean.events[event_id].actual_time = (
                self.ean.events[event_id].scheduled_time + delay
            )
        
        return delays
    
    def simple_propagate_delays(self, source_delays: Dict[int, float]) -> Dict[int, float]:
        """
        Simple delay propagation without LP (for comparison/fallback).
        
        Propagates delays through the network using a topological approach,
        maintaining all connections.
        """
        delays = {event_id: source_delays.get(event_id, 0.0) 
                  for event_id in self.ean.events}
        
        # Iteratively propagate delays
        max_iterations = 100
        for _ in range(max_iterations):
            updated = False
            for activity in self.ean.activities.values():
                source = activity.source_event
                target = activity.target_event
                
                source_event = self.ean.events[source]
                target_event = self.ean.events[target]
                
                # Calculate required delay at target
                required_delay = (
                    delays[source] + 
                    (source_event.scheduled_time + activity.min_duration - 
                     target_event.scheduled_time)
                )
                
                if required_delay > delays[target]:
                    delays[target] = required_delay
                    updated = True
            
            if not updated:
                break
        
        # Update EAN
        for event_id, delay in delays.items():
            self.ean.events[event_id].delay = delay
            self.ean.events[event_id].actual_time = (
                self.ean.events[event_id].scheduled_time + delay
            )
        
        return delays
