import base64
import json
import unittest
from unittest import mock

from flask import session

import main
from main import app, common_words


def cookie_payload(client):
    raw = client.get_cookie("session").value.lstrip(".").split(".")[0]
    return json.loads(base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)))


def answer_for(client):
    with client.session_transaction() as s:
        game = s["game"]
    with app.test_request_context():
        session["game"] = game
        return main.secret_word()


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.get("/")

    def guess(self, body):
        return self.client.post("/guess", json=body)

    def test_cookie_does_not_reveal_answer(self):
        payload = cookie_payload(self.client)
        answer = answer_for(self.client)
        self.assertNotIn("secret", payload)
        self.assertNotIn(answer, json.dumps(payload))

    def test_tampered_cookie_is_rejected(self):
        self.client.set_cookie("session", "eyJnYW1lIjoiYWJjIiwidHJpZXMiOjB9.fake.sig")
        r = self.guess({"guess": "crane"})
        self.assertEqual(r.status_code, 400)

    def test_guess_without_game(self):
        r = app.test_client().post("/guess", json={"guess": "crane"})
        self.assertEqual(r.status_code, 400)

    def test_bad_inputs_do_not_crash(self):
        bad = [None, {}, [], "crane", {"guess": None}, {"guess": 12345}, {"guess": ["c"]},
               {"guess": {"a": 1}}, {"guess": "abc"}, {"guess": "crane!"}, {"guess": "<scr>"},
               {"guess": "ÄÖÜßé"}, {"guess": "a" * 500}]
        for body in bad:
            r = self.guess(body)
            self.assertEqual(r.status_code, 400, body)
            self.assertIn("error", r.get_json())
        r = self.client.post("/guess", data="not json", content_type="application/json")
        self.assertEqual(r.status_code, 400)
        r = self.client.post("/guess", data="guess=crane")
        self.assertEqual(r.status_code, 400)

    def test_huge_request_rejected(self):
        r = self.guess({"guess": "a" * 5000})
        self.assertEqual(r.status_code, 413)

    def test_answer_hidden_until_game_lost(self):
        answer = answer_for(self.client)
        wrong = [w for w in common_words if w != answer][:6]
        for i, w in enumerate(wrong):
            data = self.guess({"guess": w}).get_json()
            self.assertEqual(data["answer"], answer if i == 5 else None)
        r = self.guess({"guess": answer})
        self.assertEqual(r.status_code, 400)

    def test_no_guesses_after_win(self):
        answer = answer_for(self.client)
        self.assertTrue(self.guess({"guess": answer}).get_json()["won"])
        self.assertEqual(self.guess({"guess": answer}).status_code, 400)

    def test_scoring(self):
        with mock.patch.object(main, "secret_word", return_value="apple"):
            data = self.guess({"guess": "paper"}).get_json()
            self.assertEqual(data["result"], ["present", "present", "correct", "present", "absent"])
            data = self.guess({"guess": "PLANT"}).get_json()
            self.assertEqual(data["result"], ["present", "present", "present", "absent", "absent"])

    def test_security_headers(self):
        r = self.client.get("/")
        for h in ["Content-Security-Policy", "X-Content-Type-Options", "X-Frame-Options", "Referrer-Policy"]:
            self.assertIn(h, r.headers)
        cookie = r.headers["Set-Cookie"]
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=Lax", cookie)

    def test_other_routes(self):
        self.assertEqual(self.client.get("/guess").status_code, 405)
        self.assertEqual(self.client.get("/nope").status_code, 404)
        self.assertEqual(self.client.get("/static/../main.py").status_code, 404)


if __name__ == "__main__":
    unittest.main()
