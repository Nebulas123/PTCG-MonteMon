from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from .cards import CARD_DEFS


ZoneName = str


@dataclass
class GameState:
    deck: list[str]
    hand: list[str] = field(default_factory=list)
    prizes: list[str] = field(default_factory=list)
    active: list[str] = field(default_factory=list)
    bench: list[str] = field(default_factory=list)
    active_turns: list[int] = field(default_factory=list)
    bench_turns: list[int] = field(default_factory=list)
    discard: list[str] = field(default_factory=list)
    stadium: list[str] = field(default_factory=list)
    attached_energy: list[str] = field(default_factory=list)
    energy_attached_turns: list[int] = field(default_factory=list)
    mulligans: int = 0
    turn: int = 0
    supporter_played: bool = False
    squawk_used: bool = False
    luminous_sign_used: bool = False
    dark_asset_used: bool = False
    summoning_star_used: bool = False
    mesagoza_used_turns: list[int] = field(default_factory=list)
    route: list[str] = field(default_factory=list)

    def zone(self, name: ZoneName) -> list[str]:
        zones = {
            "deck": self.deck,
            "hand": self.hand,
            "prizes": self.prizes,
            "active": self.active,
            "bench": self.bench,
            "discard": self.discard,
            "stadium": self.stadium,
        }
        try:
            return zones[name]
        except KeyError as exc:
            raise KeyError(f"Unknown zone: {name}") from exc

    def draw(self, count: int) -> list[str]:
        drawn = []
        for _ in range(min(count, len(self.deck))):
            card = self.deck.pop(0)
            self.hand.append(card)
            drawn.append(card)
        return drawn

    def copy(self) -> "GameState":
        return GameState(
            deck=list(self.deck),
            hand=list(self.hand),
            prizes=list(self.prizes),
            active=list(self.active),
            bench=list(self.bench),
            active_turns=list(self.active_turns),
            bench_turns=list(self.bench_turns),
            discard=list(self.discard),
            stadium=list(self.stadium),
            attached_energy=list(self.attached_energy),
            energy_attached_turns=list(self.energy_attached_turns),
            mulligans=self.mulligans,
            turn=self.turn,
            supporter_played=self.supporter_played,
            squawk_used=self.squawk_used,
            luminous_sign_used=self.luminous_sign_used,
            dark_asset_used=self.dark_asset_used,
            summoning_star_used=self.summoning_star_used,
            mesagoza_used_turns=list(self.mesagoza_used_turns),
            route=list(self.route),
        )


def has_basic_pokemon(cards: list[str]) -> bool:
    return any(CARD_DEFS[name].is_basic_pokemon for name in cards)


def setup_game(deck_cards: list[str], rng: Random) -> GameState:
    mulligans = 0

    while True:
        deck = list(deck_cards)
        rng.shuffle(deck)
        hand = [deck.pop(0) for _ in range(7)]
        if has_basic_pokemon(hand):
            break
        mulligans += 1

    state = GameState(deck=deck, hand=hand, mulligans=mulligans)
    choose_starting_board(state)
    state.prizes = [state.deck.pop(0) for _ in range(6)]
    return state


def setup_opening_hand(deck_cards: list[str], rng: Random) -> GameState:
    mulligans = 0

    while True:
        deck = list(deck_cards)
        rng.shuffle(deck)
        hand = [deck.pop(0) for _ in range(7)]
        if has_basic_pokemon(hand):
            return GameState(deck=deck, hand=hand, mulligans=mulligans)
        mulligans += 1


def setup_choices(opening: GameState) -> list[GameState]:
    basic_indexes = [index for index, name in enumerate(opening.hand) if CARD_DEFS[name].is_basic_pokemon]
    choices: list[GameState] = []
    preferred_indexes: list[int] = []
    for preferred in ("Lugia V", "Squawkabilly ex"):
        preferred_indexes.extend(index for index in basic_indexes if opening.hand[index] == preferred)
    if basic_indexes:
        preferred_indexes.append(basic_indexes[0])

    for active_index in sorted(set(preferred_indexes)):
        active_name = opening.hand[active_index]
        remaining = list(opening.hand)
        remaining.pop(active_index)
        state = opening.copy()
        state.hand = list(remaining)
        state.active = [active_name]
        state.active_turns = [0]
        state.route.append(f"opening hand: {format_cards(opening.hand)}")
        state.route.append(f"setup: choose {active_name} as Active")
        state.bench = []
        state.bench_turns = []
        state.prizes = [state.deck.pop(0) for _ in range(6)]
        state.route.append(f"setup: prize cards: {format_cards(state.prizes)}")
        choices.append(state)

    return choices


def choose_starting_board(state: GameState) -> None:
    active_priority = [
        "Lugia V",
        "Minccino",
        "Squawkabilly ex",
        "Lumineon V",
        "Iron Bundle",
        "Iron Hands ex",
        "Bloodmoon Ursaluna ex",
        "Fezandipiti ex",
    ]
    basic_in_hand = [name for name in state.hand if CARD_DEFS[name].is_basic_pokemon]

    for preferred in active_priority:
        if preferred in basic_in_hand:
            active = preferred
            break
    else:
        active = basic_in_hand[0]

    state.hand.remove(active)
    state.active.append(active)
    state.active_turns.append(0)

    bench_priority = [
        "Lugia V",
        "Minccino",
        "Squawkabilly ex",
        "Lumineon V",
        "Iron Bundle",
        "Iron Hands ex",
        "Bloodmoon Ursaluna ex",
        "Fezandipiti ex",
    ]

    for preferred in bench_priority:
        while preferred in state.hand and len(state.bench) < 5 and CARD_DEFS[preferred].is_basic_pokemon:
            state.hand.remove(preferred)
            state.bench.append(preferred)
            state.bench_turns.append(0)


def format_cards(cards: list[str]) -> str:
    return ", ".join(cards) if cards else "nothing"
