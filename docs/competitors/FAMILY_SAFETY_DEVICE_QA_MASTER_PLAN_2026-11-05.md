# FAMILY SAFETY — Device QA Master Plan (скрины 2026-11-05)

**Дата:** 2026-11-05 · **роль:** principal iOS + product UX (15+ лет)  
**Пилот:** владелец · **Меха:** агент (код только после GO по батчам)  
**Скрины:** `docs/competitors/qa_device_2026-11-05/` + `FILE_INDEX.txt` (Q01–Q36)  
**Канон продукта:** `FAMILY_SAFETY_KASPERSKY_LIFE360_MASTER_PLAN.md` v1.4 · fact: `FAMILY_SAFETY_PLAN_FACT_CHECKLIST.md`  
**Сборка / Device QA:** только после явного **GO на сборку** владельца.

---

## 0. Промпт агенту (копировать в новый чат)

```text
Роль: principal iOS + family-safety UX ALADDIN (15+ лет). Mech Pilot: владелец даёт GO; ты — минимальный diff + evidence.

ОБЯЗАТЕЛЬНО СНАЧАЛА:
1) git rev-parse --show-toplevel → …/ALADDIN_iOS; ветка master.
2) Прочитай ЦЕЛИКОМ этот файл:
   docs/competitors/FAMILY_SAFETY_DEVICE_QA_MASTER_PLAN_2026-11-05.md
3) Открой JPG по FILE_INDEX (Qxx) в docs/competitors/qa_device_2026-11-05/
4) Сверь с кодом якорями §1. Не выдумывай API.

ПРАВИЛА:
- Loc: только localized() + RU+EN в Localizable.strings. Сырых ключей на экране — FAIL.
- Нет spy-copy («следить»). Нет «помощь едет». Нет fake pins / mock parental.
- Storm glass + gold #F59E0B · не purple Life360 brand.
- Один Map hub = WhereIsPhone. 4 таба внутри хаба — OK.
- Invite codes TTL = 3 дня (72h). Soft invite push на D+1.
- Driving weekly + 4 иконки инцидентов + PDF week/month — по Life360 Q02–Q06.
- Map sheet detents как Life360 Q08/Q34–Q36.
- Antifake media (doc/voice/video/call) — честный timeout + retry; text тоже smoke.
- Onboarding heroes: без crop головы/рук на device (не только симулятор).
- Не трогать OB_* Figma onboarding file без SYNC-чеклиста.
- xcodebuild / Simulator — только «GO на сборку».

ФОРМАТ ОТЧЁТА: Qxx | было | стало | evidence | loc keys | остаток.
Один батч GO за раз (см. §3 Waves).
```

---

## 1. Якоря кода (есть сейчас)

| Зона | Файл |
|------|------|
| Удобный 3 двери | `Screens/SimpleHomeScreen.swift` |
| Map hub | `Screens/WhereIsPhoneScreen.swift` |
| Wave A / C extras | `Screens/FamilySafetyRemainderHub.swift` |
| Call Directory | `Shared/Components/AntifakeCallDirectorySettingsCard.swift` |
| Анти-Баннер | `Core/ContentBlocker/ContentBlockerManager.swift` + Wave A section |
| Driving | `Shared/Components/Modals/DrivingReportsModal.swift` |
| Crash confirm | `FamilyCrashConfirmSheet` · `FamilyImOkService.sendNeedHelp` |
| Antifake media | `ViewModels/AntifakeMediaCheckViewModel.swift` · Hub |
| Invite TTL | `app/routers/family.py` → `ALADDIN_FAMILY_INVITE_TTL_HOURS` **default 24** |
| Onboarding hero | `Shared/Components/HeroAmbientPresentation.swift` (`scaledToFill` + zoom) |
| Main «Удобный» | `Screens/01_MainScreen.swift` (gold stroke уже в коде) |
| Parental bot card | `Screens/07_ParentalControlScreen.swift` · component `parental_control_bot` |

---

## 2. GATES (до слова «готово» по батчу)

| Id | Критерий | Evidence |
|----|----------|----------|
| G1 | Нет сырых ключей RU/EN | grep UI + strings |
| G2 | Нет spy-copy / «помощь едет» / fake pins | grep + скрин |
| G3 | Invite TTL = 72h + soft D+1 | API + local notif schedule |
| G4 | Weekly driving 4 icons + PDF export | UI + файл PDF |
| G5 | Map sheet: detent collapsed / half / full | device video |
| G6 | Onboarding Q09–Q11: руки/голова в кадре | device screenshot |
| G7 | Crash «Да, нужна помощь» → toast/ack ≤3s или честная ошибка | smoke |
| G8 | Antifake doc/voice/video/call: не вечный spinner | timeout UX + retry |
| G9 | SimpleHome ← → Main работает | a11y tap |
| G10 | Call Filter / Safari blocker: deep-link + guide | Settings open + status |

---

## 3. Волны исполнения (не всё одним PR)

| Wave | Содержание | Priority |
|------|------------|----------|
| **W0** | Hotfix: Q13 back · Q21 spy copy · Q23 fake-pins copy · Q24 calendar contrast · Q25 crash hang · Q22/23 pet | P0 |
| **W1** | Antifake media pipeline Q27–Q29, Q32–Q33 (+ text smoke) | P0 |
| **W2** | Map Life360 parity: avatar pin · sheet detents · FAB · invite banner Q08, Q18, Q34–Q36 | P0 |
| **W3** | Driving weekly 4 icons + PDF Q02–Q06 | P1 |
| **W4** | Invite soft D+1 + TTL 3 days Q01 | P1 |
| **W5** | Premium value notifications Q07 | P1 |
| **W6** | Settings deep-links Call Directory + Safari Q16–Q17 · Call Filter Q31 | P1 |
| **W7** | Onboarding hero crop Q09–Q11 | P1 |
| **W8** | Tariffs card rewrite Q12 · Main gold tile verify Q19 · Connect device Q20 | P2 |
| **W9** | Bluetooth / Motion honesty Q14–Q15 · Parental bot decision Q30 · Habits bleed Q26 | P2 |

---

## 4. Чеклист по каждому скрину (Q01–Q36)

Легенда Факт: **есть** / **частично** / **нет**. Решение — канон для кода.

### Q01 — Soft invite «на следующий день» + коды 3 дня

| | |
|--|--|
| **Что на скрине** | Life360: high-five art · «Пора сделать это официальным» · коды **2 дня** · CTA «Пригласить» |
| **У нас** | Invite API есть; TTL default **24h** (`ALADDIN_FAMILY_INVITE_TTL_HOURS`). Soft D+1 prompt **нет**. |
| **Решение** | 1) Env/prod: TTL **72** часа. 2) Local/push: если семья <2 участников через **24h** после первого open map/home → sheet+notif «Пригласите близких». 3) Copy: коды действуют **3 дня**. 4) Не multi-circle. |
| **Куда** | Backend `family.py` · iOS scheduler (UNNotification / AppStorage lastPrompt) · sheet в SimpleHome / WhereIsPhone invite banner |
| **Loc** | RU: «Коды приглашения действуют 3 дня…» · EN: «Invite codes work for 3 days…» · keys `family_invite_soft_*`, `family_invite_ttl_hint` |
| **Чеклист** | [ ] TTL 72h API [ ] D+1 prompt once [ ] dismissible [ ] RU+EN [ ] no spy |

### Q02–Q05 — Инциденты вождения (4 иконки + detail sheet)

| Иконка (Life360) | Смысл | Данные |
|------------------|-------|--------|
| 🔴 спидометр / phone | Отвлечение на телефон / риск-событие | count за неделю |
| 🔵 телефон | Использование телефона за рулём | count |
| ⚡ молния | Резкий разгон | count + explain sheet |
| 🟡 / тормоз | Резкое торможение | count + explain |

| | |
|--|--|
| **У нас** | `DrivingReportsModal` + Analytics — **нет** Life360-полоски 4 icon + explain modal «Что такое резкий разгон?» |
| **Решение** | В таб **Вождение** хаба: weekly strip 4 counters → tap → explain sheet (как Q02). Источник: CoreMotion / trip agent если есть; иначе честный empty «Пока нет поездок — включите доступ к движению». **Не** fake 16. |
| **PDF** | см. Q06 |
| **Loc** | `drive_inc_phone_*`, `drive_inc_speed_*`, `drive_inc_accel_*`, `drive_inc_brake_*`, `drive_inc_explain_*` |
| **Чеклист** | [ ] 4 icons UI [ ] explain sheets [ ] empty honesty [ ] RU+EN |

### Q06 — Еженедельный отчёт: поездки · км · макс скорость · PDF

| | |
|--|--|
| **Что** | «Эта / Прошлая неделя» · max speed card · trips · km · member row · risky events |
| **У нас** | Modal есть, **не** Life360 density; PDF weekly drive **нет** (есть PDF parental monitoring в Family — другой продукт) |
| **Лучшее PDF** | 1) **Клиент:** `UIGraphicsPDFRenderer` локальный отчёт (неделя/месяц) → Share Sheet. 2) Позже server PDF если нужен email. v1 = local PDF достаточно. Поля: период, член, поездки, км, макс км/ч, 4 инцидента, дисклеймер «оценка, не страховой отчёт». |
| **Куда** | `WhereIsPhone` tab Driving + `DrivingReportsModal` redesign · `FamilyDrivingWeeklyReportPDF.swift` |
| **Чеклист** | [ ] week/month toggle [ ] stats cards [ ] Export PDF [ ] Share [ ] RU+EN |

### Q07 — Premium notifications (ценность → апгрейд)

| | |
|--|--|
| **Что** | Life360 value pushes для Premium |
| **У нас** | Soft paywall map `01e` есть; **нет** системной матрицы premium notifs |
| **Где делать (макс ценность)** | 1) После 3 дней карты без Family → soft. 2) После 1-го Antifake success на Free limit → «Больше проверок в Family». 3) Weekly digests только Family+. 4) Crash/SOS tips. 5) Places enter/leave (уже Places) — Premium copy upsell если locked. |
| **Не** | Спам каждый час; spy wording |
| **Loc** | `premium_nudge_*` |
| **Чеклист** | [ ] matrix 5 triggers [ ] frequency cap [ ] deep-link Tariffs [ ] RU+EN |

### Q08 + Q34–Q36 — Map hub: avatar pin · FAB · sheet detents (как Life360)

| | |
|--|--|
| **Что** | Full-bleed map · avatar pin + «N мин назад» · SOS left · FAB right · bottom sheet: invite → chips → members; **drag up** = map shrink / list expand; **drag down** = map fullscreen |
| **У нас** | 4-tab + chips + MapKit **есть**; **нет** настоящих `presentationDetents` / fraction map height; pin = PNG/FIG interim, не photo-avatar pin |
| **Решение** | 1) `mapHeightFraction` 0.15…0.85 tied to sheet offset (Geometry + DragGesture) **или** `.presentationDetents([.fraction(0.25), .medium, .large])` если sheet = system. 2) Member pin = circular `UIImage` avatar + gold ring + time bubble. 3) FAB: locate / layers / +. 4) Storm chrome (не purple). |
| **Чеклист** | [ ] 3 detents [ ] avatar pin [ ] time ago [ ] SOS [ ] FAB [ ] invite banner [ ] device video |

### Q09–Q11 — Онбординг: герой обрезан

| | |
|--|--|
| **Проблема** | Q09 голова/торс справа; Q10 руки/мусор; Q11 руки за краем («Где семья») |
| **Почему правки «не применились»** | `HeroAmbientPresentation`: всё ещё `scaledToFill` + zoom `1.02` на части hero — на **реальном** iPhone aspect ≠ 393/852 → crop по X. TestFlight мог быть **до** asset swap; или в бандле старый PNG; правило OB_03 просит `scaledToFit` — код Fill доминирует. |
| **Решение** | 1) Для OB hero: `scaledToFit` + letterbox canvas BG **или** per-asset `alignment` (`.leading`/`.center`) + max zoom 1.0. 2) Verify asset names `OnboardingHero_0N` в xcassets = «новые» PNG. 3) Device screenshot gate G6. 4) Не чинить через LocManager. |
| **Чеклист** | [ ] asset hash vs «новые» [ ] fit/alignment fix [ ] Q09–11 device PASS |

### Q12 — «Три уровня защиты» под Premium

| | |
|--|--|
| **Сейчас** | Карточка сверху тарифов; «Fam/Pro»; техслова last-point / Always Allow; EN abbreviations |
| **Решение** | Перенести блок **под** карточку Premium. Переписать простым языком + **число устройств** на тариф. RU без английских ярлыков. |
| **Пример RU** | Free: «1 устройство · базовая проверка · карта последней точки». Family: «До N устройств · живая карта · Antifake». Premium: «Максимум устройств · всё Family + расширенные проверки». |
| **Куда** | `10_TariffsScreen.swift` + strings |
| **Чеклист** | [ ] position under Premium [ ] device counts [ ] no raw EN [ ] simple copy |

### Q13 — Back «Удобный режим» → Main не работает

| | |
|--|--|
| **Факт** | `SimpleHome.onBack` → `goBackToPreviousScreen`. Если SimpleHome = **корень входа** (pay-pains), стек пуст → back no-op / не на Main. |
| **Решение** | Back: если нет previous → `navigateToRoot(.main)` (явный «Полная версия»). Или скрыть chevron когда SimpleHome root и показать «Полная версия» в Меню only. **Рекомендация:** back → Main всегда из SimpleHome (владелец ждёт Main 1). |
| **Чеклист** | [ ] tap back → Main [ ] a11y id |

### Q14–Q15 — Bluetooth · Движение и фитнес (Life360 settings)

| | |
|--|--|
| **Зачем Life360** | BT: обнаружение «рядом» / Tile / car Bluetooth context. Motion: поездки, crash, steps. |
| **У нас** | Нет отдельных toggles в map settings (честно: нет BT presence product). Motion частично через location/crash. |
| **Решение** | **Не клонировать** пустые toggles. Добавить в Always Allow / map settings honest rows: «Движение» → `UIApplication.openSettings` + copy «Нужно для отчётов о поездках». Bluetooth: **SKIP** до Tile partner (P4) **или** row «Скоро» без fake ON. |
| **Чеклист** | [ ] Motion deep-link [ ] BT skip/soon [ ] copy RU+EN |

### Q16–Q17 — Call Blocking · Safari Content Blockers (системные экраны)

| | |
|--|--|
| **У нас** | Guide sheet Call Directory → `openSettingsURLString` (общий Settings). **Нет** гарантированного deep-link в Phone→Blocking (Apple restriction — в коде уже комментарий). Content Blocker: toggle в Wave A; активация всё равно в Safari Settings. |
| **Решение** | 1) Кнопки: «Открыть Настройки» + **пошаговый** guide (уже есть). 2) Добавить вторую CTA «Как включить в Safari» → guide Анти-Баннер. 3) Status ON/OFF refresh после return (`scenePhase`). 4) Точки входа: Проверить (Wave A) · Настройки защиты · first-run. |
| **Чеклист** | [ ] dual CTA [ ] status refresh [ ] Safari guide [ ] Call guide |

### Q18 — Превью метки / аватар на карте

| | |
|--|--|
| **Что** | Редактор вида пина (Life360 «Как вам вид?») |
| **У нас** | `pinPreviewDone` AppStorage chrome; нет editor размера/фото |
| **Решение** | Sheet: выбор фото из Family member avatar · размер S/M/L · preview на map · Save local. |
| **Чеклист** | [ ] avatar pick [ ] size [ ] persist |

### Q19 — «Удобный режим» золотом на Main

| | |
|--|--|
| **Код** | Уже gold stroke + title `secondaryGold` в `01_MainScreen` (QA16 B2). |
| **Почему на скрине «серо»** | Слабый opacity 0.08 fill / старый билд / соседние карточки тоже gold-ish. |
| **Решение** | Усилить: fill gold 0.18 · stroke 2pt · badge «Главный вход» · не emoji-only. |
| **Чеклист** | [ ] visual distinct device |

### Q20 — «Подключите устройство для защиты»

| | |
|--|--|
| **Проблема** | Серый / сложный текст |
| **Цвет** | Storm navy card + **gold** CTA (не mint Family card, не flat gray) |
| **3 варианта текста** | **A (рекомендую):** RU «Добавьте телефон близкого — увидите защиту и точку на карте.» EN «Add a family phone — see protection and their place on the map.» · **B:** «Один шаг: отправьте приглашение на iPhone близкого.» · **C:** «Пока здесь пусто. Пригласите человека из семьи.» |
| **Чеклист** | [ ] pick A [ ] gold CTA [ ] RU+EN |

### Q21 — Убрать «не чтобы следить» · «Точные места»

| | |
|--|--|
| **Факт** | `map_perm_always_body` RU содержит «не чтобы следить»; `map_perm_precise_hint` = «Включите также «Точные» места» |
| **Precise** | iOS Location: Precise ON в Настройки→ALADDIN→Геопозиция. Нужно для точной точки; без Precise — грубая зона. |
| **Решение** | Убрать spy-negation. Новый body: «Так карта обновляется, когда приложение закрыто — вы видите, где телефоны семьи.» Precise: «В Настройках iPhone включите «Точные» для ALADDIN — точка будет точнее.» + кнопка Открыть Настройки. |
| **Чеклист** | [ ] strings RU+EN [ ] no следить [ ] precise explain |

### Q22 — Питомец: лекарства → своё поле

| | |
|--|--|
| **Решение** | Toggle medicine → optional **TextField** «Своё напоминание» (свободный текст) + keep walk/feed. Medicine can stay as preset chip, не единственный смысл. |
| **Чеклист** | [ ] custom field [ ] save local |

### Q23 — Убрать «без фейковых точек»

| | |
|--|--|
| **Факт** | `pet_saved_local` RU/EN содержит fake-pins disclaimer |
| **Решение** | RU: «Сохранено на этом iPhone. Живая карта питомца появится позже.» EN: «Saved on this iPhone. Live pet map comes later.» |
| **Чеклист** | [ ] strings only surgical |

### Q24 — Календарь: чёрные цифры

| | |
|--|--|
| **Причина** | Системный `DatePicker` `.graphical` на тёмном фоне → UIKit чёрный текст |
| **Лучшее** | 1) Обернуть DatePicker в `.colorScheme(.light)` внутри белой/cream карточки **или** 2) кастомный month grid белым текстом (больше работы). **Рекомендация v1:** light inset card для календаря (контраст WCAG). |
| **Чеклист** | [ ] readable days [ ] selected gold |

### Q25 — «Да, нужна помощь» зависает

| | |
|--|--|
| **Код** | `isSending=true` → `sendNeedHelp` (location capture + family chat) → dismiss. Hang = await location/API без timeout / нет UI Progress / ошибка глотается. |
| **Решение** | 1) Timeout 8s на location. 2) Progress «Отправляем семье…». 3) `defer { isSending=false }`. 4) Toast success/fail. 5) Offline queue already exists — показать «Сохраним и отправим при сети». |
| **Чеклист** | [ ] no infinite disable [ ] ack UI [ ] offline path |

### Q26 — Два экрана / зелёная линия / ободки

| | |
|--|--|
| **Гипотеза** | Sheet поверх Family + Habits: double backgroundGradient / safeArea inset / accent strip bleed; или screenshot of translucent modal. |
| **Решение** | Audit `FamilyHabit*` presentation: один background · clipShape · no stacked NavigationView. Remove green diagnostic overlays if any. |
| **Чеклист** | [ ] single layer device |

### Q27–Q29 · Q32–Q33 — Antifake Voice / Document / Video / Call

| | |
|--|--|
| **Симптомы** | Вечный «Загрузка файла…» · «Анализ занял слишком много времени» · «не удалось синхронизировать» · text иногда OK |
| **Код** | Upload → poll до SLA (audio 120s / video 300s / doc 120s) → `NetworkError.timeout`. Spinner на upload без отдельного fail. `.txt` в document разрешён — но сервер может ждать image/PDF → долгий fail. |
| **Корневые причины (вероятность)** | 1) Backend job queue slow/down на `:8002`. 2) Auth token. 3) Большой mp4. 4) Poll URL/base mismatch. 5) UI не сбрасывает `isChecking` при cancel. |
| **Решение (наилучшее)** | **A Client:** cancel button · progress % · на timeout — Retry + «Сообщить в поддержку» · не оставлять spinner. Validate type (doc: photo/PDF preferred; warn on .txt). **B Server:** health antifake workers · job status logs · soft-fail message. **C Smoke:** script text/doc/voice fixtures. |
| **Чеклист** | [ ] text PASS [ ] doc photo PASS [ ] voice 5s PASS [ ] video small PASS [ ] call PASS or honest disabled [ ] timeout UX |

### Q30 — «Бот родительского контроля»

| | |
|--|--|
| **Что** | Component toggle `parental_control_bot` в Parental — legacy «enhanced» flag, **не** Telegram-бот. |
| **Дубль?** | Да, путает с реальным Parental / Screen Time / «Защита детей». |
| **Решение (рекомендация)** | **Скрыть/убрать** карточку из UI Parental; логику оставить server-side если API depends. Copy заменить нельзя — название «бот» токсично. Функции родителя = дверь «Ребёнок» + Parental screen без bot naming. |
| **Чеклист** | [ ] owner GO hide [ ] no broken API |

### Q31 — ALADDIN Call Filter не найти / не включить

| | |
|--|--|
| **Логика** | Call Directory **extension** появляется в Настройки→Телефон→Блокировка **только если** extension установлен в сборке, signed, first sync done. Status `.unknown` = не установлен / не в билде. |
| **Решение** | 1) Verify target `ALADDINCallDirectory` в Archive/TestFlight. 2) После install: Sync button + reopen Settings. 3) Guide уже говорит «ALADDIN Call Filter» — сверить **Display Name** extension Info.plist = exactly that string. 4) Если `.unknown` — UI: «Расширение не в этой сборке» честно, не «включите». |
| **Чеклист** | [ ] extension in TF build [ ] display name match [ ] status honest |

### Extra — Content Blocker / Анти-Баннер (связано с Q17)

| | |
|--|--|
| **Функционал в коде** | **Есть** (`ContentBlockerManager`, Wave A toggle). Пользователь должен ещё включить в Safari→Расширения. |
| **Решение** | После toggle ON → sheet «Откройте Настройки → Safari → Расширения → ALADDIN». Status from `SFContentBlockerManager`. |

---

## 5. Локализация (правила)

1. Ключи только в `Resources/Localization/{ru,en}.lproj/Localizable.strings`.  
2. LocManager — **точечный** StrReplace только если ключ ещё читается из dict; иначе strings достаточно.  
3. После правок: `./scripts/verify_localization_manager_integrity.sh` если трогали mega-file.  
4. Fail: сырой `map_perm_*` / `drive_inc_*` на экране.

---

## 6. PDF еженедельного вождения — решение (деталь)

```text
User → Driving tab → «Отчёт за неделю|месяц» → Share
  → FamilyDrivingWeeklyReportBuilder
      inputs: trips[], km, maxSpeed, incidents[4], memberName, period
      output: URL temp PDF (UIGraphicsPDFRenderer)
  → UIActivityViewController
```

Страницы PDF: обложка ALADDIN · сводка · 4 инцидента · дисклеймер.  
Не требует нового серверного endpoint для v1.

---

## 7. Порядок GO (фразы владельцу)

1. `GO код W0` — hotfixes copy/back/crash/calendar/pet  
2. `GO код W1` — Antifake media  
3. `GO код W2` — map detents + avatar pin  
4. `GO код W3` — driving weekly + PDF  
5. `GO код W4–W6` — invite / premium notif / settings links  
6. `GO код W7–W9` — onboarding / tariffs / BT-motion / bot hide  
7. `GO на сборку` — Device QA по GATES  

Figma Life360 pixel (7b) — **отдельный** долг, не блокирует W0–W3.

---

## 8. Связь с прошлым планом

| Прошлый lock | Этот QA |
|--------------|---------|
| §17 1–7a код remainder | **Device** нашёл gaps UX/bugs |
| 7b Figma [D] | остаётся |
| 8 Device QA [-] | **этот документ = вход в 8** |
| P4 out | BT Tile / live Pet / dispatch — out |

Обновить `FAMILY_SAFETY_PLAN_FACT_CHECKLIST.md` после каждого закрытого Qxx.

---

## 9. Быстрые ответы владельцу (сводка)

| Вопрос | Ответ |
|--------|--------|
| Invite как Life360 D+1, коды 3 дня? | Да: soft prompt + TTL 72h (сейчас 24h). |
| Driving 4 icons + PDF? | Делаем в tab Вождение; PDF local Share. |
| Premium notifs куда? | Map soft + Antifake limit + weekly digest + Places lock. |
| Sheet map expand/collapse? | W2 detents — сейчас нет. |
| Онбординг crop почему? | `scaledToFill` на device; проверить assets в TF. |
| Тарифы 3 уровня? | Перенести под Premium, простой RU, device counts. |
| Back Удобный? | Root stack — чинить → Main. |
| BT / Fitness? | Motion → Settings link; BT skip/soon. |
| Call Blocking / Safari links? | Guides + open Settings; true deep-link Phone Apple не даёт. |
| Анти-Баннер есть? | Да в коде; нужен Safari enable + UX tip. |
| Pin editor? | W2/Q18. |
| Gold Удобный? | В коде слабо — усилить. |
| Connect device copy? | Вариант A + gold. |
| Убрать «следить»? | Да, strings. |
| Precise? | iOS Precise Location; explain + Settings. |
| Pet medicine / fake pins? | Custom field; rewrite saved copy. |
| Calendar black? | Light inset DatePicker. |
| Crash Yes hang? | Timeout + progress + toast. |
| Double UI green? | Presentation layer bug — audit sheet. |
| Antifake all broken? | Upload/poll/SLA + server; fix W1. |
| Parental bot? | Hide — дубль naming. |
| Call Filter missing? | Extension not in build or name mismatch. |

---

## 10. Честная готовность плана (ответ пилоту)

| Вопрос | Ответ |
|--------|--------|
| Все 36 скринов покрыты решением? | **Да** — матрица §10.1 (раньше Q02–05 / Q27–33 / Q34–36 были **сгруппированы**; ниже — **по одному Q**). |
| Все задачи из ТЗ владельца? | **Да** по смыслу §9 + §10.1. Пробел v1: не у каждой строки были готовые **полные** RU+EN фразы — закрыто в §10.2. |
| Анализ «как специалист по промпту»? | **Да** — §0 промпт + сверка с кодом якорей §1 + GATES §2. Не «на словах». |
| Логика работы предусмотрена? | **Да** критичные потоки §10.3 (invite · crash · antifake · map sheet · call filter). |
| Чеклист по каждой задаче/подзадаче? | **Да** — §10.1 атомарные `[ ]` на каждый Q. |
| «До мелочей 100% до кода»? | **План-канон 100%:** остаток = только evidence на device/prod (не дыры в ТЗ). См. §10.5 lock. |

---

## 10.1 Мастер-матрица Q01–Q36 (1 строка = 1 скрин · атомарный чеклист)

| Q | Суть | Wave | Факт сейчас | Решение (канон) | Подзадачи (ничего не забыть) |
|---|------|------|-------------|-----------------|------------------------------|
| **Q01** | Soft invite D+1 · TTL 3 дня | W4 | TTL 24h · soft нет | TTL 72h + sheet/notif D+1 | [ ] env 72h [ ] API expires_at [ ] AppStorage firstUse [ ] schedule D+1 [ ] sheet CTA invite [ ] dismiss [ ] copy 3 дня RU+EN [ ] no multi-circle |
| **Q02** | Incident «Быстрый разгон» sheet | W3 | нет | Explain sheet на tap иконки accel | [ ] icon [ ] title/body RU+EN [ ] count week [ ] CTA «Ясно» [ ] empty=0 honesty |
| **Q03** | Incident phone/distraction detail | W3 | нет | Explain sheet phone-use | [ ] icon [ ] title/body [ ] count [ ] CTA [ ] Motion permission tip |
| **Q04** | Incident hard brake detail | W3 | нет | Explain sheet brake | [ ] icon [ ] title/body [ ] count [ ] CTA |
| **Q05** | Strip 4 иконки под weekly | W3 | нет | Horizontal 4 counters + trend | [ ] layout [ ] tap→Q02–04 [ ] 4th speed/phone [ ] a11y |
| **Q06** | Weekly overview trips/km/max + PDF | W3 | modal thin | Cards + week/month + PDF Share | [ ] period pills [ ] max speed card [ ] trips/km [ ] member row [ ] PDF builder [ ] Share [ ] disclaimer |
| **Q07** | Premium value notifications | W5 | soft map only | 5 triggers + cap + deep-link Tariffs | [ ] matrix [ ] D+3 map [ ] antifake limit [ ] weekly digest Family+ [ ] places lock [ ] crash tip [ ] frequency cap [ ] RU+EN |
| **Q08** | Map avatar · FAB · invite · SOS | W2 | частично | Photo pin + FAB stack + SOS + invite | [ ] avatar circle+ring [ ] time bubble [ ] SOS left [ ] FAB locate/layers/+ [ ] invite banner [ ] storm not purple |
| **Q09** | Onboarding hero crop (boy) | W7 | Fill crop | Fit/align + asset verify | [ ] which Hero_0N [ ] asset = new PNG [ ] scaledToFit or align [ ] device shot |
| **Q10** | Onboarding hands/clutter | W7 | crop | Same + no side bleed | [ ] asset [ ] clip [ ] device |
| **Q11** | Onboarding «Где семья» hands | W7 | crop | Same for that page | [ ] page index [ ] asset [ ] device |
| **Q12** | Тарифы 3 уровня под Premium | W8 | сверху · техcopy | Move under Premium · simple · devices | [ ] move UI [ ] Free/Family/Premium devices from config [ ] no Fam/Pro EN [ ] no last-point jargon [ ] RU+EN |
| **Q13** | Back Удобный → Main | W0 | broken on root | back→Main | [ ] navigateToRoot(.main) [ ] a11y [ ] smoke |
| **Q14** | Bluetooth settings (Life360) | W9 | нет | Row «Скоро» or SKIP P4 | [ ] decision owner [ ] soon copy OR hide [ ] no fake toggle ON |
| **Q15** | Motion & Fitness | W9 | нет UI | Row → open Settings + copy | [ ] row [ ] openSettings [ ] why needed (trips) RU+EN |
| **Q16** | Call Blocking system screen | W6 | guide→Settings | Dual CTA + status refresh | [ ] open Settings [ ] 4-step guide [ ] scenePhase refresh [ ] entry: Проверить |
| **Q17** | Safari Content Blockers | W6 | blocker code есть | Safari guide + status | [ ] tip sheet [ ] SFContentBlocker state [ ] entry Wave A |
| **Q18** | Pin / avatar size editor | W2 | preview flag only | Photo + S/M/L + save | [ ] pick avatar [ ] sizes [ ] preview map [ ] persist UD |
| **Q19** | Gold «Удобный режим» Main | W8 | weak gold | Stronger gold tile | [ ] fill 0.18 [ ] stroke 2 [ ] badge [ ] device |
| **Q20** | Connect device empty | W8 | gray/complex | Variant A + gold CTA | [ ] copy A [ ] color storm+gold [ ] CTA invite [ ] RU+EN |
| **Q21** | Spy copy + Precise | W0 | spy in strings | Rewrite + Precise explain | [ ] remove следить [ ] always body [ ] precise hint [ ] Settings CTA [ ] EN |
| **Q22** | Pet medicine → custom | W0 | medicine toggle | Custom text field | [ ] TextField [ ] save [ ] keep walk/feed [ ] RU+EN ph |
| **Q23** | «Без фейковых точек» | W0 | in pet_saved_local | Rewrite strings | [ ] RU [ ] EN [ ] no fake |
| **Q24** | Calendar black digits | W0 | DatePicker dark | Light inset card | [ ] colorScheme light OR custom grid [ ] contrast [ ] selected gold |
| **Q25** | Crash Yes hang | W0 | await hang | Timeout 8s + progress + toast | [ ] progress [ ] timeout loc [ ] defer isSending [ ] success toast [ ] offline queue msg |
| **Q26** | Double UI / green bleed | W9 | presentation bug | Single layer sheet | [ ] find stacked Nav/bg [ ] clip [ ] device |
| **Q27** | Antifake Voice hang | W1 | upload stuck | Cancel/retry/timeout UX | [ ] cancel [ ] progress [ ] timeout copy [ ] retry [ ] auth check [ ] server job |
| **Q28** | Antifake Document hang | W1 | same | Prefer photo/PDF warn .txt | [ ] type gate [ ] same UX as Q27 |
| **Q29** | Document timeout error | W1 | SLA timeout | Honest retry + support | [ ] message RU+EN [ ] retry [ ] log jobId |
| **Q30** | Parental bot card | W9 | legacy component | **Hide** card (GO) | [ ] hide UI [ ] API safe [ ] Child door remains |
| **Q31** | Call Filter missing | W6 | .unknown possible | TF extension + name + honest UI | [ ] target in Archive [ ] Display Name [ ] Sync [ ] unknown copy |
| **Q32** | Video upload hang | W1 | same as voice | Size limit tip + cancel | [ ] max size UX [ ] poll SLA 300s [ ] cancel |
| **Q33** | Call check broken | W1 | same | Fix or honest «скоро» | [ ] smoke call [ ] or disable with copy |
| **Q34** | Map sheet half (invite visible) | W2 | no detents | Detent ~0.35 | [ ] fraction [ ] gesture [ ] video |
| **Q35** | Map sheet mid (chips+member) | W2 | no | Detent ~0.55 | [ ] chips [ ] member [ ] add person |
| **Q36** | Map sheet full / map tiny | W2 | no | Detent ~0.85 + reverse | [ ] list expand [ ] map shrink [ ] drag down fullscreen map |

**Итого подзадач:** ~170 атомарных `[ ]` · закрывать в checklist plan/fact по мере GO.

---

## 10.2 Локализация RU+EN (канон фраз · без сырых ключей)

Правило: ключ → сразу обе строки в `ru.lproj` + `en.lproj`. Ниже — **готовые тексты** для кода.

### Invite / soft (Q01)
| Key | RU | EN |
|-----|----|----|
| `family_invite_soft_title` | Пора пригласить близких | Time to invite your family |
| `family_invite_soft_body` | В семье безопаснее вместе. Пригласите кого-то — увидите друг друга на карте. | Family safety works best together. Invite someone to see each other on the map. |
| `family_invite_ttl_hint` | Коды приглашения действуют 3 дня. Если не успели — отправьте новый. | Invite codes work for 3 days. If it expired, send a new one. |
| `family_invite_soft_cta` | Пригласить | Invite |
| `family_invite_soft_dismiss` | Не сейчас | Not now |

### Driving incidents (Q02–Q06)
| Key | RU | EN |
|-----|----|----|
| `drive_week_title` | Отчёт о поездках за неделю | Weekly driving report |
| `drive_month_title` | Отчёт о поездках за месяц | Monthly driving report |
| `drive_period_this_week` | Эта неделя | This week |
| `drive_period_last_week` | Прошлая неделя | Last week |
| `drive_stat_trips` | Поездки | Trips |
| `drive_stat_km` | Всего км | Total km |
| `drive_stat_max_speed` | Макс. скорость | Max speed |
| `drive_inc_phone_title` | Телефон за рулём | Phone while driving |
| `drive_inc_phone_body` | Фиксируем, когда телефон мог отвлечь за рулём. Это оценка, не штраф. | We note when the phone may have been distracting. An estimate, not a ticket. |
| `drive_inc_accel_title` | Резкий разгон | Rapid acceleration |
| `drive_inc_accel_body` | Резкий разгон может означать опасное или невнимательное вождение. | Rapid acceleration can mean risky or distracted driving. |
| `drive_inc_brake_title` | Резкое торможение | Hard braking |
| `drive_inc_brake_body` | Резкая остановка — сигнал риска на дороге. | A hard stop can signal risk on the road. |
| `drive_inc_speed_title` | Превышение / риск скорости | Speeding risk |
| `drive_inc_speed_body` | Скорость выше обычного для участка — посмотрите отчёт. | Speed higher than usual for the area — review the report. |
| `drive_inc_count_fmt` | %d за период | %d this period |
| `drive_inc_got_it` | Ясно | Got it |
| `drive_empty_body` | Пока нет поездок. Включите доступ к движению и проедьте с телефоном. | No trips yet. Allow Motion access and take a drive with the phone. |
| `drive_pdf_export` | Выгрузить PDF | Export PDF |
| `drive_pdf_disclaimer` | Оценка для семьи, не страховой и не юридический отчёт. | A family estimate — not an insurance or legal report. |

### Map / permissions (Q08, Q18, Q21, Q34–36)
| Key | RU | EN |
|-----|----|----|
| `map_perm_always_body` | Так карта обновляется, когда приложение закрыто — вы видите, где телефоны семьи. | So the map can update when the app is closed — you see where family phones are. |
| `map_perm_precise_hint` | В Настройках iPhone включите «Точные» для ALADDIN — точка будет точнее. | In iPhone Settings turn on Precise Location for ALADDIN for a sharper pin. |
| `map_perm_open_settings` | Открыть Настройки | Open Settings |
| `map_pin_preview_title` | Как выглядит метка | How your pin looks |
| `map_pin_size_s` | Маленькая | Small |
| `map_pin_size_m` | Обычная | Medium |
| `map_pin_size_l` | Крупная | Large |
| `map_motion_row_title` | Движение и фитнес | Motion & Fitness |
| `map_motion_row_body` | Нужно для отчётов о поездках. Включается в Настройках iPhone. | Needed for driving reports. Turn on in iPhone Settings. |
| `map_bt_soon_title` | Bluetooth | Bluetooth |
| `map_bt_soon_body` | Рядом / метки — в скором времени. | Nearby / tags — coming soon. |

### Pet / calendar / crash (Q22–Q25)
| Key | RU | EN |
|-----|----|----|
| `pet_custom_reminder_ph` | Своё напоминание | Custom reminder |
| `pet_saved_local` | Сохранено на этом iPhone. Живая карта питомца появится позже. | Saved on this iPhone. Live pet map comes later. |
| `crash_confirm_sending` | Отправляем сигнал семье… | Notifying your family… |
| `crash_confirm_sent` | Семья получила сигнал | Family notified |
| `crash_confirm_fail` | Не удалось отправить. Попробуйте ещё раз или напишите в чат семьи. | Couldn’t send. Try again or message family chat. |
| `crash_confirm_offline` | Нет сети — сохраним и отправим позже. | You’re offline — we’ll save and send later. |

### Connect device / Main / Tariffs (Q12, Q19, Q20)
| Key | RU | EN |
|-----|----|----|
| `connect_device_title` | Подключите устройство близкого | Connect a family device |
| `connect_device_body_a` | Добавьте телефон близкого — увидите защиту и точку на карте. | Add a family phone — see protection and their place on the map. |
| `connect_device_cta` | Пригласить | Invite |
| `main_simple_badge` | Главный вход | Main entry |
| `tariffs_levels_title` | Что входит в тарифы | What’s in each plan |
| `tariffs_free_simple` | 1 устройство · базовая проверка · карта последней точки · ребёнок и SOS | 1 device · basic checks · last place on map · child & SOS |
| `tariffs_family_simple` | Несколько устройств · живая карта · Antifake · места и история дня | Several devices · live map · Antifake · places & day history |
| `tariffs_premium_simple` | Всё из Family · расширенные проверки · приоритетная поддержка | Everything in Family · more checks · priority support |
| *(device N)* | Подставить числа из тарифной матрицы при коде W8 | Same from config |

### Antifake (Q27–Q29, Q32–Q33)
| Key | RU | EN |
|-----|----|----|
| `antifake_upload_cancel` | Отменить | Cancel |
| `antifake_retry` | Повторить | Retry |
| `antifake_timeout_friendly` | Проверка заняла слишком много времени. Проверьте сеть и попробуйте ещё раз. | The check took too long. Check your network and try again. |
| `antifake_doc_prefer_photo` | Лучше фото или PDF штрафа/договора. Текстовый файл может не подойти. | Prefer a photo or PDF of the fine/contract. A text file may not work. |
| `antifake_video_size_hint` | Большое видео грузится дольше. Попробуйте короткий ролик до 25 МБ. | Large videos take longer. Try a short clip under 25 MB. |
| `antifake_call_soon` | Проверка звонка скоро будет стабильнее. Пока можно проверить текст или голос. | Call check will be more stable soon. For now try text or voice. |
| `antifake_sync_fail` | Не удалось связаться с сервером проверки. Повторите через минуту. | Couldn’t reach the check server. Try again in a minute. |

### Call Directory / Safari / bot (Q16, Q17, Q30, Q31)
| Key | RU | EN |
|-----|----|----|
| `calldir_unknown_build` | Расширение звонков не найдено в этой сборке. Обновите приложение из TestFlight. | Call extension isn’t in this build. Update the app from TestFlight. |
| `adblock_safari_steps_title` | Включите в Safari | Turn on in Safari |
| `adblock_safari_steps_body` | Настройки → Safari → Расширения → ALADDIN → включите. | Settings → Safari → Extensions → ALADDIN → turn on. |
| `parental_bot_hidden_note` | *(не показывать пользователю — карточку убрать)* | *(hide card)* |

### Premium nudges (Q07)
| Key | RU | EN |
|-----|----|----|
| `premium_nudge_map_title` | Больше спокойствия на карте | More peace of mind on the map |
| `premium_nudge_map_body` | В Family — живая карта и больше мест для семьи. | Family unlocks live map and more places. |
| `premium_nudge_antifake_title` | Нужно больше проверок? | Need more checks? |
| `premium_nudge_antifake_body` | В Family и Premium — расширенный Antifake для семьи. | Family and Premium include more Antifake for your family. |
| `premium_nudge_cta` | Смотреть тарифы | See plans |

---

## 10.3 Логика потоков (предусмотрено)

### A. Soft invite
```
first_open_map_or_home → store ts
→ +24h && members < 2 && !dismissed
→ local notif + in-app sheet
→ CTA → existing invite flow
→ codes expire_at = now+72h (server)
```

### B. Crash «Да, нужна помощь»
```
tap Yes → isSending
→ Task timeout 8s around location
→ FamilyImOkService.sendNeedHelp
→ success toast + dismiss | fail toast + re-enable
→ offline → queue + crash_confirm_offline
```

### C. Antifake media
```
pick file → validate type/size
→ upload (status uploading + Cancel)
→ enqueue job → poll ≤ SLA
→ verdict UI | timeout → antifake_timeout_friendly + Retry
→ sync/network fail → antifake_sync_fail
Text path: separate VM — smoke always first
```

### D. Map sheet detents
```
drag sheet y → mapHeightFraction = f(y)
detents: 0.25 (map max) / 0.55 / 0.85 (list max)
chips + members only fully usable ≥ 0.55
```

### E. Call Filter
```
refresh CX status on appear + scenePhase active
.enabled → green ON
.disabled → guide + Open Settings
.unknown → calldir_unknown_build (не врать «включите»)
```

---

## 10.4 Что ещё сделать при коде (мелочи, не забыты)

- [ ] Числа устройств Free/Family/Premium — из живой тарифной матрицы, не хардкод «наугад» → **W8 lock §10.5**
- [ ] PDF шрифты: системные, кириллица ок
- [ ] Trend arrows на Q05 — только если есть реальные previous-week counts; иначе без стрелок
- [ ] Antifake text smoke в том же W1 → **W1 lock §10.5**
- [ ] Evidence folder `qa_device_2026-11-05/evidence/Qxx_after.jpg` → **после GO на сборку §10.5**
- [ ] Обновлять `FAMILY_SAFETY_PLAN_FACT_CHECKLIST.md` на каждый закрытый Q
- [ ] Не коммитить bot/`.env` · iOS только master

---

## 10.5 Lock «остаток без кода/девайса» — обязательно в плане (не опционально)

| Id | Когда | Что сделать | Done when |
|----|-------|-------------|-----------|
| **L-W8-DEVICES** | Wave **W8** (тарифы Q12) | Читать лимиты устройств из **живой** матрицы (`SubscriptionManager` / `AppConfig` / тарифный SSOT), подставлять в `tariffs_*_simple` через `String(format:)`. **Запрет:** хардкод «3/5/10» наугад. | grep: format args from config; UI shows real N |
| **L-W1-AF-SMOKE** | После кода **W1** Antifake | Smoke на прод/staging `:8002`: text · doc(photo) · voice 5s · video small · call (или honest disabled). Запись в `qa_device_…/evidence/antifake_smoke_YYYYMMDD.md` (status codes, jobId, no secrets). | 4/5 PASS или documented skip |
| **L-DEV-EVIDENCE** | Только после **`GO на сборку`** | Device screenshots after-fix: `evidence/Qxx_after.jpg` для закрытых Q; обновить FACT checklist. **Запрет:** агент сам `xcodebuild` без GO. | folder + checklist rows |

Эти три пункта — **часть DoD** соответствующих волн, не «потом когда-нибудь».

---

**Конец плана v1.2** (+ §10.5 lock).

### Журнал исполнения

| Дата | GO | Статус |
|------|-----|--------|
| 2026-11-05 | **W0** | ✅ код: Q13 · Q21 · Q22 · Q23 · Q24 · Q25 · §10.5 в план. Device evidence — после `GO на сборку`. |

---

## 11. Статус 36 скринов — просто (код на 2026-11-05)

Легенда: ✅ сделано в коде (W0) · ⬜ ещё нет · 📋 только в плане · ⏳ ждёт GO на сборку (скрин after)

| # | Экран / задача | Код | Волна |
|---|----------------|-----|-------|
| Q01 | Invite soft D+1 · коды 3 дня | ✅ код | W4 (TTL default 72h · soft sheet D+1 once) |
| Q02 | Инцидент «быстрый разгон» | ✅ код | W3 (explain sheet · count 0 until trips) |
| Q03 | Инцидент телефон за рулём | ✅ код | W3 |
| Q04 | Инцидент резкое торможение | ✅ код | W3 |
| Q05 | Полоска 4 иконки weekly | ✅ код | W3 |
| Q06 | Отчёт поездки/км/макс + PDF | ✅ код | W3 (local PDF + Share) |
| Q07 | Premium уведомления ценности | ✅ код | W5 (map soft + premium_nudge_* · Antifake gate) |
| Q08 | Карта: аватар · FAB · SOS · invite | ✅ код | W2 (avatar pin + letter · FAB already) |
| Q09 | Онбординг crop (голова) | ✅ код | W7 (`scaledToFit` + letterbox) |
| Q10 | Онбординг руки / clutter | ✅ код | W7 |
| Q11 | Онбординг «Где семья» руки | ✅ код | W7 |
| Q12 | Тарифы 3 уровня под Premium | ✅ код | W8 (+L-W8-DEVICES live N) |
| Q13 | Back Удобный → Main | ✅ | W0 |
| Q14 | Bluetooth в настройках карты | ✅ код | W9 (honest «скоро») |
| Q15 | Движение и фитнес | ✅ код | W9 (row + Open Settings) |
| Q16 | Call Blocking deep-link/guide | ✅ код | W6 (scenePhase refresh + guide) |
| Q17 | Safari Content Blocker tip | ✅ код | W6 (steps + Open Settings) |
| Q18 | Редактор метки/аватара | ✅ код | W2 (S/M/L + preview) |
| Q19 | Gold «Удобный режим» на Main | ✅ код | W8 (badge + stroke 2pt) |
| Q20 | Подключите устройство (copy+цвет) | ✅ код | W8 (storm + gold · copy A) |
| Q21 | Убрать «следить» · Precise | ✅ | W0 |
| Q22 | Питомец: своё напоминание | ✅ | W0 |
| Q23 | Убрать «фейковые точки» | ✅ | W0 |
| Q24 | Календарь: читаемые цифры | ✅ | W0 |
| Q25 | Crash «Да, нужна помощь» hang | ✅ | W0 |
| Q26 | Двойной UI / зелёная линия | ✅ код | W9 (habits strip removed + clip) |
| Q27 | Antifake Голос | ✅ код | W1 (cancel/retry/SLA · ⏳ L-W1-AF-SMOKE) |
| Q28 | Antifake Документ upload | ✅ код | W1 (photo/PDF tip) |
| Q29 | Antifake Документ timeout | ✅ код | W1 (friendly timeout) |
| Q30 | Бот родительского контроля | ✅ код | W9 (UI hidden) |
| Q31 | ALADDIN Call Filter | ✅ код | W6 (`calldir_unknown_build`) |
| Q32 | Antifake Видео | ✅ код | W1 (size tip · SLA 300s) |
| Q33 | Antifake Звонок | ✅ код | W1 (`antifake_call_soon`) |
| Q34 | Map sheet detent half | ✅ код | W2 (`sheetExpansion` snap) |
| Q35 | Map sheet detent mid | ✅ код | W2 |
| Q36 | Map sheet full / map fullscreen | ✅ код | W2 |

**Итого кода:** 36 / 36 ✅ код (W0–W9).  
**L-W1-AF-SMOKE:** ✅ 5/5 (2026-11-06) — корень Q27–Q33 был на сервере: воркер Antifake без `.env` падал на каждой медиа-джобе с 16.10. Починено drop-in `env.conf`. Evidence: `qa_device_2026-11-05/evidence/antifake_smoke_20261106.md`.  
**Device evidence:** ⏳ после `GO на сборку` + L-DEV-EVIDENCE.  
**Не путать:** ✅ код ≠ ✅ device PASS.
