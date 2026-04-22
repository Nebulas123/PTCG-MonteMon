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
    inferred: bool = False

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
        implemented_effects=("Evolution action.", "Summoning Star for Archeops from discard to bench."),
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
    "Crobat V": CardDef(
        name="Crobat V",
        kind=CardKind.POKEMON,
        set_code="DAA",
        number="104",
        pokemon_stage=PokemonStage.BASIC,
        notes=("Ability: Dark Asset draws until 6 cards when played from hand to bench.",),
        implemented_effects=("Dark Asset draw-until-6 when benched.",),
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
    "Radiant Charizard": CardDef(
        name="Radiant Charizard",
        kind=CardKind.POKEMON,
        set_code="PGO",
        number="11",
        pokemon_stage=PokemonStage.BASIC,
    ),
    "Yveltal": CardDef(
        name="Yveltal",
        kind=CardKind.POKEMON,
        set_code="SHF",
        number="46",
        pokemon_stage=PokemonStage.BASIC,
    ),
    "Raikou": CardDef(
        name="Raikou",
        kind=CardKind.POKEMON,
        set_code="VIV",
        number="50",
        pokemon_stage=PokemonStage.BASIC,
    ),
    "Pumpkaboo": CardDef(
        name="Pumpkaboo",
        kind=CardKind.POKEMON,
        set_code="EVS",
        number="76",
        pokemon_stage=PokemonStage.BASIC,
        notes=("Ability: Pumpkin Pit discards a Stadium when played from hand to bench.",),
        missing_effects=("Pumpkin Pit stadium discard is not relevant to current target unless stadium wars matter.",),
    ),
    "Dunsparce": CardDef(
        name="Dunsparce",
        kind=CardKind.POKEMON,
        set_code="FST",
        number="207",
        pokemon_stage=PokemonStage.BASIC,
    ),
    "Manaphy": CardDef(
        name="Manaphy",
        kind=CardKind.POKEMON,
        set_code="BRS",
        number="41",
        pokemon_stage=PokemonStage.BASIC,
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
        set_code="BRS",
        number="132",
        trainer_kind=TrainerKind.SUPPORTER,
        missing_effects=("Opponent bench switching is out of scope for our-side setup targets.",),
    ),
    "Professor's Research": CardDef(
        name="Professor's Research",
        kind=CardKind.TRAINER,
        set_code="BRS",
        number="147",
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
    "Marnie": CardDef(
        name="Marnie",
        kind=CardKind.TRAINER,
        set_code="SSH",
        number="169",
        trainer_kind=TrainerKind.SUPPORTER,
        notes=("Each player puts hand on bottom of deck; our side draws 5.",),
        implemented_effects=("Our-side hand to bottom, draw 5.",),
    ),
    "Serena": CardDef(
        name="Serena",
        kind=CardKind.TRAINER,
        set_code="SIT",
        number="164",
        trainer_kind=TrainerKind.SUPPORTER,
        notes=("Choose one: discard up to 3 cards and draw until 5, or gust a Pokemon V.",),
        implemented_effects=("Discard up to 3 cards by greedy discard priority, then draw until 5.",),
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
    "Professor Burnet": CardDef(
        name="Professor Burnet",
        kind=CardKind.TRAINER,
        set_code="SWSH",
        number="167",
        trainer_kind=TrainerKind.SUPPORTER,
        notes=("Search your deck for up to 2 cards and discard them, then shuffle your deck.",),
        implemented_effects=("Discard up to 2 Archeops from deck for the current Lugia target.",),
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
        set_code="BRS",
        number="150",
        trainer_kind=TrainerKind.ITEM,
        notes=("Discard 2 cards from hand, search deck for a Pokemon.",),
        missing_effects=("Item action: choose discard costs and search target.",),
    ),
    "Quick Ball": CardDef(
        name="Quick Ball",
        kind=CardKind.TRAINER,
        set_code="FST",
        number="237",
        trainer_kind=TrainerKind.ITEM,
        notes=("Discard 1 card from hand, search deck for a Basic Pokemon.",),
        implemented_effects=("Discard 1 by greedy discard priority and search Basic Pokemon.",),
    ),
    "Evolution Incense": CardDef(
        name="Evolution Incense",
        kind=CardKind.TRAINER,
        set_code="SSH",
        number="163",
        trainer_kind=TrainerKind.ITEM,
        notes=("Search deck for an Evolution Pokemon.",),
        implemented_effects=("Search one Evolution Pokemon.",),
    ),
    "Lost Vacuum": CardDef(
        name="Lost Vacuum",
        kind=CardKind.TRAINER,
        set_code="LOR",
        number="162",
        trainer_kind=TrainerKind.ITEM,
        missing_effects=("Lost Zone tool/stadium effect is out of scope for current setup target.",),
    ),
    "Choice Belt": CardDef(
        name="Choice Belt",
        kind=CardKind.TRAINER,
        set_code="BRS",
        number="135",
        trainer_kind=TrainerKind.ITEM,
        missing_effects=("Damage modifier is out of scope for current setup target.",),
    ),
    "Collapsed Stadium": CardDef(
        name="Collapsed Stadium",
        kind=CardKind.TRAINER,
        set_code="BRS",
        number="137",
        trainer_kind=TrainerKind.STADIUM,
        missing_effects=("Bench-size reduction is not modeled for current target.",),
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
    "Powerful Colorless Energy": CardDef(
        name="Powerful Colorless Energy", kind=CardKind.ENERGY, set_code="DAA", number="176"
    ),
    "Aurora Energy": CardDef(name="Aurora Energy", kind=CardKind.ENERGY, set_code="SSH", number="186"),
    "Capture Energy": CardDef(name="Capture Energy", kind=CardKind.ENERGY, set_code="RCL", number="171"),
    "Heat Fire Energy": CardDef(name="Heat Fire Energy", kind=CardKind.ENERGY, set_code="DAA", number="174"),
    "Speed Lightning Energy": CardDef(
        name="Speed Lightning Energy", kind=CardKind.ENERGY, set_code="RCL", number="173"
    ),
}


def get_card_def(name: str) -> CardDef:
    try:
        return CARD_DEFS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown card definition: {name}") from exc


def register_unknown_card(name: str, set_code: str, number: str, section: str | None = None) -> CardDef:
    if name in CARD_DEFS:
        return CARD_DEFS[name]

    normalized_section = (section or "").lower().replace("é", "e")
    if normalized_section.startswith(("pokemon", "pok")):
        card_def = CardDef(
            name=name,
            kind=CardKind.POKEMON,
            set_code=set_code,
            number=number,
            pokemon_stage=PokemonStage.BASIC,
            notes=("Imported from deck list as an unknown Basic Pokemon.",),
            missing_effects=("Card effect is not implemented; treated as a no-effect Basic Pokemon.",),
            inferred=True,
        )
    elif normalized_section.startswith("energy"):
        card_def = CardDef(
            name=name,
            kind=CardKind.ENERGY,
            set_code=set_code,
            number=number,
            notes=("Imported from deck list as an unknown Energy card.",),
            missing_effects=("Energy effect is not implemented; treated as a no-effect Energy.",),
            inferred=True,
        )
    else:
        card_def = CardDef(
            name=name,
            kind=CardKind.TRAINER,
            set_code=set_code,
            number=number,
            trainer_kind=TrainerKind.ITEM,
            notes=("Imported from deck list as an unknown Trainer card.",),
            missing_effects=("Card effect is not implemented; treated as a no-effect Item.",),
            inferred=True,
        )

    CARD_DEFS[name] = card_def
    return card_def
