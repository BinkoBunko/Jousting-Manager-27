

import random
import re
from dataclasses import dataclass
from collections.abc import Mapping

# Matches one term: a dice group like "2d4", "d20", "-5d8", or a constant like "+5".
_TERM_RE = re.compile(r"([+-]?)(\d*)d(\d+)|([+-]?)(\d+)", re.IGNORECASE)


@dataclass
class RollResult:
    total: int
    breakdown: str


def _parse(expression):
    """Split an expression like '2d4 + 5d8 - 2' into dice and constant terms."""
    text = expression.replace(" ", "")
    if not text:
        raise ValueError("Empty dice expression")

    terms = []
    pos = 0
    while pos < len(text):
        match = _TERM_RE.match(text, pos)
        if not match:
            raise ValueError(f"Invalid dice expression near '{text[pos:]}'")
        pos = match.end()

        if match.group(3) is not None:  # dice group
            sign = -1 if match.group(1) == "-" else 1
            count = int(match.group(2)) if match.group(2) else 1
            sides = int(match.group(3))
            if count < 1 or sides < 1:
                raise ValueError("Dice count and sides must be at least 1")
            terms.append(("dice", sign, count, sides))
        else:  # constant modifier
            sign = -1 if match.group(4) == "-" else 1
            terms.append(("const", sign, int(match.group(5))))

        if pos < len(text) and text[pos] not in "+-":
            raise ValueError(f"Invalid dice expression near '{text[pos:]}'")

    return terms


def _structured_terms(groups):
    """Convert structured dice groups into the same terms used by the expression parser."""
    terms = []
    for index, group in enumerate(groups):
        if not isinstance(group, Mapping):
            raise TypeError(f"Dice group {index} must be a mapping")

        unknown_keys = set(group) - {"count", "roll", "operator"}
        if unknown_keys:
            raise ValueError(f"Unknown keys in dice group {index}: {', '.join(sorted(unknown_keys))}")
        if "count" not in group or "roll" not in group:
            raise ValueError(f"Dice group {index} must include 'count' and 'roll'")

        count = group["count"]
        sides = group["roll"]
        operator = group.get("operator", "+")
        if type(count) is not int or count < 1:
            raise ValueError(f"Dice group {index} count must be a positive integer")
        if type(sides) is not int or sides < 1:
            raise ValueError(f"Dice group {index} roll must be a positive integer")
        if operator not in ("+", "-"):
            raise ValueError(f"Dice group {index} operator must be '+' or '-'")

        terms.append(("dice", -1 if operator == "-" else 1, count, sides))

    if not terms:
        raise ValueError("At least one dice group is required")
    return terms


def _roll_once(terms):
    total = 0
    parts = []
    for term in terms:
        if term[0] == "dice":
            _, sign, count, sides = term
            rolls = [random.randint(1, sides) for _ in range(count)]
            total += sign * sum(rolls)
            parts.append(f"{'-' if sign < 0 else '+'}{count}d{sides}{rolls}")
        else:
            _, sign, value = term
            total += sign * value
            parts.append(f"{'-' if sign < 0 else '+'}{value}")
    breakdown = " ".join(parts).lstrip("+")
    return total, breakdown


def roll(expression, advantage=False):
    """
    Roll an expression or structured dice groups, for example:
    roll([{"count": 2, "roll": 4}, {"count": 5, "roll": 8, "operator": "-"}]).

    In a structured group, "roll" is the die's number of sides and "operator"
    applies that group's total. It defaults to addition. String expressions
    such as "1d20+5" remain supported.

    With advantage=True the entire input is rolled twice and the higher total is kept.
    """
    if isinstance(expression, str):
        terms = _parse(expression)
    else:
        terms = _structured_terms(expression)

    if not advantage:
        total, breakdown = _roll_once(terms)
        return RollResult(total, breakdown)

    first_total, first_breakdown = _roll_once(terms)
    second_total, second_breakdown = _roll_once(terms)
    if first_total >= second_total:
        best_total, best_breakdown = first_total, first_breakdown
    else:
        best_total, best_breakdown = second_total, second_breakdown
    breakdown = f"advantage [{first_breakdown} | {second_breakdown}] -> {best_breakdown}"
    return RollResult(best_total, breakdown)