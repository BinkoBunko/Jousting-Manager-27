from dataclasses import dataclass, field

import dice
from npc import Npc
from variables import DEFAULT_PROFICIENCY

LANCE_LIMIT = 3
SHIELD_AC_BONUS = 2

# Maneuver -> (attack bonus, AC bonus, Animal Handling bonus), in tendency order.
MANEUVERS = {
    "none": (0, 0, 0),
    "aggressive": (5, -5, 0),
    "defensive": (-5, 5, 0),
    "braced": (-5, 0, 5),
    "highInSaddle": (5, 0, -5),
    "eyesFixed": (5, 0, 0),
}


def roll_total(expression):
    return dice.roll(expression).total


def strength_modifier(npc):
    return (npc.stats["strength"] - 10) // 2


def proficiency(npc):
    return npc.stats.get("proficiency", DEFAULT_PROFICIENCY)


def maneuver_from_roll(tendencies, roll):
    upper = 0
    for maneuver in MANEUVERS:
        upper += tendencies.get(maneuver, 0)
        if roll <= upper:
            return maneuver
    return "none"


def choose_maneuver(npc):
    return maneuver_from_roll(npc.tendencies, roll_total("1d100"))


def effective_ac(npc, maneuver):
    shield = SHIELD_AC_BONUS if npc.shield_proficient else 0
    return npc.stats["ac"] + shield + MANEUVERS[maneuver][1]


@dataclass
class Jouster:
    npc: Npc
    hits: int = 0
    eyes: set = field(default_factory=lambda: {"left eye", "right eye"})
    scars: list = field(default_factory=list)

    @property
    def name(self):
        return self.npc.name


def apply_eyes_fixed_injury(jouster, roll):
    """Apply the Eyes Fixed injury table. DMG effects of the injuries are not modeled."""
    if roll == 1:
        if "left eye" in jouster.eyes:
            jouster.eyes.remove("left eye")
            return "loses left eye"
        return "no effect (no left eye)"
    if roll == 2:
        if "right eye" in jouster.eyes:
            jouster.eyes.remove("right eye")
            return "loses right eye"
        return "no effect (no right eye)"
    if roll <= 4:
        jouster.scars.append("Horrible Scar")
        return "Horrible Scar"
    if roll <= 10:
        jouster.scars.append("Minor Scar")
        return "Minor Scar"
    return "no injury"


def lance_strike(attacker, attack_maneuver, defender, defend_maneuver, log):
    """Resolve one lance attack. Returns True if the defender is unhorsed."""
    attack = (
        roll_total("1d20")
        + strength_modifier(attacker.npc)
        + proficiency(attacker.npc)
        + MANEUVERS[attack_maneuver][0]
    )
    target = effective_ac(defender.npc, defend_maneuver)
    if attack < target:
        log.append(f"  {attacker.name} attacks ({attack} vs AC {target}): miss")
        return False

    attacker.hits += 1
    damage = max(0, roll_total("1d12") + strength_modifier(attacker.npc))
    log.append(f"  {attacker.name} hits ({attack} vs AC {target}) for {damage}; lance broken")

    if defend_maneuver == "eyesFixed":
        outcome = apply_eyes_fixed_injury(defender, roll_total("1d20"))
        log.append(f"  {defender.name} (Eyes Fixed) injury: {outcome}")

    brace = roll_total("1d20") + defender.npc.stats["animalHandling"] + MANEUVERS[defend_maneuver][2]
    if brace >= damage:
        log.append(f"  {defender.name} braces ({brace} vs DC {damage}): stays mounted")
        return False
    log.append(f"  {defender.name} fails brace ({brace} vs DC {damage}): unhorsed")
    return True


def run_pass(a, b, log):
    """Play one pass with simultaneous attacks. Returns (a_unhorsed, b_unhorsed)."""
    maneuver_a = choose_maneuver(a.npc)
    maneuver_b = choose_maneuver(b.npc)
    log.append(f"  {a.name}: {maneuver_a} | {b.name}: {maneuver_b}")
    b_unhorsed = lance_strike(a, maneuver_a, b, maneuver_b, log)
    a_unhorsed = lance_strike(b, maneuver_b, a, maneuver_a, log)
    return a_unhorsed, b_unhorsed


@dataclass
class MatchResult:
    winner: Npc
    loser: Npc
    reason: str
    passes: int
    log: list[str]


def run_match(npc_a, npc_b, lance_limit=LANCE_LIMIT):
    a, b = Jouster(npc_a), Jouster(npc_b)
    log = []
    passes = 0
    while True:
        passes += 1
        log.append(f"Pass {passes}")
        a_unhorsed, b_unhorsed = run_pass(a, b, log)
        log.append(f"  Score: {a.name} {a.hits} - {b.name} {b.hits}")

        if a_unhorsed != b_unhorsed:
            winner, loser = (b, a) if a_unhorsed else (a, b)
            return MatchResult(winner.npc, loser.npc, "opponent unhorsed", passes, log)
        if a_unhorsed and b_unhorsed:
            # Both unhorsed on the same pass: the joust continues.
            continue
        if a.hits != b.hits and max(a.hits, b.hits) >= lance_limit:
            winner, loser = (a, b) if a.hits > b.hits else (b, a)
            return MatchResult(winner.npc, loser.npc, f"reached {lance_limit} lances", passes, log)


if __name__ == "__main__":
    result = run_match(Npc(None, None, None), Npc(None, None, None))
    print("\n".join(result.log))
    print(f"\n{result.winner.name} wins by {result.reason} after {result.passes} passes.")
