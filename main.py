import hashlib
import hmac
import os
import re
import secrets
from flask import Flask, render_template, request, jsonify, session

with open("words2.txt") as f:
    words = set(f.read().lower().split())

with open("words.txt") as f:
    common_words = f.read().lower().split()

app = Flask(__name__)
# Never fall back to a guessable key; a random one just resets games on restart.
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# Render sets RENDER=true; only require HTTPS cookies there so local dev still works.
app.config["SESSION_COOKIE_SECURE"] = bool(os.environ.get("RENDER"))

MAX_TRIES = 6
GUESS_PATTERN = re.compile(r"^[a-z]{5}$")


def secret_word():
    # The cookie is signed but readable, so it only holds a random game id.
    # The word is derived from that id with the server's secret key.
    digest = hmac.new(app.secret_key.encode(), session["game"].encode(), hashlib.sha256).digest()
    return common_words[int.from_bytes(digest, "big") % len(common_words)]


def new_game():
    session.clear()
    session["game"] = secrets.token_hex(16)
    session["tries"] = 0
    session["done"] = False


@app.after_request
def security_headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if app.config["SESSION_COOKIE_SECURE"]:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Request too large"}), 413


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Something went wrong"}), 500


@app.route("/")
def home():
    new_game()
    return render_template("index.html")

@app.route("/about")
def about():
    return "<h1>My Wordle game</h1><p>Made by me</p>"

@app.route("/guess", methods=["POST"])
def guess():
    if "game" not in session:
        return jsonify({"error": "No game in progress, please refresh the page"}), 400
    if session.get("done"):
        return jsonify({"error": "Game is over, press Restart"}), 400

    data = request.get_json(silent=True)
    guess = data.get("guess") if isinstance(data, dict) else None
    if not isinstance(guess, str) or not GUESS_PATTERN.match(guess.lower()):
        return jsonify({"error": "Guess must be 5 letters"}), 400
    guess = guess.lower()

    if guess not in words:
        return jsonify({"error": "Not in word list"})

    secret = secret_word()
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

    won = guess == secret
    lost = not won and session["tries"] >= MAX_TRIES
    session["done"] = won or lost

    return jsonify({"result": result, "won": won, "answer": secret if lost else None})

if __name__ == "__main__":
    app.run(debug=True)
