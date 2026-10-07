import random
from flask import Flask, render_template, request, jsonify

with open("words2.txt") as f:
    words = set(f.read().lower().split())

with open("words.txt") as f:
    common_words = f.read().lower().split()

secret = random.choice(common_words)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return "<h1>My Wordle game</h1><p>Made by me</p>"

@app.route("/guess", methods=["POST"])
def guess():
    guess = request.get_json()["guess"].lower()
    last = request.get_json()["last"]

    if guess not in words:
        return jsonify({"error": "Not in word list"})

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

    return jsonify({"result": result, "won": guess == secret, "answer": secret if last else None})

@app.route("/restart", methods=["POST"])
def restart():
    global secret
    secret = random.choice(common_words)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)