import pytest

import joust
from joust import Jouster
from npc import Npc


def make_npc(name="Arin", strength=14, ac=14, animal_handling=6, proficiency=2, shield=True):
    stats = {"strength": strength, "animalHandling": animal_handling, "ac": ac, "proficiency": proficiency}
    tendencies = {"none": 100, "aggressive": 0, "defensive": 0, "braced": 0, "highInSaddle": 0, "eyesFixed": 0}
    return Npc(name, "Human", "Damaran", stats, tendencies, shield_proficient=shield)


def script_rolls(monkeypatch, *values):
    results = iter(values)
    monkeypatch.setattr(joust, "roll_total", lambda expression: next(results))


def test_lance_attack_adds_proficiency_and_maneuver_bonus(monkeypatch):
    # d20 10 + Str mod 2 + proficiency 2 + aggressive 5 = 19, vs AC 14 + shield 2 - aggressive 5 = 11.
    attacker = Jouster(make_npc("A", strength=14, proficiency=2))
    defender = Jouster(make_npc("B", ac=14, shield=True))
    script_rolls(monkeypatch, 10, 7, 2)  # attack d20, damage d12, brace d20
    log = []

    unhorsed = joust.lance_strike(attacker, "aggressive", defender, "aggressive", log)

    assert attacker.hits == 1
    assert "19 vs AC 11" in log[0]
    assert "for 9" in log[0]  # 7 + Str mod 2
    assert unhorsed is True  # brace 2 + AH 6 = 8 < DC 9


def test_shield_only_adds_ac_when_proficient():
    assert joust.effective_ac(make_npc(ac=14, shield=True), "none") == 16
    assert joust.effective_ac(make_npc(ac=14, shield=False), "none") == 14


def test_defensive_maneuver_raises_effective_ac():
    assert joust.effective_ac(make_npc(ac=14, shield=True), "defensive") == 21


def test_brace_failure_unhorses_and_success_keeps_rider(monkeypatch):
    attacker = Jouster(make_npc("A"))
    defender = Jouster(make_npc("B", animal_handling=6))

    script_rolls(monkeypatch, 20, 8, 3)  # hit, damage 8+2=10, brace 3+6=9 < 10
    assert joust.lance_strike(attacker, "none", defender, "none", []) is True

    script_rolls(monkeypatch, 20, 8, 4)  # brace 4+6=10 >= 10
    assert joust.lance_strike(attacker, "none", defender, "none", []) is False


def test_braced_maneuver_adds_to_brace_check(monkeypatch):
    attacker = Jouster(make_npc("A"))
    defender = Jouster(make_npc("B", animal_handling=6))
    script_rolls(monkeypatch, 20, 8, 0)  # damage 10; brace 0+6+5 = 11 >= 10
    assert joust.lance_strike(attacker, "none", defender, "braced", []) is False


@pytest.mark.parametrize(
    ("roll", "expected"),
    [
        (1, "loses left eye"),
        (2, "loses right eye"),
        (3, "Horrible Scar"),
        (4, "Horrible Scar"),
        (5, "Minor Scar"),
        (10, "Minor Scar"),
        (11, "no injury"),
    ],
)
def test_eyes_fixed_injury_table(roll, expected):
    jouster = Jouster(make_npc())
    assert joust.apply_eyes_fixed_injury(jouster, roll) == expected


def test_maneuver_selection_follows_tendency_ranges():
    tendencies = {"none": 10, "aggressive": 20, "defensive": 20, "braced": 20, "highInSaddle": 20, "eyesFixed": 10}
    assert joust.maneuver_from_roll(tendencies, 10) == "none"
    assert joust.maneuver_from_roll(tendencies, 11) == "aggressive"
    assert joust.maneuver_from_roll(tendencies, 100) == "eyesFixed"


def script_passes(monkeypatch, passes):
    """Each entry: (a_unhorsed, b_unhorsed, a_hits_gained, b_hits_gained)."""
    remaining = iter(passes)

    def fake_pass(a, b, log):
        a_unhorsed, b_unhorsed, a_gain, b_gain = next(remaining)
        a.hits += a_gain
        b.hits += b_gain
        return a_unhorsed, b_unhorsed

    monkeypatch.setattr(joust, "run_pass", fake_pass)


def test_double_unhorse_continues_the_match(monkeypatch):
    script_passes(monkeypatch, [(True, True, 0, 0), (False, True, 1, 0)])

    result = joust.run_match(make_npc("A"), make_npc("B"))

    assert result.passes == 2
    assert result.winner.name == "A"
    assert result.reason == "opponent unhorsed"


def test_reaching_lance_limit_wins(monkeypatch):
    script_passes(monkeypatch, [(False, False, 1, 0), (False, False, 1, 1), (False, False, 1, 0)])

    result = joust.run_match(make_npc("A"), make_npc("B"), lance_limit=3)

    assert result.winner.name == "A"
    assert result.passes == 3


def test_tie_at_lance_limit_continues_until_one_is_ahead(monkeypatch):
    script_passes(
        monkeypatch,
        [(False, False, 3, 3), (False, False, 0, 0), (False, False, 1, 0)],
    )

    result = joust.run_match(make_npc("A"), make_npc("B"), lance_limit=3)

    assert result.winner.name == "A"
    assert result.passes == 3
