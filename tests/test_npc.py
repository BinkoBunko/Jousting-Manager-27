import npc
from npc import Npc


def test_constructor_preserves_supplied_values():
    stats = {"strength": 12, "animalHandling": 7, "ac": 15}
    tendencies = {
        "aggressive": 20,
        "defensive": 20,
        "braced": 20,
        "highInSaddle": 20,
        "eyesFixed": 20,
    }

    jouster = Npc("Arin Ashford", "Elf", "Damaran", stats, tendencies)

    assert jouster.name == "Arin Ashford"
    assert jouster.race == "Elf"
    assert jouster.nationality == "Damaran"
    assert jouster.stats is stats
    assert jouster.tendencies is tendencies


def test_constructor_generates_values_for_missing_fields(monkeypatch):
    choices = iter(("Arin", "Ashford", "Dwarf", "Damaran"))
    gauss_values = iter((12.6, 7.4, 15.7))
    monkeypatch.setattr(npc.random, "choice", lambda options: next(choices))
    monkeypatch.setattr(npc.random, "gauss", lambda mean, deviation: next(gauss_values))
    monkeypatch.setattr(npc.random, "sample", lambda population, k: [10, 30, 50, 70, 90])

    jouster = Npc(None, None, None)

    assert jouster.name == "Arin Ashford"
    assert jouster.race == "Dwarf"
    assert jouster.nationality == "Damaran"
    assert jouster.stats == {"strength": 13, "animalHandling": 7, "ac": 16, "proficiency": 2}
    assert jouster.shield_proficient is True
    assert jouster.tendencies == {
        "none": 10,
        "aggressive": 20,
        "defensive": 20,
        "braced": 20,
        "highInSaddle": 20,
        "eyesFixed": 10,
    }


def test_generated_tendencies_are_positive_and_sum_to_100(monkeypatch):
    monkeypatch.setattr(npc.random, "sample", lambda population, k: [80, 20, 60, 40, 90])

    jouster = Npc("Arin Ashford", "Elf", "Damaran", {}, {})
    tendencies = jouster.generate_npc_tendencies()

    assert set(tendencies) == {
        "none",
        "aggressive",
        "defensive",
        "braced",
        "highInSaddle",
        "eyesFixed",
    }
    assert all(value > 0 for value in tendencies.values())
    assert sum(tendencies.values()) == 100


def test_string_representations():
    jouster = Npc(
        "Arin Ashford",
        "Elf",
        "Damaran",
        {"strength": 12, "animalHandling": 7, "ac": 15},
        {},
    )

    assert str(jouster) == (
        "Arin Ashford (Elf, Damaran) | Strength: 12, "
        "Animal Handling: 7, AC: 15"
    )
    assert repr(jouster) == (
        "Npc(name='Arin Ashford', race='Elf', nationality='Damaran')"
    )
