"""First-pass runtime card bindings for Exiled Prince v0.1 first 10 cards."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any


@dataclass(frozen=True)
class CardDefinition:
    card_id: str
    name: str
    description: str
    card_type: str
    rarity: str
    cost: int
    target: str
    numbers: dict[str, int]
    opcodes: list[dict[str, Any]]
    tooltips: list[dict[str, str]]


class ExiledPrinceCardLibrary:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self._cards = self._load_cards()

    def _load_json(self, relpath: str) -> dict[str, Any]:
        with (self.repo_root / relpath).open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _load_cards(self) -> dict[str, dict[str, Any]]:
        return {
            c["id"]: c
            for c in self._load_json("runtime/exiled_prince/cards_first10_v0_1.json")["cards"]
        }

    def card(self, card_id: str, *, upgraded: bool = False) -> CardDefinition:
        base = self._cards[card_id]
        localization = self._load_json("runtime/exiled_prince/localization_en.cards_first10.json")["cards"]
        keywords = self._load_json("design/shared/keyword_registry.json")

        numbers = dict(base.get("numbers", {}))
        cost = int(base["cost"])
        opcodes = list(base.get("opcodes", []))
        description_lookup_key = card_id

        if upgraded:
            upgrade = base.get("upgrade", {})
            cost += int(upgrade.get("cost_delta", 0))
            for key, delta in upgrade.get("number_deltas", {}).items():
                numbers[key] = int(numbers.get(key, 0)) + int(delta)
            if upgrade.get("opcode_overrides"):
                opcodes = list(upgrade["opcode_overrides"])
            if f"{card_id}+" in localization:
                description_lookup_key = f"{card_id}+"

        description = localization[description_lookup_key]["description"]
        for key, value in numbers.items():
            description = description.replace(f"!{key}!", str(value))

        tooltip_defs = []
        for keyword_id in base.get("tooltips", []):
            if keyword_id not in keywords:
                continue
            tooltip_defs.append(
                {
                    "id": keyword_id,
                    "name": keywords[keyword_id]["name"],
                    "short": keywords[keyword_id]["short"],
                    "tooltip": keywords[keyword_id]["tooltip"],
                }
            )

        return CardDefinition(
            card_id=base["id"],
            name=localization[card_id]["name"],
            description=description,
            card_type=base["type"],
            rarity=base["rarity"],
            cost=cost,
            target=base["target"],
            numbers=numbers,
            opcodes=opcodes,
            tooltips=tooltip_defs,
        )


if __name__ == "__main__":
    lib = ExiledPrinceCardLibrary(Path(__file__).resolve().parents[2])
    for cid in lib._cards:
        print(lib.card(cid).description)
        print(lib.card(cid, upgraded=True).description)
