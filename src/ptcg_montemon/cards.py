from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class CardKind(StrEnum):
    POKEMON = "pokemon"
    TRAINER = "trainer"
    ENERGY = "energy"


class PokemonStage(StrEnum):
    BASIC = "basic"
    STAGE_1 = "stage_1"
    STAGE_2 = "stage_2"
    VSTAR = "vstar"


class TrainerKind(StrEnum):
    ITEM = "item"
    SUPPORTER = "supporter"
    STADIUM = "stadium"


@dataclass(frozen=True)
class CardDef:
    name: str
    kind: CardKind
    set_code: str | None = None
    number: str | None = None
    pokemon_stage: PokemonStage | None = None
    evolves_from: str | None = None
    trainer_kind: TrainerKind | None = None
    notes: tuple[str, ...] = ()
    implemented_effects: tuple[str, ...] = ()
    missing_effects: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_basic_pokemon(self) -> bool:
        return self.kind == CardKind.POKEMON and self.pokemon_stage == PokemonStage.BASIC


CARD_DEFS: dict[str, CardDef] = {
    "Archeops": CardDef(
        name="Archeops",
        kind=CardKind.POKEMON,
        set_code="SIT",
        number="147",
        pokemon_stage=PokemonStage.STAGE_2,
        evolves_from="Archen",
        notes=("Ability: Primal Turbo attaches up to 2 Special Energy from deck to 1 Pokemon.",),
        missing_effects=("Primal Turbo action and energy attachment targeting.",),
    ),
    "Lugia V": CardDef(
        name="Lugia V",
        kind=CardKind.POKEMON,
        set_code="SIT",
        number="138",
        pokemon_stage=PokemonStage.BASIC,
    ),
    "Lugia VSTAR": CardDef(
        name="Lugia VSTAR",
        kind=CardKind.POKEMON,
        set_code="SIT",
        number="139",
        pokemon_stage=PokemonStage.VSTAR,
        evolves_from="Lugia V",
        notes=("VSTAR Power: Summoning Star benches up to 2 Colorless Pokemon from discard.",),
        missing_effects=("Evolution action and Summoning Star once-per-game action.",),
    ),
    "Minccino": CardDef(
        name="Minccino",
        kind=CardKind.POKEMON,
        set_code="TEF",
        number="136",
        pokemon_stage=PokemonStage.BASIC,
    ),
    "Cinccino": CardDef(
        name="Cinccino",
        kind=CardKind.POKEMON,
        set_code="TEF",
        number="137",
        pokemon_stage=PokemonStage.STAGE_1,
        evolves_from="Minccino",
        missing_effects=("Attack/effect text if it matters for target state.",),
    ),
    "Lumineon V": CardDef(
        name="Lumineon V",
        kind=CardKind.POKEMON,
        set_code="BRS",
        number="40",
        pokemon_stage=PokemonStage.BASIC,
        notes=("Ability: Luminous Sign searches a Supporter when played from hand to bench.",),
        missing_effects=("Luminous Sign search action.",),
    ),
    "Squawkabilly ex": CardDef(
        name="Squawkabilly ex",
        kind=CardKind.POKEMON,
        set_code="PAL",
        number="169",
        pokemon_stage=PokemonStage.BASIC,
        notes=("Ability: Squawk and Seize discards hand and draws 6 on first turn.",),
        missing_effects=("Squawk and Seize once-on-first-turn action.",),
    ),
    "Iron Bundle": CardDef(
        name="Iron Bundle",
        kind=CardKind.POKEMON,
        set_code="PAR",
        number="56",
        pokemon_stage=PokemonStage.BASIC,
        missing_effects=("Hyper Blower ability if opponent active manipulation matters.",),
    ),
    "Bloodmoon Ursaluna ex": CardDef(
        name="Bloodmoon Ursaluna ex",
        kind=CardKind.POKEMON,
        set_code="TWM",
        number="141",
        pokemon_stage=PokemonStage.BASIC,
        missing_effects=("Attack cost reduction usually depends on opponent prizes.",),
    ),
    "Iron Hands ex": CardDef(
        name="Iron Hands ex",
        kind=CardKind.POKEMON,
        set_code="PAR",
        number="70",
        pokemon_stage=PokemonStage.BASIC,
    ),
    "Fezandipiti ex": CardDef(
        name="Fezandipiti ex",
        kind=CardKind.POKEMON,
        set_code="SFA",
        number="38",
        pokemon_stage=PokemonStage.BASIC,
        missing_effects=("Flip the Script draw ability if knockout state is modeled.",),
    ),
    "Boss's Orders": CardDef(
        name="Boss's Orders",
        kind=CardKind.TRAINER,
        set_code="PAL",
        number="172",
        trainer_kind=TrainerKind.SUPPORTER,
        missing_effects=("Opponent bench switching is out of scope for our-side setup targets.",),
    ),
    "Professor's Research": CardDef(
        name="Professor's Research",
        kind=CardKind.TRAINER,
        set_code="SVI",
        number="189",
        trainer_kind=TrainerKind.SUPPORTER,
        notes=("Discard hand and draw 7.",),
        missing_effects=("Supporter action: discard hand, draw 7.",),
    ),
    "Iono": CardDef(
        name="Iono",
        kind=CardKind.TRAINER,
        set_code="PAL",
        number="185",
        trainer_kind=TrainerKind.SUPPORTER,
        notes=("Each player shuffles hand to bottom, then draws for remaining prizes.",),
        missing_effects=("Our-side hand reset using own remaining prizes.",),
    ),
    "Roseanne's Backup": CardDef(
        name="Roseanne's Backup",
        kind=CardKind.TRAINER,
        set_code="BRS",
        number="148",
        trainer_kind=TrainerKind.SUPPORTER,
        missing_effects=("Recovery action from discard.",),
    ),
    "Jacq": CardDef(
        name="Jacq",
        kind=CardKind.TRAINER,
        set_code="SVI",
        number="175",
        trainer_kind=TrainerKind.SUPPORTER,
        notes=("Search deck for up to 2 Evolution Pokemon.",),
        missing_effects=("Search action for evolution Pokemon.",),
    ),
    "Thorton": CardDef(
        name="Thorton",
        kind=CardKind.TRAINER,
        set_code="LOR",
        number="167",
        trainer_kind=TrainerKind.SUPPORTER,
        missing_effects=("Basic Pokemon swap from discard with in-play Pokemon.",),
    ),
    "Carmine": CardDef(
        name="Carmine",
        kind=CardKind.TRAINER,
        set_code="TWM",
        number="145",
        trainer_kind=TrainerKind.SUPPORTER,
        missing_effects=("Turn-dependent discard hand and draw action.",),
    ),
    "Ultra Ball": CardDef(
        name="Ultra Ball",
        kind=CardKind.TRAINER,
        set_code="SVI",
        number="196",
        trainer_kind=TrainerKind.ITEM,
        notes=("Discard 2 cards from hand, search deck for a Pokemon.",),
        missing_effects=("Item action: choose discard costs and search target.",),
    ),
    "Capturing Aroma": CardDef(
        name="Capturing Aroma",
        kind=CardKind.TRAINER,
        set_code="SIT",
        number="153",
        trainer_kind=TrainerKind.ITEM,
        notes=("Flip heads for Evolution Pokemon search, tails for Basic Pokemon search.",),
        missing_effects=("Coin flip and search action.",),
    ),
    "Great Ball": CardDef(
        name="Great Ball",
        kind=CardKind.TRAINER,
        set_code="PAL",
        number="183",
        trainer_kind=TrainerKind.ITEM,
        notes=("Look at top 7 cards, reveal a Pokemon, put it into hand.",),
        missing_effects=("Top-7 search action.",),
    ),
    "Mesagoza": CardDef(
        name="Mesagoza",
        kind=CardKind.TRAINER,
        set_code="SVI",
        number="178",
        trainer_kind=TrainerKind.STADIUM,
        notes=("Once during each player's turn, flip heads to search a Pokemon.",),
        missing_effects=("Stadium play and once-per-turn coin-flip search action.",),
    ),
    "Jet Energy": CardDef(name="Jet Energy", kind=CardKind.ENERGY, set_code="PAL", number="190"),
    "Mist Energy": CardDef(name="Mist Energy", kind=CardKind.ENERGY, set_code="TEF", number="161"),
    "Gift Energy": CardDef(name="Gift Energy", kind=CardKind.ENERGY, set_code="LOR", number="171"),
    "Double Turbo Energy": CardDef(name="Double Turbo Energy", kind=CardKind.ENERGY, set_code="BRS", number="151"),
    "V Guard Energy": CardDef(name="V Guard Energy", kind=CardKind.ENERGY, set_code="SIT", number="169"),
    "Legacy Energy": CardDef(name="Legacy Energy", kind=CardKind.ENERGY, set_code="TWM", number="167"),
}


def get_card_def(name: str) -> CardDef:
    try:
        return CARD_DEFS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown card definition: {name}") from exc
