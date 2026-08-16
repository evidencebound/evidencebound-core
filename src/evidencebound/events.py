"""Provider-neutral structured event hooks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class Event:
    name: str
    attributes: dict[str, Any]


class EventSink(Protocol):
    def emit(self, event: Event) -> None: ...


class NullEventSink:
    def emit(self, event: Event) -> None:
        return None


class ListEventSink:
    def __init__(self) -> None:
        self.events: list[Event] = []

    def emit(self, event: Event) -> None:
        self.events.append(event)
