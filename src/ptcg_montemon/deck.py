from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .cards import get_card_def


DECK_LINE_RE = re.compile(r"^(?P<count>\d+)\s+(?P<name>.+?)\s+(?P<set>[A-Z0-9]+)\s+(?P<number>[A-Z0-9]+)$")


@dataclass(frozen=True)
class DeckEntry:
    count: int
    name: str
    set_code: str
    number: str


def parse_deck_text(text: str) -> list[DeckEntry]:
    entries: list[DeckEntry] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.endswith(":") or ":" in line and not line[0].isdigit():
            continue

        match = DECK_LINE_RE.match(line)
        if not match:
            raise ValueError(f"Cannot parse deck line: {raw_line!r}")

        entries.append(
            DeckEntry(
                count=int(match.group("count")),
                name=match.group("name"),
                set_code=match.group("set"),
                number=match.group("number"),
            )
        )

    total = sum(entry.count for entry in entries)
    if total != 60:
        raise ValueError(f"Expected a 60-card deck, got {total} cards.")

    for entry in entries:
        card_def = get_card_def(entry.name)
        if card_def.set_code != entry.set_code or card_def.number != entry.number:
            raise ValueError(
                f"Deck line {entry.name} {entry.set_code} {entry.number} does not match card database."
            )

    return entries


def load_deck(path: str | Path) -> list[DeckEntry]:
    return parse_deck_text(Path(path).read_text(encoding="utf-8"))


def expand_deck(entries: list[DeckEntry]) -> list[str]:
    cards: list[str] = []
    for entry in entries:
        cards.extend([entry.name] * entry.count)
    return cards
