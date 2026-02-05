from __future__ import annotations

import argparse
from pathlib import Path

from .manager import ChoirManager
from .models import EventType, parse_datetime

DEFAULT_STORAGE = Path("data/choir.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clarinet choir management")
    parser.add_argument(
        "--storage",
        type=Path,
        default=DEFAULT_STORAGE,
        help="Path to JSON storage file.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_space = subparsers.add_parser("add-space", help="Add a rehearsal space")
    add_space.add_argument("space_id")
    add_space.add_argument("name")
    add_space.add_argument("capacity", type=int)
    add_space.add_argument("address")
    add_space.add_argument("--feature", action="append", default=[])
    add_space.add_argument("--notes")

    add_event = subparsers.add_parser("add-event", help="Add an event")
    add_event.add_argument("event_id")
    add_event.add_argument("title")
    add_event.add_argument("event_type", choices=[e.value for e in EventType])
    add_event.add_argument("start")
    add_event.add_argument("end")
    add_event.add_argument("--space")
    add_event.add_argument("--participant", action="append", default=[])
    add_event.add_argument("--notes")
    add_event.add_argument("--min-capacity", type=int)
    add_event.add_argument("--require", action="append", default=[])

    list_events = subparsers.add_parser("list-events", help="List events")
    list_events.add_argument("--start")
    list_events.add_argument("--end")
    list_events.add_argument("--type", choices=[e.value for e in EventType])

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    manager = ChoirManager(args.storage)

    if args.command == "add-space":
        manager.add_space(
            space_id=args.space_id,
            name=args.name,
            capacity=args.capacity,
            address=args.address,
            features=args.feature,
            notes=args.notes,
        )
        print(f"Added space '{args.name}'.")
        return

    if args.command == "add-event":
        event = manager.add_event(
            event_id=args.event_id,
            title=args.title,
            event_type=EventType(args.event_type),
            start=parse_datetime(args.start),
            end=parse_datetime(args.end),
            space_id=args.space,
            participants=args.participant,
            notes=args.notes,
            min_capacity=args.min_capacity,
            required_features=args.require,
        )
        print(f"Added event '{event.title}' in space '{event.space_id}'.")
        return

    if args.command == "list-events":
        start = parse_datetime(args.start) if args.start else None
        end = parse_datetime(args.end) if args.end else None
        event_type = EventType(args.type) if args.type else None
        events = manager.list_events(start=start, end=end, event_type=event_type)
        for event in events:
            print(
                f"{event.start:%Y-%m-%d %H:%M} - {event.end:%H:%M} | "
                f"{event.title} ({event.event_type.value}) @ {event.space_id}"
            )
        return


if __name__ == "__main__":
    main()
