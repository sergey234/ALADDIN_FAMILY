# Traceability Matrix (META-1, G1-G24)

| Goal | Primary Artifact(s) | Proof |
|---|---|---|
| G1 | `docs/ADR-CONTENT-PERSISTENCE-G1.md` | ADR committed and referenced in plan |
| G2 | `Core/Content/Sync/`, `Core/Content/Cache/` | content/sync smokes + code review |
| G3 | `docs/CONTENT_MANIFEST_SIGNATURE_POLICY_G3.md`, `Core/Validation/` | signature policy + tests |
| G4 | `Core/Content/ContentManager.swift`, `Screens/ChildContentScreen.swift` | routing checks + QA smoke |
| G5 | `Screens/ParentDashboardView.swift` | dashboard trends/export validations |
| G6 | `Screens/ParentDashboardView.swift`, localization files | i18n pass + localization lint |
| G7 | activity digest services/screens | digest checks + UI validation |
| G8 | `Core/Audio/BackgroundMusicController.swift`, `AudioOneShotPlayer.swift` | audio interruption tests |
| G9 | `scripts/validate_app_sound_effects.py` | CI gate for sound assets |
| G10 | transition manager + UI usage | transition consistency checks |
| G11 | performance budget docs/scripts | perf smoke reports |
| G12 | feedback facade components | integration and review proof |
| G13 | rich progress in child content | progress UI + tests/smokes |
| G14 | `docs/FAMILY_SHARING_APP_PROFILES_FAMILYCONTROLS_G14.md` | family role/help UX proof |
| G15 | `Core/Profile/*`, roster policy tests | conflict resolution tests |
| G16 | unified limits screen/services | limit flows validated |
| G17 | `docs/CONTENT_QA_MATRIX_G17.md`, `scripts/phase7_content_qa_matrix_smoke.py` | generated QA report |
| G18 | `docs/DEVICE_MATRIX_PROCESS_G18.md`, `scripts/phase7_device_matrix_process_smoke.py` | device matrix smoke pass |
| G19 | `docs/FIELD_UX_CHILDREN_PROTOCOL_G19.md`, `docs/FIELD_UX_CHILDREN_FINDINGS_G19.md` | protocol + findings template |
| G20 | `scripts/ipa_size_gate.py`, CI step | IPA/app size report (`docs/IPA_SIZE_GATE_REPORT_G20.*`) |
| G21 | `docs/THREAT_MODEL_DELTA_G21_G23.md` | threat delta evidence |
| G22 | `docs/DATA_MAP_G21_G23.md` | data map snapshot |
| G23 | `docs/DSAR_SCREENSHOTS_LOG_G21_G23.md`, `scripts/phase7_evidence_pack_g21_g23.py` | evidence pack archive/report |
| G24 | localization docs + `scripts/localization_lint.py` + W-LOC tasks | lint pass + W-LOC evidence |

## Notes

- This matrix is the canonical META-1 checklist for release readiness review.
- For machine-friendly consumption, keep `docs/PLAN_PROOF_MATRIX.json` aligned in follow-up updates.

