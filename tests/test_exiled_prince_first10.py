from __future__ import annotations

import csv
from pathlib import Path
import re
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from runtime.exiled_prince.cards_runtime import ExiledPrinceCardLibrary



def _load_first10_csv_ids() -> list[str]:
    with (REPO / "design/exiled_prince/cards_v0_1.csv").open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return [row["card_id"] for row in rows[:10]]


def test_loads_first_10_cards_only():
    library = ExiledPrinceCardLibrary(REPO)
    assert set(_load_first10_csv_ids()) == set(library._cards.keys())


def test_upgraded_values_match_csv_definitions():
    library = ExiledPrinceCardLibrary(REPO)

    checks: dict[str, tuple[str, int]] = {
        "EX_STRIKE": ("damage", 9),
        "EX_DEFEND": ("block", 8),
        "TACTICAL_BRIEFING": ("magic", 3),
        "CHAIN_OF_COMMAND": ("block", 11),
        "FEINT_RETREAT": ("block", 8),
        "TARGET_EXPOSURE": ("vulnerable_base", 2),
        "CUT_SUPPLY_LINES": ("damage", 10),
        "BLACK_ORDER": ("damage", 12),
    }

    for card_id, (field, expected) in checks.items():
        upgraded = library.card(card_id, upgraded=True)
        assert upgraded.numbers[field] == expected

    compel = library.card("COMPEL", upgraded=True)
    assert compel.cost == 0

    black_order = library.card("BLACK_ORDER", upgraded=True)
    assert black_order.numbers["influence_cost"] == 2


def test_card_text_matches_behavior_smoke():
    library = ExiledPrinceCardLibrary(REPO)
    first10 = _load_first10_csv_ids()

    for card_id in first10:
        for upgraded in (False, True):
            card = library.card(card_id, upgraded=upgraded)

            # no unresolved token markers
            assert "!" not in card.description

            # any explicit integer in description should come from configured numbers or cost
            ints_in_text = {int(v) for v in re.findall(r"\d+", card.description)}
            allowed_values = set(card.numbers.values()) | {card.cost}
            assert ints_in_text.issubset(allowed_values | {0, 1}), (
                card_id,
                upgraded,
                ints_in_text,
                allowed_values,
            )


def test_tooltip_registry_binding_for_each_card():
    library = ExiledPrinceCardLibrary(REPO)

    for card_id in _load_first10_csv_ids():
        card = library.card(card_id)
        assert card.tooltips, f"{card_id} missing tooltip bindings"
        for tip in card.tooltips:
            assert tip["name"]
            assert tip["tooltip"]
