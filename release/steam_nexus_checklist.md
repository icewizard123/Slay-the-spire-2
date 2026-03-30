# Steam Workshop + Nexus Mods Release Checklist

Status legend:
- `TODO` = not started
- `IN_PROGRESS` = actively being completed
- `DONE` = completed and verified
- `BLOCKED` = cannot proceed yet

## Packaging
| Item | Owner | Status | Evidence/Notes |
|---|---|---|---|
| Include version in title and description (e.g., `v0.1.0`). | Release Manager | DONE | Covered by release notes template title format. |
| Include dependency + load-order notes. | Mod Integrations | TODO | Populate per target build dependencies. |
| Include known issues and compatibility notes. | QA Lead | DONE | Included in release notes template sections. |
| Add changelog section with date-stamped entries. | Release Manager | DONE | `CHANGELOG.md` includes dated and unreleased entries. |

## Legal/IP hygiene
| Item | Owner | Status | Evidence/Notes |
|---|---|---|---|
| Use original art/audio only. | Art Lead | TODO | Verify asset manifest at packaging time. |
| Do not use anime screenshots, logos, or ripped voice lines. | Marketing + Art Lead | TODO | Manual pre-publish audit required. |
| Use inspiration language ("inspired by") not official franchise branding. | Release Manager | DONE | Required language included in release notes template legal notice. |

## Player-facing docs
| Item | Owner | Status | Evidence/Notes |
|---|---|---|---|
| Install instructions. | Documentation Owner | DONE | Added to `README.md`. |
| Uninstall instructions. | Documentation Owner | DONE | Added to `README.md`. |
| Save compatibility warning for mid-run install/removal. | Documentation Owner | DONE | Added to `README.md` and release template compatibility section. |
| FAQ: crash report/log file location. | Support Owner | IN_PROGRESS | Placeholder section in README; finalize exact paths per platform. |

## Launch-day QA
| Item | Owner | Status | Evidence/Notes |
|---|---|---|---|
| New run with character completes without soft-locks. | QA Lead | BLOCKED | Runtime implementation not available yet (`READINESS_REPORT.md`). |
| All starter cards/relic render and localize correctly. | QA + Localization | BLOCKED | Runtime implementation/localization wiring missing. |
| Workshop + Nexus descriptions match the shipped build. | Release Manager | TODO | Verify after first build artifact is produced. |
