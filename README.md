# Clarinet Choir Manager

A lightweight, file-backed system for managing clarinet choir rehearsal spaces, concerts, and outreach events. It automatically assigns available venues based on capacity and feature requirements, preventing scheduling conflicts.

## Features
- Track rehearsal spaces with capacities, addresses, and equipment.
- Schedule events with automatic space assignment.
- Detect scheduling conflicts for the same space.
- List events by date range or type.

## Quick start

```bash
python -m clarinet_choir.cli add-space studio-a "Studio A" 40 "123 Music Ln" --feature "piano" --feature "accessible"
python -m clarinet_choir.cli add-space hall-main "Main Hall" 120 "456 Concert Ave" --feature "stage" --feature "recording"

python -m clarinet_choir.cli add-event reh-001 "Tuesday Rehearsal" rehearsal 2024-11-05T18:00 2024-11-05T20:00 --min-capacity 35 --require piano
python -m clarinet_choir.cli add-event con-001 "Fall Concert" concert 2024-11-12T19:30 2024-11-12T21:00 --space hall-main --participant "Full Choir"

python -m clarinet_choir.cli list-events --start 2024-11-01T00:00 --end 2024-12-01T00:00
```

## Data storage
Data is stored in `data/choir.json` by default. You can override the path with `--storage`.

## Extending
The `ChoirManager` class in `clarinet_choir/manager.py` can be used by other scripts or integrations to automate reminders, sync with calendars, or generate reports.
