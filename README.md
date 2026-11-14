# Jousting Manager 27

A Python tool for generating and managing NPC jousters for a 5e jousting system. NPCs are randomly generated with a race, nationality, combat stats, and maneuver tendencies, and are saved to a local JSON database.

Rules reference: [JOUSTING_RULES.md](JOUSTING_RULES.md) (from [Homebrew Homunculus](https://homebrewhomunculus.blogspot.com/2018/02/simple-jousting-rules-for-5e.html)).

## Features

- **NPC generation** ([npc.py](npc.py)): random name, race (Human, Elf, Dwarf), and nationality, plus:
  - **Stats** (Strength, Animal Handling, AC) drawn from normal distributions.
  - **Tendencies** (Aggressive, Defensive, Braced, High in Saddle, Eyes Fixed) with random values from 0 to 1.
- **Stat distributions** are configured in [variables.py](variables.py) (means and standard deviations).
- **Persistence** ([db.py](db.py)): NPCs are appended to `db.json`, which is created on first use. The file is git-ignored, so each machine keeps its own data.

## Project Structure

| File | Purpose |
|------|---------|
| `npc.py` | `Npc` class: random generation and string formatting |
| `variables.py` | Currently stores Stat means and standard deviations but planning more |
| `db.py` | Load and save NPC records in `db.json` |
| `appConsole.py` | Command-line entry point that generates and reports NPCs (for development) |
| `app.py` | Reserved for the GUI (currently empty) |
| `JOUSTING_RULES.md` | Jousting rules and maneuver summary |
| `requirements.txt` | Python dependencies |

## Requirements

- Python 3.10 or newer (the code uses `str | None` type hints).
- Dependencies listed in `requirements.txt`:
  - `customtkinter` (for the planned GUI)
  - `darkdetect`
  - `packaging`

## Setup

```powershell
git clone https://github.com/BinkoBunko/Jousting-Manager-27.git
cd Jousting-Manager-27
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

To run the UI:

```powershell
python app.py
```

WIP

## Database Format

`db.json` holds a JSON array of NPC records:

```json
{
  "name": "Eryn Caldwell",
  "race": "Dwarf",
  "nationality": "Damaran",
  "stats": { "strength": 10, "animalHandling": 4, "ac": 10 },
  "tendencies": {
    "aggressive": 0.2,
    "defensive": 0.2,
    "braced": 0.2,
    "highInSaddle": 0.2,
    "eyesFixed": 0.2
  }
}
```

## Roadmap / Known TODOs

These are noted in the source code:

- Connect name generation to a name generator API.
- Manual npc creation.
- Move races and nationalities into the database or a game data source.
- Generate tendencies that sum to 1.0.
- Base tendencies on stats (for example, high Animal Handling makes riding braced less likely).
- Build the GUI in `app.py` with CustomTkinter.
- Tournament simulator functionality.
- And more!
