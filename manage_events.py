import json
import argparse
import sys
from datetime import datetime
import generate_ics

EVENTS_FILE = 'events.json'
ICS_FILE = 'calendar_events.ics'

def load_events():
    try:
        with open(EVENTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_events(events):
    with open(EVENTS_FILE, 'w') as f:
        json.dump(events, f, indent=2)

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD.")

def add_event(args):
    events = load_events()
    new_event = {
        "summary": args.summary,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "category": args.category
    }
    events.append(new_event)
    save_events(events)
    print(f"Added event: {args.summary}")
    
    if args.regenerate:
        print("Regenerating ICS file...")
        generate_ics.generate_ics(EVENTS_FILE, ICS_FILE)

def delete_event(args):
    events = load_events()
    initial_count = len(events)
    
    # Filter out events that exactly match the summary (case-insensitive)
    events = [e for e in events if e['summary'].lower() != args.summary.lower()]
    
    if len(events) < initial_count:
        save_events(events)
        print(f"Deleted event(s) matching: {args.summary}")
        
        if args.regenerate:
            print("Regenerating ICS file...")
            generate_ics.generate_ics(EVENTS_FILE, ICS_FILE)
    else:
        print(f"No event found with summary: {args.summary}")

def list_events(args):
    events = load_events()
    if not events:
        print("No events found.")
        return

    print(f"{'Date':<25} | {'Category':<15} | {'Summary'}")
    print("-" * 80)
    for event in events:
        date_range = f"{event['start_date']} to {event['end_date']}"
        print(f"{date_range:<25} | {event.get('category', 'N/A'):<15} | {event['summary']}")

def main():
    parser = argparse.ArgumentParser(description="Manage sports events for calendar generation.")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Add command
    parser_add = subparsers.add_parser('add', help='Add a new event')
    parser_add.add_argument('summary', help='Name of the event')
    parser_add.add_argument('start_date', type=validate_date, help='Start date (YYYY-MM-DD)')
    parser_add.add_argument('end_date', type=validate_date, help='End date (YYYY-MM-DD)')
    parser_add.add_argument('--category', default='General', help='Event category')
    parser_add.add_argument('--regenerate', action='store_true', help='Regenerate the ICS file after adding')
    parser_add.set_defaults(func=add_event)

    # Delete command
    parser_delete = subparsers.add_parser('delete', help='Delete an event by summary')
    parser_delete.add_argument('summary', help='Exact name of the event to delete')
    parser_delete.add_argument('--regenerate', action='store_true', help='Regenerate the ICS file after deleting')
    parser_delete.set_defaults(func=delete_event)

    # List command
    parser_list = subparsers.add_parser('list', help='List all events')
    parser_list.set_defaults(func=list_events)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
