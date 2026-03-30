from __future__ import annotations

from dataclasses import dataclass

from .event_bus import EventBus


@dataclass
class CombatState:
    influence: int = 0
    hp: int = 80
    energy: int = 3
    block: int = 0

    def gain_influence(
        self,
        amount: int,
        *,
        bus: EventBus,
        tags: list[str] | None = None,
        turn: int | None = None,
    ) -> int:
        if amount <= 0:
            return 0
        self.influence += amount
        payload = {
            "source_id": "player",
            "target_id": "player",
            "value": amount,
            "tags": tags or [],
        }
        if turn is not None:
            payload["turn"] = turn
        bus.emit("OnInfluenceGained", payload)
        return amount

    def spend_influence(self, amount: int, *, bus: EventBus, tags: list[str] | None = None) -> int:
        requested = max(0, amount)
        mutable_payload = {
            "source_id": "player",
            "target_id": "player",
            "value": requested,
            "tags": list(tags or []),
        }
        bus.emit("BeforeInfluenceSpent", mutable_payload)

        cost = max(0, mutable_payload["value"])
        if self.influence < cost:
            raise ValueError("Not enough Influence")

        self.influence -= cost
        bus.emit(
            "OnInfluenceSpent",
            {
                "source_id": "player",
                "target_id": "player",
                "value": cost,
                "tags": mutable_payload["tags"],
            },
        )
        return cost

    def lose_hp(self, amount: int, *, bus: EventBus, tags: list[str] | None = None) -> int:
        taken = max(0, amount)
        self.hp -= taken
        bus.emit(
            "OnDamageTaken",
            {
                "source_id": "combat",
                "target_id": "player",
                "value": taken,
                "tags": tags or [],
            },
        )
        return taken

    def gain_block(self, amount: int, *, bus: EventBus, tags: list[str] | None = None) -> int:
        gained = max(0, amount)
        self.block += gained
        bus.emit(
            "OnBlockGained",
            {
                "source_id": "combat",
                "target_id": "player",
                "value": gained,
                "tags": tags or [],
            },
        )
        return gained

    def gain_energy(self, amount: int) -> int:
        gained = max(0, amount)
        self.energy += gained
        return gained
