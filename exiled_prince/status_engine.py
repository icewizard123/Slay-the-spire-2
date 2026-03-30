from __future__ import annotations

from dataclasses import dataclass
import csv
from pathlib import Path
from typing import Optional


CATALOG_PATH = Path(__file__).resolve().parents[1] / "design" / "exiled_prince" / "status_effects_catalog.csv"


@dataclass(frozen=True)
class StatusSpec:
    status_id: str
    stacking_rule: str
    decay_timing: str
    balance_guardrail: str


@dataclass
class CombatState:
    hp: int
    rebellion_active: bool = False
    rebellion_turns_remaining: Optional[int] = None
    rebellion_upkeep_hp_loss: int = 2
    order_bonus_percent: int = 0
    player_turn: int = 0
    _last_rebellion_upkeep_turn: Optional[int] = None


class ExiledPrinceStatusEngine:
    """Reference implementation for Rebellion/Order interaction semantics."""

    def __init__(self, catalog_path: Path = CATALOG_PATH):
        self.specs = self._load_specs(catalog_path)

    @staticmethod
    def _load_specs(catalog_path: Path) -> dict[str, StatusSpec]:
        specs: dict[str, StatusSpec] = {}
        with catalog_path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                specs[row["status_id"]] = StatusSpec(
                    status_id=row["status_id"],
                    stacking_rule=row["stacking_rule"],
                    decay_timing=row["decay_timing"],
                    balance_guardrail=row["balance_guardrail"],
                )
        return specs

    def apply_rebellion(self, state: CombatState, duration_turns: Optional[int] = None) -> None:
        spec = self.specs["EX_POWER_REBELLION"]
        if "Non-stack" not in spec.stacking_rule:
            raise ValueError("Catalog mismatch: Rebellion must be non-stacking")

        state.rebellion_active = True

        # Non-stack + refresh duration when explicit duration is supplied.
        if duration_turns is not None:
            state.rebellion_turns_remaining = duration_turns

    def apply_order_bonus(self, state: CombatState, bonus_percent: int) -> None:
        spec = self.specs["EX_BUFF_ORDER_BONUS"]
        if "Additive" not in spec.stacking_rule:
            raise ValueError("Catalog mismatch: Order bonus must stack additively")

        state.order_bonus_percent += bonus_percent
        # Guardrail from catalog: cap at +50% total.
        state.order_bonus_percent = min(state.order_bonus_percent, 50)

    def order_potency_multiplier(self, state: CombatState) -> float:
        # Bonus applies only while Rebellion is active.
        if not state.rebellion_active:
            return 1.0
        return 1.0 + (state.order_bonus_percent / 100.0)

    def on_end_player_turn(self, state: CombatState) -> None:
        # Upkeep triggers once per player turn while Rebellion is active.
        if not state.rebellion_active:
            return

        if state._last_rebellion_upkeep_turn == state.player_turn:
            return

        state.hp -= state.rebellion_upkeep_hp_loss
        state._last_rebellion_upkeep_turn = state.player_turn

        if state.rebellion_turns_remaining is not None:
            state.rebellion_turns_remaining -= 1
            if state.rebellion_turns_remaining <= 0:
                state.rebellion_active = False
                state.rebellion_turns_remaining = 0

    def next_player_turn(self, state: CombatState) -> None:
        state.player_turn += 1

    def on_end_combat(self, state: CombatState) -> None:
        # Catalog decay timing for Order Potency: end of combat.
        state.order_bonus_percent = 0
        state.rebellion_active = False
        state.rebellion_turns_remaining = None
        state._last_rebellion_upkeep_turn = None
