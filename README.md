# PTCG-MonteMon

PTCG-MonteMon is a Pokemon TCG Monte Carlo simulator for checking whether a deck can reach a custom board state by a chosen timing point.

The current project focuses on our side of the game. It can simulate opening hands, setup, prizes, a greedy two-turn Lugia/Archeops line, hand disruption from the opponent, and custom target-scene checks.

## Features

- Import a deck list in Pokemon TCG text format.
- Check custom target scenes across `hand`, `active`, `bench`, `prizes`, `discard`, `stadium`, and `deck`.
- Choose timing: opening hand, after setup, or after our second turn.
- Choose going first, going second, or both.
- Simulate opponent turn 1 / turn 2 hand disruption with Iono or Judge.
- Use a configurable greedy strategy file.
- Show probability and 3 successful route examples.
- Web UI with target-scene form editing and JSON preview.
- Button to open the Limitless deck image generator.

## Quick Start: Web UI

From the project root:

```powershell
$env:PYTHONPATH='src'
python -m ptcg_montemon.webapp 8765
```

Open:

```text
http://127.0.0.1:8765
```

The web page includes:

- deck import textarea
- sample count
- optional fixed random seed
- first / second / both choice
- timing choice
- opponent turn 1 and turn 2 disruption choices
- target-scene form builder
- JSON preview
- probability result
- 3 successful greedy routes

If the fixed seed checkbox is disabled, each run uses a fresh random seed. Enable it when you want reproducible results.

## Quick Start: CLI

Opening hand contains Lugia V:

```powershell
$env:PYTHONPATH='src'
python -m ptcg_montemon.cli --deck "Lugia Archeops1.txt" --target examples\targets\opening_hand_lugia_v.json --mode opening-hand --trials 10000 --seed 42 --explain
```

Turn-two Lugia VSTAR target, both going first and second:

```powershell
$env:PYTHONPATH='src'
python -m ptcg_montemon.cli --deck "Lugia Archeops1.txt" --target examples\targets\t2_lugia_vstar_in_play_2_archeops_discard.json --mode two-turn --going both --trials 10000 --seed 42 --strategy examples\strategies\lugia_greedy.json
```

Going first into opponent turn 1 Iono:

```powershell
python -m ptcg_montemon.cli --deck "Lugia Archeops1.txt" --target examples\targets\t2_lugia_vstar_in_play_2_archeops_discard.json --mode two-turn --going first --trials 10000 --seed 42 --strategy examples\strategies\lugia_greedy.json --opponent-turn1-disruption iono
```

JSON output for UI or scripts:

```powershell
python -m ptcg_montemon.cli --deck "Lugia Archeops1.txt" --target examples\targets\t2_lugia_vstar_in_play_2_archeops_discard.json --mode two-turn --going both --trials 1000 --json --explain
```

## Target Scene Format

Targets are JSON files. `zones` are requirements that must all be true.

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

Use `any_of` when at least one group can satisfy the target:

```json
{
  "name": "T2 Lugia VSTAR in play, 2 Archeops discarded",
  "zones": {
    "discard": {
      "Archeops": 2
    }
  },
  "any_of": [
    {
      "active": {
        "Lugia VSTAR": 1
      }
    },
    {
      "bench": {
        "Lugia VSTAR": 1
      }
    }
  ]
}
```

Supported zones:

- `hand`
- `active`
- `bench`
- `prizes`
- `discard`
- `stadium`
- `deck`

## Modes

- `opening-hand`: checks the mulligan-valid opening hand before choosing an Active Pokemon.
- `setup`: checks after choosing an Active Pokemon, placing Basic Pokemon on the Bench, and setting Prize cards.
- `two-turn`: plays the configured greedy strategy through our second turn, then checks the target.

## Greedy Strategy

The default strategy is:

```text
examples/strategies/lugia_greedy.json
```

It controls:

- action priority
- opening Active Pokemon priority
- Bench priority
- Pokemon search priority
- Supporter priority
- Ultra Ball discard priority
- whether to use Mesagoza
- whether to use Squawkabilly ex
- maximum actions per turn

The strategy is intentionally configurable because it is not a perfect player. Use `--explain` or the web route output to inspect whether the greedy line matches how you would play.

## Current Limitations

- Only our side is modeled.
- The two-turn simulation uses one fixed greedy strategy and does not search for alternate lines.
- Many card effects are only implemented where needed for the current Lugia/Archeops target.
- Attacks, retreating, switching, Energy attachment, Prize taking, and Lugia VSTAR's Summoning Star are not fully modeled yet.
- Opponent interaction is limited to optional Iono/Judge-style hand disruption.

## Example Files

- `Lugia Archeops1.txt`: sample Lugia/Archeops deck list.
- `examples/targets/opening_hand_lugia_v.json`: opening-hand Lugia V target.
- `examples/targets/t2_lugia_vstar_in_play_2_archeops_discard.json`: turn-two Lugia VSTAR plus discarded Archeops target.
- `examples/strategies/lugia_greedy.json`: default greedy strategy.
