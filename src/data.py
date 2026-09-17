from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any

REFERENCE_NOW = datetime.fromisoformat("2026-09-16T16:48:00-07:00")
CURRENT_USER = "greg"

ROOMS = [
    {
        "name": "Summit",
        "capacity": 6,
        "floor": 4,
        "features": ["display", "whiteboard"],
        "notes": "Near the east elevators. Bright in the afternoon.",
        "internal_asset_id": "rm_001_az4",
    },
    {
        "name": "Redwood",
        "capacity": 10,
        "floor": 4,
        "features": ["display", "whiteboard", "video conferencing"],
        "notes": "Large table. Camera framing works best from the north side.",
        "internal_asset_id": "rm_002_az4",
    },
    {
        "name": "Sequoia",
        "capacity": 8,
        "floor": 5,
        "features": ["display", "video conferencing"],
        "notes": "Quiet room near the stairwell.",
        "internal_asset_id": "rm_003_az5",
    },
    {
        "name": "Juniper",
        "capacity": 4,
        "floor": 3,
        "features": ["whiteboard"],
        "notes": "Small focus room.",
        "internal_asset_id": "rm_004_az3",
    },
    {
        "name": "Canyon",
        "capacity": 12,
        "floor": 6,
        "features": ["display", "whiteboard", "video conferencing"],
        "notes": "Boardroom layout.",
        "internal_asset_id": "rm_005_az6",
    },
    {
        "name": "Maple",
        "capacity": 8,
        "floor": 2,
        "features": ["display"],
        "notes": "Interior room with no exterior windows.",
        "internal_asset_id": "rm_006_az2",
    },
]

INITIAL_BOOKINGS = [
    {
        "id": "bkg_1001",
        "room": "Redwood",
        "start": "2026-09-17T14:00:00-07:00",
        "end": "2026-09-17T15:00:00-07:00",
        "title": "Revenue planning",
        "owner": "alex",
    },
    {
        "id": "bkg_1002",
        "room": "Summit",
        "start": "2026-09-17T15:00:00-07:00",
        "end": "2026-09-17T16:00:00-07:00",
        "title": "Partner sync",
        "owner": "jamie",
    },
    {
        "id": "bkg_2001",
        "room": "Juniper",
        "start": "2026-09-17T10:00:00-07:00",
        "end": "2026-09-17T10:30:00-07:00",
        "title": "Hiring sync",
        "owner": CURRENT_USER,
    },
    {
        "id": "bkg_2002",
        "room": "Maple",
        "start": "2026-09-17T11:00:00-07:00",
        "end": "2026-09-17T12:00:00-07:00",
        "title": "Design review",
        "owner": CURRENT_USER,
    },
]


@dataclass
class OfficeDB:
    rooms: list[dict[str, Any]]
    bookings: list[dict[str, Any]]
    next_booking_number: int = 3000

    @classmethod
    def fresh(cls) -> "OfficeDB":
        return cls(rooms=deepcopy(ROOMS), bookings=deepcopy(INITIAL_BOOKINGS))

    def snapshot(self) -> dict[str, Any]:
        return asdict(self)
