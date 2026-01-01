import json
import argparse
import sys
import os
import uuid
from datetime import datetime, timedelta

EVENTS_FILE = 'events.json'
ICS_FILE = 'calendar_events.ics'

def load_template(template_name):
    template_path = os.path.join('templates', template_name)
    with open(template_path, 'r') as f:
        return f.read()

def generate_ics(json_file, output_file):
    try:
        with open(json_file, 'r') as f:
            events = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_file} not found.")
        return

    # Load templates
    calendar_template = load_template('calendar_template.txt')
    event_template = load_template('event_template.txt')

    events_content = []

    for event in events:
        summary = event['summary']
        start_date_str = event['start_date']
        end_date_str = event['end_date']
        category = event.get('category', 'General')

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        # Adjust end date for exclusive DTEND (add 1 day)
        end_date_exclusive = end_date + timedelta(days=1)
        dtstart = start_date.strftime("%Y-%m-%d").replace("-", "")
        dtend = end_date_exclusive.strftime("%Y-%m-%d").replace("-", "")
        # Use datetime.now(datetime.UTC) if available (Python 3.11+), else fallback or ignore deprecation for now
        # Keeping it simple and compatible
        dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        uid = str(uuid.uuid4())

        # Fill event template
        event_str = event_template.format(
            uid=uid,
            dtstamp=dtstamp,
            dtstart=dtstart,
            dtend=dtend,
            summary=summary,
            category=category
        )
        events_content.append(event_str)

    # Fill calendar template
    final_ics = calendar_template.format(events="\n".join(events_content))

    with open(output_file, 'w') as f:
        f.write(final_ics)

    print(f"Successfully generated {output_file} with {len(events)} events.")

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
        generate_ics(EVENTS_FILE, ICS_FILE)

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
            generate_ics(EVENTS_FILE, ICS_FILE)
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

def generate_command(args):
    generate_ics(EVENTS_FILE, ICS_FILE)

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

    # Generate command
    parser_generate = subparsers.add_parser('generate', help='Generate ICS file from events')
    parser_generate.set_defaults(func=generate_command)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
