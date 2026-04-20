from __future__ import annotations

from dataclasses import dataclass
from random import Random

from .cards import CARD_DEFS, CardKind, PokemonStage, TrainerKind
from .state import GameState, format_cards
from .strategy import GreedyStrategy, default_strategy
from .target import Target


SUPPORTERS = {
    name
    for name, card in CARD_DEFS.items()
    if card.kind == CardKind.TRAINER and card.trainer_kind == TrainerKind.SUPPORTER
}

USEFUL_POKEMON = {
    "Archeops",
    "Lugia V",
    "Lugia VSTAR",
    "Lumineon V",
    "Squawkabilly ex",
}

@dataclass(frozen=True)
class GreedyOptions:
    going_first: bool
    first_turn_draw: bool = True
    strategy: GreedyStrategy = default_strategy()
    opponent_disruption: str = "none"
    opponent_turn1_disruption: str = "none"
    opponent_turn2_disruption: str = "none"


def greedy_reaches_target_by_second_turn(
    opening: GameState, target: Target, options: GreedyOptions, rng: Random
) -> tuple[bool, list[str]]:
    state = greedy_setup(opening, options.strategy)
    for own_turn in (1, 2):
        if own_turn == 1 and not options.going_first:
            apply_opponent_disruption(state, normalize_disruption(options.opponent_turn1_disruption), rng, "opponent turn 1")
        start_turn(state, own_turn, options)
        run_greedy_turn(state, options, rng)
        if own_turn == 1:
            if options.going_first:
                disruption = normalize_disruption(options.opponent_turn1_disruption, options.opponent_disruption)
                label = "opponent turn 1"
            else:
                disruption = normalize_disruption(options.opponent_turn2_disruption, options.opponent_disruption)
                label = "opponent turn 2"
            apply_opponent_disruption(state, disruption, rng, label)
    return target.matches(state), state.route


def greedy_setup(opening: GameState, strategy: GreedyStrategy) -> GameState:
    state = opening.copy()
    state.route.append(f"opening hand: {format_cards(opening.hand)}")

    active = choose_active(state.hand, strategy)
    state.hand.remove(active)
    state.active = [active]
    state.active_turns = [0]
    state.route.append(f"setup: choose {active} as Active")
    state.prizes = [state.deck.pop(0) for _ in range(6)]
    return state


def choose_active(hand: list[str], strategy: GreedyStrategy) -> str:
    for preferred in strategy.active_priority:
        if preferred in hand and CARD_DEFS[preferred].is_basic_pokemon:
            return preferred
    for card_name in hand:
        if CARD_DEFS[card_name].is_basic_pokemon:
            return card_name
    raise ValueError("Opening hand has no Basic Pokemon.")


def start_turn(state: GameState, own_turn: int, options: GreedyOptions) -> None:
    state.turn = own_turn
    state.supporter_played = False
    if own_turn == 2 or options.first_turn_draw:
        drawn = state.draw(1)
        state.route.append(f"turn {own_turn}: draw {format_cards(drawn)}")
    else:
        state.route.append(f"turn {own_turn}: skip first-turn draw")


def run_greedy_turn(state: GameState, options: GreedyOptions, rng: Random) -> None:
    action_map = {
        "evolve_lugia": lambda: evolve_lugia(state),
        "bench_basic": lambda: bench_basic(state, options.strategy),
        "play_mesagoza": lambda: play_mesagoza(state, options.strategy),
        "use_mesagoza": lambda: use_mesagoza(state, options.strategy, rng),
        "ultra_ball": lambda: use_ultra_ball(state, options.strategy),
        "great_ball": lambda: use_great_ball(state, options.strategy),
        "capturing_aroma": lambda: use_capturing_aroma(state, options.strategy, rng),
        "supporter": lambda: use_supporter(state, options),
        "squawkabilly": lambda: use_squawkabilly(state, options.strategy),
    }
    for _ in range(options.strategy.max_actions_per_turn):
        for action_name in options.strategy.action_priority:
            action = action_map.get(action_name)
            if action is not None and action():
                break
        else:
            break
        if action is None:
            break


def normalize_disruption(disruption: str, fallback: str = "none") -> str:
    return disruption if disruption != "none" else fallback


def apply_opponent_disruption(state: GameState, disruption: str, rng: Random, label: str) -> None:
    if disruption == "none":
        return
    if disruption == "iono":
        apply_opponent_iono(state, rng, label)
        return
    if disruption == "judge":
        apply_opponent_judge(state, rng, label)
        return
    raise ValueError(f"Unknown opponent disruption: {disruption}")


def apply_opponent_iono(state: GameState, rng: Random, label: str) -> None:
    disrupted = list(state.hand)
    rng.shuffle(disrupted)
    state.hand = []
    state.deck.extend(disrupted)
    drawn = state.draw(len(state.prizes))
    state.route.append(
        f"{label} disruption: Iono puts {format_cards(disrupted)} on bottom, draw {format_cards(drawn)}"
    )


def apply_opponent_judge(state: GameState, rng: Random, label: str) -> None:
    disrupted = list(state.hand)
    state.hand = []
    state.deck.extend(disrupted)
    rng.shuffle(state.deck)
    drawn = state.draw(4)
    state.route.append(
        f"{label} disruption: Judge shuffles {format_cards(disrupted)}, draw {format_cards(drawn)}"
    )


def evolve_lugia(state: GameState) -> bool:
    if state.turn != 2 or "Lugia VSTAR" not in state.hand:
        return False
    if state.active == ["Lugia V"] and state.active_turns and state.active_turns[0] < state.turn:
        state.hand.remove("Lugia VSTAR")
        state.active = ["Lugia VSTAR"]
        state.route.append("turn 2: evolve Active Lugia V into Lugia VSTAR")
        return True
    for index, card_name in enumerate(state.bench):
        if card_name == "Lugia V" and index < len(state.bench_turns) and state.bench_turns[index] < state.turn:
            state.hand.remove("Lugia VSTAR")
            state.bench[index] = "Lugia VSTAR"
            state.route.append("turn 2: evolve Benched Lugia V into Lugia VSTAR")
            return True
    return False


def bench_basic(state: GameState, strategy: GreedyStrategy) -> bool:
    if len(state.bench) >= 5:
        return False
    for card_name in strategy.bench_priority:
        if card_name in state.hand and CARD_DEFS[card_name].is_basic_pokemon:
            move_one(state.hand, state.bench, card_name)
            state.bench_turns.append(state.turn)
            state.route.append(f"turn {state.turn}: bench {card_name}")
            if card_name == "Lumineon V" and not state.luminous_sign_used:
                use_lumineon(state, strategy)
            return True
    return False


def use_lumineon(state: GameState, strategy: GreedyStrategy) -> None:
    supporter = choose_supporter_from_deck(state, strategy)
    state.luminous_sign_used = True
    if supporter is None:
        state.route.append(f"turn {state.turn}: Lumineon V finds no Supporter")
        return
    move_one(state.deck, state.hand, supporter)
    state.route.append(f"turn {state.turn}: Lumineon V searches {supporter}")


def choose_supporter_from_deck(state: GameState, strategy: GreedyStrategy) -> str | None:
    for supporter in supporter_priority(state, strategy):
        if supporter in state.deck:
            return supporter
    return None


def play_mesagoza(state: GameState, strategy: GreedyStrategy) -> bool:
    if not strategy.use_mesagoza or "Mesagoza" not in state.hand:
        return False
    move_one(state.hand, state.stadium, "Mesagoza")
    if len(state.stadium) > 1:
        state.discard.extend(state.stadium[:-1])
        state.stadium = state.stadium[-1:]
    state.route.append(f"turn {state.turn}: play Mesagoza")
    return True


def use_mesagoza(state: GameState, strategy: GreedyStrategy, rng: Random) -> bool:
    if not strategy.use_mesagoza or "Mesagoza" not in state.stadium or state.turn in state.mesagoza_used_turns:
        return False
    state.mesagoza_used_turns.append(state.turn)
    if rng.random() >= 0.5:
        state.route.append(f"turn {state.turn}: Mesagoza flips tails")
        return True
    pokemon = choose_pokemon_from_deck(state, strategy)
    if pokemon is None:
        state.route.append(f"turn {state.turn}: Mesagoza flips heads, finds no Pokemon")
        return True
    move_one(state.deck, state.hand, pokemon)
    state.route.append(f"turn {state.turn}: Mesagoza flips heads, searches {pokemon}")
    return True


def use_ultra_ball(state: GameState, strategy: GreedyStrategy) -> bool:
    if "Ultra Ball" not in state.hand:
        return False
    remaining = list(state.hand)
    remaining.remove("Ultra Ball")
    if len(remaining) < 2:
        return False
    costs = choose_discard_costs(state, strategy, remaining)
    pokemon = choose_pokemon_from_deck(state, strategy)
    if pokemon is None:
        return False
    move_one(state.hand, state.discard, "Ultra Ball")
    for card_name in costs:
        move_one(state.hand, state.discard, card_name)
    move_one(state.deck, state.hand, pokemon)
    state.route.append(
        f"turn {state.turn}: Ultra Ball discards {costs[0]} + {costs[1]}, searches {pokemon}"
    )
    return True


def use_great_ball(state: GameState, strategy: GreedyStrategy) -> bool:
    if "Great Ball" not in state.hand:
        return False
    top_cards = state.deck[:7]
    choices = [card_name for card_name in top_cards if CARD_DEFS[card_name].kind == CardKind.POKEMON]
    move_one(state.hand, state.discard, "Great Ball")
    if not choices:
        state.route.append(f"turn {state.turn}: Great Ball whiffs")
        return True
    pokemon = choose_best_pokemon(state, strategy, choices)
    state.deck.remove(pokemon)
    state.hand.append(pokemon)
    state.route.append(f"turn {state.turn}: Great Ball takes {pokemon} from top 7")
    return True


def use_capturing_aroma(state: GameState, strategy: GreedyStrategy, rng: Random) -> bool:
    if "Capturing Aroma" not in state.hand:
        return False
    is_heads = rng.random() < 0.5
    result = "heads" if is_heads else "tails"
    predicate = is_evolution_pokemon if is_heads else is_basic_pokemon
    choices = [card_name for card_name in state.deck if predicate(card_name)]
    move_one(state.hand, state.discard, "Capturing Aroma")
    if not choices:
        state.route.append(f"turn {state.turn}: Capturing Aroma flips {result}, finds no matching Pokemon")
        return True
    pokemon = choose_best_pokemon(state, strategy, choices)
    move_one(state.deck, state.hand, pokemon)
    state.route.append(f"turn {state.turn}: Capturing Aroma flips {result}, searches {pokemon}")
    return True


def use_supporter(state: GameState, options: GreedyOptions) -> bool:
    if state.supporter_played or not supporter_allowed(state, options):
        return False
    for supporter in supporter_priority(state, options.strategy):
        if supporter not in state.hand:
            continue
        if supporter == "Professor's Research":
            discard_hand_and_draw(state, supporter, 7)
            return True
        if supporter == "Carmine":
            discard_hand_and_draw(state, supporter, 5)
            return True
        if supporter == "Iono":
            use_iono(state)
            return True
        if supporter == "Jacq":
            use_jacq(state)
            return True
    return False


def supporter_allowed(state: GameState, options: GreedyOptions) -> bool:
    if state.turn != 1:
        return True
    if not options.going_first:
        return True
    return "Carmine" in state.hand


def supporter_priority(state: GameState, strategy: GreedyStrategy) -> list[str]:
    if (
        strategy.prefer_research_when_holding_archeops
        and count_in_zone(state.discard, "Archeops") < 2
        and has_in_hand(state, "Archeops")
    ):
        return ["Professor's Research", "Carmine", "Iono", "Jacq"]
    if (
        strategy.prefer_jacq_when_missing_lugia_vstar
        and "Lugia VSTAR" not in state.hand
        and not has_in_play(state, "Lugia VSTAR")
    ):
        return ["Jacq", "Professor's Research", "Carmine", "Iono"]
    return list(strategy.supporter_priority)


def discard_hand_and_draw(state: GameState, supporter: str, draw_count: int) -> None:
    state.hand.remove(supporter)
    state.discard.append(supporter)
    discarded = list(state.hand)
    state.discard.extend(discarded)
    state.hand = []
    drawn = state.draw(draw_count)
    state.supporter_played = True
    state.route.append(
        f"turn {state.turn}: {supporter} discards {format_cards(discarded)} and draws {format_cards(drawn)}"
    )


def use_iono(state: GameState) -> None:
    state.hand.remove("Iono")
    state.discard.append("Iono")
    bottom = list(state.hand)
    state.hand = []
    state.deck.extend(bottom)
    drawn = state.draw(len(state.prizes))
    state.supporter_played = True
    state.route.append(f"turn {state.turn}: Iono draws {format_cards(drawn)}")


def use_jacq(state: GameState) -> None:
    move_one(state.hand, state.discard, "Jacq")
    choices = [card_name for card_name in state.deck if is_evolution_pokemon(card_name)]
    searched: list[str] = []
    for pokemon in ["Lugia VSTAR", "Archeops", "Cinccino"]:
        if pokemon in choices and len(searched) < 2:
            move_one(state.deck, state.hand, pokemon)
            searched.append(pokemon)
    state.supporter_played = True
    state.route.append(f"turn {state.turn}: Jacq searches {format_cards(searched)}")


def use_squawkabilly(state: GameState, strategy: GreedyStrategy) -> bool:
    if (
        not strategy.use_squawkabilly
        or state.turn != 1
        or state.squawk_used
        or "Squawkabilly ex" not in state.active + state.bench
    ):
        return False
    if not state.hand:
        return False
    discarded = list(state.hand)
    state.discard.extend(discarded)
    state.hand = []
    drawn = state.draw(6)
    state.squawk_used = True
    state.route.append(
        f"turn 1: use Squawkabilly ex, discard {format_cards(discarded)} and draw {format_cards(drawn)}"
    )
    return True


def choose_discard_costs(state: GameState, strategy: GreedyStrategy, cards: list[str]) -> list[str]:
    scored = sorted(cards, key=lambda card_name: discard_score(state, strategy, card_name), reverse=True)
    return scored[:2]


def discard_score(state: GameState, strategy: GreedyStrategy, card_name: str) -> tuple[int, str]:
    labels = discard_labels(state, card_name)
    for index, label in enumerate(strategy.discard_priority):
        if label in labels:
            return (len(strategy.discard_priority) - index, card_name)
    return (0, card_name)


def discard_labels(state: GameState, card_name: str) -> set[str]:
    card = CARD_DEFS[card_name]
    labels = {card_name}
    labels.add(card.kind.value.title())
    if card.kind == CardKind.ENERGY:
        labels.add("Energy")
    if card.kind == CardKind.TRAINER:
        labels.add("Trainer")
    if card.kind == CardKind.POKEMON:
        labels.add("Pokemon")
    if card_name == "Lugia VSTAR" and has_in_play(state, "Lugia VSTAR"):
        labels.add("duplicate Lugia VSTAR")
    return labels


def choose_pokemon_from_deck(state: GameState, strategy: GreedyStrategy) -> str | None:
    choices = [card_name for card_name in state.deck if CARD_DEFS[card_name].kind == CardKind.POKEMON]
    if not choices:
        return None
    return choose_best_pokemon(state, strategy, choices)


def choose_best_pokemon(state: GameState, strategy: GreedyStrategy, choices: list[str]) -> str:
    priorities = pokemon_priority(state, strategy)
    for pokemon in priorities:
        if pokemon in choices:
            return pokemon
    return choices[0]


def pokemon_priority(state: GameState, strategy: GreedyStrategy) -> list[str]:
    priorities: list[str] = []
    if not has_in_play(state, "Lugia V") and "Lugia VSTAR" not in state.active + state.bench:
        priorities.append("Lugia V")
    if "Lugia VSTAR" not in state.hand and not has_in_play(state, "Lugia VSTAR"):
        priorities.append("Lugia VSTAR")
    if count_in_zone(state.discard, "Archeops") < 2:
        priorities.append("Archeops")
    if not state.luminous_sign_used:
        priorities.append("Lumineon V")
    if state.turn == 1 and not state.squawk_used and "Squawkabilly ex" not in state.active + state.bench:
        priorities.append("Squawkabilly ex")
    priorities.extend(strategy.pokemon_search_priority)
    return priorities


def is_basic_pokemon(name: str) -> bool:
    return CARD_DEFS[name].is_basic_pokemon


def is_evolution_pokemon(name: str) -> bool:
    card = CARD_DEFS[name]
    return card.kind == CardKind.POKEMON and card.pokemon_stage in {
        PokemonStage.STAGE_1,
        PokemonStage.STAGE_2,
        PokemonStage.VSTAR,
    }


def has_in_hand(state: GameState, card_name: str) -> bool:
    return card_name in state.hand


def has_in_play(state: GameState, card_name: str) -> bool:
    return card_name in state.active or card_name in state.bench


def count_in_zone(zone: list[str], card_name: str) -> int:
    return sum(1 for name in zone if name == card_name)


def move_one(source: list[str], destination: list[str], card_name: str) -> None:
    source.remove(card_name)
    destination.append(card_name)
