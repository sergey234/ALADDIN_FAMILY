# ALADDIN · План + чеклист по скринам QA (2026-11-14)

**Статус:** LOCKED решения владельца · **полный handoff для другой ML** →  
`docs/ML_SYSTEM_HANDOFF_UX_QA_38_SCREENS_2026-11-14.md`  
**Скрины S01–S38:** `docs/qa_ux_38_screens_2026-11-14/` + `MANIFEST.tsv`  
**Cursor TODO + REGISTRY:** `.cursor/UX_QA_38_TASK_REGISTRY.md` (ids `uxqa-*`)  
**Код:** ждать **GO на P0** · **сборка = владелец в конце** (агент без `xcodebuild` без GO)

---

## LOCKED (владелец 2026-11-14)

| Тема | Решение |
|------|---------|
| Family strip | **A★** `Семья · N из M мест` + `Добавить в семью` |
| Поездки | **H1 Hybrid★** local push + deep link + трек polyline на карте |
| Порядок исполнения | Wave **A→B→C→D→E** (trust/geo → trips RCA→H1 → SimpleHome one-diff → Trial) |

**Не делать:** Nativo / Pet Finder / Tile help clone · CapCut ради scale · xcodebuild без GO.

---

## 0. Очередь батчей (Wave A→E — канон пилота)

| Wave | Батч | Cursor ids | Скрины |
|------|------|------------|--------|
| **A** | Точность + refresh icon | `uxqa-A-05*` | S13 |
| **B** | Map tap не dismiss | `uxqa-B-06*` | S14 |
| **C** | Поездки RCA → H1 push+link+track + default «Вы» | `uxqa-C-04*` | S07–12, S13, S38 |
| **D** | Hero+double+strip **одним** diff | `uxqa-D-*` | S01–S06 |
| **E** | Trial green card audit (≠ slots) | `uxqa-E-07*` | Main |
| P1 | Журнал / вождение / crash / inbox / photo / hub LAST | `uxqa-P1-*` | S14–21,23–25,35,37 |
| P2 | Help / paywall | optional | S27–S34 |
| — | Nativo / Pet Finder / CapCut | **НЕТ** | S22, S26 |

---

## 1. Скрины 1–6 · Aladdin start

### Факт кода сейчас

| Элемент | Сейчас | Файл |
|---------|--------|------|
| Орбита | 318×318 | `SimpleHomeScreen` |
| Двери | 88, icon **0.72** | `hybridGlassDoor` |
| Hero 5811 | 168×196 + rounded chrome | → **S05 double** |
| Hero R02–R06 | 176×200, PNG alpha | rotation OK |
| Strip iOS15 | `slotsCompact` / short add | регресс смысла |

### Задачи

| ID | Задача | Делать | Как |
|----|--------|--------|-----|
| S1-A | Круглый слот hero для всех 6 | ДА | `Circle` D≈254 (80% орбиты) |
| S1-B | Gap ≥10–14 pt до дверей | ДА | подбор 240→260 |
| S1-C | Door icon 0.86–0.92 | ДА | |
| S1-D | QA всех 6 кадров | ДА | Device QA + GO |
| S1-E | CapCut re-export | **НЕТ** | scale = Swift |
| S5-A/C | Убрать double на S05 | ДА | один контейнер; убрать 5811 chrome / cutout |
| S2-A | Copy **A★** `Семья · N из M мест` | ДА LOCKED | Loc + strip |
| S2-B | Кнопка всегда `Добавить в семью` | ДА | scale/2-line |
| S2-C | a11y full strings | ДА | |

**Скрины:** `docs/qa_ux_38_screens_2026-11-14/S01_*` … `S06_*`

---

## 2. Скрины 7–12 · Life360 trip ref → ALADDIN H1

| S# | Содержание | Действие |
|----|------------|----------|
| 7 | Push: аватар·имя·км·vmax | Шаблон T7-A |
| 8 | Тап → карта + BG tip | Deep link + свой tip |
| 9–12 | Точки + polyline | WhereIsPhone + TrackStore |

| ID | Задача | Делать |
|----|--------|--------|
| T7-A | Local notif RU/EN | ДА H1 |
| T7-B | Deep link → map + trip polyline | ДА |
| T7-C | RCA пустого трека при Always+Motion | ДА |
| T7-D | Клон Life360 BG wording | **НЕТ** |

Код база: `FamilyDrivingTripLedger`, `DrivingTripTrackStore`, `FamilyMapAutoTripTracker`, `FamilyPushDeepLink`.

---

## 3. Скрины 13–14 · Карта ALADDIN

| ID | Замечание | Делать |
|----|-----------|--------|
| M13-A | Нет маршрута/push после поездки | ДА → T7 |
| M13-B | ±4200 м / чужое место | ДА RCA LocationManager |
| M13-C | «Обновить место» → icon | ДА |
| M14-A | Тап по карте выбрасывает | ДА |
| M14-B | «С понедельник.» → «С понедельника, …» | ДА P1 |
| M14-C | Period picker | ДА P1 |

Скрины: `S13_*`, `S14_*`

---

## 4. Скрины 15–16 · Вождение + crash tip

| ID | Задача | Делать |
|----|--------|--------|
| D15-A | Убрать «Ничего не выдумываем» | ДА |
| D15-B | Один CTA «Отчёт о реальной поездке» | ДА |
| D15-C | Accordion выбор членов семьи | ДА |
| D15-D | «Готово» apply+dismiss | ДА |
| D16-A | Tip разрешений crash/geo/motion/push | ДА |
| D16-B | Human copy | ДА |

---

## 5. Скрины 17–18 · Inbox / chrome

| ID | Задача | Делать |
|----|--------|--------|
| I17-A | Фильтры Советы/Предложения/Уведомления/Все | Проверить → добить |
| I18-A | Конверт на Где семья | ДА если нет |
| I18-B | Шестерёнка → settings hub | Связь C19 |

---

## 6. Скрины 19–36 · Settings catalog

Полная таблица окон → `ML_SYSTEM_HANDOFF_UX_QA_38_SCREENS_2026-11-14.md` §6.

| Делать | Не делать |
|--------|-----------|
| C19 hub: роли, добавить, покинуть, privacy | S22 Nativo |
| S23/S35 request data / delete | S26 Pet Finder |
| S24 activity share — рассмотреть | Tile help articles clone |
| S25 Profile polish | Life360 Gold 1:1 (S34 → свой upsell) |

---

## 7. Скрины 37–38 · Journal + Driving empty

| ID | Задача | Делать |
|----|--------|--------|
| J37-A | Photo picker с «В» | ДА regression |
| J38-A | Empty при реальной поездке | ДА → T7 RCA |
| J38-B | Default «Вы» не «Родитель В» | ДА |

---

## 8. Trial green card

| ID | Задача |
|----|--------|
| TR-A | Найти UI + `trialEndsAt` / `main_family_restore_trial_cta` |
| TR-B | Честный copy (дата или remain days) |
| TR-C | Не смешивать со strip slots |

Логика: W-pre-D в `SubscriptionManager` — CTA «Вернуть пробный» после раннего downgrade, пока endDate в будущем. Docs: `PLAN_FAMILY_SERIF_AND_TARIFF_SLOTS_2026-11-10.md`.

---

## 9. Чеклист исполнения (синхрон с Cursor `uxqa-*`)

### Wave A / B (P0 trust)

- [ ] `uxqa-A-05a` RCA ±4200 LocationManager
- [ ] `uxqa-A-05b` Honest accuracy + precise CTA (RU/EN)
- [ ] `uxqa-A-05c` Refresh = icon/FAB + a11y
- [ ] `uxqa-B-06a/b` Map tap не dismiss

### Wave C (P0 trips H1)

- [ ] `uxqa-C-04a/b` RCA + data path (до push)
- [ ] `uxqa-C-04c` UNNotification RU/EN keys
- [ ] `uxqa-C-04d/e` Deep link + polyline + BG tip
- [ ] `uxqa-C-04f` Default «Вы» / You

### Wave D / E (P0 home + trial)

- [ ] `uxqa-D-02a` + `D-01a/b` hero one container + scale + doors
- [ ] `uxqa-D-03a/b/c` strip **A★** + loc verify
- [ ] `uxqa-E-07a/b` trial card audit (дата, ≠ slots)

### P1

- [ ] `uxqa-P1-14a/b` дата + period
- [ ] `uxqa-P1-15a/b/c` driving UI + Готово
- [ ] `uxqa-P1-16a` crash tip
- [ ] `uxqa-P1-17a` + `18a` inbox + chrome
- [ ] `uxqa-P1-37a` photo
- [ ] `uxqa-P1-19a/b` C19 hub audit → gap LAST

### Closeout / out of scope

- [ ] `uxqa-loc-verify` все новые ключи RU+EN + integrity script
- [ ] `uxqa-gates` evidence
- [ ] `uxqa-device-qa` — **владелец** собирает в Xcode в конце
- [ ] Help / Pet / Nativo / CapCut — не делать
- [ ] Loc matrix: `.cursor/UX_QA_38_TASK_REGISTRY.md` § Localization
- [ ] **Финальный tap-through (куда нажимать):** `docs/DEVICE_QA_UX_38_TAP_THROUGH_2026-11-15.md` — пункты 1–26 + GATES

---

## 10. GATES

1. 6 кадров: один слой, круг ~80%, gap ≥10 pt  
2. Strip A★ читается полностью  
3. Поездка → push + трек или честный error  
4. Accuracy UI честный; refresh = icon  
5. Trial = реальный `trialEndsAt`  
6. Static verify + Device QA (GO)

---

## 11. Передача другой ML

1. Открыть workspace `ALADDIN_iOS`  
2. Вставить paste из §0 файла `ML_SYSTEM_HANDOFF_UX_QA_38_SCREENS_2026-11-14.md`  
3. Открыть `MANIFEST.tsv` и просмотреть S01–S38  
4. Ждать **GO на P0** от пилота (если ещё нет) → код  
5. Device QA только с отдельным GO  

**SSOT исполнения = handoff MD. Этот PLAN = краткий чеклист.**

---

## 12. ПЛАН-ФАКТ AUDIT · 2026-11-15 (по каждому замечанию владельца)

**Честно:** агент **не** прогнал Device QA / симулятор / реальную поездку.  
Проверено = **код + strings + grep + integrity**.  
Работает на телефоне = **только после сборки владельца** (`DEVICE_QA_UX_38_TAP_THROUGH`).

Легенда: ✅ код готов · ⏳ Device QA · ❌ не делать (LOCKED) · ⚠ gap / не полный Life360 · 🔧 добито в audit-pass

### S01–S06 · Aladdin start (замечания: круг + центр + strip + S05 double)

| # | Замечание владельца (дословно по смыслу) | Нужно? | Код | Device | Аргумент |
|---|------------------------------------------|--------|-----|--------|----------|
| S01–06 | Картинки в центре круга почти во весь круг, центр, не перекрывать двери | ДА | ✅ Circle D=254, `scaledToFit`, clip Circle | ⏳ | Orbit 318 не трогали; gap door≥10 |
| S01–06 | Увеличить иконки дверей | ДА | ✅ fill **0.88** (было 0.72) | ⏳ | |
| S01–06 | CapCut менять ради scale? | **НЕТ** | ❌ | — | LOCKED: scale = Swift |
| S05 | Две картинки друг на друге (красный маркер) | ДА | ✅ убран dual 5811 RoundedRect; один контейнер | ⏳ | Если на device всё ещё видно — проверить PNG alpha R01/5811 |
| S01–06 strip | «1 из 1» + «Добавить» непонятно; без сокращений | ДА A★ | ✅ `Семья · N из M мест` + `Добавить в семью` | ⏳ | Top-5 вариантов → владелец выбрал **A★** (B–E отклонены) |
| Strip Top-5 (справочно) | A★ LOCKED · B «Места: N/M» · C «Семья N/M» · D иконка+tooltip · E только a11y | — | A★ ship | — | Не переоткрывать без GO |

### S07–S12 · Life360 ref → H1 Hybrid★ (push + карта + точки)

| # | Замечание | Нужно? | Код | Device | Аргумент |
|---|-----------|--------|-----|--------|----------|
| S07 | Push: аватар·имя·машинка·км·vmax RU/EN | ДА H1 | ✅ `notifyTripEnded` + keys | ⏳ | Аватар в UNNotification — системный/attachment; машинка = текст, не Life360 UI 1:1 |
| S08 | Тап push → карта + tip BG refresh | ДА | ✅ deep link + `bg_refresh_*` tip | ⏳ | Tip свой ALADDIN, не клон Life360 |
| S09–12 | Точки + polyline на карте | ДА | ✅ gold MKPolyline + highlight trip | ⏳ | Стиль ALADDIN gold, не purple Life360 |
| Цепочка | Почему нет уведомлений / маршрута | ДА RCA | ✅ accuracy gate, quiet-zone, ≥2 pts, logs `TRIP_AUTO` | ⏳ | На device: Always+Motion+Push + не quiet zone; иначе honest empty |
| 3 варианта (было) | H1 Hybrid★ / H2 только modal / H3 server push | H1 LOCKED | ✅ | — | H2/H3 отклонены |

### S13 · ALADDIN карта (точность / refresh / маршрут)

| # | Замечание | Нужно? | Код | Device | Аргумент |
|---|-----------|--------|-----|--------|----------|
| S13 | ±4200 м / чужое место | ДА | ✅ precise flag; pin не обновляется coarse; CTA Settings | ⏳ | Пользователь должен включить **Точные** в Settings; код не врёт |
| S13 | «Обновить место» огромная карточка → иконка | ДА | ✅ FAB 40pt | ⏳ | |
| S13 | Нет маршрута после поездки | ДА → H1 | ✅ path | ⏳ | Зависит от finalize + deep link |
| S13 | Stale tip | ДА | 🔧 stale_hint >5 мин | ⏳ | |

### S14 · Тап карты / дата / период / поездка в журнале

| # | Замечание | Нужно? | Код | Device | Аргумент |
|---|-----------|--------|-----|--------|----------|
| S14 | Тап карты выбрасывает | ДА | ✅ hit-test + interactiveDismissDisabled | ⏳ | |
| S14 | «С понедельник.» → «С понедельника, …» | ДА | 🔧 RU genitive | ⏳ | |
| S14 | Выбрать период | ДА | 🔧 today/week/custom фильтрует trail+trips | ⏳ | |
| S14 | Нет поездки в журнале | ДА → T7 | ✅ filter + ledger | ⏳ | Нет данных = нет записи в TrackStore |

### S15 · Вождение empty / pills / Готово

| # | Замечание | Нужно? | Код | Device | Аргумент |
|---|-----------|--------|-----|--------|----------|
| S15 | Убрать «Ничего не выдумываем» | ДА | ✅ lead заменён | ⏳ | |
| S15 | Один «Отчёт о реальной поездке» | ДА | ✅ | ⏳ | |
| S15 | Гармошка выбор членов (1 или несколько) | ДА | ✅ accordion **single** | ⚠ | Multi-select Set не ship: отчёт per-member; overflow pills убраны |
| S15 | «Готово» ничего не делает | ДА | ✅ apply+collapse | ⏳ | |

### S16 · Crash tip

| # | Замечание | Нужно? | Код | Device | Аргумент |
|---|-----------|--------|-----|--------|----------|
| S16 | Совет Always / Motion / Push рядом с тумблером | ДА | ✅ `family_crash_tip_*` на Safety | ⏳ | Не клон «Aladdin AI» канцелярит |

### S17–S18 · Inbox + chrome

| # | Замечание | Нужно? | Код | Device | Аргумент |
|---|-----------|--------|-----|--------|----------|
| S17 | Советы / Предложения / Уведомления / Все | ДА | ✅ `12_NotificationsScreen` filters | ⏳ | |
| S18 | Конверт → inbox | ДА | ✅ envelope hub header | ⏳ | |
| S18 | Шестерёнка → настройки Где семья | ДА | ✅ gear → gap hub C19 | ⏳ | |

### S19–S36 · Settings catalog (Life360 ref)

| # | Что на скрине | Делать? | Код | Аргумент |
|---|---------------|---------|-----|----------|
| S19 | Carousel управление кругом | Gap hub | ⚠ sheet 4 пункта | Не полный клон Life360 carousel |
| S20 | Роли / админ / добавить / покинуть | Частично | ⚠ → Family / Roles | Leave circle / cloaks — не отдельный экран |
| S21 | Privacy Center | Entry | ⚠ → Settings privacy | |
| S22 | Nativo ads | **НЕТ** | ❌ | LOCKED |
| S23 | Policy / data rights | Links | ⚠ | |
| S24 | Activity sharing toggle | Опционально | ⚠ нет 1:1 | |
| S25 | Account phone/email/delete | Profile | ✅ уже Profile | Не дублировать |
| S26 | Pet Finder | **НЕТ** | ❌ | LOCKED |
| S27–S33 | Help articles | P2 optional | ❌ сейчас | Не Tile clone |
| S34 | Gold trip upsell | Свой paywall P2 | ❌ сейчас | Не Gold 1:1 |
| S35 | Request/delete data | GDPR | ⚠ entry | |
| S36 | Related privacy | Link | ⚠ | |

### S37–S38 · Journal photo + Driving default

| # | Замечание | Нужно? | Код | Device | Аргумент |
|---|-----------|--------|-----|--------|----------|
| S37 | Тап «В» / фото не выбирается | ДА | ✅ PHPicker | ⏳ | Nested sheet |
| S38 | Нет данных при Always+Motion | ДА → T7 | ✅ RCA path | ⏳ | |
| S38 | Default «Родитель В» → «Вы» | ДА | ✅ `where_phone_you` + device member | ⏳ | |

### Trial · зелёная карточка

| # | Замечание | Нужно? | Код | Device | Аргумент |
|---|-----------|--------|-----|--------|----------|
| TR | «Вернуть пробный ещё на 13 дней» — что это? | Audit | ✅ | ⏳ | W-pre-D: после раннего downgrade, пока `recoverableTrialEndDate` в будущем → CTA **«Вернуть пробный до {дата}»** (не путать со strip мест) |

### Closeout

| Пункт | Статус |
|-------|--------|
| Loc RU+EN + integrity | ✅ |
| GATES evidence | ⏳ владелец |
| Device tap-through 1–26 | ⏳ владелец · `docs/DEVICE_QA_UX_38_TAP_THROUGH_2026-11-15.md` |
| Commit / xcodebuild | Только по GO |

**Итог одной строкой:** весь P0+P1 **код** по замечаниям S01–S18/S37–S38/Trial сделан; S19–36 = gap/SKIP по LOCKED; **«всё работает» на телефоне = НЕ подтверждено** без вашей сборки + поездки.
