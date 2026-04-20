# Simulation model

PTCG-MonteMon models only our side of the game.

Tracked zones:

- active
- bench
- prizes
- hand
- discard
- stadium
- deck

Setup-state Monte Carlo:

1. Shuffle a 60-card deck.
2. Draw 7 cards.
3. Mulligan until the hand contains at least one Basic Pokemon.
4. Choose a starting active Pokemon using a configurable priority in code.
5. Bench Basic Pokemon from hand up to 5 using a priority in code.
6. Take 6 prize cards from the deck.
7. Check whether the target JSON matches the resulting zones.

Card effects are registered in `src/ptcg_montemon/cards.py`, but most actions are intentionally marked as missing until their exact behavior matters for a target.

## Opening-hand targets

The `opening-hand` mode checks only the mulligan-valid opening hand before choosing an Active Pokemon or setting Prize cards.

Example:

```powershell
python -m ptcg_montemon.cli --deck "Lugia Archeops1.txt" --target examples/targets/opening_hand_lugia_v.json --mode opening-hand --trials 10000 --seed 42
```

Target JSON:

```json
{
  "name": "Opening hand contains Lugia V",
  "zones": {
    "hand": {
      "Lugia V": 1
    }
  }
}
```

Change the `zones` requirements to test other custom scenes, such as 2 Ultra Ball in hand, Archeops prized, or Lugia V in Active after setup.

## Two-turn greedy strategy

The `two-turn` mode samples an opening state, then plays a fixed greedy strategy through our second turn.

The strategy can be configured with `--strategy examples/strategies/lugia_greedy.json`.

Opponent hand disruption can be configured with `--opponent-disruption none|iono|judge`. It is applied after our first turn finishes and before our second turn starts. To model going first into the opponent's first-turn disruption, use `--going first --opponent-disruption iono`.

Currently implemented for the Lugia Archeops target:

- setup active choice with a small target-oriented priority
- repeatedly using available actions in priority order until the turn has no more greedy action
- playing Basic Pokemon to the Bench
- evolving Lugia V in the Active Spot or on the Bench into Lugia VSTAR on our second turn
- blocking same-turn evolution for Pokemon that were just played
- Ultra Ball discarding 2 cards and searching a Pokemon
- Great Ball taking a useful Pokemon from the top 7 cards
- Capturing Aroma as one sampled coin flip per use: heads searches Evolution Pokemon, tails searches Basic Pokemon
- Professor's Research
- Iono
- Jacq
- Carmine
- Squawkabilly ex's first-turn discard-and-draw ability
- Lumineon V's Supporter search when played from hand to Bench
- playing Mesagoza as the Stadium
- using Mesagoza's coin-flip Pokemon search once per turn

Important limitations:

- Capturing Aroma samples one coin flip per use during Monte Carlo trials.
- This mode does not search for alternate action lines. It follows one fixed greedy priority.
- It intentionally ignores opponent effects.
- It does not yet model attacks, Energy attachment, retreating, switching, prize taking, or Lugia VSTAR's Summoning Star.
- It assumes the first player draws on their first turn unless `--no-first-turn-draw` is passed.
- `--explain` prints one successful greedy line with the opening hand, draw cards, and action details.
- `--json` returns structured results for UI integration.
- `--opponent-disruption iono` puts our hand on the bottom of the deck in random order, then draws cards equal to our remaining Prize cards.
- `--opponent-disruption judge` shuffles our hand into the deck, then draws 4 cards.

## Strategy file

The greedy strategy JSON currently supports these UI-friendly fields:

- `action_priority`: order to try actions each turn.
- `active_priority`: opening Active Pokemon preference.
- `bench_priority`: Pokemon benching preference.
- `pokemon_search_priority`: Pokemon search preference for Ultra Ball, Great Ball, Capturing Aroma, Mesagoza.
- `supporter_priority`: default Supporter preference.
- `discard_priority`: Ultra Ball discard-cost preference.
- `max_actions_per_turn`: guardrail against action loops.
- `prefer_research_when_holding_archeops`: prioritize discard-and-draw Supporters when Archeops is in hand and fewer than 2 Archeops are discarded.
- `prefer_jacq_when_missing_lugia_vstar`: prioritize Jacq when Lugia VSTAR is missing.
- `use_mesagoza`: enable playing and using Mesagoza.
- `use_squawkabilly`: enable Squawkabilly ex.

## Known rule/effect questions

These are the first details to confirm next:

- Whether the first player draws on their first turn in the rule set you want.
- Whether opponent effects are ignored completely except for prize count.
