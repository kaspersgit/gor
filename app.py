from flask import Flask, session, render_template, request, redirect, url_for
import uuid
import json
import os
import pickle 

app = Flask(__name__, template_folder='templates', static_folder='staticFiles')

# Set secret key
app.config["SECRET_KEY"] = uuid.uuid4().hex

# The actual riddles
with open('riddles.json') as f:
    riddles = json.load(f)

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return redirect(url_for('riddling', method='GET'))

@app.route('/login', methods=['POST'])
def do_login():
    session['username'] = request.form['username']
    session['logged_in'] = True

    try:
        with open('usernames.json', 'r') as f:
            usernames_dict = json.load(f)
    except FileNotFoundError:
        usernames_dict = {}
    
    if not session['username'] in usernames_dict:
        usernames_dict[session['username']] = 0

        # Save new username to file
        with open('usernames.json', 'w') as f:
            json.dump(usernames_dict, f)

    return home()

@app.route('/riddling', methods=['POST','GET'])
def riddling():
    # The usernames
    with open('usernames.json', 'r') as f:
        usernames_dict = json.load(f)

    try:
        current_riddle_index = usernames_dict[session['username']]
    except KeyError:
        current_riddle_index = 0

    if session.get('username'):
        print("User " + session.get('username'))
    else:
        session['username'] = 'Anonymous'
        print("New user " + session.get('username'))

    if current_riddle_index == len(riddles):
        return render_template("win.html")
    
    if request.method == "POST":
        answer = request.form.get("answer")

        # If correct answer
        if answer.lower() == riddles[current_riddle_index]["answer"]:
            
            # Set riddle index to next riddle and update for user
            current_riddle_index += 1
            usernames_dict[session['username']] = current_riddle_index
                
            # Save file keeping track of user progress
            with open('usernames.json', 'w') as f:
                json.dump(usernames_dict, f)

        # If riddle is last riddle then show win screen
        if current_riddle_index == len(riddles):
            return render_template("win.html")
    
    # Return updated page with new riddle
    return render_template("index.html", riddle=riddles[current_riddle_index], visitor=session)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
