import random
from variables import *

class Npc:
    def generate_npc_name(self):
        # Generate a random name for the NPC
        #TODO: Hookup to name generator API
        first_names = ["Arin", "Bryn", "Cai", "Dara", "Eryn", "Finn", "Gwen", "Hale", "Iris", "Jace"]
        last_names = ["Ashford", "Blackwood", "Caldwell", "Davenport", "Everhart", "Fairchild", "Grayson", "Hawthorne"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def generate_npc_race(self):
        # Randomly select a race for the NPC
        #TODO: Apply in game races via API or database
        return random.choice(["Human", "Elf", "Dwarf"])

    def generate_npc_nationality(self):
        # Randomly select a nationality for the NPC
        #TODO: Apply in game nationalities via database
        return random.choice(["Andorran", "Alturiak", "Amnian", "Chondathan", "Damaran", "Hill Giant"])

    def generate_npc_stats(self):
        # Randomly generate NPC stats and tendencies
        stats = {}
        stats["strength"] = round(random.gauss(AVG_STR, STD_DEV_STR))
        stats["animalHandling"] = round(random.gauss(AVG_ANIMAL_HANDLING, STD_DEV_ANIMAL_HANDLING))
        stats["ac"] = round(random.gauss(AVG_AC, STD_DEV_AC))
        return stats

    def generate_npc_tendencies(self):
        # Integer counts of d100 values (1-100) per tendency; each gets at least one, sum is 100
        #TODO: Potentially base tendencies on stats (e.g. high animal handling = less likely to ride braced)
        names = ["aggressive", "defensive", "braced", "highInSaddle", "eyesFixed"]
        cuts = sorted(random.sample(range(1, 100), k=len(names) - 1))
        bounds = [0] + cuts + [100]
        return {name: bounds[i + 1] - bounds[i] for i, name in enumerate(names)}

    def __init__(self, name: str|None, race: str|None, nationality: str|None, stats: dict|None = None, tendencies: dict|None = None):
        if name is None:
            name = self.generate_npc_name()
        if race is None:
            race = self.generate_npc_race()
        if nationality is None:
            nationality = self.generate_npc_nationality()
        if stats is None:
            stats = self.generate_npc_stats()
        if tendencies is None:
            tendencies = self.generate_npc_tendencies()


        self.name = name
        self.race = race
        self.nationality = nationality
        self.stats = stats
        self.tendencies = tendencies

    def __str__(self) -> str:
        return (
            f"{self.name} ({self.race}, {self.nationality}) | "
            f"Strength: {self.stats['strength']}, "
            f"Animal Handling: {self.stats['animalHandling']}, "
            f"AC: {self.stats['ac']}"
        )

    def __repr__(self) -> str:
        return (
            f"Npc(name={self.name!r}, race={self.race!r}, "
            f"nationality={self.nationality!r})"
        )

    