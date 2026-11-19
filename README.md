# Jousting Manager 27

A Python tool for generating and managing NPC jousters for a 5e jousting system. NPCs are randomly generated with a race, nationality, combat stats, and maneuver tendencies, and are saved to a local JSON database.

Rules reference: [JOUSTING_RULES.md](JOUSTING_RULES.md) (from [Homebrew Homunculus](https://homebrewhomunculus.blogspot.com/2018/02/simple-jousting-rules-for-5e.html)).

## Features

- **NPC generation** ([npc.py](npc.py)): random name, race (Human, Elf, Dwarf), and nationality, plus:
  - **Stats** (Strength, Animal Handling, AC) drawn from normal distributions.
  - **Tendencies** (Aggressive, Defensive, Braced, High in Saddle, Eyes Fixed) as whole numbers that sum to 100, so each tendency maps to a range of d100 results (1 to 100). Each tendency gets at least 1.
- **Stat distributions** are configured in [variables.py](variables.py) (means and standard deviations).
- **Persistence** ([db.py](db.py)): NPCs are appended to `db.json`, which is created on first use. The file is git-ignored, so each machine keeps its own data.

## Project Structure

| File | Purpose |
|------|---------|
| `npc.py` | `Npc` class: random generation and string formatting |
| `variables.py` | Currently stores Stat means and standard deviations but planning more |
| `db.py` | Load and save NPC records in `db.json` |
| `joust.py` | 1v1 match engine: runs passes between two NPCs until a winner is decided |
| `dice.py` | Dice expression and structured roll helpers |
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

To run a simulated 1v1 match between two random NPCs and print the pass-by-pass log:

```powershell
python joust.py
```

A match ends when one jouster is unhorsed (and the other is not), or when a jouster reaches 3 lances broken (hits) while the other has fewer. If both are unhorsed on the same pass, the joust continues.

## Database Format

`db.json` holds a JSON array of NPC records:

```json
{
  "name": "Eryn Caldwell",
  "race": "Dwarf",
  "nationality": "Damaran",
  "stats": { "strength": 10, "animalHandling": 4, "ac": 10, "proficiency": 2 },
  "tendencies": {
    "none": 10,
    "aggressive": 18,
    "defensive": 8,
    "braced": 25,
    "highInSaddle": 22,
    "eyesFixed": 17
  },
  "shieldProficient": true
}
```

## Roadmap / Known TODOs

These are noted in the source code:

- Connect name generation to a name generator API.
- Manual npc creation.
- Move races and nationalities into the database or a game data source.
- Base tendencies on stats (for example, high Animal Handling makes riding braced less likely).
- Build the GUI in `app.py` with CustomTkinter.
- Tournament simulator functionality.
- And more!
