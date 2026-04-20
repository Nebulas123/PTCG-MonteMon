from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from random import Random
import sys
from urllib.parse import urlparse

from .deck import expand_deck, parse_deck_text
from .greedy import GreedyOptions, greedy_reaches_target_by_second_turn
from .state import setup_game, setup_opening_hand
from .strategy import load_strategy
from .target import parse_target


ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = ROOT / "web"


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self.send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return
        if parsed.path == "/app.css":
            self.send_file(STATIC_DIR / "app.css", "text/css; charset=utf-8")
            return
        if parsed.path == "/app.js":
            self.send_file(STATIC_DIR / "app.js", "text/javascript; charset=utf-8")
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/simulate":
            self.send_error(404)
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            result = run_web_simulation(payload)
            self.send_json(200, result)
        except Exception as exc:
            self.send_json(400, {"error": str(exc)})

    def send_file(self, path: Path, content_type: str) -> None:
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args) -> None:
        return


def run_web_simulation(payload: dict) -> dict:
    deck = parse_deck_text(str(payload["deck"]))
    target = parse_target(json.loads(str(payload["target"])))
    strategy = load_strategy(payload.get("strategy_path") or ROOT / "examples" / "strategies" / "lugia_greedy.json")
    deck_cards = expand_deck(deck)
    trials = int(payload.get("trials", 1000))
    seed = payload.get("seed")
    rng = Random(None if seed in {None, ""} else int(seed))
    mode = str(payload.get("mode", "two-turn"))
    going = str(payload.get("going", "first"))
    goings = [True, False] if going == "both" else [going == "first"]
    opponent_turn1_disruption = str(payload.get("opponent_turn1_disruption", "none"))
    opponent_turn2_disruption = str(payload.get("opponent_turn2_disruption", "none"))

    results = []
    if mode == "opening-hand":
        return run_opening_hand_web(deck_cards, target, trials, rng)
    if mode == "setup":
        return run_setup_web(deck_cards, target, trials, rng)

    for index, going_first in enumerate(goings):
        local_seed = None if seed in {None, ""} else int(seed) + index
        local_rng = Random(local_seed)
        successes = 0
        total_mulligans = 0
        routes: list[list[str]] = []
        options = GreedyOptions(
            going_first=going_first,
            strategy=strategy,
            opponent_turn1_disruption=opponent_turn1_disruption,
            opponent_turn2_disruption=opponent_turn2_disruption,
        )

        for _ in range(trials):
            opening = setup_opening_hand(deck_cards, local_rng if local_seed is not None else rng)
            total_mulligans += opening.mulligans
            success, route = greedy_reaches_target_by_second_turn(
                opening, target, options, local_rng if local_seed is not None else rng
            )
            if success:
                successes += 1
                if len(routes) < 3:
                    routes.append(route)

        results.append(
            {
                "going": "first" if going_first else "second",
                "trials": trials,
                "successes": successes,
                "probability": successes / trials if trials else 0.0,
                "average_mulligans": total_mulligans / trials if trials else 0.0,
                "routes": routes,
            }
        )

    return {"target": target.name, "results": results}


def run_opening_hand_web(deck_cards: list[str], target, trials: int, rng: Random) -> dict:
    successes = 0
    total_mulligans = 0
    routes: list[list[str]] = []
    for _ in range(trials):
        state = setup_opening_hand(deck_cards, rng)
        total_mulligans += state.mulligans
        if target.matches(state):
            successes += 1
            if len(routes) < 3:
                routes.append([f"opening hand: {', '.join(state.hand)}"])
    return {
        "target": target.name,
        "results": [
            {
                "going": "opening-hand",
                "trials": trials,
                "successes": successes,
                "probability": successes / trials if trials else 0.0,
                "average_mulligans": total_mulligans / trials if trials else 0.0,
                "routes": routes,
            }
        ],
    }


def run_setup_web(deck_cards: list[str], target, trials: int, rng: Random) -> dict:
    successes = 0
    total_mulligans = 0
    routes: list[list[str]] = []
    for _ in range(trials):
        state = setup_game(deck_cards, rng)
        total_mulligans += state.mulligans
        if target.matches(state):
            successes += 1
            if len(routes) < 3:
                routes.append(
                    [
                        f"active: {', '.join(state.active) or 'none'}",
                        f"bench: {', '.join(state.bench) or 'none'}",
                        f"hand: {', '.join(state.hand) or 'none'}",
                        f"prizes: {', '.join(state.prizes) or 'none'}",
                    ]
                )
    return {
        "target": target.name,
        "results": [
            {
                "going": "setup",
                "trials": trials,
                "successes": successes,
                "probability": successes / trials if trials else 0.0,
                "average_mulligans": total_mulligans / trials if trials else 0.0,
                "routes": routes,
            }
        ],
    }


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    server = ThreadingHTTPServer(("127.0.0.1", port), AppHandler)
    print(f"PTCG-MonteMon web app: http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
