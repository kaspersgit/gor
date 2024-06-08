from flask import Flask, render_template, request

app = Flask(__name__)

# Sample riddles (replace with your own!)
riddles = [
    {"riddle": "I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. What am I?", "answer": "a map"},
    {"riddle": "What has to be broken before you can use it?", "answer": "an egg"},
]

current_riddle_index = 0

@app.route("/")
def home():
  global current_riddle_index
  if request.method == "POST":
    answer = request.form.get("answer")
    if answer.lower() == riddles[current_riddle_index]["answer"]:
      current_riddle_index += 1
      if current_riddle_index == len(riddles):
        return render_template("win.html")
  return render_template("index.html", riddle=riddles[current_riddle_index])

if __name__ == "__main__":
  app.run(debug=True)
