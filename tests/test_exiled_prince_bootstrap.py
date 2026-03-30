from pathlib import Path

from runtime.character_registry import CharacterRegistry
from runtime.exiled_prince_bootstrap import (
    EXILED_PRINCE_CHARACTER_ID,
    build_exiled_prince_definition,
    register_exiled_prince,
)


def test_character_registration_and_select_screen_metadata() -> None:
    registry = CharacterRegistry()
    definition = register_exiled_prince(registry)

    assert definition.id == EXILED_PRINCE_CHARACTER_ID
    assert registry.get(EXILED_PRINCE_CHARACTER_ID) == definition
    assert definition.select_screen.display_name == "The Exiled Prince"
    assert definition.select_screen.portrait_art_ref.startswith("placeholder://")


def test_starter_deck_and_relic_match_starter_kit() -> None:
    definition = build_exiled_prince_definition()

    assert definition.loadout.starting_relics == ["EX_RELIC_BLACK_SEAL"]
    assert definition.loadout.starting_deck == [
        "EX_CARD_EX_STRIKE",
        "EX_CARD_EX_STRIKE",
        "EX_CARD_EX_STRIKE",
        "EX_CARD_EX_STRIKE",
        "EX_CARD_EX_DEFEND",
        "EX_CARD_EX_DEFEND",
        "EX_CARD_EX_DEFEND",
        "EX_CARD_EX_DEFEND",
        "EX_CARD_TACTICAL_BRIEFING",
        "EX_CARD_COMPEL",
    ]


def test_bootstrap_is_stable_for_first_combat_entry_contract() -> None:
    definition = build_exiled_prince_definition()

    assert definition.max_hp == 72
    assert definition.resource.name == "Influence"
    assert definition.resource.minimum == 0
    assert definition.resource.maximum == 10
    assert definition.resource.start_of_combat == 0


def test_paths_resolve_from_repo_root() -> None:
    definition = build_exiled_prince_definition(
        starter_kit_path=Path("design/exiled_prince/starter_kit.json"),
        art_refs_path=Path("assets/placeholders/exiled_prince_art_refs.json"),
    )
    assert definition.id == EXILED_PRINCE_CHARACTER_ID
