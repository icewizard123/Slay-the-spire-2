from exiled_prince.status_engine import CombatState, ExiledPrinceStatusEngine


def test_rebellion_non_stack_refreshes_duration_when_reapplied() -> None:
    engine = ExiledPrinceStatusEngine()
    state = CombatState(hp=50)

    engine.apply_rebellion(state, duration_turns=2)
    engine.apply_rebellion(state, duration_turns=5)

    assert state.rebellion_active is True
    assert state.rebellion_turns_remaining == 5


def test_order_bonus_applies_only_while_rebellion_active() -> None:
    engine = ExiledPrinceStatusEngine()
    state = CombatState(hp=50)

    engine.apply_order_bonus(state, 30)
    assert engine.order_potency_multiplier(state) == 1.0

    engine.apply_rebellion(state)
    assert engine.order_potency_multiplier(state) == 1.3


def test_order_bonus_additive_and_capped_at_50_percent() -> None:
    engine = ExiledPrinceStatusEngine()
    state = CombatState(hp=50)

    engine.apply_rebellion(state)
    engine.apply_order_bonus(state, 30)
    engine.apply_order_bonus(state, 30)

    assert state.order_bonus_percent == 50
    assert engine.order_potency_multiplier(state) == 1.5


def test_rebellion_upkeep_triggers_once_per_player_turn() -> None:
    engine = ExiledPrinceStatusEngine()
    state = CombatState(hp=20)
    engine.apply_rebellion(state)

    # Same turn: should only charge once.
    engine.on_end_player_turn(state)
    engine.on_end_player_turn(state)
    assert state.hp == 18

    engine.next_player_turn(state)
    engine.on_end_player_turn(state)
    assert state.hp == 16


def test_order_bonus_decays_on_end_of_combat() -> None:
    engine = ExiledPrinceStatusEngine()
    state = CombatState(hp=20)

    engine.apply_rebellion(state)
    engine.apply_order_bonus(state, 40)
    assert engine.order_potency_multiplier(state) == 1.4

    engine.on_end_combat(state)
    assert state.order_bonus_percent == 0
    assert state.rebellion_active is False
    assert engine.order_potency_multiplier(state) == 1.0


def test_rebellion_duration_decays_from_end_turn_upkeep() -> None:
    engine = ExiledPrinceStatusEngine()
    state = CombatState(hp=20)

    engine.apply_rebellion(state, duration_turns=2)
    engine.on_end_player_turn(state)
    assert state.rebellion_active is True
    assert state.rebellion_turns_remaining == 1

    engine.next_player_turn(state)
    engine.on_end_player_turn(state)
    assert state.rebellion_active is False
    assert state.rebellion_turns_remaining == 0
