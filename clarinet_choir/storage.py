from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import Event, EventType, Space, format_datetime, parse_datetime


class ChoirStorage:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> tuple[list[Space], list[Event]]:
        if not self.path.exists():
            return [], []
        data = json.loads(self.path.read_text())
        spaces = [self._space_from_dict(item) for item in data.get("spaces", [])]
        events = [self._event_from_dict(item) for item in data.get("events", [])]
        return spaces, events

    def save(self, spaces: list[Space], events: list[Event]) -> None:
        payload = {
            "spaces": [self._space_to_dict(space) for space in spaces],
            "events": [self._event_to_dict(event) for event in events],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    def _space_from_dict(self, payload: dict[str, Any]) -> Space:
        return Space(
            space_id=payload["space_id"],
            name=payload["name"],
            capacity=payload["capacity"],
            address=payload["address"],
            features=tuple(payload.get("features", [])),
            notes=payload.get("notes"),
        )

    def _event_from_dict(self, payload: dict[str, Any]) -> Event:
        return Event(
            event_id=payload["event_id"],
            title=payload["title"],
            event_type=EventType(payload["event_type"]),
            start=parse_datetime(payload["start"]),
            end=parse_datetime(payload["end"]),
            space_id=payload.get("space_id"),
            participants=tuple(payload.get("participants", [])),
            notes=payload.get("notes"),
        )

    def _space_to_dict(self, space: Space) -> dict[str, Any]:
        payload = asdict(space)
        payload["features"] = list(space.features)
        return payload

    def _event_to_dict(self, event: Event) -> dict[str, Any]:
        payload = asdict(event)
        payload["event_type"] = event.event_type.value
        payload["start"] = format_datetime(event.start)
        payload["end"] = format_datetime(event.end)
        payload["participants"] = list(event.participants)
        return payload
