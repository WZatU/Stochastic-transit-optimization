from __future__ import annotations

import heapq
from dataclasses import dataclass
from math import inf
from typing import Dict, Iterable, List, Set, Tuple

from src.ean import EventActivityNetwork


@dataclass
class PathResult:
    cost: float
    activities: List[int]


def shortest_event_path(
    ean: EventActivityNetwork,
    realized_times: Dict[int, float],
    origin_station: str,
    destination_station: str,
    inactive_activities: Set[int] | None = None,
    start_time: float = 0.0,
) -> PathResult | None:
    if inactive_activities is None:
        inactive_activities = set()

    departures = ean.station_departures(origin_station)
    arrivals = set(ean.station_arrivals(destination_station))
    if not departures or not arrivals:
        return None

    dist: Dict[int, float] = {eid: inf for eid in ean.events}
    prev_event: Dict[int, int] = {}
    prev_act: Dict[int, int] = {}
    pq: List[Tuple[float, int]] = []

    for dep in departures:
        dep_time = realized_times[dep]
        if dep_time >= start_time:
            dist[dep] = dep_time - start_time
            heapq.heappush(pq, (dist[dep], dep))

    while pq:
        cur_cost, u = heapq.heappop(pq)
        if cur_cost != dist[u]:
            continue
        if u in arrivals:
            acts: List[int] = []
            v = u
            while v in prev_event:
                acts.append(prev_act[v])
                v = prev_event[v]
            acts.reverse()
            return PathResult(cost=cur_cost, activities=acts)

        for a in ean.outgoing(u):
            if a.activity_id in inactive_activities:
                continue
            # Travel time on activity in realized timetable.
            w = max(0.0, realized_times[a.to_event] - realized_times[a.from_event])
            cand = cur_cost + w
            if cand < dist[a.to_event]:
                dist[a.to_event] = cand
                prev_event[a.to_event] = u
                prev_act[a.to_event] = a.activity_id
                heapq.heappush(pq, (cand, a.to_event))

    return None


def assign_flows(
    ean: EventActivityNetwork,
    od: Dict[Tuple[str, str], float],
    realized_times: Dict[int, float],
    inactive_activities: Set[int] | None = None,
    unserved_penalty: float = 60.0,
) -> tuple[Dict[int, float], Dict[Tuple[str, str], float], Dict[Tuple[str, str], float]]:
    """
    Algorithm-1-style assignment on current EAN:
    - shortest path for each OD
    - load demand on activities
    """
    if inactive_activities is None:
        inactive_activities = set()

    loads = {aid: 0.0 for aid in ean.activities}
    travel_time: Dict[Tuple[str, str], float] = {}
    served: Dict[Tuple[str, str], float] = {}

    for pair, demand in od.items():
        path = shortest_event_path(
            ean,
            realized_times,
            pair[0],
            pair[1],
            inactive_activities=inactive_activities,
            start_time=0.0,
        )
        if path is None:
            travel_time[pair] = unserved_penalty
            served[pair] = 0.0
            continue

        travel_time[pair] = path.cost
        served[pair] = demand
        for aid in path.activities:
            loads[aid] += demand

    return loads, travel_time, served
