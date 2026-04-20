from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


DEFAULT_ACTION_PRIORITY = [
    "evolve_lugia",
    "bench_basic",
    "play_mesagoza",
    "use_mesagoza",
    "ultra_ball",
    "great_ball",
    "capturing_aroma",
    "supporter",
    "squawkabilly",
]

DEFAULT_BASIC_PRIORITY = [
    "Lugia V",
    "Squawkabilly ex",
    "Lumineon V",
    "Minccino",
    "Iron Bundle",
    "Iron Hands ex",
    "Bloodmoon Ursaluna ex",
    "Fezandipiti ex",
]

DEFAULT_POKEMON_SEARCH_PRIORITY = [
    "Lugia V",
    "Lugia VSTAR",
    "Archeops",
    "Lumineon V",
    "Squawkabilly ex",
]

DEFAULT_SUPPORTER_PRIORITY = [
    "Professor's Research",
    "Carmine",
    "Jacq",
    "Iono",
]

DEFAULT_DISCARD_PRIORITY = [
    "Archeops",
    "duplicate Lugia VSTAR",
    "Energy",
    "Boss's Orders",
    "Roseanne's Backup",
    "Thorton",
    "Trainer",
    "Pokemon",
    "Lugia VSTAR",
    "Lugia V",
]


@dataclass(frozen=True)
class GreedyStrategy:
    action_priority: tuple[str, ...] = tuple(DEFAULT_ACTION_PRIORITY)
    active_priority: tuple[str, ...] = tuple(DEFAULT_BASIC_PRIORITY)
    bench_priority: tuple[str, ...] = tuple(DEFAULT_BASIC_PRIORITY)
    pokemon_search_priority: tuple[str, ...] = tuple(DEFAULT_POKEMON_SEARCH_PRIORITY)
    supporter_priority: tuple[str, ...] = tuple(DEFAULT_SUPPORTER_PRIORITY)
    discard_priority: tuple[str, ...] = tuple(DEFAULT_DISCARD_PRIORITY)
    max_actions_per_turn: int = 80
    prefer_research_when_holding_archeops: bool = True
    prefer_jacq_when_missing_lugia_vstar: bool = True
    use_mesagoza: bool = True
    use_squawkabilly: bool = True


def default_strategy() -> GreedyStrategy:
    return GreedyStrategy()


def load_strategy(path: str | Path | None) -> GreedyStrategy:
    if path is None:
        return default_strategy()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return parse_strategy(data)


def parse_strategy(data: dict[str, Any]) -> GreedyStrategy:
    defaults = default_strategy()
    return GreedyStrategy(
        action_priority=tuple(data.get("action_priority", defaults.action_priority)),
        active_priority=tuple(data.get("active_priority", defaults.active_priority)),
        bench_priority=tuple(data.get("bench_priority", defaults.bench_priority)),
        pokemon_search_priority=tuple(data.get("pokemon_search_priority", defaults.pokemon_search_priority)),
        supporter_priority=tuple(data.get("supporter_priority", defaults.supporter_priority)),
        discard_priority=tuple(data.get("discard_priority", defaults.discard_priority)),
        max_actions_per_turn=int(data.get("max_actions_per_turn", defaults.max_actions_per_turn)),
        prefer_research_when_holding_archeops=bool(
            data.get("prefer_research_when_holding_archeops", defaults.prefer_research_when_holding_archeops)
        ),
        prefer_jacq_when_missing_lugia_vstar=bool(
            data.get("prefer_jacq_when_missing_lugia_vstar", defaults.prefer_jacq_when_missing_lugia_vstar)
        ),
        use_mesagoza=bool(data.get("use_mesagoza", defaults.use_mesagoza)),
        use_squawkabilly=bool(data.get("use_squawkabilly", defaults.use_squawkabilly)),
    )
