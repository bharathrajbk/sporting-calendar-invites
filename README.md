# Sports Calendar 2026 Generator

This project generates an iCalendar (`.ics`) file containing major sporting events for 2026, extracted from the "HOT DATES 2026" list.

## Files

- `events.json`: Contains the structured list of events.
- `manage_events.py`: CLI script to add, delete, list, and generate events.
- `templates/`: Directory containing ICS templates.
    - `calendar_template.txt`: Template for the main calendar structure.
    - `event_template.txt`: Template for individual events.
- `calendar_events.ics`: The generated calendar file.

## Customizing Templates

You can customize the output format by editing the files in the `templates/` directory.

- **`calendar_template.txt`**: Controls the VCALENDAR header and footer. The `{events}` placeholder is replaced by the list of events.
- **`event_template.txt`**: Controls the VEVENT block for each event. Available placeholders: `{uid}`, `{dtstamp}`, `{dtstart}`, `{dtend}`, `{summary}`, `{category}`.

## Managing Events (CLI)

You can use the `manage_events.py` script to easily add, delete, list, or generate events.

### List Events

To see all currently configured events:

```bash
python3 manage_events.py list
```

### Add an Event

To add a new event:

```bash
python3 manage_events.py add "Event Name" YYYY-MM-DD YYYY-MM-DD --category "Category Name"
```

**Example:**
```bash
python3 manage_events.py add "My Special Match" 2026-05-10 2026-05-10 --category "Football"
```

To add an event and **immediately regenerate** the calendar file, use the `--regenerate` flag:

```bash
python3 manage_events.py add "My Special Match" 2026-05-10 2026-05-10 --category "Football" --regenerate
```

### Delete an Event

To delete an event (must match the summary exactly):

```bash
python3 manage_events.py delete "Event Name"
```

To delete and **immediately regenerate** the calendar file:

```bash
python3 manage_events.py delete "Event Name" --regenerate
```

### Generate Calendar

To manually regenerate the `.ics` file from `events.json`:

```bash
python3 manage_events.py generate
```

## Importing into Google Calendar

1.  Open [Google Calendar](https://calendar.google.com/).
2.  Click the **Settings** (gear icon) > **Settings**.
3.  In the left sidebar, click **Import & export**.
4.  Under **Import**, click **Select file from your computer**.
5.  Select the `calendar_events.ics` file.
6.  Choose the destination calendar.
7.  Click **Import**.
