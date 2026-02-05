from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Iterable


class EventType(str, Enum):
    REHEARSAL = "rehearsal"
    CONCERT = "concert"
    OUTREACH = "outreach"
    OTHER = "other"


@dataclass(frozen=True)
class Space:
    space_id: str
    name: str
    capacity: int
    address: str
    features: tuple[str, ...] = ()
    notes: str | None = None


@dataclass
class Event:
    event_id: str
    title: str
    event_type: EventType
    start: datetime
    end: datetime
    space_id: str | None = None
    participants: tuple[str, ...] = ()
    notes: str | None = None

    def overlaps(self, other: "Event") -> bool:
        return not (self.end <= other.start or self.start >= other.end)

    def conflicts_with(self, other: "Event") -> bool:
        if not self.overlaps(other):
            return False
        if self.space_id is None or other.space_id is None:
            return False
        return self.space_id == other.space_id


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def format_datetime(value: datetime) -> str:
    return value.isoformat(timespec="minutes")


def normalize_features(features: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({feature.strip() for feature in features if feature.strip()}))
