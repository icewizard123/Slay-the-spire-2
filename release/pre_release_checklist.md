# Pre-Release Checklist (Owner + Status)

This tracker consolidates Steam/Nexus publishing readiness with save-compat policy and current implementation status.

| Area | Checklist Item | Owner | Status | Source |
|---|---|---|---|---|
| Versioning | Version bump matches change scope (patch/minor/major). | Release Manager | TODO | `policy/save_compatibility_policy.md` |
| Versioning | Breaking changes flagged with `BREAKING SAVE CHANGE` in title when required. | Release Manager | DONE | `release/release_notes_template.md` |
| Changelog | Dated changelog entry added for this release. | Release Manager | DONE | `CHANGELOG.md` |
| Docs | Install instructions present. | Documentation Owner | DONE | `README.md` |
| Docs | Uninstall instructions present. | Documentation Owner | DONE | `README.md` |
| Docs | Active-run compatibility statement included in release notes. | Documentation Owner | DONE | `release/release_notes_template.md` |
| Docs | Existing-save compatibility statement included in release notes. | Documentation Owner | DONE | `release/release_notes_template.md` |
| Docs | Rollback instructions included in release notes. | Documentation Owner | DONE | `release/release_notes_template.md` |
| Legal/IP | Original or properly licensed assets only. | Art Lead | TODO | `release/steam_nexus_checklist.md` |
| Legal/IP | No ripped franchise assets (logos/voice/screenshot misuse). | Art Lead + Marketing | TODO | `release/steam_nexus_checklist.md` |
| Legal/IP | "Inspired by" wording used instead of official branding claims. | Release Manager | DONE | `release/release_notes_template.md` |
| QA | New run completes without soft-locks. | QA Lead | BLOCKED | `READINESS_REPORT.md` |
| QA | Starter content renders and localizes correctly. | QA Lead + Localization | BLOCKED | `READINESS_REPORT.md` |
| QA | Steam/Nexus descriptions match shipped artifact. | Release Manager | TODO | `release/steam_nexus_checklist.md` |

## Current gate summary
- **Do not publish yet**: implementation and runtime QA gates are still blocked per readiness report.
