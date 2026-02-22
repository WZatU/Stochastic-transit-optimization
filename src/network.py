"""
Backward-compatible aliases for the old `src.network` module.

The canonical implementation now lives in `src.ean`.
"""

from src.ean import Activity, Event, EventActivityNetwork

__all__ = ["Event", "Activity", "EventActivityNetwork"]
