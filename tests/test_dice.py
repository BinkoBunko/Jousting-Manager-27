import pytest

import dice


def patch_rolls(monkeypatch, *values):
    results = iter(values)
    calls = []

    def randint(minimum, maximum):
        calls.append((minimum, maximum))
        return next(results)

    monkeypatch.setattr(dice.random, "randint", randint)
    return calls


@pytest.mark.parametrize("sides", (4, 6, 8, 10, 12, 20, 100))
def test_supported_die_types_roll_within_bounds(monkeypatch, sides):
    calls = patch_rolls(monkeypatch, sides)

    result = dice.roll(f"1d{sides}")

    assert result.total == sides
    assert calls == [(1, sides)]


def test_structured_groups_add_by_default(monkeypatch):
    patch_rolls(monkeypatch, 2, 4, 7)
    groups = [
        {"count": 2, "roll": 4},
        {"count": 1, "roll": 8},
    ]

    result = dice.roll(groups)

    assert result.total == 13


def test_structured_groups_can_subtract(monkeypatch):
    patch_rolls(monkeypatch, 2, 3, 6)
    groups = [
        {"count": 2, "roll": 4},
        {"count": 1, "roll": 6, "operator": "-"},
    ]

    result = dice.roll(groups)

    assert result.total == -1


def test_expression_supports_addition_subtraction_and_modifiers(monkeypatch):
    calls = patch_rolls(monkeypatch, 3, 4, 2)

    result = dice.roll("1d4 + 1d6 - 1d8 + 5")

    assert result.total == 10
    assert calls == [(1, 4), (1, 6), (1, 8)]


def test_advantage_keeps_higher_roll(monkeypatch):
    calls = patch_rolls(monkeypatch, 4, 17)

    result = dice.roll("1d20", advantage=True)

    assert result.total == 17
    assert calls == [(1, 20), (1, 20)]


@pytest.mark.parametrize("expression", ("", "2x6", "1d0", "1d20+"))
def test_invalid_expressions_raise_value_error(expression):
    with pytest.raises(ValueError):
        dice.roll(expression)


@pytest.mark.parametrize(
    "groups",
    (
        [],
        [{"count": 1, "roll": 6, "operator": "*"}],
        [{"count": 0, "roll": 6}],
        [{"count": 1, "roll": 0}],
        [{"count": 1}],
        [{"count": 1, "roll": 6, "typo": True}],
        [None],
    ),
)
def test_invalid_structured_groups_raise_error(groups):
    with pytest.raises((TypeError, ValueError)):
        dice.roll(groups)
