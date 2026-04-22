from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .cards import get_card_def, register_unknown_card


DECK_LINE_RE = re.compile(r"^(?P<count>\d+)\s+(?P<name>.+?)\s+(?P<set>[A-Z0-9]+)\s+(?P<number>[A-Z0-9]+)$")


@dataclass(frozen=True)
class DeckEntry:
    count: int
    name: str
    set_code: str
    number: str
    section: str | None = None


def parse_deck_text(text: str) -> list[DeckEntry]:
    entries: list[DeckEntry] = []
    current_section: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith(":") or ":" in line and not line[0].isdigit():
            current_section = line.rstrip(":").strip()
            continue

        match = DECK_LINE_RE.match(line)
        if not match:
            raise ValueError(f"Cannot parse deck line: {raw_line!r}")

        name = match.group("name")
        set_code = match.group("set")
        number = match.group("number")
        register_unknown_card(name, set_code, number, current_section)
        entries.append(
            DeckEntry(
                count=int(match.group("count")),
                name=name,
                set_code=set_code,
                number=number,
                section=current_section,
            )
        )

    total = sum(entry.count for entry in entries)
    if total != 60:
        raise ValueError(f"Expected a 60-card deck, got {total} cards.")

    return entries


def load_deck(path: str | Path) -> list[DeckEntry]:
    return parse_deck_text(Path(path).read_text(encoding="utf-8"))


def expand_deck(entries: list[DeckEntry]) -> list[str]:
    cards: list[str] = []
    for entry in entries:
        cards.extend([entry.name] * entry.count)
    return cards


def unknown_deck_entries(entries: list[DeckEntry]) -> list[DeckEntry]:
    return [entry for entry in entries if get_card_def(entry.name).inferred]
