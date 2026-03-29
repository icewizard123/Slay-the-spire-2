from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from runtime.character_registry import (
    CharacterDefinition,
    CharacterLoadout,
    CharacterRegistry,
    ResourceDefinition,
    SelectScreenMetadata,
)

EXILED_PRINCE_CHARACTER_ID = "EX_CHAR_EXILED_PRINCE"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def _to_card_id(card_short_id: str) -> str:
    return f"EX_CARD_{card_short_id}"


def _to_relic_id(relic_short_id: str) -> str:
    return f"EX_RELIC_{relic_short_id}"


def build_exiled_prince_definition(
    starter_kit_path: Path | None = None,
    art_refs_path: Path | None = None,
) -> CharacterDefinition:
    root = _project_root()
    starter_kit_path = starter_kit_path or root / "design" / "exiled_prince" / "starter_kit.json"
    art_refs_path = art_refs_path or root / "assets" / "placeholders" / "exiled_prince_art_refs.json"

    starter_kit = _load_json(starter_kit_path)
    art_refs = _load_json(art_refs_path)

    loadout = CharacterLoadout(
        starting_gold=starter_kit["starting_gold"],
        starting_relics=[_to_relic_id(starter_kit["starting_relic"])],
        starting_deck=[_to_card_id(card_id) for card_id in starter_kit["starting_deck"]],
    )

    select_screen = SelectScreenMetadata(
        display_name=starter_kit["display_name"],
        title="The Dispossessed Strategist",
        flavor_text="A banished heir who bends the battlefield through command.",
        portrait_art_ref=art_refs["portrait"],
        shoulder_art_ref=art_refs["shoulder"],
        corpse_art_ref=art_refs["corpse"],
    )

    return CharacterDefinition(
        id=EXILED_PRINCE_CHARACTER_ID,
        max_hp=starter_kit["max_hp"],
        resource=ResourceDefinition(
            name=starter_kit["resource"]["name"],
            minimum=starter_kit["resource"]["min"],
            maximum=starter_kit["resource"]["max"],
            start_of_combat=starter_kit["resource"]["start_of_combat"],
        ),
        loadout=loadout,
        select_screen=select_screen,
    )


def register_exiled_prince(registry: CharacterRegistry) -> CharacterDefinition:
    definition = build_exiled_prince_definition()
    registry.register(definition)
    return definition


def bootstrap_default_registry() -> CharacterRegistry:
    registry = CharacterRegistry()
    register_exiled_prince(registry)
    return registry


if __name__ == "__main__":
    registry = bootstrap_default_registry()
    print("Registered characters:", ", ".join(registry.list_character_ids()))
