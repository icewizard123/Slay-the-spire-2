from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class ResourceDefinition:
    name: str
    minimum: int
    maximum: int
    start_of_combat: int


@dataclass(frozen=True)
class CharacterLoadout:
    starting_gold: int
    starting_relics: List[str]
    starting_deck: List[str]


@dataclass(frozen=True)
class SelectScreenMetadata:
    display_name: str
    title: str
    flavor_text: str
    portrait_art_ref: str
    shoulder_art_ref: str
    corpse_art_ref: str


@dataclass(frozen=True)
class CharacterDefinition:
    id: str
    max_hp: int
    resource: ResourceDefinition
    loadout: CharacterLoadout
    select_screen: SelectScreenMetadata


@dataclass
class CharacterRegistry:
    _definitions: Dict[str, CharacterDefinition] = field(default_factory=dict)

    def register(self, definition: CharacterDefinition) -> None:
        if definition.id in self._definitions:
            raise ValueError(f"Character already registered: {definition.id}")
        self._definitions[definition.id] = definition

    def get(self, character_id: str) -> CharacterDefinition:
        return self._definitions[character_id]

    def list_character_ids(self) -> List[str]:
        return sorted(self._definitions.keys())
