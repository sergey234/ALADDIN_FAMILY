# Family Safety — что не доделали · почему · план доделки

**Дата:** 2026-11-09 · **Build в коде:** 19 · marketing **1.0.2**  
**Роль:** Principal iOS · Mech Pilot  
**SSOT доделки 100%:** [`FAMILY_SAFETY_MASTER_FINISH_88_PLAN_2026-11-09.md`](FAMILY_SAFETY_MASTER_FINISH_88_PLAN_2026-11-09.md)  
**Code-fact:** [`FAMILY_SAFETY_CODE_FACT_CHECKLIST_100_2026-11-09.md`](FAMILY_SAFETY_CODE_FACT_CHECKLIST_100_2026-11-09.md)  
**Этот файл:** почему дыры · 7 скринов S19: `qa_device_2026-11-09/S19_life360_member/` ✅  
**Правило:** не закрывать Round2 до 100% по 88 + evidence.

---

## 0. Промпт агента (копировать)

```text
Principal iOS + Family Safety ALADDIN. Mech Pilot.
SSOT: FAMILY_SAFETY_REMAINING_WORK_PLAN_2026-11-09.md + FULL_TZ + MATRIX_88 + CANON_B.
Эталон S19: qa_device_2026-11-09/S19_life360_member/ (7 jpg).
Только реальные GPS/скорость/поездки — no mock. RU+EN Localizable.strings first.
Сборка / commit / push — только после явного GO владельца.
FIG-L — отдельный файл, не OB_* onboarding Figma.
```

---

## 1. Почему «частично / нет» — честно

| Тема | Было в статусе | Почему так | Что на самом деле |
|------|----------------|------------|-------------------|
| Voice 30s | «частично» | Строки + recorder 30s **есть**; device QA не закрыт | **Код ✅** · evidence ⏳ |
| Antifake short | «частично» | Ключи укорочены; disclaimer-простыня местами ещё всплывает в UI | **Код ~80%** · вычистить остатки |
| Call Filter X AI | «частично» | Strings = `ALADDIN X AI`; UI ещё может говорить «Call Filter» | **Strings ✅** · UI labels ⏳ |
| Trial / tariffs | «частично» | Trial A / antifake bullets в strings; таблица S16 + Subscribe EN | **Код ~70%** · polish S13–16 |
| Snowball | «частично» | Palette на hub/trips; не все экраны | **Tokens ✅** · rollout ⏳ |
| Full-bleed OB 8 стр. | **НЕТ** | R0 сделали Fill, потом регресс (`scaledToFit` / отступы) | **Сломано — чинить P0** |
| Sheet 90–95% | **НЕТ** | Сделали Life360 canvas + snap 0.92, но не 90–95% **видимой** высоты | **Не дотянули** |
| Pin tap → member | **НЕТ** | Sheet есть из **списка**; MKAnnotation tap **не** wired | **Пропуск в R5.5** |
| Avatar crop в member | **НЕТ** | AvatarCropEditor есть в профиле; на пине/member sheet — нет | **Не в скоупе волны** |
| S19 one scroll window | **частично** | У нас sheet с weekly+locks+quiet; **нет** inline trip cards+maps как L360 | **Минимум R5.5, не паритет** |
| FIG-L | **НЕТ** | Отдельный GO Figma; whoami/create aborted; не блокер кода | **Долг дизайна** |
| Device evidence 88 | **НЕТ** | Нет «GO на сборку» → нет after-фото | **Ждёт владельца** |
| 7 скринов S19 | **были «ждём»** | Владелец прислал сейчас | **✅ индекс готов** |

**Итог причины:** шли волнами (legal B → code B → play → bump). P0 map/OB/S19 **не закрывали end-to-end**, потому что переключались на канон B / bump / PIF. Не «забыли ТЗ» — **не добили приоритет после смены волны**.

---

## 2. Эталон Life360 (7 скринов) → что должно быть в ОДНОМ окне

Одно окно member (тап по аватару на карте) = **ScrollView**, сверху вниз:

| # | Файл эталона | Блок Life360 | У нас сейчас | Делать |
|---|--------------|--------------|--------------|--------|
| S19a | `…header_near_save*.jpg` | Аватар поверх sheet · имя · «Возле:» · «С HH:MM» · **Сохранить место** | Имя/Возле/С · Save есть; **аватар не поверх**; **нет crop** | Доделать |
| S19b | weekly locked | «Посмотрите поездки за неделю» + замки рисков | Карточка weekly + locks есть (честный paywall) | Polish UI |
| S19c | places day | Stay cards «В улица» · мин · Сохранить место | Places отдельно; **нет stay-ленты в member** | Добавить |
| S19d–f | trip cards | Мини-карта маршрута · адрес→адрес · время · км · авто/пин art · риск | Trip play в Driving; **не inline в member** | Добавить |
| S19g | upsell 30d | История 30 дней · CTA trial | Ключи B1 есть; экран upsell слабый | Доделать |
| S19h | drive risk row | 59 км/ч · N рискованных | Есть в DrivingReports; **не в member scroll** | Связать |
| FAB | все | «Создать шапку-невидимку» | Quiet zone FAB/sheet есть | Имя **Тихая зона** (канон B) |

**«Не могу поменять фото»:** в Life360 аватар в шапке sheet — у нас тап по пину **не открывает** этот sheet; crop фото — отдельный редактор. Нужно: pin tap → member sheet + tap avatar → AvatarCropEditor (pan/zoom, без обреза).

---

## 3. Чеклист доделки (сделано / нет)

### P0 — сломано / дыра UX (сначала)

| ID | Задача | Сделано? |
|----|--------|----------|
| P0-1 | Онбординг OB_00…07 full-bleed как build 17 (Fill+zoom, без letterbox, руки/края) | **КОД ✅** · device ⏳ |
| P0-2 | Sheet карты max **90–95%** высоты (оставить 5–10% карты) | **КОД ✅** snap full=1.0 → ~95% · any chip → full · device ⏳ |
| P0-3 | Tap по аватару-пину на карте → member sheet | **КОД ✅** · device ⏳ |
| P0-4 | Member = **одно** scroll-окно (header→trips→stays→upsell→quiet) | **КОД ✅** · mini-map → S19 · device ⏳ |
| P0-5 | Tap аватар в member → crop/pan фото (AvatarCropEditor) | **КОД ✅** · device ⏳ |
| P0-6 | «Телефон потерян» / CTA не под tab bar (scroll-to Events + sheet lift) | **КОД ✅** · device ⏳ |
| P0-7 | «Телефон потерян» sticky | **ОТКАТ** 2026-11-09 — владелец: «некрасиво / не двигается»; снова только scroll-карточка (P0-6) |

### P1 — S19 паритет по 7 скринам

| ID | Задача | Сделано? |
|----|--------|----------|
| P1-1 | Header: аватар overlap + Возле + С HH:MM + Сохранить место | **частично** |
| P1-2 | Inline trip cards с мини-картой (наши GPS / endpoints) | **НЕТ** |
| P1-3 | Stay cards дня без «В » у улиц (C1) | **частично** (C1 в places) |
| P1-4 | Weekly trips + honest locks | **частично** |
| P1-5 | Upsell 30d ALADDIN (не Gold L360) | **частично** |
| P1-6 | FAB Тихая зона в member | **частично** (есть quiet, имя) |

### P2 — ранее «частично»

| ID | Задача | Сделано? |
|----|--------|----------|
| P2-1 | Voice 30s | **ДА (код)** · device ⏳ |
| P2-2 | Antifake short — убрать остатки простыни disclaimer | **~80%** |
| P2-3 | UI везде `ALADDIN X AI`, не Call Filter | **strings ДА · UI ⏳** |
| P2-4 | Trial auto + убрать путаницу 2× бесплатно | **частично** |
| P2-5 | Tariffs antifake bullets / Subscribe RU | **частично** |
| P2-6 | Snowball на ParentDashboard + ещё экраны | **частично** |
| P2-7 | Play пин по треку (слой 1+2) | **ДА (код)** · device ⏳ |

### P3 — долг / не код этой волны

| ID | Задача | Сделано? | Почему нет |
|----|--------|----------|------------|
| P3-1 | FIG-L Figma файл | **НЕТ** | Отдельный GO · не блокирует код |
| P3-2 | Device evidence 88 after | **НЕТ** | Нужен **GO на сборку** |
| P3-3 | Commit / push build 19 | **НЕТ** | Ждём GO на commit / push |

---

## 4. Порядок работ (после GO на код)

```text
WAVE FIX-P0  → P0-1…P0-7 (OB + sheet 95% + pin tap + member scroll + crop + lost scroll + **lost sticky**)
WAVE S19     → P1-1…P1-6 по эталону 7 jpg (одно окно)
WAVE P2-polish → P2-2…P2-6 остатки
WAVE VERIFY  → loc integrity · static · (сборка только после GO)
WAVE FIG-L   → отдельный GO
WAVE DEVICE  → GO на сборку · 88 evidence
```

**Гибрид (рекомендация):**  
Life360 **один scroll member** + ALADDIN Storm/Snowball + **Тихая зона** + реальные треки (без Directions API). Аватар crop — наш AvatarCropEditor, не чужой SDK.

---

## 5. Локализация (сразу в план, RU / EN)

| Ключ (логика) | RU | EN |
|---------------|----|----|
| member save place | Сохранить место | Save place |
| near place | Возле: %@ | Near: %@ |
| since time | С %@ | Since %@ |
| weekly trips | Посмотрите поездки за эту неделю | See trips for this week |
| unlock weekly | Разблокировать отчёт о поездках за эту неделю | Unlock this week’s trip report |
| history 30d | История мест за 30 дней | 30-day location history |
| quiet zone FAB | Создать тихую зону | Create quiet zone |
| try free | Попробовать | Try free |

(Существующие ключи не дублировать сырыми — только точечный StrReplace / strings.)

---

## 6. Definition of Done (P0+S19)

- [ ] OB_00…07: нет letterbox; герой не режется по бокам без смысла; текст читаем  
- [ ] Sheet max ≈ 95% как L360 *(snap 1.0 есть; чип держит mid 0.55 — см. UNIFIED MAP-95)*  
- [x] «Телефон потерян» sticky — **ОТКАТ**; только scroll P0-6
- [ ] Tap pin → member sheet  
- [ ] В member одно окно: scroll видит header + trips + stays + upsell + quiet  
- [ ] Tap avatar → crop/pan фото  
- [ ] Нет mock скорости/маршрута  
- [ ] `verify_localization_manager_integrity.sh` OK если трогали LocManager  
- [ ] Device evidence — только после GO на сборку  

---

## 6b. Sheet карта — план A–G (код после GO)

| # | Что | Зачем |
|---|-----|--------|
| A | Формула высоты: `fraction` так, чтобы expansion≈1.0 → **~95%** видимой высоты | Сейчас `0.22+0.73*exp` при 0.95 ≈91% |
| B | Snap full = **1.0** (или 0.95 если формула уже даёт 95%) | Не «подпись 0.95 ≠ 95%» |
| C | **Любой** чип → full sheet (не только Events) | Семья/Питомцы/… тоже как дверь «Ребёнок» |
| D | Drag / scroll не схлопывают mid | Не залипать на 0.55 |
| **E / P0-7** | **Sticky «Телефон потерян»** — compact bar (заголовок + кнопка) **всегда** внизу sheet над hub tab bar; полная карточка со шагами остаётся в скролле (Events) | ✅ `stickyLostBar` |
| F | FAB / map chrome при full — как сейчас (приглушить) | ✅ порог 0.85 без изменений |
| G | Static grep + device smoke (после GO сборки) | ✅ grep · device ⏳ |

**Не делаем в E:** дублировать 3 шага в sticky (только title+CTA). Тап sticky CTA = тот же `openLocator()`.

---

## 7. Журнал

| Дата | Событие |
|------|---------|
| 2026-11-09 | 7 скринов S19 проиндексированы |
| 2026-11-09 | План доделки: этот файл · причина «частично» зафиксирована |
| 2026-11-09 | В план sheet добавлен **P0-7 sticky «Телефон потерян»** (A–G §6b) |
| 2026-11-09 | **GO код** sheet A–G: snap 1.0 · any chip full · `stickyLostBar` в `WhereIsPhoneScreen` |
| — | Ждём **GO на сборку** / device smoke sheet 95% + sticky lost |
