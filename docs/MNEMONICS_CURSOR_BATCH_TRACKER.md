# ALADDIN Memory Academy — Cursor Batch Tracker

**Updated:** 2026-06-06  
**Master plan:** `docs/MNEMONICS_CHILD_IMPLEMENTATION_PLAN.md` (v2.3)  
**Полная синхронизация (для ML):** `docs/MNEMO_PROJECT_SYNC.md` ← **читать первым**  
**Краткий handoff:** `docs/MNEMONICS_ML_HANDOFF.md`

## Summary

| Part | Batches | Tasks | Done | Pending | Progress |
|------|---------|-------|------|---------|----------|
| **v2 MVP (Part 1)** | 0, 1C, 1–8 | 62 | 58 | 4 | **94%** |
| **v3 Course (Part 2)** | 9–15 | 57 | 53 | 4 | **93%** |
| **TOTAL** | **16** | **119** | **111** | **8** | **93%** |

**Код реализации:** ✅ **100%** (111 задач с кодом/docs)  
**Phase C (QA):** ⏳ **8 задач** — tests, manual, sign-off

```bash
python3 scripts/mnemo_batch_progress.py
python3 scripts/child_localization_gate.py --mnemo-full   # 389 keys
# Phase C (конец):
./scripts/mnemo_run_tests.sh
```

---

## Incremental gate (после batch с i18n)

```bash
python3 scripts/child_localization_gate.py
python3 scripts/child_localization_gate.py --mnemo-full
python3 scripts/child_localization_gate.py --prefix child_mnemo_
python3 scripts/child_localization_gate.py --prefix parent_mnemo_
```

---

## v2 MVP — Part 1

| Batch | Name | Tasks | Done | Status |
|-------|------|-------|------|--------|
| **0** | Foundation | 2 | 2 | ✅ DONE |
| **1C** | Brand Academy | 8 | 8 | ✅ DONE |
| **1** | UI Labels | 6 | 6 | ✅ DONE |
| **2** | MnemoCore | 7 | 7 | ✅ DONE |
| **3** | Games 7–12 | 7 | 7 | ✅ DONE |
| **4** | Study 4ф + 30 | 11 | 11 | ✅ DONE |
| **5** | Songs + Cartoons | 5 | 5 | ✅ DONE |
| **6** | Teen + Young | 6 | 6 | ✅ DONE |
| **7** | Rewards + Parent | 5 | 5 | ✅ DONE |
| **8** | QA v2 | 5 | 1 | ⏳ **Phase C:** T02–T05 |

---

## v3 Course — Part 2

| Batch | Name | Tasks | Done | Status |
|-------|------|-------|------|--------|
| **9** | Curriculum Spine | 8 | 7 | ⏳ Phase C: T08 tests |
| **10** | SRS v2 + Push | 8 | 7 | ⏳ Phase C: T08 tests |
| **11** | Co-creation | 6 | 6 | ✅ DONE |
| **12** | Assessment + Capstone | 8 | 8 | ✅ DONE |
| **13** | Мнемотаблица | 6 | 6 | ✅ DONE |
| **14** | Parent + polish | 16 | 16 | ✅ DONE |
| **15** | QA v3 | 5 | 3 | ⏳ Phase C: T04–T05 |

---

## Execution order (финальный)

```
✅ ФАЗА A — v2 код (B0–B7, B10 код)
✅ ФАЗА B — v3 код (B9–B15 код, B14 optional, тесты НАПИСАНЫ)
🏁 ФАЗА C — QA финал (NEXT)
  1. gate --mnemo-full
  2. B8-T02 + B9-T08 + B10-T08 + B15-T02 (прогон unit)
  3. B8-T03 + B15-T03 (прогон UITest)
  4. B8-T04 manual 4×8 + B15-T04 manual 8×4
  5. B8-T05 + B15-T05 → F1–F15 sign-off §N.5
```

**NEXT:** Phase C — `B8-T02–T05`, `B9-T08`, `B10-T08`, `B15-T04–T05`

---

## Phase C — 8 pending задач

| ID | Тип |
|----|-----|
| B8-T02 | Unit run |
| B8-T03 | UITest run |
| B8-T04 | Manual 4×8 |
| B8-T05 | F1–F10 sign-off |
| B9-T08 | Unit run unlock/mastery |
| B10-T08 | Unit run notifications |
| B15-T04 | Manual 8×4 |
| B15-T05 | F1–F15 sign-off |

---

## F-flags

| Flag | Code | Sign-off |
|------|------|----------|
| F16 Brand | ✅ | ✅ |
| F1–F9 | ✅ | ⏳ B8-T05 |
| F10 smoke | ⏳ | ⏳ B8-T04 |
| F11 spine | ✅ | ⏳ B15 |
| F12–F13 | ✅ | ⏳ B15-T05 |
| F14 pictogram | ✅ | ✅ |
| F15 table | ✅ | ⏳ B15-T05 |
