from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import uuid
import json
import os
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'eestech-challenge-2024-secret')

EXPERIMENT_ID = 3
EXPERIMENT_NAME = "Add welcome text for conversion"
SEGMENTS = [
    {"name": "control", "percentage": 0.5},
    {"name": "additional_text", "percentage": 0.5},
]
EXPERIMENT_PERCENTAGE = 1.0  # 100%

EVENTS_LOG_FILE = os.path.join(os.path.dirname(__file__), 'events.jsonl')


def assign_segment():
    """Assign a user to a segment based on configured percentages."""
    roll = random.random()
    if roll > EXPERIMENT_PERCENTAGE:
        return None  # not in experiment
    cumulative = 0.0
    for segment in SEGMENTS:
        cumulative += segment['percentage']
        if roll < cumulative * EXPERIMENT_PERCENTAGE:
            return segment['name']
    return SEGMENTS[-1]['name']


def get_or_create_session():
    """Ensure the session has a user_id and segment assigned."""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    if 'segment' not in session:
        session['segment'] = assign_segment()
    return session['user_id'], session['segment']


def log_event(event_id, segment_id, extra=None):
    """Append a tracking event to the JSONL log file."""
    event = {
        'experiment_id': EXPERIMENT_ID,
        'experiment_name': EXPERIMENT_NAME,
        'event_id': event_id,
        'segment_id': segment_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'user_id': session.get('user_id'),
    }
    if extra:
        event.update(extra)
    with open(EVENTS_LOG_FILE, 'a') as f:
        f.write(json.dumps(event) + '\n')
    return event


@app.route('/')
def index():
    """Entry point: assign segment and redirect to the appropriate variant."""
    user_id, segment = get_or_create_session()
    if segment == 'additional_text':
        return redirect(url_for('recording_additional_text'))
    # control or not in experiment
    return redirect(url_for('recording_control'))


@app.route('/experiment/control')
def recording_control():
    """Control variant: standard recording start page without welcome text."""
    user_id, segment = get_or_create_session()
    # Override segment to control if someone navigates directly (for testing)
    segment = session.get('segment', 'control')
    log_event('recording_start_view', segment_id=segment)
    return render_template('control.html', segment=segment)


@app.route('/experiment/additional-text')
def recording_additional_text():
    """Additional text variant: recording start page with welcome text."""
    user_id, segment = get_or_create_session()
    segment = session.get('segment', 'additional_text')
    log_event('recording_start_view', segment_id=segment)
    return render_template('additional_text.html', segment=segment)


@app.route('/track/recording-start', methods=['POST'])
def track_recording_start():
    """Track the recording_start_click event."""
    user_id, segment = get_or_create_session()
    segment = session.get('segment', 'control')
    event = log_event('recording_start_click', segment_id=segment)
    return jsonify({'status': 'ok', 'event': event})


@app.route('/recording')
def recording():
    """Actual recording page reached after clicking start."""
    user_id, segment = get_or_create_session()
    return render_template('recording.html', segment=segment)


@app.route('/events')
def view_events():
    """Developer view: display all logged events."""
    events = []
    if os.path.exists(EVENTS_LOG_FILE):
        with open(EVENTS_LOG_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    return render_template('events.html', events=events)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
