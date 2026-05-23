# Онбординг OB_01–06 — мастер TODO (≈30 пунктов)

**Обновлено:** 2026-05-22 · **Алгоритм:** `ONBOARDING_FINAL_ML_ALGORITHM.md` §3.1  
**Журнал:** `ONBOARDING_PAGE_BY_PAGE_LOG.md` · **SYNC:** `ONBOARDING_SYNC_LOG_20260522.md`

---

## Почему ломалось (инцидент OB_02 / OB_03) — не повторять

| Симптом | Причина | Правило |
|---------|---------|---------|
| Симулятор ≠ Figma, текст Y совпал | **Другой PNG** в Xcode (`cover-crop` md5 `dc46…`) vs Figma (`zone94` `be22…`) | **SYNC-H:** один файл → imageset **и** `upload_assets` на hero node |
| «Две картинки» / полосы | Zone 361×460 **растянута** на 393×852 | Hero: **compose** zone на `#0a1128` или art-directed crop, не FILL zone на весь экран |
| Scrim «не тот» при том же rect | В коде stop всегда **@0.4**; в Figma OB_02 **@0.45** | **SYNC-T-S5:** stops = `scrimGradientStops()` ↔ Figma `gradientStops` |
| «Готово» без проверки | SYNC-T/I по коду, **без** симулятора | **SYNC-D обязателен** перед статусом ✅ |

---

## Обязательные проверки (встроены в план)

Перед ✅ на странице **все** пункты:

```bash
# MD5 hero (должен совпадать с тем PNG, что залили в Figma)
md5 -q Assets.xcassets/OnboardingHero_0N.imageset/OnboardingHero_0N.png

# Симулятор (Debug)
xcrun simctl launch booted family.aladdin.ios -RESET_ONBOARDING -OnboardingPageN
# N = currentPage: 1→OB_01, 2→OB_02, 3→OB_03 …
```

| Шлюз | Авто / ручное | FAIL = стоп |
|------|---------------|-------------|
| **SYNC-H** | md5 imageset + Figma audit 393×852 + upload из **того же** PNG | Другой кадр на симуляторе |
| **SYNC-T** | Figma: SF Pro, Y title/desc, scrim **y,h**, **3 stops** | stop @0.45 vs код @0.4 |
| **SYNC-I** | `OnboardingFigmaAnchor` case N-1 = §4 | `OnboardingBottomTextPanel` вместо anchor |
| **SYNC-C** | TITLE/DESC = LocalizationManager | Расхождение copy |
| **SYNC-D** | Side-by-side Figma frame vs Simulator | Визуально разный hero/scrim |

**Запрещено:** ставить ✅ SYNC-H только по `imageHash` (перекодирование ≠ md5 файла).

---

## Статус задач (30)

| # | ID | Задача | Статус |
|---|-----|--------|--------|
| 1 | `ml-algo-doc` | `ONBOARDING_FINAL_ML_ALGORITHM.md` + §3.1 SYNC | ✅ |
| 2 | `layer-rules` | `ONBOARDING_LAYER_RULES.md` | ✅ |
| 3 | `readability-plan` | `ONBOARDING_OB_01_06_READABILITY_PLAN.md` | ✅ |
| 4 | `sync-log` | `ONBOARDING_SYNC_LOG_20260522.md` | ✅ |
| 5 | `page-log` | `ONBOARDING_PAGE_BY_PAGE_LOG.md` | ✅ |
| 6 | `anti-regression-doc` | §0.3 инцидент + SYNC-T-S5/H-S6 в ML-алгоритме | ⏳ (правки в ML-алгоритме локально, ждёт commit) |
| 7 | `ob01-sync-h` | OB_01 hero → Xcode + Figma upload | ✅ |
| 8 | `ob01-sync-t` | OB_01 SF Pro, Y, scrim 528×324 | ✅ |
| 9 | `ob01-sync-i` | `OnboardingFigmaAnchor` case 0 | ✅ |
| 10 | `ob01-sync-c` | Copy page1 | ✅ |
| 11 | `ob01-sync-d` | Симулятор SE/Max ≈ Figma | ⏳ |
| 12 | `ob02-sync-h` | Hero zone94 `be22a36d` = Figma upload | ✅ |
| 13 | `ob02-sync-t` | Scrim 552×300, stops 0 / 0.189@**0.45** / 0.42 | ✅ |
| 14 | `ob02-sync-i` | case 1 + `scrimGradientStops` | ✅ |
| 15 | `ob02-sync-d` | Симулятор = Figma | ⏳ |
| 16 | `ob03-sync-h` | Hero zone94-style `73cfae32` = Figma upload | ✅ |
| 17 | `ob03-sync-t` | Scrim **500×320**, stops 0 / 0.16@0.4 / 0.40 | ✅ |
| 18 | `ob03-sync-i` | case 2 + `scrimGradientStops` | ✅ |
| 19 | `ob03-sync-d` | Симулятор = Figma | ⏳ |
| 20 | `ob04-hero` | Hero 04: master/compose → imageset + Figma | ⏳ |
| 21 | `ob04-sync-htid` | OB_04: SYNC-H,T,I,C,D (Y 496/566, scrim 542×310) | ⏳ |
| 22 | `ob04-anchor` | `OnboardingFigmaAnchor` case 3 | ⏳ |
| 23 | `ob05-hero` | Hero 05 → imageset + Figma | ⏳ |
| 24 | `ob05-sync-htid` | OB_05: SYNC-H,T,I,C,D (496/566, scrim 532×320) | ⏳ |
| 25 | `ob05-anchor` | case 4 | ⏳ |
| 26 | `ob06-hero` | Hero 06 → imageset + Figma | ⏳ |
| 27 | `ob06-sync-htid` | OB_06: SYNC-H,T,I,C,D | ⏳ |
| 28 | `ob06-anchor` | case 5 | ⏳ |
| 29 | `script-hero-build` | `build_onboarding_hero_imagesets.py`: не слепо 393×852 | ⏳ |
| 30 | `read-docs` | Полный §11 `ONBOARDING_FIGMA_PAGE_QA_ALGORITHM` на 01–06 | ⏳ |

**Вне scope 01–06:** OB_07 (ScrollView, согласия), Main hero.

---

## Сводка: **15 / 30** ✅ · **15** ⏳

**Закрыто (15)** — код/push `87f9c2c4` или доки в репо:

| Группа | # в таблице |
|--------|-------------|
| Доки в коммите | 1, 4 |
| OB_01 H,T,I,C | 7–10 |
| OB_02 H,T,I + hero zone94 | 12–14 |
| OB_03 H,T,I + hero zone94-style | 16–18 |
| Доки/план (были раньше) | 2, 3, 5 |

**Осталось (15):**

| # | Задача |
|---|--------|
| 6 | anti-regression → commit + push доков |
| 11 | OB_01 **SYNC-D** |
| 15, 19 | OB_02, OB_03 **SYNC-D** (симулятор ≈ Figma, «Принято») |
| 20–22 | OB_04 hero + anchor case 3 + SYNC |
| 23–25 | OB_05 |
| 26–28 | OB_06 |
| 29–30 | скрипт hero + §11 QA |

**Правило:** пункт **D** = ✅ только после твоего «Принято» на симуляторе.

---

## Scrim / hero эталон (не путать 02 и 03)

| OB | Hero compose | Scrim rect | Middle stop |
|----|--------------|------------|-------------|
| **02** | zone ×0.94 center `#0a1128` | **552×300** | **@0.45** → α 0.189 |
| **03** | zone ×0.94 center `#0a1128` | **500×320** | **@0.4** → α 0.16 |

Код: `scrimGradientStops(for:)` в `14_OnboardingScreen.swift`.
