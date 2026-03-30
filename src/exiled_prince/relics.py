from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .combat import CombatState
from .event_bus import EventBus


class Relic:
    relic_id: str

    def bind(self, bus: EventBus, state: CombatState) -> None:
        raise NotImplementedError

    def on_combat_start(self, bus: EventBus, state: CombatState) -> None:
        """Optional eager effects for combat start."""


@dataclass
class BlackSeal(Relic):
    relic_id: str = "BLACK_SEAL"
    used_discount_this_combat: bool = False

    def bind(self, bus: EventBus, state: CombatState) -> None:
        bus.subscribe("CombatStart", owner=self.relic_id, handler=lambda e: self._combat_start(e, bus, state), priority=100)
        bus.subscribe("BeforeInfluenceSpent", owner=self.relic_id, handler=lambda e: self._discount_order_once(e), priority=100)

    def _combat_start(self, _event: dict, bus: EventBus, state: CombatState) -> None:
        self.used_discount_this_combat = False
        state.gain_influence(1, bus=bus, tags=[self.relic_id, "COMBAT_START"])

    def _discount_order_once(self, event: dict) -> None:
        tags = event.get("tags", [])
        if self.used_discount_this_combat:
            return
        if "ORDER" not in tags:
            return
        event["value"] = max(0, int(event.get("value", 0)) - 1)
        tags.append("BLACK_SEAL_DISCOUNT")
        self.used_discount_this_combat = True


@dataclass
class MaskOfResolve(Relic):
    relic_id: str = "MASK_OF_RESOLVE"

    def bind(self, bus: EventBus, state: CombatState) -> None:
        bus.subscribe("OnDamageTaken", owner=self.relic_id, handler=lambda e: self._on_damage_taken(e, bus, state), priority=50)

    def _on_damage_taken(self, event: dict, bus: EventBus, state: CombatState) -> None:
        if "REBELLION" in event.get("tags", []):
            state.gain_block(4, bus=bus, tags=[self.relic_id])


@dataclass
class InsurgentBadge(Relic):
    relic_id: str = "INSURGENT_BADGE"
    current_turn: int | None = None
    bonus_granted_turn: int | None = None

    def bind(self, bus: EventBus, state: CombatState) -> None:
        bus.subscribe("TurnStart", owner=self.relic_id, handler=self._on_turn_start, priority=100)
        bus.subscribe("OnInfluenceGained", owner=self.relic_id, handler=lambda e: self._on_influence_gained(e, bus, state), priority=40)

    def _on_turn_start(self, event: dict) -> None:
        self.current_turn = event.get("turn")

    def _on_influence_gained(self, event: dict, bus: EventBus, state: CombatState) -> None:
        turn = event.get("turn", self.current_turn)
        if turn is None:
            return
        if self.bonus_granted_turn == turn:
            return
        if "INSURGENT_BADGE_BONUS" in event.get("tags", []):
            return
        self.bonus_granted_turn = turn
        state.gain_influence(1, bus=bus, tags=[self.relic_id, "INSURGENT_BADGE_BONUS", f"TURN_{turn}"])


@dataclass
class ChessmasterGambit(Relic):
    relic_id: str = "CHESSMASTER_GAMBIT"

    def bind(self, bus: EventBus, state: CombatState) -> None:
        bus.subscribe("TurnStart", owner=self.relic_id, handler=lambda e: self._on_turn_start(e, bus, state), priority=30)

    def _on_turn_start(self, event: dict, bus: EventBus, state: CombatState) -> None:
        if state.influence == 0:
            state.gain_energy(2)
            state.lose_hp(6, bus=bus, tags=[self.relic_id, "SELF_DAMAGE"])


RELIC_REGISTRY: dict[str, Callable[[], Relic]] = {
    "BLACK_SEAL": BlackSeal,
    "MASK_OF_RESOLVE": MaskOfResolve,
    "INSURGENT_BADGE": InsurgentBadge,
    "CHESSMASTER_GAMBIT": ChessmasterGambit,
}


@dataclass
class RelicLoadout:
    relics: list[Relic] = field(default_factory=list)

    def bind_all(self, bus: EventBus, state: CombatState) -> None:
        for relic in self.relics:
            relic.bind(bus, state)


def register_relics_from_csv(csv_path: str | Path) -> RelicLoadout:
    csv_path = Path(csv_path)
    relics: list[Relic] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            relic_id = row["relic_id"]
            if relic_id not in RELIC_REGISTRY:
                raise KeyError(f"Missing relic implementation for {relic_id}")
            relics.append(RELIC_REGISTRY[relic_id]())
    return RelicLoadout(relics)
