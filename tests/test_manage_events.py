import unittest
import sys
import os
import json
import argparse
import io
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

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_events_file_not_found(self, mock_file):
        events = manage_events.load_events()
        self.assertEqual(events, [])

    @patch('builtins.open', new_callable=mock_open, read_data='[{"summary": "Test"}]')
    def test_load_events_success(self, mock_file):
        events = manage_events.load_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['summary'], "Test")

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
    @patch('manage_events.generate_ics')
    def test_add_event_regenerate(self, mock_gen, mock_save, mock_load):
        mock_load.return_value = []
        args = MagicMock()
        args.summary = "New Event"
        args.start_date = "2026-02-01"
        args.end_date = "2026-02-02"
        args.category = "General"
        args.regenerate = True

        manage_events.add_event(args)
        mock_gen.assert_called_once()

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
    @patch('manage_events.generate_ics')
    def test_delete_event_regenerate(self, mock_gen, mock_save, mock_load):
        mock_load.return_value = [self.sample_event]
        args = MagicMock()
        args.summary = "Test Event"
        args.regenerate = True

        manage_events.delete_event(args)
        mock_gen.assert_called_once()

    @patch('manage_events.load_events')
    @patch('manage_events.save_events')
    def test_delete_event_not_found(self, mock_save, mock_load):
        mock_load.return_value = [self.sample_event]
        args = MagicMock()
        args.summary = "Nonexistent Event"
        args.regenerate = False

        manage_events.delete_event(args)

        mock_save.assert_not_called()

    @patch('manage_events.load_events')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_list_events_empty(self, mock_stdout, mock_load):
        mock_load.return_value = []
        args = MagicMock()
        manage_events.list_events(args)
        self.assertIn("No events found.", mock_stdout.getvalue())

    @patch('manage_events.load_events')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_list_events_populated(self, mock_stdout, mock_load):
        mock_load.return_value = [self.sample_event]
        args = MagicMock()
        manage_events.list_events(args)
        self.assertIn("Test Event", mock_stdout.getvalue())

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

    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_generate_ics_file_not_found(self, mock_stdout, mock_file):
        manage_events.generate_ics('missing.json', 'out.ics')
        self.assertIn("Error: missing.json not found.", mock_stdout.getvalue())

    @patch('manage_events.generate_ics')
    def test_generate_command(self, mock_gen_ics):
        args = MagicMock()
        manage_events.generate_command(args)
        mock_gen_ics.assert_called_once_with(manage_events.EVENTS_FILE, manage_events.ICS_FILE)

    @patch('manage_events.add_event')
    def test_main_add(self, mock_add):
        test_args = ['manage_events.py', 'add', 'Test', '2026-01-01', '2026-01-02']
        with patch.object(sys, 'argv', test_args):
            manage_events.main()
            mock_add.assert_called_once()

    @patch('manage_events.delete_event')
    def test_main_delete(self, mock_delete):
        test_args = ['manage_events.py', 'delete', 'Test']
        with patch.object(sys, 'argv', test_args):
            manage_events.main()
            mock_delete.assert_called_once()
            
    @patch('manage_events.list_events')
    def test_main_list(self, mock_list):
        test_args = ['manage_events.py', 'list']
        with patch.object(sys, 'argv', test_args):
            manage_events.main()
            mock_list.assert_called_once()

    @patch('manage_events.generate_command')
    def test_main_generate(self, mock_generate):
        test_args = ['manage_events.py', 'generate']
        with patch.object(sys, 'argv', test_args):
            manage_events.main()
            mock_generate.assert_called_once()

if __name__ == '__main__':
    unittest.main()
