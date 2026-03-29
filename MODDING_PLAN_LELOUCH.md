# Slay the Spire 2 Mod Plan: "The Exiled Prince" (Lelouch-Inspired Character)

This plan is designed for publishing on **Steam Workshop** and **Nexus Mods**.
It is inspired by Lelouch (Code Geass) while avoiding direct copyrighted names/assets.

## 1) Character fantasy and identity

**Working name:** The Exiled Prince  
**Core mechanic theme:** Commands, tactics, and sacrifice.

### Design pillars
- **Command over force:** You issue "Orders" that alter enemy behavior or buff allies.
- **Calculated sacrifice:** Trade HP/resources now to secure bigger future turns.
- **Win by setup:** Strong payoff turns after sequencing multiple setup cards.

## 2) Unique mechanics (mod-friendly)

## A. Order cards (new card tag)
- Cards with `Order` tag apply temporary control effects.
- Examples:
  - "Compel": Enemy deals reduced damage next turn.
  - "Kneel": Enemy gains Vulnerable but you lose Block.

## B. Influence resource (secondary meter)
- Starts at 0, capped (e.g., 10).
- Gain from Skills/Powers; spend on high-impact Commands.
- Keeps turns tactical rather than pure energy scaling.

## C. Rebellion stance-like state
- Entered by specific cards/relics.
- While active: stronger Orders, but negative upkeep (lose HP/Block each turn).

## 3) Starter kit (suggested)

- 4x Strike-equivalent
- 4x Defend-equivalent
- 1x low-cost Influence generator
- 1x basic Order card

**Starter relic idea:** "Black Seal"  
At combat start, gain 1 Influence. First `Order` each combat costs 1 less Influence.

## 4) Card pool blueprint (first pass)

Target ~55 cards for v0.1:
- 20 Attacks
- 20 Skills
- 12 Powers
- 3 Colorless-compatible character cards

Rarity split (example):
- Common: 26
- Uncommon: 18
- Rare: 11

## 5) Artifact/content checklist

Create original assets only:
- Character portrait + shoulder image
- Card frames/icons for Influence + Order tag
- Orb/resource UI (if needed by API)
- 75x75 relic art
- Event option icons

Avoid copyrighted material from anime:
- No direct Lelouch face art, logos, screenshots, soundtrack clips, or ripped voice lines.
- Use "inspired by" language and original naming.

## 6) Steam Workshop + Nexus packaging checklist

- Keep semantic versioning (`0.1.0`, `0.1.1`, ...).
- Include clear dependency list in description.
- Add changelog and known issues.
- Include uninstall notes and save compatibility warning.
- Add credits/licenses for all third-party tools/fonts.

## 7) Playtest & balance loop

Track these metrics over 20+ runs:
- Win rate by ascension/difficulty
- Average turn damage in Act 1 / 2 / 3
- Dead draws and hand clog frequency
- Infinite/combo abuse cases

Patch priorities:
1. Unfun patterns (hard locks, degenerate loops)
2. Broken synergies
3. Underpicked cards/relics

## 8) 2-week implementation roadmap

### Week 1
- Character registration + select screen + animations
- Starter deck/relic
- 20 basic cards + 5 relics
- Influence meter UI

### Week 2
- Remaining cards/relics
- VFX/SFX placeholders
- Tooltips, localization, keywords
- QA pass + Workshop/Nexus publish pipeline

## 9) Safe naming set (recommended)

- Character: The Exiled Prince
- Keywords: Order, Influence, Rebellion
- Relics: Black Seal, Mask of Resolve, Zero Oath (optional)

## 10) Immediate next actions

1. Set up a minimal mod project skeleton.
2. Implement character registration + starter deck.
3. Add 10 commons (5 attack, 5 skill) and 1 resource system.
4. Internal playtest for crash safety and basic balance.
