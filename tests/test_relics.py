from pathlib import Path

from exiled_prince.combat import CombatState
from exiled_prince.event_bus import EventBus
from exiled_prince.relics import register_relics_from_csv


def _load_relics():
    return register_relics_from_csv(Path("design/exiled_prince/relics_v0_1.csv"))


def test_black_seal_grants_start_of_combat_influence_and_order_discount_once_per_combat():
    bus = EventBus()
    state = CombatState(influence=2)
    loadout = _load_relics()
    loadout.bind_all(bus, state)

    bus.emit("CombatStart", {"source_id": "system", "target_id": "player", "tags": []})
    assert state.influence == 3

    first_cost = state.spend_influence(2, bus=bus, tags=["ORDER"])
    assert first_cost == 1
    assert state.influence == 2

    second_cost = state.spend_influence(2, bus=bus, tags=["ORDER"])
    assert second_cost == 2
    assert state.influence == 0


def test_no_duplicate_trigger_firings_when_binding_relics_again():
    bus = EventBus()
    state = CombatState(influence=0)
    loadout = _load_relics()

    loadout.bind_all(bus, state)
    loadout.bind_all(bus, state)

    bus.emit("CombatStart", {"source_id": "system", "target_id": "player", "tags": []})
    assert state.influence == 1


def test_per_turn_and_one_time_relic_effects():
    bus = EventBus()
    state = CombatState(influence=0, energy=3, hp=50, block=0)
    loadout = _load_relics()
    loadout.bind_all(bus, state)

    bus.emit("TurnStart", {"source_id": "system", "target_id": "player", "turn": 1, "tags": []})
    assert state.energy == 5  # Chessmaster Gambit at 0 influence
    assert state.hp == 44

    state.gain_influence(1, bus=bus, turn=1)
    assert state.influence == 2  # Insurgent Badge bonus once on first gain this turn

    state.gain_influence(1, bus=bus, turn=1)
    assert state.influence == 3  # no second bonus on same turn

    bus.emit("TurnStart", {"source_id": "system", "target_id": "player", "turn": 2, "tags": []})
    state.lose_hp(3, bus=bus, tags=["REBELLION"])
    assert state.block == 4  # Mask of Resolve

    state.gain_influence(1, bus=bus, turn=2)
    assert state.influence == 5  # bonus again on new turn
