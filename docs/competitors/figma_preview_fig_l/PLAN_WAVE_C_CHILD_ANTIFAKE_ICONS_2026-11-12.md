# Wave C — иконки «Ребёнок» + «Проверить» (как Wave A)

**Дата:** 2026-11-12  
**Статус:** стиль **Вариант A LOCKED** владельцем · код/art — только после GO  
**Сборку Xcode делает владелец сам** (агент не `xcodebuild`). Старт: другой чат + `ML_HANDOFF_WAVE_C_…` · конец батча = evidence → стоп.  

**Образец:** Wave A = Классика (SF/emoji) · Золото (`*_Glyph`) · Значки (`*_Black`) · `AliveGlyph` · wire по одному слоту  

**Полный handoff для другой ML (промпт + 100% слоты):**  
`ML_HANDOFF_WAVE_C_VARIANT_A_CHILD_ANTIFAKE_ICONS_2026-11-12.md`

Связанные планы:
- Wave A icons: `PLAN_ENTRY_ICONS_MAP_UNICORN_2026-11-11.md` ✅  
- Wave B ASC/CapCut: `PLAN_WAVE_B_CAPCUT_TODAY_HANDOFF_2026-11-12.md`  
- ASC чеклист: `docs/AppStore/asc_screenshots_wave_b_2026-11-12/CHECKLIST_WAVE_B_H20_23_AND_LOC.md`

---

## 0. Решения владельца (зафиксировано)

| Решение | Статус |
|---------|--------|
| App Store: грузить **H\* + Draft A–D** | ✅ «делаем всё» 2026-11-12 |
| Draft A–D = только ASC, **не** в UI Ребёнок/Проверить | ✅ |
| Gary оставляем | ✅ |
| Wave C = иконки Ребёнок + Проверить **по образу Wave A** (3 стиля) | ⏳ план готов → GO art |
| OB_01 wordmark выше головы | ⏳ отдельно (Figma↔iOS SYNC) |
| Tip wire / SOS mid-tips | ✅ закрыто в Wave B чате 2026-11-12 · см. `ARTIFACT_MAP_…` |

---

## 1. Аудит «как сейчас» (ничего не пропустить)

### 1.1 Дверь «Ребёнок» — `SimpleHomeScreen.payPainsChildDoorSheet`

Файл: `Screens/SimpleHomeScreen.swift`

| # | Слот UI | Сейчас | SF / emoji | Wire size сейчас | Нужен Alive ID |
|---|---------|--------|------------|------------------|----------------|
| C00 | Заголовок «Обзор ребёнка» | текст only | — | — | нет иконки |
| C01 | Карта «Кто виден на карте» · header | SF | `map.fill` | ~title3 (~22) | **C01_MapVis** |
| C02 | Toggle «Вся семья» | SF | `person.3.fill` | caption (~12) | **C02_MapAll** (или reuse F03) |
| C03 | Toggle «Только я» | SF | `person.fill` | caption (~12) | **C03_MapMe** |
| C04 | Пауза | SF | `pause.circle.fill` | door row **28** | **C04_Pause** |
| C05 | Сайты | SF | `globe` | 28 | **C05_Sites** |
| C06 | Лимит | SF | `hourglass` | 28 | **C06_Limit** |
| C07 | Время сна | SF | `moon.zzz.fill` | 28 | **C07_Bedtime** |
| C08 | Награда | SF | `gift.fill` | 28 | **C08_Reward** (или unicorn U01) |
| C09 | Минуты | SF | `clock.fill` | 28 | **C09_Minutes** |
| C10 | Экран ребёнка | SF | `gamecontroller.fill` | 28 | **C10_ChildScreen** |
| — | chevron / Done | SF chrome | оставить SF | — | **не трогать** |

`payPainsDoor` уже умеет `AliveGlyph` (см. двери Удобного) — wire тот же паттерн.

### 1.2 «Родительский контроль» на Семье — `FamilyParentalControlCard`

Файл: `Screens/02_FamilyScreen.swift` · emoji **28pt** в карточке

| # | Карточка | Сейчас | Alive ID |
|---|----------|--------|----------|
| P01 | Блокировка контента | 🔒 | **P01_ContentBlock** |
| P02 | Управление временем | ⏱️ | **P02_Time** |
| P03 | Мониторинг | 👀 | **P03_Monitor** |
| P04 | Геолокация | 📍 | **P04_Geo** |
| P05 | Отчёты | 📊 | **P05_Reports** |
| P06 | Дополнительно | ⚙️ | **P06_More** (или reuse M04) |
| P07 | Защита от обхода (если SmartDNS) | 🚨 | **P07_Bypass** |
| — | Награда/единорог CTA | 🦄 40 | уже U01 / оставить |
| — | Реферал 🎁 | emoji | опц. later |

### 1.3 «Проверить» — `AntifakeHubScreen`

| # | Слот | Сейчас | SF | Wire size | Alive ID |
|---|------|--------|-----|-----------|----------|
| AF01 | Tab Текст | SF | `text.quote` | ~body в плитке | **AF01_Text** |
| AF02 | Tab Документ | SF | `doc.text.viewfinder` | same | **AF02_Doc** |
| AF03 | Tab Голос | SF | `waveform` | same | **AF03_Audio** |
| AF04 | Tab Видео | SF | `video.fill` | same | **AF04_Video** |
| AF05 | Tab Звонок | SF | `phone.fill` | same | **AF05_Call** |
| AF06 | Trust banner | SF | `exclamationmark.shield` | 12–16 | **AF06_Trust** (опц.) |
| AF07 | Спросить помощника | SF | `sparkles` | title3 (~22) | **AF07_Ask** (или M01) |
| AF08 | Семейная база / share family | SF | `person.3.fill` | subheadline | **AF08_FamilyDB** |
| AF09 | Info / how it works | SF | `info.circle` | nav | оставить SF |
| AF10 | Share tip dismiss | SF | `xmark` / share | chrome | оставить SF |
| — | Paste / Check / Translate buttons | SF labels | — | — | **не в Wave C v1** (текст+SF ок) |
| — | Input mode pills Текст/Ссылка/Контакт | text pills | — | — | без PNG v1 |

**Дверь Удобного «Проверить»** уже `AliveIconID.check` (A07) ✅ — не перерисовывать.

---

## 2. Размеры (канон как Wave A)

| Контекст | 1x display | Asset 2x | Asset 3x | Примечание |
|----------|------------|----------|----------|------------|
| Child door rows (C04–C10) | **28** | 56 | 84 | как F01–F04 |
| Map card header (C01) | **28–32** | 64 | 96 | |
| Map toggles (C02–C03) | **18–20** in capsule | 40 | 60 | мелкие, не перегрузить |
| Parental grid cards (P01–P07) | **28** (замена emoji) | 56 | 84 | карточка уже `font 28` / frame 32 |
| Antifake tabs (AF01–05) | **28** внутри плитки ~44–48 tap | 56 | 84 | selected = gold tint |
| Ask / Family DB (AF07–08) | **28** | 56 | 84 | |
| Trust (AF06) | **20** | 40 | 60 | optional |

**Export pack:** `ICON_G1_<ID>_Glyph` + `ICON_G1_<ID>_Black`  
**Не делать `*_Blue`.**  
**Классика:** текущий SF/emoji без PNG.

---

## 3. Три топ-варианта стиля (выбрать один GO)

### Вариант A — «Как Семья / Wave A» ✅ LOCKED 2026-11-12
- Clay soft 3D · navy+gold · тот же Glyph/Black язык  
- Список/табы читаются как F01–F04  
- Antifake tabs = маленькие глифы в ряду (не lab)

### Вариант B / C — отклонены (не делать без нового GO)

---

## 4. Порядок работ (мелочи)

1. **GO стиль** A/B/C  
2. CapCut/FIG-L: batch **Child C04–C10** first (самый частый экран Удобного)  
3. Wire `AliveIconID` + `payPainsDoor(..., aliveIcon:)`  
4. Batch **P01–P07** → `FamilyParentalControlCard` принять `AliveIconID?` вместо emoji String  
5. Batch **AF01–05** → `AntifakeHubTab.aliveIcon`  
6. AF07–08 · C01–C03  
7. AF06 optional  
8. Settings уже переключает стиль — новые ID подхватят Glyph/Black  
9. QA: Классика / Золото / Значки · Reduce Motion · a11y labels  
10. **Не** xcodebuild без GO · commit только «Сохраняй»

### Запреты
- Не путать с Draft A–D ASC  
- Не трогать OB_* / wordmark в этом пакете  
- Не mass-rewrite LocManager  
- Не bot в iOS commit  
- Pin/chips карты Where — не в Wave C

---

## 5. Полный список задач (чеклист)

### Wave B ASC (контекст)
- [x] H\* + Draft A–D решение: грузить всё  
- [x] Fitted RU+EN Draft / H03 / H21  
- [x] Tip wire + SOS mid ✅  
- [x] Artifact map no-dupes ✅  
- [x] Commit Wave A+B `55fb5602` ✅  

- [ ] ASC upload слоты  
- [ ] OB wordmark — Figma SYNC отдельно  

### Wave C art
- [x] GO вариант A LOCKED  

- [ ] C04–C10 Glyph+Black  
- [ ] P01–P07 Glyph+Black  
- [ ] AF01–AF05 Glyph+Black  
- [ ] C01–C03 · AF07–AF08  
- [ ] AF06 optional  

### Wave C wire
- [ ] Extend `AliveIconID`  
- [ ] Child door rows  
- [ ] Parental cards  
- [ ] Antifake tabs + ask + family DB  
- [ ] Verify Classic fallback SF/emoji  

### Wave C QA (владелец)
- [ ] Удобный → Ребёнок: все ряды  
- [ ] Семья → ПК карточки  
- [ ] Проверить: 5 табов + 2 CTA  
- [ ] 3 стиля Settings  

---

## 6. Куда вставлять (карта файлов)

| Слот | Файл | Точка |
|------|------|-------|
| C01–C03 | `SimpleHomeScreen.swift` | `familyMapVisibilityCard` |
| C04–C10 | `SimpleHomeScreen.swift` | `payPainsChildDoorSheet` → `payPainsDoor` |
| P01–P07 | `02_FamilyScreen.swift` | `FamilyParentalControlCard` callers + struct |
| AF01–05 | `AntifakeHubScreen.swift` | `AntifakeHubTab` + `tabPicker` |
| AF06–08 | `AntifakeHubScreen.swift` | `trustBanner` / `askAssistantHelpCard` / family DB card |
| IDs | `AliveIconStyle.swift` | `AliveIconID` |
| Assets | `Assets.xcassets` | `ICON_G1_C*_` / `P*_` / `AF*_` Glyph+Black |

---

## 7. Оценка объёма

| Пакет | Уник. иконок ×2 (Glyph+Black) |
|-------|-------------------------------|
| Child doors C04–C10 | 7×2 = 14 |
| Map C01–C03 | 3×2 = 6 |
| Parental P01–P07 | 7×2 = 14 |
| Antifake AF01–05 +07–08 | 7×2 = 14 |
| **Итого v1** | **~41 PNG** (без AF06) |

Reuse где логично: C02≈F03, C08≈gift/U01, P06≈M04, AF07≈M01/sparkles — экономия после ревью.

---

**Следующий шаг владельцу:** выбрать **вариант A / B / C** → фраза **«GO Wave C art»** (или сначала «Сохраняй» на ASC Wave B).
