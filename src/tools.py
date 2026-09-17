from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from .data import CURRENT_USER, OfficeDB, REFERENCE_NOW

# Intentionally terse / overlapping tool descriptions. Improving these is part of the exercise.
TOOL_DEFINITIONS = [
    {
        "name": "list_rooms",
        "description": "List conference rooms.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "search_rooms",
        "description": "Search for rooms.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_room_schedule",
        "description": "Get information about a room and its schedule.",
        "input_schema": {
            "type": "object",
            "properties": {
                "room_name": {"type": "string"},
                "date": {"type": "string", "description": "Date."},
            },
            "required": ["room_name", "date"],
        },
    },
    {
        "name": "list_my_bookings",
        "description": "List bookings.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string"},
            },
            "required": ["date"],
        },
    },
    {
        "name": "book_room",
        "description": "Book a room.",
        "input_schema": {
            "type": "object",
            "properties": {
                "room_name": {"type": "string"},
                "start": {"type": "string"},
                "end": {"type": "string"},
                "title": {"type": "string"},
            },
            "required": ["room_name", "start", "end"],
        },
    },
    {
        "name": "cancel_booking",
        "description": "Cancel a booking.",
        "input_schema": {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string"},
            },
            "required": ["booking_id"],
        },
    },
]


def _parse_dt(value: str) -> datetime:
    """Parse an ISO-8601 datetime. Naive datetimes are intentionally accepted in starter code."""
    return datetime.fromisoformat(value)


def _same_date(iso_datetime: str, date_string: str) -> bool:
    return datetime.fromisoformat(iso_datetime).date().isoformat() == date_string


def _find_room(db: OfficeDB, room_name: str) -> dict[str, Any] | None:
    wanted = room_name.strip().lower()
    return next((room for room in db.rooms if room["name"].lower() == wanted), None)


def list_rooms(db: OfficeDB) -> list[dict[str, Any]]:
    # Starter version returns every field, including fields that do not help the model decide.
    return db.rooms


def search_rooms(db: OfficeDB, query: str) -> list[dict[str, Any]]:
    # Starter implementation only searches the room name, not features or other structured criteria.
    # It is also case-sensitive.
    return [room for room in db.rooms if query in room["name"]]


def get_room_schedule(db: OfficeDB, room_name: str, date: str) -> dict[str, Any]:
    room = _find_room(db, room_name)
    if room is None:
        return {"error": f"Unknown room: {room_name}"}

    bookings = [
        booking
        for booking in db.bookings
        if booking["room"].lower() == room["name"].lower()
        and _same_date(booking["start"], date)
    ]
    # Deliberately returns the full room record and full booking records.
    return {"room": room, "bookings": bookings}


def list_my_bookings(db: OfficeDB, date: str) -> list[dict[str, Any]]:
    return [
        booking
        for booking in db.bookings
        if booking["owner"] == CURRENT_USER and _same_date(booking["start"], date)
    ]


def book_room(
    db: OfficeDB,
    room_name: str,
    start: str,
    end: str,
    title: str = "Reserved room",
) -> dict[str, Any]:
    room = _find_room(db, room_name)
    if room is None:
        return {"error": f"Unknown room: {room_name}"}

    start_dt = _parse_dt(start)
    end_dt = _parse_dt(end)
    if end_dt <= start_dt:
        return {"error": "end must be after start"}

    conflicts = []
    for booking in db.bookings:
        if booking["room"].lower() != room["name"].lower():
            continue
        booked_start = _parse_dt(booking["start"])
        booked_end = _parse_dt(booking["end"])
        if start_dt < booked_end and end_dt > booked_start:
            conflicts.append(booking)

    if conflicts:
        return {"error": "room is not available", "conflicts": conflicts}

    booking = {
        "id": f"bkg_{db.next_booking_number}",
        "room": room["name"],
        "start": start,
        "end": end,
        "title": title,
        "owner": CURRENT_USER,
    }
    db.next_booking_number += 1
    db.bookings.append(booking)
    return {"ok": True, "booking": booking}


def cancel_booking(db: OfficeDB, booking_id: str) -> dict[str, Any]:
    booking = next((b for b in db.bookings if b["id"] == booking_id), None)
    if booking is None:
        return {"error": f"Unknown booking: {booking_id}"}
    if booking["owner"] != CURRENT_USER:
        return {"error": "You may only cancel your own bookings"}

    db.bookings.remove(booking)
    return {"ok": True, "cancelled": booking}


ToolFn = Callable[..., Any]

TOOL_FUNCTIONS: dict[str, ToolFn] = {
    "list_rooms": list_rooms,
    "search_rooms": search_rooms,
    "get_room_schedule": get_room_schedule,
    "list_my_bookings": list_my_bookings,
    "book_room": book_room,
    "cancel_booking": cancel_booking,
}


def execute_tool(db: OfficeDB, name: str, tool_input: dict[str, Any]) -> Any:
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return {"error": f"Unknown tool: {name}"}

    try:
        return fn(db=db, **tool_input)
    except (TypeError, ValueError) as exc:
        # Starter loop serializes this as an ordinary successful tool result.
        return {"error": str(exc)}
