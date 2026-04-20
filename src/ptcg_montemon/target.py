from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .state import GameState


@dataclass(frozen=True)
class ZoneRequirement:
    zone: str
    cards: dict[str, int]


@dataclass(frozen=True)
class Target:
    name: str
    requirements: tuple[ZoneRequirement, ...]
    any_of: tuple[tuple[ZoneRequirement, ...], ...] = ()

    def matches(self, state: GameState) -> bool:
        if not requirements_match(self.requirements, state):
            return False
        if self.any_of and not any(requirements_match(group, state) for group in self.any_of):
            return False
        return True


def requirements_match(requirements: tuple[ZoneRequirement, ...], state: GameState) -> bool:
    for requirement in requirements:
        counts = Counter(state.zone(requirement.zone))
        for card_name, minimum in requirement.cards.items():
            if counts[card_name] < minimum:
                return False
    return True


def parse_zone_requirements(data: dict[str, Any]) -> tuple[ZoneRequirement, ...]:
    requirements = []
    for zone, cards in data.items():
        requirements.append(ZoneRequirement(zone=zone, cards={str(k): int(v) for k, v in cards.items()}))
    return tuple(requirements)


def load_target(path: str | Path) -> Target:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return parse_target(data)


def parse_target(data: dict[str, Any]) -> Target:
    any_of = tuple(parse_zone_requirements(group) for group in data.get("any_of", []))
    return Target(
        name=str(data.get("name", "unnamed target")),
        requirements=parse_zone_requirements(data.get("zones", {})),
        any_of=any_of,
    )
