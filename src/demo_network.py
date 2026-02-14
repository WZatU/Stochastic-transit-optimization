from __future__ import annotations

from typing import Dict, List, Tuple

from src.ean import EventActivityNetwork


ODMatrix = Dict[Tuple[str, str], float]


def build_demo_network() -> tuple[EventActivityNetwork, ODMatrix, List[int]]:
    """
    Small network (4 stations, <=8 required by PRD).

    Main transfer decisions:
    - B arrival -> B departure to D (controllable transfer)
    - D arrival -> D departure to C (controllable transfer)
    """
    ean = EventActivityNetwork()

    # Events
    a_dep0 = ean.add_event("A", "departure", 0)
    b_arr10 = ean.add_event("B", "arrival", 10)
    b_dep12 = ean.add_event("B", "departure", 12)
    c_arr26 = ean.add_event("C", "arrival", 26)

    b_dep13 = ean.add_event("B", "departure", 13)
    d_arr20 = ean.add_event("D", "arrival", 20)
    d_dep22 = ean.add_event("D", "departure", 22)
    c_arr31 = ean.add_event("C", "arrival", 31)

    # Drive activities
    ean.add_activity("drive", a_dep0, b_arr10, 10)
    ean.add_activity("drive", b_dep12, c_arr26, 14)
    ean.add_activity("drive", b_dep13, d_arr20, 7)
    ean.add_activity("drive", d_dep22, c_arr31, 9)

    # Same-vehicle waits (always active)
    ean.add_activity("wait", b_arr10, b_dep12, 2, controllable=False)
    # Controllable transfers
    transfer_1 = ean.add_activity("transfer", b_arr10, b_dep13, 2, controllable=True)
    transfer_2 = ean.add_activity("transfer", d_arr20, d_dep22, 1, controllable=True)

    od: ODMatrix = {
        ("A", "D"): 60,
        ("A", "C"): 80,
        ("B", "C"): 40,
        ("D", "C"): 20,
    }

    return ean, od, [transfer_1, transfer_2]
