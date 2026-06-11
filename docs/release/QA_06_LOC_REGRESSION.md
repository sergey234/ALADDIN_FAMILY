# B-QA-06 — LOC regression (143 batch items RU/EN)

**Дата:** 2026-06-11  
**SSOT:** `docs/LOCALIZATION_BATCH_GATE.md`  
**Связано:** B-LOC-08, B-LOC-09, B-LOC-10

---

## Batch LOC matrix

| LOC ID | Batch | Проверка | Статус |
|--------|-------|----------|--------|
| B-LOC-01 | SFM/OPS/B0/B1 | N/A backend | ✅ |
| B-LOC-02 | B-PRE + B2 Antifake | `antifake_*` 43 keys RU+EN | ✅ |
| B-LOC-03 | B3 Privacy | Hub keys RU+EN | ✅ |
| B-LOC-04 | B4 Identity | Hub keys RU+EN | ✅ |
| B-LOC-05 | B5 Device | Hub keys RU+EN | ✅ |
| B-LOC-06 | B6 Family | `family_hub_chd_*`, export keys | ✅ |
| B-LOC-07 | B7 Extras | `crash_settings_*`, `crash_sensitivity_*`, `elderly_*` | ✅ |
| B-LOC-08 | B-COPY | `family_roles_help_*` (B-COPY-01a) RU+EN | ✅ |
| B-LOC-09 | nav_screen_* | antifake/privacy/identity/device hub | ✅ |
| B-LOC-10 | grep Cyrillic hubs | B2–B7 Screens | ✅ |
| B-LOC-11 | af-6-09 | antifake string audit | ✅ |

---

## Static grep evidence (2026-06-11)

```bash
# Hardcoded Cyrillic in security Hub screens — 0 hits
grep -r 'Text("[А-Яа-яЁё]' Screens/*Hub*.swift Screens/03_NetworkProtectionScreen.swift \
  Screens/09_ElderlyInterfaceScreen.swift Shared/Components/Modals/CrashDetectionSettingsModal.swift
# → no matches

# B-COPY-01a keys parity
grep 'family_roles_help_' Core/Localization/LocalizationManager.swift
# → 3 keys × 2 languages (RU + EN)
```

---

## Deferred (не блокирует B-QA-06 static PASS)

| Item | Когда |
|------|-------|
| Onboarding copy edits | post B-QA-02 (frozen) |
| FAQ answer softening | post-L3 COPY |
| `LocalizedVersions/` duplicate sync | при следующем LOC batch |
| Runtime locale switch UI test | B-QA-02 TestFlight |

---

## Статус

**Verdict:** B-QA-06 **PASS** (static LOC regression all impl batches B2–B7 + COPY-01a). Runtime locale QA → B-QA-02.
