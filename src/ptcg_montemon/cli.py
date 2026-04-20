from __future__ import annotations

import argparse
import json

from .deck import load_deck
from .sim import run_opening_hand_trials, run_setup_trials, run_two_turn_trials
from .strategy import load_strategy
from .target import load_target


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Estimate PTCG target board-state odds.")
    parser.add_argument("--deck", required=True, help="Path to a deck list text file.")
    parser.add_argument("--target", required=True, help="Path to a target JSON file.")
    parser.add_argument("--trials", type=int, default=10000, help="Number of Monte Carlo trials.")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed.")
    parser.add_argument(
        "--mode",
        choices=["opening-hand", "setup", "two-turn"],
        default="setup",
        help="Simulation mode.",
    )
    parser.add_argument(
        "--going",
        choices=["first", "second", "both"],
        default="both",
        help="Whether our side goes first, second, or both. Used by --mode two-turn.",
    )
    parser.add_argument(
        "--no-first-turn-draw",
        action="store_true",
        help="Disable drawing at the start of the first player's first turn.",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Print one successful route when the route finder finds one.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Print structured JSON results for UI integration.",
    )
    parser.add_argument(
        "--strategy",
        default=None,
        help="Optional greedy strategy JSON file for --mode two-turn.",
    )
    parser.add_argument(
        "--opponent-disruption",
        choices=["none", "iono", "judge"],
        default="none",
        help="Optional opponent hand disruption after our turn 1 and before our turn 2.",
    )
    parser.add_argument(
        "--opponent-turn1-disruption",
        choices=["none", "iono", "judge"],
        default="none",
        help="Opponent turn 1 disruption. Going first: before our turn 2. Going second: before our turn 1.",
    )
    parser.add_argument(
        "--opponent-turn2-disruption",
        choices=["none", "iono", "judge"],
        default="none",
        help="Opponent turn 2 disruption. Relevant when going second: before our turn 2.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    deck = load_deck(args.deck)
    target = load_target(args.target)
    strategy = load_strategy(args.strategy)
    if args.mode == "opening-hand":
        result = run_opening_hand_trials(deck, target, trials=args.trials, seed=args.seed)
        if args.json_output:
            print_json_results(target.name, [result], explain=args.explain)
            return
        print_result(target.name, result, explain=args.explain)
        return

    if args.mode == "setup":
        result = run_setup_trials(deck, target, trials=args.trials, seed=args.seed)
        if args.json_output:
            print_json_results(target.name, [result], explain=args.explain)
            return
        print_result(target.name, result, explain=args.explain)
        return

    goings = [True, False] if args.going == "both" else [args.going == "first"]
    results = []
    for index, going_first in enumerate(goings):
        result = run_two_turn_trials(
            deck,
            target,
            trials=args.trials,
            seed=None if args.seed is None else args.seed + index,
            going_first=going_first,
            first_turn_draw=not args.no_first_turn_draw,
            strategy=strategy,
            opponent_disruption=args.opponent_disruption,
            opponent_turn1_disruption=args.opponent_turn1_disruption,
            opponent_turn2_disruption=args.opponent_turn2_disruption,
        )
        results.append(result)
    if args.json_output:
        print_json_results(target.name, results, explain=args.explain)
        return
    for result in results:
        print_result(target.name, result, explain=args.explain)


def print_result(target_name: str, result, explain: bool = False) -> None:
    print(f"target: {target_name}")
    print(f"mode: {result.mode}")
    if result.going:
        print(f"going: {result.going}")
    if result.opponent_disruption != "none":
        print(f"opponent_disruption: {result.opponent_disruption}")
    if result.opponent_turn1_disruption != "none":
        print(f"opponent_turn1_disruption: {result.opponent_turn1_disruption}")
    if result.opponent_turn2_disruption != "none":
        print(f"opponent_turn2_disruption: {result.opponent_turn2_disruption}")
    print(f"trials: {result.trials}")
    print(f"successes: {result.successes}")
    print(f"probability: {result.probability:.4%}")
    print(f"average_mulligans: {result.average_mulligans:.4f}")
    if explain and result.example_route:
        print("example_route:")
        for step in result.example_route:
            print(f"- {step}")


def print_json_results(target_name: str, results, explain: bool = False) -> None:
    payload = {
        "target": target_name,
        "results": [
            {
                "mode": result.mode,
                "going": result.going,
                "opponent_disruption": result.opponent_disruption,
                "opponent_turn1_disruption": result.opponent_turn1_disruption,
                "opponent_turn2_disruption": result.opponent_turn2_disruption,
                "trials": result.trials,
                "successes": result.successes,
                "probability": result.probability,
                "average_mulligans": result.average_mulligans,
                "example_route": list(result.example_route) if explain else [],
            }
            for result in results
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
