# TIE Smart Home – Web Interface & A/B Test

This directory contains the Flask web application that exposes the Smart Home
Voice Assistant and hosts the **A/B test experiment #3**:
_"Add welcome text for conversion"_.

## Setup

```bash
cd web
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 in your browser.

## Experiment

| Segment | Route | Description |
|---|---|---|
| `control` | `/experiment/control` | Standard recording start page (no welcome text) |
| `additional_text` | `/experiment/additional-text` | Recording start page with welcome banner |

Users are automatically assigned a segment (50/50 split) when they visit `/`
and are redirected to the appropriate variant. The assignment is stored in the
server-side session for the duration of the browser session.

## Tracked Events

| Event | Fired when |
|---|---|
| `recording_start_view` | User is shown the recording start page |
| `recording_start_click` | User clicks the **Start Recording** button |

All events are appended to `web/events.jsonl` in newline-delimited JSON format.
You can inspect them at http://localhost:5000/events.

## Metric

```
CONVERSION = COUNT(recording_start_click) / COUNT(recording_start_view)
```
