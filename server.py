#!/usr/bin/env python3
"""Simple HTTP server for Rock Paper Scissors with leaderboard stored in scores.json"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

SCORES_FILE = os.path.join(os.path.dirname(__file__), "scores.json")
PORT = 8765


def load_scores():
    if not os.path.exists(SCORES_FILE):
        return {}
    with open(SCORES_FILE, "r") as f:
        return json.load(f)


def save_scores(data):
    with open(SCORES_FILE, "w") as f:
        json.dump(data, f, indent=2)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silence request logs

    def send_json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/leaderboard":
            scores = load_scores()
            # Sort by wins desc, then win_rate desc
            ranking = []
            for name, s in scores.items():
                total = s["wins"] + s["losses"] + s["draws"]
                rate = round(s["wins"] / total * 100, 1) if total > 0 else 0
                ranking.append({
                    "name": name,
                    "wins": s["wins"],
                    "losses": s["losses"],
                    "draws": s["draws"],
                    "total": total,
                    "win_rate": rate,
                })
            ranking.sort(key=lambda x: (-x["wins"], -x["win_rate"]))
            self.send_json(200, ranking)
            return

        # Serve the HTML file
        html_path = os.path.join(os.path.dirname(__file__), "rock-paper-scissors.html")
        with open(html_path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/score":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            name = body.get("name", "").strip()
            result = body.get("result")  # "win", "loss", "draw"

            if not name or result not in ("win", "loss", "draw"):
                self.send_json(400, {"error": "Invalid payload"})
                return

            scores = load_scores()
            if name not in scores:
                scores[name] = {"wins": 0, "losses": 0, "draws": 0}

            if result == "win":
                scores[name]["wins"] += 1
            elif result == "loss":
                scores[name]["losses"] += 1
            else:
                scores[name]["draws"] += 1

            save_scores(scores)
            self.send_json(200, {"ok": True, "stats": scores[name]})
            return

        self.send_json(404, {"error": "Not found"})


if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Handler)
    print(f"Rock Paper Scissors server running at http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
