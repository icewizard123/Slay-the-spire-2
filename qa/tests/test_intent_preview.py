import random
import unittest

from ui.intent_preview import (
    AttackIntent,
    EffectIntent,
    INTENT_ICONS,
    IntentPreviewEngine,
    ModifierState,
)


class IntentPreviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = IntentPreviewEngine()

    def test_preview_damage_matches_execution_for_sampled_combats(self) -> None:
        rng = random.Random(42)
        for _ in range(100):
            base = rng.randint(4, 20)
            hits = rng.randint(1, 4)
            strength = rng.randint(-2, 6)
            weak_mult = rng.choice([0.75, 1.0])
            vuln_mult = rng.choice([1.0, 1.5])
            other_mult = rng.choice([1.0, 1.1, 1.25])

            modifiers = ModifierState(
                attacker_strength=strength,
                attacker_weak_multiplier=weak_mult,
                defender_vulnerable_multiplier=vuln_mult,
                other_multiplier=other_mult,
            )
            intent = AttackIntent(base_damage=base, hits=hits)
            preview = self.engine.preview_attack(intent, modifiers)

            executed = int((base + strength) * weak_mult * vuln_mult * other_mult)
            self.assertEqual(preview.damage_per_hit, executed)
            self.assertEqual(preview.total_damage, executed * hits)

    def test_unknown_icon_only_used_for_uncertain_intents(self) -> None:
        deterministic = self.engine.preview_attack(
            AttackIntent(base_damage=10, hits=1),
            ModifierState(attacker_strength=2),
        )
        random_unknown = self.engine.preview_attack(
            AttackIntent(base_damage=10, random_roll=True),
            ModifierState(),
        )
        hidden_unknown = self.engine.preview_attack(
            AttackIntent(base_damage=10, hidden_by_status=True),
            ModifierState(),
        )

        self.assertEqual(deterministic.icon, INTENT_ICONS["ATTACK"])
        self.assertNotEqual(deterministic.icon, INTENT_ICONS["UNKNOWN"])
        self.assertEqual(random_unknown.icon, INTENT_ICONS["RANDOM_ATTACK"])
        self.assertEqual(hidden_unknown.icon, INTENT_ICONS["UNKNOWN"])

    def test_multi_hit_and_range_render_correctly(self) -> None:
        multi = self.engine.preview_attack(
            AttackIntent(base_damage=8, hits=3),
            ModifierState(attacker_strength=2),
        )
        self.assertEqual(multi.summary, "10 x3")

        ranged = self.engine.preview_attack(
            AttackIntent(base_damage=0, hits=2, range_damage=(6, 12)),
            ModifierState(attacker_strength=1),
        )
        self.assertEqual(ranged.summary, "7-13 x2")
        self.assertEqual(ranged.damage_range_per_hit, (7, 13))

    def test_live_update_reflects_modifier_changes(self) -> None:
        intent = AttackIntent(base_damage=10, hits=1)
        initial = self.engine.preview_attack(intent, ModifierState(attacker_strength=0))
        updated = self.engine.preview_attack(intent, ModifierState(attacker_strength=3))
        self.assertEqual(initial.damage_per_hit, 10)
        self.assertEqual(updated.damage_per_hit, 13)

    def test_effect_tooltip_uses_keyword_registry(self) -> None:
        weak = self.engine.preview_effect(EffectIntent("DEBUFF", "WEAK", 2))
        self.assertIn("Weak reduces attack damage", weak.tooltip)


if __name__ == "__main__":
    unittest.main()
