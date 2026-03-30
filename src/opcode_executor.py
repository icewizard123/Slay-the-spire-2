from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


PIPELINE_STEPS = [
    "onPlay",
    "target_resolution",
    "cost_and_resource_spend",
    "base_effect_opcode_execution",
    "damage_block_debuff_calculations",
    "reactive_triggers",
    "post_play_hooks",
    "zone_cleanup",
    "end_of_action_state_reconciliation",
]

SUPPORTED_OPS = {
    "DEAL_DAMAGE",
    "GAIN_BLOCK",
    "APPLY_DEBUFF",
    "APPLY_BUFF",
    "GAIN_RESOURCE",
    "SPEND_RESOURCE",
    "DRAW",
    "ENTER_STATE",
}

SPEND_PHASE_OPS = {"SPEND_RESOURCE"}


class OpcodeExecutionError(ValueError):
    """Raised when opcode execution or validation fails."""


@dataclass
class EntityState:
    hp: int = 0
    block: int = 0
    resource: Dict[str, int] = field(default_factory=dict)
    buffs: Dict[str, int] = field(default_factory=dict)
    debuffs: Dict[str, int] = field(default_factory=dict)
    hand_size: int = 0
    statuses: List[str] = field(default_factory=list)


@dataclass
class BattleState:
    actor_id: str
    entities: Dict[str, EntityState]


class OpcodeExecutor:
    def __init__(self, schema_path: str = "architecture/card_data_schema.yaml") -> None:
        self.schema = self._load_schema(schema_path)

    @staticmethod
    def _load_schema(schema_path: str) -> Dict[str, Any]:
        """Minimal schema loader for required keys from card_data_schema.yaml."""
        required: List[str] = []
        in_required = False
        with open(schema_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped == "required:":
                    in_required = True
                    continue
                if in_required:
                    if stripped.startswith("- "):
                        required.append(stripped[2:].strip())
                    elif stripped and not stripped.startswith("#"):
                        break
        return {"required": required}

    def execute_card(
        self,
        card: Dict[str, Any],
        state: BattleState,
        *,
        target_id: Optional[str] = None,
        seed: int = 0,
    ) -> Dict[str, Any]:
        self._validate_card(card)
        actor = self._require_entity(state, state.actor_id)
        target = self._resolve_target(card.get("target"), state, target_id)

        trace: List[Dict[str, Any]] = []
        trace.append({"step": PIPELINE_STEPS[0], "seed": seed, "events": []})
        trace.append(
            {
                "step": PIPELINE_STEPS[1],
                "seed": seed,
                "events": [{"target_id": target_id, "resolved": target is not None}],
            }
        )

        if card.get("cost", 0) > 0:
            self._apply_spend_resource(actor, {"resource": "energy", "amount": card["cost"]}, 0, "CARD_COST")

        spend_ops = [op for op in card["opcodes"] if op["op"] in SPEND_PHASE_OPS]
        base_ops = [op for op in card["opcodes"] if op["op"] not in SPEND_PHASE_OPS]

        cost_events: List[Dict[str, Any]] = []
        for i, opcode in enumerate(spend_ops):
            before = self._snapshot_state(state)
            self._execute_opcode(opcode, state, actor, target, i)
            after = self._snapshot_state(state)
            cost_events.append(self._build_event(opcode["op"], before, after))
        trace.append({"step": PIPELINE_STEPS[2], "seed": seed, "events": cost_events})

        base_events: List[Dict[str, Any]] = []
        for i, opcode in enumerate(base_ops):
            before = self._snapshot_state(state)
            self._execute_opcode(opcode, state, actor, target, i)
            after = self._snapshot_state(state)
            base_events.append(self._build_event(opcode["op"], before, after))
        trace.append({"step": PIPELINE_STEPS[3], "seed": seed, "events": base_events})

        for step in PIPELINE_STEPS[4:]:
            trace.append({"step": step, "seed": seed, "events": []})

        return {"state": state, "trace": trace}

    def _validate_card(self, card: Dict[str, Any]) -> None:
        required = self.schema.get("required", [])
        missing = [field for field in required if field not in card]
        if missing:
            raise OpcodeExecutionError(f"Card definition missing required fields: {missing}")

        if not isinstance(card.get("opcodes"), list):
            raise OpcodeExecutionError("Card opcodes must be a list.")

        for i, opcode in enumerate(card["opcodes"]):
            if not isinstance(opcode, dict):
                raise OpcodeExecutionError(f"Opcode at index {i} must be a mapping.")
            if "op" not in opcode or "args" not in opcode:
                raise OpcodeExecutionError(f"Opcode at index {i} must include 'op' and 'args'.")
            if opcode["op"] not in SUPPORTED_OPS:
                raise OpcodeExecutionError(
                    f"Unsupported opcode '{opcode['op']}' at index {i}. Supported: {sorted(SUPPORTED_OPS)}"
                )
            if not isinstance(opcode["args"], dict):
                raise OpcodeExecutionError(f"Opcode '{opcode['op']}' args at index {i} must be a map/object.")

    def _resolve_target(self, target_mode: str, state: BattleState, target_id: Optional[str]) -> Optional[EntityState]:
        if target_mode in ("Self", "None", None):
            return None
        if target_id is None:
            return None
        return state.entities.get(target_id)

    def _execute_opcode(
        self,
        opcode: Dict[str, Any],
        state: BattleState,
        actor: EntityState,
        target: Optional[EntityState],
        opcode_index: int,
    ) -> None:
        op = opcode["op"]
        args = opcode["args"]
        if op == "DEAL_DAMAGE":
            self._require_args(op, args, {"amount": int})
            target_entity = self._require_target(op, target, opcode_index)
            dmg = args["amount"]
            blocked = min(target_entity.block, dmg)
            target_entity.block -= blocked
            target_entity.hp -= dmg - blocked
        elif op == "GAIN_BLOCK":
            self._require_args(op, args, {"amount": int})
            actor.block += args["amount"]
        elif op == "APPLY_DEBUFF":
            self._require_args(op, args, {"debuff": str, "stacks": int})
            target_entity = self._require_target(op, target, opcode_index)
            key = args["debuff"]
            target_entity.debuffs[key] = target_entity.debuffs.get(key, 0) + args["stacks"]
        elif op == "APPLY_BUFF":
            self._require_args(op, args, {"buff": str, "stacks": int})
            key = args["buff"]
            actor.buffs[key] = actor.buffs.get(key, 0) + args["stacks"]
        elif op == "GAIN_RESOURCE":
            self._require_args(op, args, {"resource": str, "amount": int})
            res = args["resource"]
            actor.resource[res] = actor.resource.get(res, 0) + args["amount"]
        elif op == "SPEND_RESOURCE":
            self._require_args(op, args, {"resource": str, "amount": int})
            self._apply_spend_resource(actor, args, opcode_index, op)
        elif op == "DRAW":
            self._require_args(op, args, {"amount": int})
            actor.hand_size += args["amount"]
        elif op == "ENTER_STATE":
            self._require_args(op, args, {"state": str})
            actor.statuses.append(args["state"])
        else:
            raise OpcodeExecutionError(f"Unhandled opcode '{op}' at index {opcode_index}.")

    def _apply_spend_resource(self, actor: EntityState, args: Dict[str, Any], opcode_index: int, op: str) -> None:
        res = args["resource"]
        amt = args["amount"]
        current = actor.resource.get(res, 0)
        if current < amt:
            raise OpcodeExecutionError(
                f"{op} failed at index {opcode_index}: insufficient '{res}' (need {amt}, have {current})."
            )
        actor.resource[res] = current - amt

    def _require_args(self, op: str, args: Dict[str, Any], expected: Dict[str, type]) -> None:
        for key, arg_type in expected.items():
            if key not in args:
                raise OpcodeExecutionError(f"{op} missing required arg '{key}'.")
            if not isinstance(args[key], arg_type):
                raise OpcodeExecutionError(
                    f"{op} arg '{key}' expected {arg_type.__name__}, got {type(args[key]).__name__}."
                )

    def _require_target(self, op: str, target: Optional[EntityState], opcode_index: int) -> EntityState:
        if target is None:
            raise OpcodeExecutionError(
                f"{op} at index {opcode_index} needs a valid target, but target was missing/invalid."
            )
        return target

    def _require_entity(self, state: BattleState, entity_id: str) -> EntityState:
        if entity_id not in state.entities:
            raise OpcodeExecutionError(f"Missing actor entity '{entity_id}' in battle state.")
        return state.entities[entity_id]

    @staticmethod
    def _snapshot_state(state: BattleState) -> Dict[str, Any]:
        return deepcopy(
            {
                entity_id: {
                    "hp": entity.hp,
                    "block": entity.block,
                    "resource": entity.resource,
                    "buffs": entity.buffs,
                    "debuffs": entity.debuffs,
                    "hand_size": entity.hand_size,
                    "statuses": entity.statuses,
                }
                for entity_id, entity in state.entities.items()
            }
        )

    @staticmethod
    def _build_event(op: str, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        delta: Dict[str, Any] = {}
        for entity_id, before_entity in before.items():
            after_entity = after[entity_id]
            changes = {}
            for key, before_value in before_entity.items():
                if after_entity[key] != before_value:
                    changes[key] = {"before": before_value, "after": after_entity[key]}
            if changes:
                delta[entity_id] = changes
        return {"opcode": op, "state_delta": delta}
