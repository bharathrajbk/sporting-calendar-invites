import json
import uuid
import os
from datetime import datetime, timedelta

def load_template(template_name):
    template_path = os.path.join('templates', template_name)
    with open(template_path, 'r') as f:
        return f.read()

def generate_ics(json_file, output_file):
    with open(json_file, 'r') as f:
        events = json.load(f)

    # Load templates
    calendar_template = load_template('calendar_template.txt')
    event_template = load_template('event_template.txt')

    events_content = []

    for event in events:
        summary = event['summary']
        start_date_str = event['start_date']
        end_date_str = event['end_date']
        category = event.get('category', 'General')

        # Parse dates
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # Adjust end date for exclusive DTEND (add 1 day)
        end_date_exclusive = end_date + timedelta(days=1)

        # Format dates for ICS (YYYYMMDD for all-day events)
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

if __name__ == "__main__":
    generate_ics('events.json', 'calendar_events.ics')
