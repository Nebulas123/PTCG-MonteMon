from __future__ import annotations

from dataclasses import dataclass
from random import Random

from .deck import DeckEntry, expand_deck
from .greedy import GreedyOptions, greedy_reaches_target_by_second_turn
from .state import GameState, setup_game, setup_opening_hand
from .strategy import GreedyStrategy, default_strategy
from .target import Target


@dataclass(frozen=True)
class SimulationResult:
    trials: int
    successes: int
    probability: float
    average_mulligans: float
    mode: str = "setup"
    going: str | None = None
    opponent_disruption: str = "none"
    opponent_turn1_disruption: str = "none"
    opponent_turn2_disruption: str = "none"
    example_route: tuple[str, ...] = ()


def run_opening_hand_trials(
    entries: list[DeckEntry], target: Target, trials: int, seed: int | None = None
) -> SimulationResult:
    rng = Random(seed)
    deck_cards = expand_deck(entries)
    successes = 0
    total_mulligans = 0
    example_route: tuple[str, ...] = ()

    for _ in range(trials):
        state = setup_opening_hand(deck_cards, rng)
        total_mulligans += state.mulligans
        if target.matches(state):
            successes += 1
            if not example_route:
                example_route = (f"opening hand: {', '.join(state.hand)}",)

    return SimulationResult(
        trials=trials,
        successes=successes,
        probability=successes / trials if trials else 0.0,
        average_mulligans=total_mulligans / trials if trials else 0.0,
        mode="opening_hand",
        example_route=example_route,
    )


def run_setup_trials(entries: list[DeckEntry], target: Target, trials: int, seed: int | None = None) -> SimulationResult:
    rng = Random(seed)
    deck_cards = expand_deck(entries)
    successes = 0
    total_mulligans = 0

    for _ in range(trials):
        state = setup_game(deck_cards, rng)
        total_mulligans += state.mulligans
        if target.matches(state):
            successes += 1

    return SimulationResult(
        trials=trials,
        successes=successes,
        probability=successes / trials if trials else 0.0,
        average_mulligans=total_mulligans / trials if trials else 0.0,
    )


def run_two_turn_trials(
    entries: list[DeckEntry],
    target: Target,
    trials: int,
    seed: int | None = None,
    going_first: bool = True,
    first_turn_draw: bool = True,
    strategy: GreedyStrategy | None = None,
    opponent_disruption: str = "none",
    opponent_turn1_disruption: str = "none",
    opponent_turn2_disruption: str = "none",
) -> SimulationResult:
    rng = Random(seed)
    deck_cards = expand_deck(entries)
    successes = 0
    total_mulligans = 0
    example_route: tuple[str, ...] = ()
    options = GreedyOptions(
        going_first=going_first,
        first_turn_draw=first_turn_draw,
        strategy=strategy or default_strategy(),
        opponent_disruption=opponent_disruption,
        opponent_turn1_disruption=opponent_turn1_disruption,
        opponent_turn2_disruption=opponent_turn2_disruption,
    )

    for _ in range(trials):
        opening = setup_opening_hand(deck_cards, rng)
        total_mulligans += opening.mulligans
        success, route = greedy_reaches_target_by_second_turn(opening, target, options, rng)
        if success:
            successes += 1
            if not example_route:
                example_route = tuple(route)

    return SimulationResult(
        trials=trials,
        successes=successes,
        probability=successes / trials if trials else 0.0,
        average_mulligans=total_mulligans / trials if trials else 0.0,
        mode="two_turn_greedy",
        going="first" if going_first else "second",
        opponent_disruption=opponent_disruption,
        opponent_turn1_disruption=opponent_turn1_disruption,
        opponent_turn2_disruption=opponent_turn2_disruption,
        example_route=example_route,
    )


def describe_state(state: GameState) -> dict[str, list[str] | int]:
    return {
        "active": state.active,
        "bench": state.bench,
        "prizes": state.prizes,
        "hand": state.hand,
        "discard": state.discard,
        "stadium": state.stadium,
        "deck_count": len(state.deck),
        "mulligans": state.mulligans,
    }
