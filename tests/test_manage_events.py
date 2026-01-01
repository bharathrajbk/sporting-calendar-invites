import unittest
import sys
import os
import json
import argparse
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime

# Add parent directory to path to import manage_events
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import manage_events

class TestManageEvents(unittest.TestCase):

    def setUp(self):
        self.sample_event = {
            "summary": "Test Event",
            "start_date": "2026-01-01",
            "end_date": "2026-01-02",
            "category": "Test"
        }

    def test_validate_date_valid(self):
        date_str = "2026-01-01"
        self.assertEqual(manage_events.validate_date(date_str), date_str)

    def test_validate_date_invalid(self):
        date_str = "01-01-2026"
        with self.assertRaises(argparse.ArgumentTypeError):
            manage_events.validate_date(date_str)

    @patch('manage_events.load_events')
    @patch('manage_events.save_events')
    def test_add_event(self, mock_save, mock_load):
        mock_load.return_value = []
        args = MagicMock()
        args.summary = "New Event"
        args.start_date = "2026-02-01"
        args.end_date = "2026-02-02"
        args.category = "General"
        args.regenerate = False

        manage_events.add_event(args)

        mock_save.assert_called_once()
        saved_events = mock_save.call_args[0][0]
        self.assertEqual(len(saved_events), 1)
        self.assertEqual(saved_events[0]['summary'], "New Event")

    @patch('manage_events.load_events')
    @patch('manage_events.save_events')
    def test_delete_event(self, mock_save, mock_load):
        mock_load.return_value = [self.sample_event]
        args = MagicMock()
        args.summary = "Test Event"
        args.regenerate = False

        manage_events.delete_event(args)

        mock_save.assert_called_once()
        saved_events = mock_save.call_args[0][0]
        self.assertEqual(len(saved_events), 0)

    @patch('manage_events.load_events')
    @patch('manage_events.save_events')
    def test_delete_event_not_found(self, mock_save, mock_load):
        mock_load.return_value = [self.sample_event]
        args = MagicMock()
        args.summary = "Nonexistent Event"
        args.regenerate = False

        manage_events.delete_event(args)

        mock_save.assert_not_called()

    @patch('builtins.open', new_callable=mock_open, read_data='[{"summary": "Test", "start_date": "2026-01-01", "end_date": "2026-01-01"}]')
    @patch('manage_events.load_template')
    def test_generate_ics(self, mock_load_template, mock_file):
        mock_load_template.side_effect = ["Calendar {events}", "Event {summary}"]
        
        manage_events.generate_ics('dummy.json', 'dummy.ics')
        
        # Check if templates were loaded
        self.assertEqual(mock_load_template.call_count, 2)
        
        # Check if output file was written
        handle = mock_file()
        handle.write.assert_called()

if __name__ == '__main__':
    unittest.main()
