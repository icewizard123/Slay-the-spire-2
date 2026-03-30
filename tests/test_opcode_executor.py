import pytest

from opcode_executor import BattleState, EntityState, OpcodeExecutionError, OpcodeExecutor


def mk_state() -> BattleState:
    return BattleState(
        actor_id="player",
        entities={
            "player": EntityState(hp=50, block=0, resource={"energy": 3, "mana": 2}),
            "enemy": EntityState(hp=40, block=5),
        },
    )


def mk_card(op: str, args: dict, *, target: str = "Enemy", cost: int = 0) -> dict:
    return {
        "id": "TEST_CARD",
        "name_key": "test.card",
        "type": "Attack",
        "rarity": "Basic",
        "cost": cost,
        "target": target,
        "opcodes": [{"op": op, "args": args}],
    }


def test_deal_damage_opcode():
    state = mk_state()
    card = mk_card("DEAL_DAMAGE", {"amount": 10})
    result = OpcodeExecutor().execute_card(card, state, target_id="enemy", seed=123)
    assert result["state"].entities["enemy"].hp == 35
    assert result["state"].entities["enemy"].block == 0


def test_gain_block_opcode():
    state = mk_state()
    card = mk_card("GAIN_BLOCK", {"amount": 7}, target="Self")
    OpcodeExecutor().execute_card(card, state, seed=1)
    assert state.entities["player"].block == 7


def test_apply_debuff_opcode():
    state = mk_state()
    card = mk_card("APPLY_DEBUFF", {"debuff": "weak", "stacks": 2})
    OpcodeExecutor().execute_card(card, state, target_id="enemy", seed=2)
    assert state.entities["enemy"].debuffs["weak"] == 2


def test_apply_buff_opcode():
    state = mk_state()
    card = mk_card("APPLY_BUFF", {"buff": "strength", "stacks": 2}, target="Self")
    OpcodeExecutor().execute_card(card, state, seed=2)
    assert state.entities["player"].buffs["strength"] == 2


def test_gain_resource_opcode():
    state = mk_state()
    card = mk_card("GAIN_RESOURCE", {"resource": "mana", "amount": 3}, target="Self")
    OpcodeExecutor().execute_card(card, state, seed=2)
    assert state.entities["player"].resource["mana"] == 5


def test_spend_resource_opcode_in_cost_phase():
    state = mk_state()
    card = mk_card("SPEND_RESOURCE", {"resource": "mana", "amount": 2}, target="Self", cost=1)
    result = OpcodeExecutor().execute_card(card, state, seed=9)
    assert state.entities["player"].resource["energy"] == 2
    assert state.entities["player"].resource["mana"] == 0
    assert result["trace"][2]["step"] == "cost_and_resource_spend"
    assert result["trace"][2]["events"][0]["opcode"] == "SPEND_RESOURCE"


def test_draw_opcode():
    state = mk_state()
    card = mk_card("DRAW", {"amount": 2}, target="Self")
    OpcodeExecutor().execute_card(card, state, seed=2)
    assert state.entities["player"].hand_size == 2


def test_enter_state_opcode():
    state = mk_state()
    card = mk_card("ENTER_STATE", {"state": "STEALTH"}, target="Self")
    OpcodeExecutor().execute_card(card, state, seed=2)
    assert "STEALTH" in state.entities["player"].statuses


def test_invalid_opcode_fails_gracefully():
    state = mk_state()
    card = mk_card("BOOM", {"amount": 1})
    with pytest.raises(OpcodeExecutionError, match="Unsupported opcode 'BOOM'"):
        OpcodeExecutor().execute_card(card, state, target_id="enemy", seed=3)


def test_invalid_args_fails_gracefully():
    state = mk_state()
    card = mk_card("DEAL_DAMAGE", {"amount": "bad"})
    with pytest.raises(OpcodeExecutionError, match="expected int"):
        OpcodeExecutor().execute_card(card, state, target_id="enemy", seed=3)


def test_deterministic_output_for_same_seed_and_state():
    card = {
        "id": "TEST_CARD",
        "name_key": "test.card",
        "type": "Attack",
        "rarity": "Basic",
        "cost": 1,
        "target": "Enemy",
        "opcodes": [
            {"op": "SPEND_RESOURCE", "args": {"resource": "mana", "amount": 1}},
            {"op": "DEAL_DAMAGE", "args": {"amount": 6}},
            {"op": "APPLY_DEBUFF", "args": {"debuff": "vuln", "stacks": 1}},
        ],
    }

    e = OpcodeExecutor()
    s1 = mk_state()
    s2 = mk_state()
    r1 = e.execute_card(card, s1, target_id="enemy", seed=777)
    r2 = e.execute_card(card, s2, target_id="enemy", seed=777)

    assert r1["trace"] == r2["trace"]
    assert s1.entities["enemy"].hp == s2.entities["enemy"].hp
    assert s1.entities["enemy"].debuffs == s2.entities["enemy"].debuffs


def test_trace_contains_opcode_and_state_delta():
    state = mk_state()
    card = mk_card("GAIN_BLOCK", {"amount": 4}, target="Self")
    result = OpcodeExecutor().execute_card(card, state, seed=4)
    events = result["trace"][3]["events"]
    assert events[0]["opcode"] == "GAIN_BLOCK"
    assert "state_delta" in events[0]
    assert events[0]["state_delta"]["player"]["block"]["after"] == 4
