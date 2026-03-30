# Exiled Prince (Slay the Spire 2 Mod Concept)

This repository currently contains design, architecture, and release-process artifacts for the **Exiled Prince** custom character project.

> Current state: not yet playable. See `READINESS_REPORT.md` for implementation blockers and release gate criteria.

## Install (for packaged release builds)

When release artifacts are published to Steam Workshop and Nexus Mods:

1. Download/subscribe to the release matching your game build.
2. Verify dependency and load-order notes from the release page.
3. Launch the game and confirm the mod appears in the mod list (if applicable).
4. Start a **new run** after install for the safest compatibility behavior.

## Uninstall

1. Exit the game completely.
2. Unsubscribe/remove the mod package from Steam Workshop or Nexus Mods.
3. Remove any local override files created for manual installs (if used).
4. Relaunch the game.

### Save safety warning

- Removing the mod during an **active run** can invalidate that run.
- Existing profile saves are expected to remain safe unless a release is explicitly marked as breaking.
- Always check the release notes compatibility statement before installing/removing mid-campaign.

## Compatibility Notes

- **Active run compatibility:** Must be declared in each release note.
- **Existing save-file compatibility:** Must be declared in each release note.
- If a release is breaking, it is labeled `BREAKING SAVE CHANGE` and includes rollback guidance.

See:
- `policy/save_compatibility_policy.md`
- `release/release_notes_template.md`
- `release/pre_release_checklist.md`

## Reporting issues

Include:
- Release version
- Platform/store source (Steam/Nexus/manual)
- Reproduction steps
- Log/crash file location and excerpt
