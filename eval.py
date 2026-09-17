from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from src.agent import AgentResult, run_agent
from src.data import CURRENT_USER, INITIAL_BOOKINGS, OfficeDB


@dataclass
class EvalCase:
    name: str
    prompt: str
    check: Callable[[AgentResult], tuple[bool, str]]


def _new_user_bookings(result: AgentResult) -> list[dict]:
    original_ids = {booking["id"] for booking in INITIAL_BOOKINGS}
    return [
        booking
        for booking in result.db.bookings
        if booking["owner"] == CURRENT_USER and booking["id"] not in original_ids
    ]


def check_capacity_booking(result: AgentResult) -> tuple[bool, str]:
    created = _new_user_bookings(result)
    if len(created) != 1:
        return False, f"expected exactly 1 new booking, got {len(created)}"

    booking = created[0]
    room = next(room for room in result.db.rooms if room["name"] == booking["room"])
    ok = (
        room["capacity"] >= 8
        and booking["start"].startswith("2026-09-17T14:00")
        and booking["end"].startswith("2026-09-17T15:00")
    )
    return ok, f"created {booking['room']} (capacity {room['capacity']})"


def check_named_availability(result: AgentResult) -> tuple[bool, str]:
    tools = [entry["tool"] for entry in result.trace]
    no_side_effect = not _new_user_bookings(result)
    used_schedule = "get_room_schedule" in tools
    mentions_unavailable = any(
        word in result.text.lower()
        for word in ("not available", "unavailable", "booked", "occupied")
    )
    ok = no_side_effect and used_schedule and mentions_unavailable
    return ok, f"tools={tools}; answer={result.text!r}"


def check_ambiguous_cancel(result: AgentResult) -> tuple[bool, str]:
    remaining = {booking["id"] for booking in result.db.bookings}
    preserved = {"bkg_2001", "bkg_2002"}.issubset(remaining)
    no_cancel = not any(entry["tool"] == "cancel_booking" for entry in result.trace)
    asks = "?" in result.text or any(
        word in result.text.lower() for word in ("which", "multiple", "clarify")
    )
    return preserved and no_cancel and asks, f"answer={result.text!r}"


def check_whiteboard_query(result: AgentResult) -> tuple[bool, str]:
    tools = [entry["tool"] for entry in result.trace]
    wasteful = "get_room_schedule" in tools or "list_my_bookings" in tools
    expected_names = {"Summit", "Redwood", "Juniper", "Canyon"}
    named = {name for name in expected_names if name.lower() in result.text.lower()}
    return not wasteful and named == expected_names, f"tools={tools}; rooms={sorted(named)}"


def check_either_room(result: AgentResult) -> tuple[bool, str]:
    created = _new_user_bookings(result)
    if len(created) != 1:
        return False, f"expected exactly 1 new booking, got {len(created)}"
    booking = created[0]
    valid_room = booking["room"] in {"Summit", "Redwood"}
    valid_time = booking["start"].startswith("2026-09-17T14:00") and booking[
        "end"
    ].startswith("2026-09-17T15:00")
    # Redwood is occupied then, so a correct implementation should end up with Summit.
    return valid_room and valid_time, f"created={booking}"


CASES = [
    EvalCase(
        "capacity_and_availability",
        "Find somewhere for eight people tomorrow at 2 PM and book it for an hour.",
        check_capacity_booking,
    ),
    EvalCase(
        "known_room_availability",
        "Is Summit available tomorrow at 3 PM?",
        check_named_availability,
    ),
    EvalCase(
        "ambiguous_cancel",
        "Cancel my meeting tomorrow.",
        check_ambiguous_cancel,
    ),
    EvalCase(
        "feature_only_query",
        "What rooms have a whiteboard?",
        check_whiteboard_query,
    ),
    EvalCase(
        "book_one_of_two",
        "Book either Summit or Redwood tomorrow from 2 PM to 3 PM, whichever works.",
        check_either_room,
    ),
]


def main() -> None:
    passed = 0
    print(f"Running {len(CASES)} evaluation cases...\n")

    for case in CASES:
        result = run_agent(case.prompt, db=OfficeDB.fresh())
        ok, detail = case.check(result)
        status = "PASS" if ok else "FAIL"
        passed += int(ok)
        print(f"[{status}] {case.name}")
        print(f"  Prompt: {case.prompt}")
        print(f"  {detail}")
        print(f"  Tool trace: {[entry['tool'] for entry in result.trace]}")
        print()

    print(f"Score: {passed}/{len(CASES)}")


if __name__ == "__main__":
    main()
