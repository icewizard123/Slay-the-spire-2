from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import math
from typing import Any, Dict, List, Optional, Tuple


INTENT_ICONS = {
    "ATTACK": "INTENT_ATTACK",
    "BUFF": "INTENT_BUFF",
    "DEBUFF": "INTENT_DEBUFF",
    "UNKNOWN": "INTENT_UNKNOWN",
    "RANDOM_ATTACK": "INTENT_RANDOM_ATTACK",
}


@dataclass(frozen=True)
class ModifierState:
    attacker_strength: int = 0
    attacker_weak_multiplier: float = 1.0
    defender_vulnerable_multiplier: float = 1.0
    other_multiplier: float = 1.0


@dataclass(frozen=True)
class AttackIntent:
    base_damage: int
    hits: int = 1
    random_roll: bool = False
    hidden_by_status: bool = False
    range_damage: Optional[Tuple[int, int]] = None


@dataclass(frozen=True)
class EffectIntent:
    effect_type: str
    effect_name: str
    stacks: int


@dataclass(frozen=True)
class IntentPreview:
    icon: str
    deterministic: bool
    summary: str
    tooltip: str
    formula: Optional[str] = None
    damage_per_hit: Optional[int] = None
    total_damage: Optional[int] = None
    damage_range_per_hit: Optional[Tuple[int, int]] = None
    actions: List[Dict[str, Any]] = field(default_factory=list)


class IntentPreviewEngine:
    """
    Recomputes preview values from current modifier state on every call.
    That provides live updates whenever combat modifiers change.
    """

    def __init__(self, keyword_registry_path: str = "design/shared/keyword_registry.json") -> None:
        self.keyword_registry = self._load_registry(keyword_registry_path)

    @staticmethod
    def _load_registry(path: str) -> Dict[str, Any]:
        p = Path(path)
        if not p.exists():
            return {}
        return json.loads(p.read_text(encoding="utf-8"))

    def preview_attack(self, intent: AttackIntent, modifiers: ModifierState) -> IntentPreview:
        deterministic = not intent.random_roll and not intent.hidden_by_status

        if not deterministic:
            if intent.random_roll:
                icon = INTENT_ICONS["RANDOM_ATTACK"]
                uncertainty = "Intent depends on random roll"
            else:
                icon = INTENT_ICONS["UNKNOWN"]
                uncertainty = "Intent hidden by status effect"

            tooltip = f"{uncertainty}. Values are shown as unknown until resolved."
            return IntentPreview(
                icon=icon,
                deterministic=False,
                summary="?",
                tooltip=tooltip,
            )

        icon = INTENT_ICONS["ATTACK"]
        formula = (
            "Final Damage = floor((Base + Strength) * WeakMultiplier * "
            "VulnerableMultiplier * OtherModifiers)"
        )

        if intent.range_damage is not None:
            min_damage = self._compute_final_damage(intent.range_damage[0], modifiers)
            max_damage = self._compute_final_damage(intent.range_damage[1], modifiers)
            summary = f"{min_damage}-{max_damage} x{intent.hits}"
            tooltip = (
                f"Range intent. Per-hit damage range: {min_damage}-{max_damage}. "
                f"Hit count: {intent.hits}."
            )
            return IntentPreview(
                icon=icon,
                deterministic=True,
                summary=summary,
                tooltip=tooltip,
                formula=formula,
                damage_range_per_hit=(min_damage, max_damage),
                total_damage=max_damage * intent.hits,
            )

        per_hit = self._compute_final_damage(intent.base_damage, modifiers)
        total = per_hit * intent.hits
        breakdown = self._modifier_breakdown(intent.base_damage, modifiers)
        summary = f"{per_hit} x{intent.hits}"
        tooltip = (
            f"{breakdown}. {formula}. Total damage if all hits land: {total}."
        )
        return IntentPreview(
            icon=icon,
            deterministic=True,
            summary=summary,
            tooltip=tooltip,
            formula=formula,
            damage_per_hit=per_hit,
            total_damage=total,
        )

    def preview_effect(self, intent: EffectIntent) -> IntentPreview:
        color_by_type = {
            "BUFF": "green",
            "DEBUFF": "purple",
        }
        icon = INTENT_ICONS.get(intent.effect_type, INTENT_ICONS["DEBUFF"])
        summary = f"{intent.effect_name} {intent.stacks}"
        registry_key = intent.effect_name.upper()
        registry_text = self.keyword_registry.get(registry_key, {}).get("tooltip")
        tooltip = registry_text or f"Applies {intent.effect_name} for {intent.stacks} stacks."
        return IntentPreview(
            icon=icon,
            deterministic=True,
            summary=summary,
            tooltip=f"[{color_by_type.get(intent.effect_type, 'purple')}] {tooltip}",
        )

    def preview_multi_action(
        self,
        attack_intent: Optional[AttackIntent],
        effect_intents: List[EffectIntent],
        modifiers: ModifierState,
    ) -> IntentPreview:
        actions: List[Dict[str, Any]] = []
        summary_chunks: List[str] = []

        if attack_intent is not None:
            attack_preview = self.preview_attack(attack_intent, modifiers)
            actions.append({"type": "ATTACK", "summary": attack_preview.summary})
            summary_chunks.append(attack_preview.summary)

        for effect in effect_intents:
            effect_preview = self.preview_effect(effect)
            actions.append({"type": effect.effect_type, "summary": effect_preview.summary})
            summary_chunks.append(effect_preview.summary)

        return IntentPreview(
            icon=INTENT_ICONS["ATTACK"] if attack_intent else INTENT_ICONS["BUFF"],
            deterministic=all("?" not in chunk for chunk in summary_chunks),
            summary=" -> ".join(summary_chunks),
            tooltip="Actions resolve in listed order.",
            actions=actions,
        )

    @staticmethod
    def _compute_final_damage(base: int, modifiers: ModifierState) -> int:
        return math.floor(
            (base + modifiers.attacker_strength)
            * modifiers.attacker_weak_multiplier
            * modifiers.defender_vulnerable_multiplier
            * modifiers.other_multiplier
        )

    @staticmethod
    def _modifier_breakdown(base: int, modifiers: ModifierState) -> str:
        return (
            f"Base={base}, Strength={modifiers.attacker_strength}, "
            f"WeakMultiplier={modifiers.attacker_weak_multiplier}, "
            f"VulnerableMultiplier={modifiers.defender_vulnerable_multiplier}, "
            f"OtherModifiers={modifiers.other_multiplier}"
        )


__all__ = [
    "AttackIntent",
    "EffectIntent",
    "IntentPreview",
    "IntentPreviewEngine",
    "ModifierState",
    "INTENT_ICONS",
]
