from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable

EventHandler = Callable[[dict[str, Any]], None]


@dataclass(order=True)
class _Subscriber:
    priority: int
    owner: str = field(compare=False)
    handler_name: str = field(compare=False)
    handler: EventHandler = field(compare=False)


class EventBus:
    """Unified combat event bus with deterministic priority ordering and depth guards."""

    def __init__(self, max_emit_depth: int = 8) -> None:
        self._subscribers: dict[str, list[_Subscriber]] = defaultdict(list)
        self._subscriber_keys: set[tuple[str, str, str]] = set()
        self._emit_depth = 0
        self._max_emit_depth = max_emit_depth

    def subscribe(
        self,
        event_type: str,
        *,
        owner: str,
        handler: EventHandler,
        priority: int = 0,
    ) -> bool:
        handler_name = getattr(handler, "__name__", repr(handler))
        key = (event_type, owner, handler_name)
        if key in self._subscriber_keys:
            return False

        self._subscriber_keys.add(key)
        self._subscribers[event_type].append(
            _Subscriber(priority=priority, owner=owner, handler_name=handler_name, handler=handler)
        )
        self._subscribers[event_type].sort(reverse=True)
        return True

    def emit(self, event_type: str, payload: dict[str, Any]) -> None:
        if self._emit_depth >= self._max_emit_depth:
            raise RuntimeError(f"Max event re-emit depth exceeded for {event_type}")

        payload.setdefault("event_type", event_type)
        payload.setdefault("tags", [])

        self._emit_depth += 1
        try:
            for subscriber in self._subscribers.get(event_type, []):
                subscriber.handler(payload)
        finally:
            self._emit_depth -= 1
