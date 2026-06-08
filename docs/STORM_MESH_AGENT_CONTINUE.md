# Storm Mesh Premium — продолжение работы (handoff для ML-агента)

**Дата:** 2026-06-09 (обновлено: Light Premium, Main v1.2 эталон)  
**Читать первым:** `docs/STORM_MESH_PREMIUM_DESIGN_HANDOFF.md` (v1.2 + **§1.5.1**)  
**Рабочий корень:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

---

## Статус

| Этап | Статус | Premium |
|------|--------|---------|
| Batch 0 — Foundation | ✅ | A |
| **Main v1.2 — эталон** | ✅ `01_MainScreen` hub + frost glass | **Light Premium reference** |
| Batch 1b–1c, 2–5 | ⏳ | — |
| Batch 6 — Chrome everywhere | ⏳ | цель ~95% |
| Batch 9 | ⏳ | без швов |
| Batch 7 QA, Batch 8 ASO | ⏳ | verified + brand |

**Правило продукта:** **ни один экран не темнее Main v1.2.** Только светлее или равно.

---

## Формула дизайна (согласовано)

```
Lazyweb (glass + mesh mood по типу экрана)
+ before.click (navy + gold бренд, ASO)
+ Light Premium (≤ Main brightness, matte storm)
= ALADDIN единый premium
```

**Меняем только:** фон ZStack + chrome карточек (`.stormGlassCard()`).  
**Не меняем:** тексты, layout, navigation, onboarding OB_00–07.

---

## Premium Layer (эталон Main v1.2)

| Слой | Файл | Что делает |
|------|------|------------|
| Атмосфера | `StormMeshBackground` `.hub` | `hubAtmosphereLayer` — indigo + gold wash |
| Глубина | blobs + scrim 28% с y=0.68 | гроза, не яма |
| Стекло | `StormGlassCardStyle` frost v1.2 | white frost + indigo tint + rim + shadow |
| Бренд | gold stroke 38% | кромка карточек |

**На каждом экране:** `.stormGlassCard()` на все интерактивные карточки — **всегда**.

---

## Три режима фона (§1.5.1)

| Режим | Экраны | Действие |
|-------|--------|----------|
| **A — Storm Light** | Main, Support, flows hub | `StormMeshBackground(.hub)` v1.2 |
| **B — Chrome Only** | Legal, Wellness forms/data | gradient/light flat + **только glass** |
| **C — Mood mesh light** | Family, Tariffs, Shield, Child… | variant из §4 + **Mesh Light Calibration** |

**Mesh Light Calibration:** atmosphere, scrim ≤30%, indigo/gold/lightning blobs, база ≥ stormDeep, **не темнее Main** на симуляторе.

---

## Ресурсы Lazyweb / before.click

| Источник | Берём | Не берём |
|----------|-------|----------|
| [Lazyweb](https://www.lazyweb.com/) | Glass depth, mesh mood, paywall/hub patterns | Layout 1:1, чужие тексты |
| [before.click](https://before.click/) | Navy+gold бренд, trust tone, 6 ASO slides | Store headlines in-app, black void |

**Добавляем в ALADDIN:** glass hierarchy (Batch 6, Tariffs), family roster mood (02), shield cold UI (03), gold rim везде, ASO hub light (Batch 8).

---

## SCREEN-SAFE (§1.7) — каждый экран

PRE → правка фон + chrome → POST → отчёт. IDs/keys не уменьшаются.

---

## Очередь батчей

| Batch | Задача | Режим | Glass |
|-------|--------|-------|-------|
| ~~1a~~ | ~~01_Main~~ | A | ✅ эталон |
| **1b** | 10_Tariffs | C `.premium` light | ✅ |
| **1c** | 02_Family | C `.family` light | ✅ |
| 2a–2c | Parental, Child, Network | C | ✅ + accent strip (2c) |
| 3a–3d | AI, Devices, Analytics, Chat | C | ✅ |
| 4a–4d | Profile, Support, Elderly, Referral | A/C | ✅ |
| 5 | Transactional + legal | C / **B** legal | ✅ / legal flat |
| **6** | Chrome pass + grep «не темнее Main» | все | ✅ все cards |
| 9a–9f | Companion, Games, Learn, Wellness… | C / **B** wellness forms | ✅ |
| 7 | QA | — | SCREEN-SAFE all |
| 8 | ASO 6 slides | hub **light** palette | — |

**Приоритет исполнения:** 1b → 1c → 2–5 (mesh light + glass) → 6 (chrome pass) → 9 → 7 → 8.

**Калибровка variants:** перед массовым rollout — перенести правила hub v1.2 на `.premium`, `.family`, `.shield` (задача `mesh-variants-light-calibration`).

---

## Сборка

- Симулятор: **iPhone 13 Pro Max**
- Не параллелить Xcode и `xcodebuild`
- `bash scripts/unlock_xcode_build_db.sh` при database locked

## Коммиты

Только по явной просьбе пользователя.

---

---

## Матрица по каждому экрану (§4.2 handoff)

См. полную таблицу в `STORM_MESH_PREMIUM_DESIGN_HANDOFF.md` **§4.2** (Mode A/B/C, статус, исключения).

| Статус | Экраны |
|--------|--------|
| ✅ **1** | 01_Main (A, hub v1.2) |
| ❌ skip | 14_Onboarding |
| ⏳ **26** | 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 18–28 |
| ⏳ **Batch 9** | Companion, Games, Learn, Wellness*, Shield settings, Flows — §4.1 |

\* Wellness forms → режим **B**; warm hubs → режим **C** `.warm` light.

---

## Улучшения (зафиксировано в плане)

| ID | Улучшение | Статус |
|----|-----------|--------|
| IMP-01 | hub v1.2 atmosphere layer | ✅ |
| IMP-02 | hub blobs: indigo/lightning/gold (не stormCloud на black) | ✅ |
| IMP-03 | scrim 28% с y=0.68 | ✅ |
| IMP-04 | StormGlassCard frost v1.2 | ✅ |
| IMP-05 | §1.5.1 Light Premium (не темнее Main) | ✅ |
| IMP-06 | Режимы A / B / C | ✅ |
| IMP-07 | Калибровка всех mesh variants light | ⏳ |
| IMP-08 | Lazyweb glass + before.click gold rim | ⏳ по батчам |
| IMP-09 | Batch 6 chrome pass all screens | ⏳ |
| IMP-10 | Batch 8 ASO hub light | ⏳ |

---

## Приоритет TODO

1. `mesh-variants-light-calibration` (IMP-07)  
2. `screen-10-tariffs` → `screen-02-family`  
3. Batch 2–5 (по §4.2 порядку)  
4. `batch-6-glass` (IMP-09)  
5. Batch 9 → 7 → 8  

---

**Следующий файл:** `Screens/10_TariffsScreen.swift` (Batch 1b, режим C, premium light + glass).
