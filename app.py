from flask import Flask, flash, session, render_template, request, redirect, url_for
from functools import wraps
import os
from aws_controller import get_user, get_riddle, get_all_riddles, update_user_progress
import botocore
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file (for development)
load_dotenv()

# Setup flask app
app = Flask(__name__, template_folder='templates', static_folder='staticFiles')

# Set the secret key from the environment variable
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

if not app.config['SECRET_KEY']:
    raise ValueError("No SECRET_KEY set for Flask application")

def completed_riddles(user_progress):
    return [int(riddle_id) for riddle_id, progress in user_progress.items() if progress.get("completed_at")]

def choose_next_riddle(riddles, user_progress):
    completed_riddle_ids = completed_riddles(user_progress)
    all_riddle_ids = [int(riddle['id']) for riddle in riddles]
    remaining_riddle_ids = [i for i in all_riddle_ids if i not in completed_riddle_ids]
    if remaining_riddle_ids:
        # return str(random.choice(remaining_riddle_ids)) # TODO proper implementation
        return str(min(remaining_riddle_ids))
    else:
        raise ValueError('No remaining riddles')

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return redirect(url_for('riddling', method='GET'))

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    session['username'] = username

    try:
        user_info = get_user(username)
        if user_info:
            session['logged_in'] = True
            session['progress'] = user_info['progress']
        else:
            session['logged_in'] = True
            session['progress'] = {}
    except botocore.exceptions.ClientError as e:
        flash(f"Error logging in: {e}")

    return redirect(url_for('home'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # Clear the session
    session['logged_in'] = False
    session.pop('current_riddle_id', None)
    session.pop('attempts_left', None)
    session.pop('progress', None)
    session.pop('progress_simple', None)
    # Redirect to the login page or home page
    return render_template('index.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/riddling', methods=['POST', 'GET'])
@login_required
def riddling():
    username = session.get('username', 'Anonymous')
    user_progress = session['progress']
    riddles = get_all_riddles()

    if len(user_progress) == len(riddles):
        return render_template("win.html")

    # Check if user is in timeout
    timeout_until = session.get('timeout_until')
    if timeout_until:
        timeout_datetime = datetime.fromisoformat(timeout_until)
        if datetime.now() < timeout_datetime:
            return render_template("timeout.html", timeout_until=timeout_until)
        else:
            # Timeout has expired, clear timeout-related session data
            session.pop('timeout_until', None)
            session.pop('attempts_left', None)
            session.pop('current_riddle_id', None)

    # Load or choose the current riddle
    current_riddle_id = session.get('current_riddle_id')
    if not current_riddle_id:
        current_riddle_id = choose_next_riddle(riddles, user_progress)
        session['current_riddle_id'] = current_riddle_id

    current_riddle = get_riddle(current_riddle_id)
    attempts_left = session.get('attempts_left', int(current_riddle['allowed_attempts']))

    if request.method == "POST":
        answer = request.form.get("answer", "").lower()
        correct = answer == current_riddle["answer"].lower()

        if correct:
            updated_progress = update_user_progress(
                username=username,
                riddle_id=current_riddle_id,
                solved=True
            )
            session['progress'] = updated_progress
            user_progress = updated_progress
            if len(user_progress) == len(riddles):
                return render_template("win.html")

            # Choose next riddle only if the current one was solved
            next_riddle_id = choose_next_riddle(riddles, user_progress)
            session['current_riddle_id'] = next_riddle_id
            current_riddle = get_riddle(next_riddle_id)
            attempts_left = int(current_riddle['allowed_attempts'])
        else:
            attempts_left -= 1
            update_user_progress(
                username=username,
                riddle_id=current_riddle_id,
                solved=False
            )

            if attempts_left == 0:
                timeout_until = (datetime.now() + timedelta(hours=12)).isoformat()
                session['timeout_until'] = timeout_until
                session['attempts_left'] = attempts_left
                return render_template("timeout.html", timeout_until=timeout_until)


    session['attempts_left'] = attempts_left
    solved_riddles = len(completed_riddles(user_progress))
    session['progress_simple'] = f'{solved_riddles + 1} / {len(riddles)}'

    return render_template(
        "riddles.html",
        riddle=current_riddle,
        visitor=session,
        attempts_left=attempts_left
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
