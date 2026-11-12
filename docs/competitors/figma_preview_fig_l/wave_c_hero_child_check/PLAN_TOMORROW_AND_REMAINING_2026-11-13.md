# Wave C Heroes · остаток + план на завтра (2026-11-13 / старт 14)

**Сделано сегодня (арт + wire):**
- 4 in-app hero в `Assets.xcassets/ICON_ALIVE_HERO_{ChildControl,ChildThreats,CheckScam,CheckFamily}`
- 4 marketing masters в `marketing_asc/` + `~/Downloads/ALADDIN_Hero_Child_Check_2026-11-13/`
- Wire: Ребёнок (`SimpleHomeScreen`) · Проверить (`AntifakeHubScreen`)
- Под CheckScam: только текст INTERPOL 442 млрд (`antifake_interpol_loss_2025`)

---

## Оставшиеся задачи (ничего не забыть)

| # | Задача | Статус | Нужен GO? |
|---|--------|--------|-----------|
| 1 | **GO на сборку** → Simulator: Ребёнок 2 hero + Проверить 2 hero + текст 442 млрд | ⏳ | да |
| 2 | Глазами: Классика / Золото / Значки (мелкие `ICON_G1_*`) на тех же экранах | ⏳ | после сборки |
| 3 | ASC: 4 marketing → кадры **1290×2796** RU + EN (телефон-рамка, navy/gold) | ⏳ | да на upload |
| 4 | ASC copy снаружи картинки (RU/EN заголовки) — без текста на PNG | ⏳ | — |
| 5 | Проверить watermark CapCut на финальных PNG в Assets (ещё раз) | ⏳ | — |
| 6 | «Сохраняй» → commit **только iOS** (без bot / `.env`) на `master` | ⏳ | «Сохраняй» |
| 7 | Push | ⏳ | «GO на push» |
| 8 | Device QA Ребёнок + Проверить | ⏳ | GO устройство |
| 9 | Опционально: FAQ со ссылкой INTERPOL PDF (не на hero) | ⏸ | позже |
| 10 | Wave C Glyph Batch1–4 (мелкие иконки) — уже wired; sim QA вместе с hero | ⏳ | в п.1–2 |

---

## План на завтра — с чего начать

### Утро (P0)
1. **GO на сборку** (ты говоришь фразу) → открыть Удобный → Ребёнок → Проверить.  
2. Чеклист глаз:
   - ChildControl сверху sheet  
   - ChildThreats перед «Ещё для ребёнка»  
   - CheckScam под header + текст 442 млрд  
   - CheckFamily перед семейной базой  
3. Если crop/высота кривые — подкрутить `frame(height: 220)` / aspect.

### День (P1 — маркетинг Apple)
4. Взять `02_MARKETING_ASC/*_ASC_full.png`  
5. Собрать **8 скринов**: 4×RU + 4×EN @ **1290×2796** (как Wave B fitted).  
6. Заголовки снаружи (не на глине).  
7. Upload в Connect — только по твоему GO.

### Вечер (P2)
8. «Сохраняй» → commit.  
9. Device QA при GO.

**Не начинать завтра с:** bump build, push, CapCut заново, правка OB_*, bot.

---

## Где лежит всё (не потерять)

| Что | Путь |
|-----|------|
| Downloads пакет | `~/Downloads/ALADDIN_Hero_Child_Check_2026-11-13/` |
| Docs + MANIFEST | `docs/competitors/figma_preview_fig_l/wave_c_hero_child_check/` |
| In-app Assets | `Assets.xcassets/ICON_ALIVE_HERO_*.imageset` |
| Wire Ребёнок | `Screens/SimpleHomeScreen.swift` |
| Wire Проверить | `Screens/AntifakeHubScreen.swift` |
| Строка 442 млрд | `Resources/Localization/{ru,en}.lproj/Localizable.strings` → `antifake_interpol_loss_2025` |
