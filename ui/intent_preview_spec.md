# Enemy Intent Preview Spec

## Goals
- Show exact expected values for intent outcomes whenever deterministic.
- Surface all applied modifiers (Weak, Vulnerable, Strength, relic modifiers, etc.).
- Clearly distinguish deterministic vs unknown/random intents.

## Display rules
1. Deterministic attack intent displays:
   - Base damage
   - Modifier breakdown
   - Final damage per hit and hit count
2. Buff/debuff intents display:
   - A concise effect summary with stack counts.
3. Multi-action intents display actions in execution order.

## Unknown/random intents
- Use a dedicated icon set (`INTENT_UNKNOWN`, `INTENT_RANDOM_ATTACK`, etc.).
- Tooltip text must explicitly state uncertainty source:
  - "Intent depends on random roll"
  - "Intent hidden by status effect"

## UX details
- Hover tooltip includes formula preview, e.g.:
  `Final Damage = floor((Base + Strength) * WeakMultiplier * OtherModifiers)`
- Color coding:
  - Red: attack components
  - Purple: debuff components
  - Green: buff/defense components
- If value range exists, show min/max (e.g., `6-12`).

## QA acceptance criteria
- Damage shown matches executed damage in 100 sampled combats.
- Unknown intent icon never appears for deterministic intents.
- Tooltip updates live when mid-turn modifiers change.
