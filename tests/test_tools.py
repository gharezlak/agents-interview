from __future__ import annotations

import unittest

from src.data import OfficeDB
from src.tools import book_room, cancel_booking, get_room_schedule


class ToolImplementationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.db = OfficeDB.fresh()

    def test_booking_rejects_time_conflict(self) -> None:
        result = book_room(
            self.db,
            room_name="Redwood",
            start="2026-09-17T14:15:00-07:00",
            end="2026-09-17T14:45:00-07:00",
        )
        self.assertIn("error", result)

    def test_back_to_back_booking_is_allowed(self) -> None:
        result = book_room(
            self.db,
            room_name="Redwood",
            start="2026-09-17T15:00:00-07:00",
            end="2026-09-17T16:00:00-07:00",
        )
        self.assertTrue(result.get("ok"))

    def test_user_cannot_cancel_someone_elses_booking(self) -> None:
        result = cancel_booking(self.db, "bkg_1001")
        self.assertIn("error", result)
        self.assertTrue(any(b["id"] == "bkg_1001" for b in self.db.bookings))

    def test_schedule_is_scoped_to_requested_date(self) -> None:
        result = get_room_schedule(self.db, "Summit", "2026-09-17")
        self.assertEqual([b["id"] for b in result["bookings"]], ["bkg_1002"])


if __name__ == "__main__":
    unittest.main()
