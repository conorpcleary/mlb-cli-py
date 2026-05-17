"""
Unit tests for the ApplicationState class.
"""
import unittest
from datetime import datetime
from app.state import ApplicationState


class TestApplicationState(unittest.TestCase):
    """Test cases for pure logic in ApplicationState."""

    def setUp(self):
        self.state = ApplicationState()

    def test_init(self):
        """Test initial state."""
        self.assertIsInstance(self.state.current_date, datetime)
        self.assertIsNone(self.state.active_page)
        # Should match today's month
        month = datetime.now().month
        if month <= 5:
            self.assertEqual(self.state.calendar_page, 0)
        elif month <= 8:
            self.assertEqual(self.state.calendar_page, 1)
        else:
            self.assertEqual(self.state.calendar_page, 2)

    def test_determine_initial_calendar_page(self):
        """Test page determination logic."""
        self.state.current_date = datetime(2026, 4, 1)
        self.state.determine_initial_calendar_page()
        self.assertEqual(self.state.calendar_page, 0)

        self.state.current_date = datetime(2026, 7, 1)
        self.state.determine_initial_calendar_page()
        self.assertEqual(self.state.calendar_page, 1)

        self.state.current_date = datetime(2026, 11, 1)
        self.state.determine_initial_calendar_page()
        self.assertEqual(self.state.calendar_page, 2)

    def test_increment_date(self):
        """Test date incrementing with boundaries."""
        # 1. Normal increment
        self.state.current_date = datetime(2026, 5, 15)
        self.assertTrue(self.state.increment_date())
        self.assertEqual(self.state.current_date, datetime(2026, 5, 16))

        # 2. Boundary snap
        self.state.current_date = datetime(2025, 12, 31)
        self.assertTrue(self.state.increment_date())
        # Snap to Jan 1, then increment to Jan 2
        self.assertEqual(self.state.current_date, datetime(2026, 1, 2))

        # 3. Upper limit
        self.state.current_date = datetime(2026, 12, 31)
        self.assertFalse(self.state.increment_date())
        self.assertEqual(self.state.current_date, datetime(2026, 12, 31))

    def test_decrement_date(self):
        """Test date decrementing with boundaries."""
        # 1. Normal decrement
        self.state.current_date = datetime(2026, 5, 15)
        self.assertTrue(self.state.decrement_date())
        self.assertEqual(self.state.current_date, datetime(2026, 5, 14))

        # 2. Boundary snap
        self.state.current_date = datetime(2027, 1, 1)
        self.assertTrue(self.state.decrement_date())
        # Snap to Dec 31, then decrement to Dec 30
        self.assertEqual(self.state.current_date, datetime(2026, 12, 30))

        # 3. Lower limit
        self.state.current_date = datetime(2026, 1, 1)
        self.assertFalse(self.state.decrement_date())
        self.assertEqual(self.state.current_date, datetime(2026, 1, 1))

    def test_calendar_pagination(self):
        """Test calendar page wrapping."""
        self.state.calendar_page = 2
        self.state.next_calendar_page()
        self.assertEqual(self.state.calendar_page, 0)

        self.state.calendar_page = 0
        self.state.prev_calendar_page()
        self.assertEqual(self.state.calendar_page, 2)

    def test_reset_to_today(self):
        """Test resetting date."""
        self.state.current_date = datetime(2020, 1, 1)
        self.state.reset_to_today()
        self.assertEqual(
            self.state.current_date.strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d')
        )

    def test_screen_properties(self):
        """Test screen property helpers."""
        self.state.active_page = "calendar:0"
        self.assertTrue(self.state.on_calendar_screen)
        self.assertFalse(self.state.on_standings_screen)

        self.state.active_page = "standings"
        self.assertFalse(self.state.on_calendar_screen)
        self.assertTrue(self.state.on_standings_screen)


if __name__ == '__main__':
    unittest.main()
