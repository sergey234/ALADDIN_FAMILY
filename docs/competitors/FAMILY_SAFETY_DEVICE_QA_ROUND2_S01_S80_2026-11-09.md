# Family Safety Device QA Round 2 — S01–S80

**Дата:** 2026-11-09 · **обновлено:** мастер доделки 88  
**Предыдущий план:** [`FAMILY_SAFETY_DEVICE_QA_MASTER_PLAN_2026-11-05.md`](FAMILY_SAFETY_DEVICE_QA_MASTER_PLAN_2026-11-05.md) (Q01–Q36)  
**Место семьи канон B:** [`FAMILY_LOCATION_CANON_B_PLAN_2026-11-09.md`](FAMILY_LOCATION_CANON_B_PLAN_2026-11-09.md)  
**⭐ МАСТЕР доделки до 100%:** [`FAMILY_SAFETY_MASTER_FINISH_88_PLAN_2026-11-09.md`](FAMILY_SAFETY_MASTER_FINISH_88_PLAN_2026-11-09.md) — **не закрывать Round2 раньше**  
**Code-fact:** [`FAMILY_SAFETY_CODE_FACT_CHECKLIST_100_2026-11-09.md`](FAMILY_SAFETY_CODE_FACT_CHECKLIST_100_2026-11-09.md)  
**Скрины:** [`qa_device_2026-11-09/FILE_INDEX.txt`](qa_device_2026-11-09/FILE_INDEX.txt) · S19: `qa_device_2026-11-09/S19_life360_member/`  
**Полный ТЗ:** [`FAMILY_SAFETY_DEVICE_QA_ROUND2_FULL_TZ_CHECKLIST_2026-11-09.md`](FAMILY_SAFETY_DEVICE_QA_ROUND2_FULL_TZ_CHECKLIST_2026-11-09.md)  
**Матрица 88:** [`FAMILY_SAFETY_DEVICE_QA_ROUND2_SCREEN_MATRIX_88.md`](FAMILY_SAFETY_DEVICE_QA_ROUND2_SCREEN_MATRIX_88.md)  
**Факт:** [`FAMILY_SAFETY_PLAN_FACT_CHECKLIST.md`](FAMILY_SAFETY_PLAN_FACT_CHECKLIST.md)  
**Figma-долг:** [`FIGMA_FAMILY_SAFETY_ML_PROMPTS.md`](FIGMA_FAMILY_SAFETY_ML_PROMPTS.md) (не OB_*)  
**Сборка:** `CFBundleVersion` **19** (push ⛔)

**Очередь:** (1) **GO на код FIX-P0** (OB + sheet 95% + pin tap + member one-scroll + crop) · (2) волны COPY/HAPTIC/TRIPS… · (3) FIG-L · (4) GO на сборку / device 88. UI: **Тихая зона**.

---

## 0. Статус Q01–Q36 (handoff)

| Факт | Статус |
|------|--------|
| Код W0–W9 / Q01–Q36 | 36/36 ✅ код |
| L-W1-AF-SMOKE | 5/5 ✅ (2026-11-06) |
| Xcode build | ✅ (2026-11-09, owner) · build **18** |
| L-DEV-EVIDENCE Qxx_after | ⏳ ждёт `GO на сборку` / device QA владельца |

**Регресс онбординга:** W7 перевёл hero на `scaledToFit`+letterbox → отступы на всех 8 OB. Round2 R0 возвращает full-bleed hybrid.

---

## 1. Запрос владельцу — S19 (+7 Life360) → **ПОЛУЧЕНО 8 скринов**

| # | ID | Что на скрине | Задача в Round2 |
|---|-----|---------------|-----------------|
| 1 | **S19a** | Member sheet «Сергей»: адрес, «С 15:27», «Сохранить место», поездки недели, Speeding/Невнимательность/Разгон (locks), FAB шапка | Паритет sheet: имя+адрес+время+CTA+weekly trips+driving locks+hat FAB |
| 2 | **S19b** | Trip detail Сб 7 нояб. (Хостел → маршрут 0,2 км) | Карточка поездки: карта+старт/финиш+время/км |
| 3 | **S19c** | Trip Sun 8 нояб. (5,7 км маршрут на карте) | То же + длинный маршрут |
| 4 | **S19d** | Places day: unlock weekly report, дата, «0 мин», Сохранить место | История мест дня + paywall weekly |
| 5 | **S19e** | Gold upsell «30-дневная история» | Paywall истории (наша копия ALADDIN, не Life360 Gold) |
| 6 | **S19f** | Drive trip: режим руль, 59 км/ч, «1 рискованное событие» | Driving summary + risk event |
| 7 | **S19g** | **ПУШ** «Срочный сигнал семье / Нужна помощь близкого» | **R10 deep-link** — НЕ Удобный режим |
| 8 | **S19h** | Places list: Львовская 15 мин, Лесная 1ч20, «В …» префикс | Список мест + грамматика «В» |

Файлы: `qa_device_2026-11-09/S19a_…` … `S19h_…` + строки в `FILE_INDEX.txt`.

---

## 2. Промпт агента

```text
Роль: Principal iOS + Family Safety (ALADDIN). Mech Pilot: пилот=владелец, меха=агент.
SSOT: docs/competitors/FAMILY_SAFETY_DEVICE_QA_ROUND2_S01_S80_2026-11-09.md
Предыдущее: FAMILY_SAFETY_DEVICE_QA_MASTER_PLAN_2026-11-05.md (Q01–Q36 код ✅; L-DEV-EVIDENCE ⏳)
Корни: ALADDIN_iOS · ветка master · Origin ALADDIN_FAMILY · bot∉iOS commit.
Правила: no mock/sfm_mock · real GPS/speed/trips · RU+EN localized() + strings · no raw keys ·
localization-megafile-safe · ask-before-ios-build · ask-before-important-ops · repowise-ios first.
Навигация: не ломать стеки; haptic — helper + очередь, без mass rewrite.
GATES: G1 UI/copy · G2 real data · G3 loc · G4 nav · G5 contrast.
Сейчас делай ТОЛЬКО: <WAVE / Sxx>.
```

---

## 3. Волны R0–R9

| Волна | Скрины | Статус кода |
|-------|--------|-------------|
| Meta | FILE_INDEX · Xcode journal · S19 request | ✅ docs |
| R0 | S01–S02 onboarding full-bleed | ✅ код (Fill+zoom hybrid) |
| R1 | S08 S09 S59 S60 S63 S70 S80 contrast | ✅ код (gold title, hide prose, time limits, family list) |
| R2 | S05 S06 S72 S73 antifake copy | ✅ код (short banner, no disclaimer, voice **30s** owner GO) |
| R3 | S07 S15 S67–S69 S76 call/safari | ✅ код (ALADDIN X AI copy, filter short strings) |
| R4 | S13 S14 S16 S54 tariffs | ✅ код (auto trial, antifake bullets); S16 table polish partial |
| R5 | S03 S10 S17 S19 S29 S53 S71 map/haptic | ✅ код (speed gate, scroll haptic, AvatarCropEditor); S19 ⏳ +7 screens |
| R6 | S20–S28 S42 S44 S58 S61–62 S77 trips/hats | ✅ код (invisible-hat FAB+slider); trips play/Figma assets partial |
| R7 | S11 S12 S31–41 S45–52 S55–57 circle/notifs | 📋 foundation (TTL was W4 72h); deeper parity next wave |
| R8 | S64–66 S74 monitoring | ✅ код (pipeline copy, routes, roadside hide, day strip) |
| R9 | S18 S43 S51 S75 S78–79 polish | ✅ policy lock (no Yandex scrape); visual polish iterative |

Evidence after: `qa_device_2026-11-09/evidence/Sxx_after.jpg` — только после `GO на сборку`.

---

## 4. Журнал исполнения Round2

| Дата | Волна | Статус |
|------|-------|--------|
| 2026-11-09 | Meta | ✅ Xcode в §11 · FACT · FILE_INDEX 80 · S19 request documented |
| 2026-11-09 | R0–R6,R8 | ✅ код в репо (см. §3). Device evidence ⏳ GO на сборку |
| 2026-11-09 | R7/R9 | 📋/partial — notifs matrix + Life360 visual density + FIG-L debt |
| 2026-11-09 | S19a–h + R10 | ✅ 8 скринов indexed · диагноз пуша→SimpleHome · R10 в §7 · сборка ⛔ |
| 2026-11-09 | OWNER GO A1+B1+C1/C2 | ✅ · матрица 88 §14 · R10 код FamilyPushDeepLink · R5.5 C1/C2/B1 strings · сборка ⛔ |
| 2026-11-09 | Voice 30s + FULL TZ checklist | ✅ AntifakeQuickVoice 30s · FULL_TZ_CHECKLIST MD · вердикт: план≈100% · код≠100% · сборка ⛔ |
| 2026-11-09 | WAVE R5.5 | ✅ member sheet weekly+locks · trip row time/max/risk · C1 streets · RU/EN · play-map 📋 · сборка ⛔ |
| 2026-11-09 | Haptic + AF timeout | ✅ day strip haptic · timeout copy dedupe · Retry text/media/quick voice · сборка ⛔ |
| 2026-11-09 | OWNER GO fork pack | ✅ Trial A · Tariffs C · Circles B · Pet B · Snowball B · Places autocomplete · Play A · BT A · BG B · Filter C · Call A · в FULL_TZ §2.2 · сборка ⛔ |
| 2026-11-09 | Loc §2.6–2.8 | ✅ аудит 88 · ключи S30+Circles B прописаны · WAVE: S30 completer → метки B · сборка ⛔ |
| 2026-11-09 | S30 code | ✅ keys ru+en · PlaceAddressSearchCompleter · GeofencesSettingsModal + chips Other · next Circles B · сборка ⛔ |
| 2026-11-09 | Circles B | ✅ keys · FamilyGroupLabelStore + FamilyGroupsModal · map filter · без 2-го roster · next Trial A / Tariffs C… · сборка ⛔ |
| 2026-11-09 | TrialA→BGB | ✅ loc+code: Trial A · Tariffs C · Play A · Snowball B · S09 A · Filter C · BG B · сборка ⛔ |

---

## 5. Чеклист (атомарно)

### Meta
- [x] M1 Xcode ✅ в старый план §11 + FACT
- [x] M2 `qa_device_2026-11-09/` + FILE_INDEX S01–S80
- [ ] M3 L-DEV-EVIDENCE Q01–Q36 (владелец + GO device)
- [x] M4 Запрос 7 скринов S19 → **получено 8 (S19a–h)** · §1 обновлён

### R0–R9 + R10
См. §3 / §7 / §9. **Открыто до сборки:** R10 (пуши), R5.5 (S19 sheet parity), M3 evidence.

---

## 6. Локализация

- Сначала `Resources/Localization/{ru,en}.lproj/Localizable.strings`
- LocManager — только точечный StrReplace
- `./scripts/verify_localization_manager_integrity.sh` после правок mega-file
- Имена в Settings: **ALADDIN X AI** (app) · extension **ALADDIN Call Filter**

---

## 7. R10 — Push deep-link (S19g + ВСЕ пуши) ⏳ код не закрыт

### Почему сейчас открывается «Удобный режим»

1. Cold start родителя: `PayPainsUIFlags.shouldOpenSimpleHomeAtLaunch` → **SimpleHome** (= Удобный режим).
2. Пуш **S19g** (`FamilyUrgentSignalService`): `type=family_urgent_signal`, **нет `deepLink`**, нет `member_id`.
3. `NotificationManager.handleDefaultAction`: нет ветки для `family_urgent_signal` / `need_help`.
4. Даже `need_help` кладёт `deepLink: aladdin://family`, но `UnicornDeepLinkRouter` понимает только `aladdin://family/habits` → **nil** → навигация не срабатывает → остаётся SimpleHome.

### Куда ДОЛЖЕН переходить тап (канон)

| Тип пуша | Куда (логика семьи) | Deep link (предложение) |
|----------|---------------------|-------------------------|
| **Срочный сигнал / Need help** (S19g) | Карта семьи → фокус на member → sheet как S19a (место + связаться) | `aladdin://family/map?member=<id>&focus=sos` |
| Я ок / ImOK | Карта / Family presence того member | `aladdin://family/map?member=<id>&focus=im_ok` |
| Батарея критическая | Карта / member sheet | `aladdin://family/map?member=<id>&focus=battery` |
| Geofence arrive/leave / no-show | Карта + place / событие | `aladdin://family/location` (уже есть в store) → **довести** до map+place |
| Привычки / medicine | Экран Семья → habits | `aladdin://family/habits` ✅ уже |
| Лимиты / shield ask parent | Семья → limits | `aladdin://family/limits` → **довести** |
| Угроза / bypass / antivirus | Network Protection / Antifake / соответствующий экран | уже частичные deepLink |
| Тарифы / trial | Tariffs | `aladdin://tariffs` ✅ |
| Post-call / antifake check | Antifake / post-call | ✅ |
| Companion / wellness / focus | соответствующие экраны | ✅ Unicorn |
| Family chat | Family chat | `NavigateToFamilyChat` ✅ |
| **Без type / битый deepLink** | **НЕ** SimpleHome по умолчанию для family category → fallback **Family map**, не Удобный режим | — |

### Задачи R10 (атомарно, без двойной работы с Q01–Q36)

- [ ] R10-1 `FamilyUrgentSignalService`: добавить `deepLink` + `member_id` + `display_name` + `type` стабильный
- [ ] R10-2 `FamilyImOkService` need_help/im_ok: deepLink → `aladdin://family/map?member=…&focus=sos|im_ok` (не голый `aladdin://family`)
- [ ] R10-3 `NotificationManager.handleDefaultAction`: ветки `family_urgent_signal`, `need_help`, `im_ok`, battery, geofence
- [ ] R10-4 Router: `aladdin://family/map` → `WhereIsPhone` / Family map + pending member focus (не SimpleHome)
- [ ] R10-5 Cold-start: если pending push deepLink family/sos — **override** `shouldOpenSimpleHomeAtLaunch`
- [ ] R10-6 Аудит 100% `deepLink` / `type` в `Core/Family/*` + NotificationManager senders → таблица в evidence
- [ ] R10-7 Device QA: тап S19g → карта+member, не Удобный режим

**Не дублировать:** QR TTL 72h (W4), spy Always Allow copy (R7 foundation), SimpleHome gold child (R1) — это другие задачи.

---

## 8. S19a–h — задачи паритета (после пушей / вместе с R5.5)

| ID | Было (ALADDIN) | Будет |
|----|----------------|-------|
| S19a | Частичный member sheet | Полный sheet: адрес «Возле…», «С HH:MM», Сохранить место, weekly trips card, 3 driving locks, FAB шапка |
| S19b–c | Trip cards есть | Карта+маршрут+флаг финиша+км/время как Life360 density |
| S19d | Places day | Unlock weekly + список остановок + Сохранить место |
| S19e | Свой paywall | ALADDIN-копирайт 30-дн. истории (не «Gold / 6,9 млн») — **согласовать текст** |
| S19f | Driving | Режим руль + скорость + «N рискованных» |
| S19g | → Удобный режим ❌ | → карта+SOS member ✅ (R10) |
| S19h | Places list | Убрать лишнее «В » перед улицей; duration pills |

---

## 9. Полная картина задач Round2 (was → will) — на согласование

| ID | Скрин/тема | Было | Решение / будет | Код | Device |
|----|------------|------|-----------------|-----|--------|
| M1 | Xcode | не в старом журнале | ✅ build 18 в §11/FACT | ✅ | — |
| M2 | FILE_INDEX | нет | S01–S80 + S19a–h | ✅ | — |
| M3 | L-DEV-EVIDENCE Q01–Q36 | код есть | evidence after — **владелец + GO** | ⏳ | ⏳ |
| M4 | S19 Life360 | запрос | **8 скринов получены** | ✅ | — |
| R0 | S01–S02 onboarding | letterbox Fit | full-bleed Fill+zoom hybrid | ✅ | ⏳ |
| R1 | S08/S09/S59… contrast | серый/простыни | gold title, hide prose, time limits | ✅ | ⏳ |
| R2 | S05/S06/S72 antifake | disclaimer+долгий voice | short banner, **30s** voice | ✅ | ⏳ |
| R3 | S07 Call Filter | ALADDIN vs Call Filter | «ALADDIN X AI» + короткие filter strings | ✅ | ⏳ |
| R4 | S13–16 tariffs | ручной trial | auto trial + antifake bullets | ✅ | ⏳ |
| R5 | map/haptic/crop | speed без gate | gate+scroll haptic+AvatarCrop | ✅ | ⏳ |
| R5.5 | S19a–h sheet | нет паритета | §8 выше | 📋 | ⏳ |
| R6 | hats/trips | quiet zone | FAB шапка + slider | ✅ | ⏳ |
| R7 | circle/notifs UI | foundation | TTL/spy; deeper S31–57 later | 📋 | ⏳ |
| **R10** | **все пуши / S19g** | **→ Удобный режим** | **→ map/SOS/family dest** | ⏳ | ⏳ |
| R8 | monitoring/parental | mismatch+roadside | pipeline copy, hide roadside | ✅ | ⏳ |
| R9 | polish/Yandex | scrape risk | no scrape lock; FIG-L debt | ✅ policy | ⏳ |

**Сборка / симулятор:** только после **100% задач кода (вкл. R10 + R5.5 минимальный deep-link)** и явного **GO на сборку**.

---

## 10. OWNER GO — тексты + продуктовые развилки (2026-11-09)

### Тексты

| | Выбор | RU | EN |
|--|-------|----|----|
| **A** | **A1 ✅** | Срочный сигнал семье / Нужна помощь близкого… | Family urgent safety signal / … |
| **B** | **B1 ✅** | История мест за 30 дней | 30-day location history |
| **C** | **C1+C2 ✅** | без «В » · «Возле: %@» | Near: %@ |
| **Voice** | **30 с ✅** | Быстрая проверка голоса (30 сек) | Quick voice check (30 sec) |

### Продукт (полный канон: FULL_TZ_CHECKLIST §2.2)

| Тема | GO |
|------|-----|
| Trial S13 | **A** auto + убрать из тарифов |
| Таблица S14/S16 | **C** карточки + сравнение; фичи реальные |
| Круги S55–57 | **B** метки в Семье, не 2-й roster; UX 100% |
| Pet/Flight | **B** скрыть; иначе «В скором времени» |
| S09 панель | **A** тёмный+золото |
| Snowball S18 | **B** палитра в коде сразу |
| Места S30 | гибрид + **MKLocalSearchCompleter** |
| Antifake copy | **C + короткий A** у кнопки |
| Фильтр S67–69 | **C** статус + как включить |
| S63 soft reminder | **A** hide flag |
| BT/Motion S22 | **A** BT не просим; motion = SOS |
| BG S21 | **B** экран + Settings |
| Play S61–62 | **A** делать сейчас |
| Блокировки S75 | **C** ничего нового |
| Имя Call | **A** ALADDIN X AI |

SSOT деталей: `FAMILY_SAFETY_DEVICE_QA_ROUND2_FULL_TZ_CHECKLIST_2026-11-09.md` §2.2–2.5.

### D) Driving locks (S19a)

Оставить замок до тарифа (как Life360) **или** показать реальные события если есть данные.
**Рекомендация:** замок + честный paywall ALADDIN; без фейковых цифр.

### E) FAB тихая зона

Уже в R6: FAB + радиус. Copy с 2026-11-09: **«Создать тихую зону»** (паритет Life360 quiet zone, канон B).

---

## 11. Чеклист «ничего не пропустить» vs исходные замечания владельца

| Замечание владельца (начало) | В плане? | Статус |
|------------------------------|----------|--------|
| Пронумеровать все скрины S01–S80 | ✅ FILE_INDEX | ✅ |
| Q01–Q36 + Xcode recall | ✅ §0 | код ✅ · evidence ⏳ |
| MD план + полный чеклист | ✅ этот файл | ✅ |
| Life360 сравнение | ✅ S19 + S19a–h | partial → R5.5 |
| Реальные данные / no mock | ✅ GATES G2 | policy |
| RU+EN без raw keys | ✅ §6 | overrides ✅ |
| Hybrid best-of | ✅ R0 Fill+zoom | ✅ код |
| Per-screen improvements | ✅ R0–R9 | ✅/📋 |
| Промпт агента в начале плана | ✅ §2 | ✅ да, описан |
| Варианты текстов на согласование | ✅ §10 | **ждём выбор A/B/C** |
| Варианты задач на согласование | ✅ §9 | **ждём OK R10/R5.5** |
| Не двойная работа vs Q01–Q36 | ✅ §7 note | checked |
| 8 досланных скринов | ✅ §1 S19a–h | indexed |
| Пуш → не Удобный режим | ✅ §7 R10 | **код ⏳** |
| Сборка только после 100% | ✅ §9 | соблюдаем |

---

## 12. Журнал дополнения 2026-11-09 (вечер)

| Что | Статус |
|-----|--------|
| S19a–h symlink + FILE_INDEX | ✅ |
| Диагноз пуша → SimpleHome | ✅ (нет deepLink + launch SimpleHome) |
| R10 задачи в SSOT | ✅ добавлены |
| Код R10 | ⏳ после согласования §10 |
| xcodebuild | ⛔ без GO · после 100% |
## 13. OWNER GO тексты (2026-11-09)

| Тема | Выбор |
|------|-------|
| A пуш срочный | **A1** (текущий RU/EN) |
| B история 30 дней | **B1** «История мест за 30 дней» / «30-day location history» |
| C places «В » | **C1** убрать «В » у улиц + **C2** «Возле:» на sheet |
| R10 + R5.5 | **GO на код** · сборка только после 100% + отдельный GO |

### Push routing (зафиксировано в плане)

| Тип | Куда |
|-----|------|
| Срочный сигнал / Нужна помощь | Карта + member SOS sheet |
| Я ок | Карта / presence member |
| Батарея | Карта / member |
| Geofence / no-show | Карта + место |
| Привычки | Семья → habits |
| Лимиты / shield | Семья → limits |
| Угроза / bypass / AV | Network Protection / Antifake |
| Тарифы | Tariffs |
| Post-call / companion / focus | Свои экраны |
| Без type | Fallback **карта семьи**, не Удобный режим |

---

## 14. Матрица 88 скринов — было → будет → текст

**Счётчик:** 88 экранных задач · ~116 экранных подзадач (база+extras S19/notif) · +10 push-route · +7 атомов R10-1…7 ≈ **133 атомарных** до device evidence.

| ID | Экран | Волна | Было | Будет | Текст |
|----|-------|-------|------|-------|-------|
| S01 | onboarding_a | R0 | letterbox Fit | full-bleed Fill+zoom | (hero, без сырых ключей) |
| S02 | onboarding_b | R0 | letterbox Fit | full-bleed Fill+zoom | как S01 |
| S03 | map_mom_view | R5 | карта/пины | density + haptic | map_anti_spy_note короткий |
| S04 | map_adjacent | R5 | смежный map | тот же стек | — |
| S05 | antifake_disclaimer | R2 | длинный disclaimer | short banner | короткий баннер |
| S06 | antifake_verdict | R2 | пустой disclaimer | hide empty | вердикт без пустого текста |
| S07 | ios_call_blocking | R3 | имя ≠ app | ALADDIN X AI | ALADDIN X AI |
| S08 | simple_child | R1 | слабый контраст | gold title | золотой заголовок ребёнка |
| S09 | parental_panel | R1 | слабый контраст | contrast+copy | читаемая панель |
| S10 | speed_181_haptic | R5 | без gate | gate+SelectionHaptic | — |
| S11 | qr_invite | R7 | TTL | 72h ✅ W4 | QR 72 часа |
| S12 | always_allow_spy | R7 | spy-tone | честный anti-spy | короткая честная формулировка |
| S13 | tariffs_trial | R4 | ручной trial | auto trial | trial авто |
| S14 | tariffs_premium | R4 | bullets | antifake bullets | фичи antifake |
| S15 | call_filter_trunc | R3 | обрезка | короткие strings | короткие подписи |
| S16 | tariffs_table | R4 | таблица partial | polish | — |
| S17 | avatar_crop | R5 | нет crop | AvatarCropEditor | — |
| S18 | sections_color | R9 | цвета | polish iterative | — |
| S19 | life360_avatar_tap | R5.5 | слабый sheet | → S19a–h | см. S19a |
| S20 | invisible_hat | R6 | quiet zone | FAB шапка | Создать шапку-невидимку |
| S21 | bg_refresh | R6 | BG refresh | гайд доступа | — |
| S22 | bt_motion | R6 | BT/motion | гайд доступов | — |
| S23 | journal_map | R6 | журнал | trip journal density | — |
| S24 | trip_car_chrono | R6 | хроно | trip car card | — |
| S25 | trip_passby | R6 | pass-by | passby card | — |
| S26 | trip_route | R6 | маршрут | route+map | — |
| S27 | hat_radius | R6 | радиус | slider | — |
| S28 | trip_details | R6 | детали | detail card | — |
| S29 | pin_shape | R5 | пин | pin parity | — |
| S30 | places_big | R5.5 | places | C1+C2 | Возле: / без «В » |
| S31 | event_create | R7 | событие | create event | — |
| S32 | event_who | R7 | кто | who picker | — |
| S33 | loc_notifs | R7+R10 | локальные пуши | deep-link карта+место | — |
| S34 | notif_battery | R10 | → Удобный режим | → карта/member | батарея близкого |
| S35 | notif_trips | R10 | → Удобный режим | → карта/trips | поездки |
| S36 | notif_safety | R10 | → Удобный режим | → карта/SOS | безопасность |
| S37 | notif_weather | R7 | weather | weather/map dest | — |
| S38 | notif_events | R7 | event notif | → event | — |
| S39 | notif_pet | R7 | pet Life360 | N/A не копируем | — |
| S40 | loc_access | R7 | доступ GPS | честный copy | — |
| S41 | circle_manage | R7 | круг | manage семьи | — |
| S42 | hats_access | R6 | доступ шапок | hat permissions | — |
| S43 | ui_compare_60 | R9 | compare | liked patterns | — |
| S44 | hat_settings | R6 | settings шапки | hat sheet | — |
| S45 | activity_share | R7 | share | activity share | — |
| S46 | leave_circle | R7 | leave | leave family | — |
| S47 | account_profile | R5 | профиль | profile+crop | — |
| S48 | flight_monitor | R7 | рейсы L360 | N/A later | — |
| S49 | lost_pets | R7 | pets | N/A | — |
| S50 | pet_alert | R7 | pet alert | N/A | — |
| S51 | ui_compare_liked | R9 | liked | перенос паттернов | — |
| S52 | inbox_mail | R7 | inbox | family inbox/chat | — |
| S53 | map_five_cards | R5 | 5 cards | map cards density | — |
| S54 | free_trial_ui | R4 | trial UI | auto trial | Попробовать / trial |
| S55 | create_circle | R7 | create | создать семью | — |
| S56 | circle_params_a | R7 | params A | params | — |
| S57 | circle_params_b | R7 | params B | params | — |
| S58 | trips_week | R6 | week trips | weekly card | Посмотрите поездки за эту неделю |
| S59 | gold_border | R1 | границы | contrast | — |
| S60 | add_wrap_pm | R1 | wrap | layout/contrast | — |
| S61 | trip_play_a | R6 | play A | replay partial | — |
| S62 | trip_play_b | R6 | play B | replay partial | — |
| S63 | soft_reminders | R1 | простыни | hide soft prose | короткие напоминания |
| S64 | chip_nav | R8 | chips | monitoring chips | — |
| S65 | monitoring_17 | R8 | mismatch | pipeline copy | короткий мониторинг |
| S66 | family_day_trunc | R8 | truncate | no truncate | полный день |
| S67 | system_filter_a | R3 | filter A | короткие строки | — |
| S68 | system_filter_b | R3 | filter B | короткие строки | — |
| S69 | safari_extensions | R3 | Safari | гайд Safari | — |
| S70 | time_limits | R1 | контраст | UnifiedTimeLimits | лимиты времени |
| S71 | main_icons | R5 | иконки | icon polish | — |
| S72 | voice_5s | R2 | ~5s→10s | voice **30s** | Быстрая проверка голоса (30 сек) |
| S73 | antifake_copy | R2 | длинный | short copy | короткий antifake |
| S74 | roadside_hide | R8 | видно roadside | hide accordion | скрыто |
| S75 | yandex_web | R9 | scrape risk | NO scrape | policy |
| S76 | call_filter_setup | R3 | setup | ALADDIN X AI | ALADDIN X AI |
| S77 | speed_online_max | R6 | speed max | gate+real | — |
| S78 | yandex_block_db | R9 | block DB | own lists | — |
| S79 | caller_id_features | R9 | caller id | polish | — |
| S80 | family_list_contrast | R1 | слабый список | contrast Family | — |
| S19a | member_sheet | R5.5 | частичный | полный sheet | Возле: · С HH:MM · Сохранить место · Создать шапку-невидимку |
| S19b | trip_sat | R5.5 | trip | map+route+км | дата · адрес → адрес · км |
| S19c | trip_sun | R5.5 | trip | длинный маршрут | как S19b |
| S19d | places_day | R5.5 | day places | unlock+stops | Разблокировать отчёт о поездках за эту неделю |
| S19e | history_upsell | R5.5 | Gold L360 | B1 ALADDIN | RU: История мест за 30 дней · EN: 30-day location history |
| S19f | trip_drive | R5.5 | drive | руль+скорость+риск | N рискованное событие |
| S19g | push_urgent | R10 | → Удобный режим | → карта+SOS | A1: Срочный сигнал семье / Нужна помощь близкого. Откройте ALADDIN и свяжитесь с ним. |
| S19h | places_list | R5.5 | «В улица» | C1+C2 | Львовская улица… · Возле: |

### Подзадачи (атомарно)

| Блок | Кол-во |
|------|--------|
| Экранные задачи S01–S80 + S19a–h | **88** |
| Экранные подзадачи (база + extras S19/notif) | **~116** |
| Push-типы маршрутизации | **10** |
| R10-1…R10-7 код | **7** |
| **Итого атомарных до device evidence** | **≈133** |
| Device evidence after (отдельный GO сборки) | +88 фото |

Код уже ✅ по волнам R0–R6,R8,R3…; **открыто кодом сейчас:** R10 + R5.5 (S19/S30/S19a–h). Сборка ⛔.

