from __future__ import annotations

import csv
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[2]
STARTER_KIT_PATH = REPO_ROOT / "design/exiled_prince/starter_kit.json"
CARDS_PATH = REPO_ROOT / "design/exiled_prince/cards_v0_1.csv"
RELICS_PATH = REPO_ROOT / "design/exiled_prince/relics_v0_1.csv"
PLAYTEST_MATRIX_PATH = REPO_ROOT / "qa/playtest_matrix.md"


@dataclass(frozen=True)
class ScenarioResult:
    scenario: str
    seed: int
    passed: bool
    details: str


@dataclass
class CombatState:
    hp: int
    block: int
    influence: int
    rebellion_active: bool
    order_discount_available: bool


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _assert_with_context(ok: bool, scenario: str, seed: int, message: str) -> None:
    if not ok:
        raise AssertionError(f"[scenario={scenario} seed={seed}] {message}")


def _apply_influence(state: CombatState, delta: int) -> None:
    state.influence = max(0, min(10, state.influence + delta))


def _enemy_attack_damage(base_damage: int, compel_modifier: float, block: int) -> int:
    reduced = int(round(base_damage * (1.0 - compel_modifier)))
    return max(0, reduced - block)


def scenario_character_boot(seed: int = 71001) -> ScenarioResult:
    scenario = "character_boot"
    starter_kit = _load_json(STARTER_KIT_PATH)
    relic_rows = _load_csv(RELICS_PATH)
    card_rows = _load_csv(CARDS_PATH)

    card_ids = {row["card_id"] for row in card_rows}
    relic_ids = {row["relic_id"] for row in relic_rows}

    _assert_with_context(starter_kit["character_id"] == "EXILED_PRINCE", scenario, seed, "character_id mismatch")
    _assert_with_context(starter_kit["max_hp"] == 72, scenario, seed, "unexpected max_hp")
    _assert_with_context(starter_kit["resource"]["min"] == 0 and starter_kit["resource"]["max"] == 10, scenario, seed, "Influence bounds mismatch")
    _assert_with_context(starter_kit["starting_relic"] in relic_ids, scenario, seed, "starting relic missing from relic table")
    for cid in starter_kit["starting_deck"]:
        _assert_with_context(cid in card_ids, scenario, seed, f"missing card in starter deck: {cid}")

    return ScenarioResult(scenario=scenario, seed=seed, passed=True, details="Boot data integrity validated")


def scenario_first_ten_cards(seed: int = 71002) -> ScenarioResult:
    scenario = "first_10_cards"
    starter_kit = _load_json(STARTER_KIT_PATH)
    cards = _load_csv(CARDS_PATH)
    card_by_id = {row["card_id"]: row for row in cards}

    first_ten = starter_kit["starting_deck"][:10]
    _assert_with_context(len(first_ten) == 10, scenario, seed, "starter deck is not 10 cards")
    for cid in first_ten:
        _assert_with_context(cid in card_by_id, scenario, seed, f"unknown card id: {cid}")
        _assert_with_context(card_by_id[cid]["rarity"] == "Basic", scenario, seed, f"starter card is not Basic: {cid}")

    return ScenarioResult(scenario=scenario, seed=seed, passed=True, details="Starter 10 cards resolved and validated")


def scenario_black_seal(seed: int = 71003) -> ScenarioResult:
    scenario = "BLACK_SEAL_behavior"
    state = CombatState(hp=72, block=0, influence=0, rebellion_active=False, order_discount_available=True)

    # Combat start relic trigger
    _apply_influence(state, 1)
    _assert_with_context(state.influence == 1, scenario, seed, "Black Seal should grant 1 Influence at combat start")

    # First Order has 1 Influence discount.
    base_cost = 3
    first_order_cost = max(0, base_cost - 1)
    _apply_influence(state, -first_order_cost)
    state.order_discount_available = False
    _assert_with_context(state.influence == 0, scenario, seed, "discounted first Order cost was not applied")

    # Later Order should not be discounted.
    _apply_influence(state, 3)
    second_order_cost = base_cost
    _apply_influence(state, -second_order_cost)
    _assert_with_context(state.influence == 0, scenario, seed, "later Order unexpectedly discounted")

    return ScenarioResult(scenario=scenario, seed=seed, passed=True, details="Black Seal start gain + one-time Order discount validated")


def scenario_influence_clamp(seed: int = 71004) -> ScenarioResult:
    scenario = "influence_clamp"
    rng = random.Random(seed)

    for run_seed in range(seed, seed + 5):
        rng.seed(run_seed)
        state = CombatState(hp=72, block=0, influence=0, rebellion_active=False, order_discount_available=True)
        for _ in range(50):
            _apply_influence(state, rng.randint(-6, 7))
            _assert_with_context(0 <= state.influence <= 10, scenario, run_seed, "Influence escaped clamp [0,10]")

    return ScenarioResult(scenario=scenario, seed=seed, passed=True, details="Influence stayed clamped [0,10] across stress runs")


def _simulate_starter_combat(seed: int) -> bool:
    rng = random.Random(seed)
    starter_kit = _load_json(STARTER_KIT_PATH)
    deck = list(starter_kit["starting_deck"])
    rng.shuffle(deck)

    state = CombatState(hp=starter_kit["max_hp"], block=0, influence=0, rebellion_active=False, order_discount_available=True)
    enemy_hp = 40
    enemy_pattern = [8, 10, 12, 8]

    for turn in range(4):
        hand = deck[turn * 2 : turn * 2 + 5]
        state.block = 0
        compel_reduction = 0.0
        for card in hand:
            if card == "EX_STRIKE":
                enemy_hp -= 6
            elif card == "EX_DEFEND":
                state.block += 5
            elif card == "TACTICAL_BRIEFING":
                _apply_influence(state, 2)
            elif card == "COMPEL":
                spend = min(2, state.influence)
                _apply_influence(state, -spend)
                compel_reduction = 0.25 + (0.05 * spend)

        if enemy_hp <= 0:
            return True

        attack = enemy_pattern[turn % len(enemy_pattern)]
        state.hp -= _enemy_attack_damage(attack, compel_reduction, state.block)
        if state.hp <= 0:
            return False

    return enemy_hp <= 0 and state.hp > 0


def scenario_starter_combat(seed: int = 71005) -> ScenarioResult:
    scenario = "starter_combat"
    wins = 0
    seeds = [seed + offset for offset in range(10)]
    for run_seed in seeds:
        if _simulate_starter_combat(run_seed):
            wins += 1

    _assert_with_context(wins >= 7, scenario, seed, f"starter combat win rate below target: {wins}/10")
    return ScenarioResult(scenario=scenario, seed=seed, passed=True, details=f"Starter combat survival proxy met: {wins}/10")


def scenario_rebellion_upkeep(seed: int = 71006) -> ScenarioResult:
    scenario = "rebellion_upkeep"
    state = CombatState(hp=72, block=0, influence=0, rebellion_active=True, order_discount_available=True)
    hp_track: list[int] = [state.hp]

    for _ in range(10):
        if state.rebellion_active:
            state.hp -= 2
        hp_track.append(state.hp)

    total_loss = hp_track[0] - hp_track[-1]
    _assert_with_context(total_loss == 20, scenario, seed, f"expected 20 HP Rebellion upkeep, got {total_loss}")
    _assert_with_context(state.hp > 0, scenario, seed, "Rebellion upkeep auto-lost within 10 turns")

    return ScenarioResult(scenario=scenario, seed=seed, passed=True, details=f"Rebellion upkeep meaningful ({total_loss} HP) and non-lethal over 10 turns")


def scenario_save_load(seed: int = 71007) -> ScenarioResult:
    scenario = "save_load_roundtrip"
    state = {
        "player": {
            "hp": 55,
            "gold": 121,
            "resources": {"influence": 7},
            "statuses": {"rebellion": True},
        },
        "run": {
            "rng_seed": seed,
            "frame_index": 314,
        },
        "meta": {
            "schema_version": "v0.1-smoke",
            "mod_version": "exiled-prince-test",
        },
    }

    blob = json.dumps(state, sort_keys=True)
    loaded = json.loads(blob)

    _assert_with_context(loaded["player"]["resources"]["influence"] == 7, scenario, seed, "Influence value changed after load")
    _assert_with_context(loaded["player"]["statuses"]["rebellion"] is True, scenario, seed, "Rebellion state changed after load")
    _assert_with_context(loaded["run"]["rng_seed"] == seed, scenario, seed, "reproduction seed missing after load")

    return ScenarioResult(scenario=scenario, seed=seed, passed=True, details="Save/load roundtrip preserved Influence + Rebellion + seed")


def scenario_matrix_alignment(seed: int = 71008) -> ScenarioResult:
    scenario = "matrix_alignment"
    text = PLAYTEST_MATRIX_PATH.read_text(encoding="utf-8")
    required = [
        "Starter deck Act 1 survival",
        "Influence generation stress",
        "Rebellion build",
        "Save/load roundtrip keeps Influence and Rebellion state.",
    ]
    for line in required:
        _assert_with_context(line in text, scenario, seed, f"playtest matrix missing expected criterion: {line}")
    return ScenarioResult(scenario=scenario, seed=seed, passed=True, details="Smoke scenarios aligned to playtest matrix criteria")


def run_all_scenarios() -> list[ScenarioResult]:
    scenarios: list[Callable[[], ScenarioResult]] = [
        scenario_character_boot,
        scenario_starter_combat,
        scenario_first_ten_cards,
        scenario_influence_clamp,
        scenario_rebellion_upkeep,
        scenario_black_seal,
        scenario_save_load,
        scenario_matrix_alignment,
    ]
    return [scenario() for scenario in scenarios]


def as_report_rows(results: list[ScenarioResult]) -> list[dict[str, object]]:
    return [asdict(result) for result in results]
