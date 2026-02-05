from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .models import Event, EventType, Space, normalize_features
from .storage import ChoirStorage


class ChoirManager:
    def __init__(self, storage_path: Path) -> None:
        self.storage = ChoirStorage(storage_path)
        self.spaces, self.events = self.storage.load()

    def save(self) -> None:
        self.storage.save(self.spaces, self.events)

    def add_space(
        self,
        space_id: str,
        name: str,
        capacity: int,
        address: str,
        features: Iterable[str] | None = None,
        notes: str | None = None,
    ) -> Space:
        space = Space(
            space_id=space_id,
            name=name,
            capacity=capacity,
            address=address,
            features=normalize_features(features or []),
            notes=notes,
        )
        self._ensure_unique_space(space.space_id)
        self.spaces.append(space)
        self.save()
        return space

    def update_space(self, space_id: str, **updates: object) -> Space:
        space = self._get_space(space_id)
        updated = replace(space, **updates)
        self._replace_space(updated)
        self.save()
        return updated

    def add_event(
        self,
        event_id: str,
        title: str,
        event_type: EventType,
        start: datetime,
        end: datetime,
        space_id: str | None = None,
        participants: Iterable[str] | None = None,
        notes: str | None = None,
        min_capacity: int | None = None,
        required_features: Iterable[str] | None = None,
    ) -> Event:
        self._ensure_unique_event(event_id)
        event = Event(
            event_id=event_id,
            title=title,
            event_type=event_type,
            start=start,
            end=end,
            space_id=space_id,
            participants=tuple(participants or []),
            notes=notes,
        )
        if event.space_id is None:
            event = self.auto_assign_space(
                event,
                min_capacity=min_capacity,
                required_features=required_features,
            )
        self._validate_event(event)
        self.events.append(event)
        self.save()
        return event

    def list_events(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        event_type: EventType | None = None,
    ) -> list[Event]:
        results = self.events
        if start:
            results = [event for event in results if event.start >= start]
        if end:
            results = [event for event in results if event.end <= end]
        if event_type:
            results = [event for event in results if event.event_type == event_type]
        return sorted(results, key=lambda event: event.start)

    def auto_assign_space(
        self,
        event: Event,
        min_capacity: int | None = None,
        required_features: Iterable[str] | None = None,
    ) -> Event:
        required = normalize_features(required_features or [])
        candidates = self.find_available_spaces(
            event.start,
            event.end,
            min_capacity=min_capacity,
            required_features=required,
        )
        if not candidates:
            raise ValueError("No available spaces match the event requirements.")
        best = max(candidates, key=lambda space: space.capacity)
        return replace(event, space_id=best.space_id)

    def find_available_spaces(
        self,
        start: datetime,
        end: datetime,
        min_capacity: int | None = None,
        required_features: Iterable[str] | None = None,
    ) -> list[Space]:
        required = normalize_features(required_features or [])
        available: list[Space] = []
        for space in self.spaces:
            if min_capacity and space.capacity < min_capacity:
                continue
            if not set(required).issubset(space.features):
                continue
            if self._space_conflicts(space.space_id, start, end):
                continue
            available.append(space)
        return available

    def _space_conflicts(self, space_id: str, start: datetime, end: datetime) -> bool:
        for event in self.events:
            if event.space_id != space_id:
                continue
            if not (end <= event.start or start >= event.end):
                return True
        return False

    def _validate_event(self, event: Event) -> None:
        if event.start >= event.end:
            raise ValueError("Event start must be before end.")
        if event.space_id is None:
            raise ValueError("Event must have a space assigned.")
        for existing in self.events:
            if event.conflicts_with(existing):
                raise ValueError(
                    f"Event '{event.title}' conflicts with '{existing.title}'."
                )

    def _ensure_unique_space(self, space_id: str) -> None:
        if any(space.space_id == space_id for space in self.spaces):
            raise ValueError(f"Space '{space_id}' already exists.")

    def _ensure_unique_event(self, event_id: str) -> None:
        if any(event.event_id == event_id for event in self.events):
            raise ValueError(f"Event '{event_id}' already exists.")

    def _get_space(self, space_id: str) -> Space:
        for space in self.spaces:
            if space.space_id == space_id:
                return space
        raise ValueError(f"Unknown space '{space_id}'.")

    def _replace_space(self, updated: Space) -> None:
        for idx, space in enumerate(self.spaces):
            if space.space_id == updated.space_id:
                self.spaces[idx] = updated
                return
        raise ValueError(f"Unknown space '{updated.space_id}'.")
