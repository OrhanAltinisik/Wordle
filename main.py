import random
from flask import Flask, render_template, request, jsonify, session

with open("words2.txt") as f:
    words = set(f.read().lower().split())

with open("words.txt") as f:
    common_words = f.read().lower().split()

app = Flask(__name__)
app.secret_key = "6cab6c7be741511d99b752e7e370e2a6"

def new_game():
    session["secret"] = random.choice(common_words)
    session["tries"] = 0

@app.route("/")
def home():
    new_game()
    return render_template("index.html")

@app.route("/about")
def about():
    return "<h1>My Wordle game</h1><p>Made by me</p>"

@app.route("/guess", methods=["POST"])
def guess():
    guess = request.get_json()["guess"].lower()
    secret = session["secret"]

    if guess not in words:
        return jsonify({"error": "Not in word list"})

    session["tries"] += 1

    result = ["absent"] * 5
    letters = list(secret)

    for i in range(5):
        if guess[i] == secret[i]:
            result[i] = "correct"
            letters[i] = None
    for i in range(5):
        if result[i] == "absent" and guess[i] in letters:
            result[i] = "present"
            letters[letters.index(guess[i])] = None

    return jsonify({"result": result, "won": guess == secret, "answer": secret if session["tries"] == 6 else None})

if __name__ == "__main__":
    app.run(debug=True)