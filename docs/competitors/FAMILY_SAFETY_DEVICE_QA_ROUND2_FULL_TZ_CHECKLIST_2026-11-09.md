# Family Safety Round2 — полный чеклист ТЗ владельца (S01–S80 + S19a–h)

**Дата:** 2026-11-09 · **обновлено:** канон места семьи **B**  
**Роль:** Principal iOS + Family Safety (ALADDIN), 15+ лет  
**Место семьи (канон B):** [`FAMILY_LOCATION_CANON_B_PLAN_2026-11-09.md`](FAMILY_LOCATION_CANON_B_PLAN_2026-11-09.md)  
**⭐ МАСТЕР доделки 100%/88:** [`FAMILY_SAFETY_MASTER_FINISH_88_PLAN_2026-11-09.md`](FAMILY_SAFETY_MASTER_FINISH_88_PLAN_2026-11-09.md)  
**Code-fact:** [`FAMILY_SAFETY_CODE_FACT_CHECKLIST_100_2026-11-09.md`](FAMILY_SAFETY_CODE_FACT_CHECKLIST_100_2026-11-09.md)  
**SSOT исполнения:** [`FAMILY_SAFETY_DEVICE_QA_ROUND2_S01_S80_2026-11-09.md`](FAMILY_SAFETY_DEVICE_QA_ROUND2_S01_S80_2026-11-09.md)  
**Матрица 88:** [`FAMILY_SAFETY_DEVICE_QA_ROUND2_SCREEN_MATRIX_88.md`](FAMILY_SAFETY_DEVICE_QA_ROUND2_SCREEN_MATRIX_88.md)  
**Figma-долг (не OB_*):** [`FIGMA_FAMILY_SAFETY_ML_PROMPTS.md`](FIGMA_FAMILY_SAFETY_ML_PROMPTS.md)  
**Скрины:** `qa_device_2026-11-09/` · S19 member: `S19_life360_member/`  
**Сборка:** ⛔ только после явного **GO на сборку** · Round2 **не закрывать** до 100%/88

---

## 0. Вердикт покрытия (честно)

| Вопрос | Ответ |
|--------|--------|
| Все слова/задачи владельца **учтены в плане**? | **Да** (S01–S80 + S19a–h + push R10 + канон B место семьи) |
| Все задачи **уже сделаны в коде**? | **Почти по Round2 UI + канон B.** R0–R10 волны, S45–47, quiet/auto-trip, юртексты на сайте. **Не закрыты:** FIG-L (7b), device evidence (фото after), ASC руками, сборка без GO |
| Можно сказать «100% готово к релизу»? | **Нет** — нет FIG-L + нет device QA evidence + нет GO на сборку |
| Гибрид где лучше? | Да: Life360 **UX** + ALADDIN copy. **Не** трек 24/7. UI: **Тихая зона** |
| Канон места | **B:** свежая точка + места при доступе «приложение закрыто»; маршрут при движении; тихая зона; сайт privacy/terms ✅ |

**Опровержение:** «всё на 100% уже сделано» — **ложь**.  
**Подтверждение:** «всё из ТЗ разложено по задачам с решением was→will» — **да, этот документ + Round2 SSOT**.

---

## 1. Промпт агента (канон — копировать в каждый чат волны)

```text
Роль: Principal iOS + Family Safety (ALADDIN). Mech Pilot: пилот=владелец, меха=агент.
Ты — ведущий iOS (15+ лет): SwiftUI, навигация, Keychain, Family Controls, карта семьи,
Antifake, локализация RU+EN, HIG, безопасность детских данных. Не «помощник» — отвечаешь
за качество продукта. Скиллы: aladdin-principal-ios-architect, aladdin-gates,
aladdin-no-mock-bypass, aladdin-figma-ios-sync (только Companion/не OB_* без ТЗ),
verification-loop, swift-reviewer, localization-megafile-safe, ask-before-ios-build,
repowise-ios first, no telegram_bot в iOS commit, master-only commits.

SSOT: docs/competitors/FAMILY_SAFETY_DEVICE_QA_ROUND2_S01_S80_2026-11-09.md
Чеклист ТЗ: docs/competitors/FAMILY_SAFETY_DEVICE_QA_ROUND2_FULL_TZ_CHECKLIST_2026-11-09.md
Матрица 88: docs/competitors/FAMILY_SAFETY_DEVICE_QA_ROUND2_SCREEN_MATRIX_88.md
Предыдущее: FAMILY_SAFETY_DEVICE_QA_MASTER_PLAN_2026-11-05.md (Q01–Q36 код ✅; L-DEV-EVIDENCE ⏳)
Figma family: FIGMA_FAMILY_SAFETY_ML_PROMPTS.md (не трогать OB_* onboarding Figma file).

Корни: ALADDIN_iOS · ветка master · Origin ALADDIN_FAMILY · bot∉iOS.
Правила: no mock/sfm_mock · только реальные GPS/скорость/поездки · RU+EN через
Localizable.strings сначала · no raw keys · haptic — helper + очередь, без mass rewrite ·
навигацию не ломать · сборка/симулятор только после фразы владельца «GO на сборку».

GATES: G1 UI/copy просто · G2 real data · G3 loc RU+EN · G4 nav intact · G5 contrast ·
G6 push deep-link (SOS→карта, не Удобный режим) · G7 hybrid Life360×ALADDIN где лучше.

Семьи и безопасность: срочный сигнал / need help → карта + member sheet; без пустышек.
Сейчас делай ТОЛЬКО: <WAVE / Sxx>. Доказательства: verify/strings/grep; device after GO.
```

**Skills / обязанности меха в этом плане**

| Skill / rule | Зачем |
|--------------|--------|
| `aladdin-principal-ios-architect` | Архитектура UI + UX семьи |
| `aladdin-gates` | Критерии до кода |
| `aladdin-no-mock-bypass` | Нет mock на parental/family |
| `localization-megafile-safe` | Только точечные strings |
| `ask-before-ios-build` | Нет xcodebuild без GO |
| `repowise-first` | Карта кода до mass Grep |
| `swift-reviewer` | После Swift-диффа |
| Figma ML prompts | FIG-L* later; **не** OB_* |

---

## 2. Зафиксированные решения OWNER GO (2026-11-09 вечер)

### 2.1 Тексты / пуши (ранее)

| ID | Решение |
|----|---------|
| **A1** | Пуш: «Срочный сигнал семье / Нужна помощь близкого…» (EN текущий) |
| **B1** | «История мест за 30 дней» / «30-day location history» |
| **C1+C2** | Без «В » у улиц · «Возле: %@» / «Near: %@» |
| **Voice** | **30 секунд** — код + RU/EN |

### 2.2 Продукт / деньги / UX — выбор владельца

| Тема | Выбор | Канон |
|------|-------|--------|
| **S13 / S54 Trial** | **A** | После онбординга сразу trial 14 дней. Блок «Пробный» из тарифов **убрать**. Один путь: вошёл → trial. Базовый тариф без второго «бесплатно» в шапке. |
| **S14 / S16 Таблица** | **C** | Сверху карточки тарифов (CTA), ниже сводная таблица сравнения. Фичи только реальные (см. §2.3). Не писать: прослушка фона, умные устройства, веб+приложение если не ship. **Не ломать** StoreKit / trial / существующие покупки — только copy + layout. |
| **S41 / S55–57 Круги** | **B (архитектура) + UX 100%** | Семья = единственный roster. «Круг» = **метка/группа внутри семьи** (школа, бабушка) — **без второго roster**. UX плотности как Life360, но данные = наша Семья. Не делать независимые круги (вариант C отклонён: риск сломать roster). До/после: verify roster + device. |
| **S48–50 Pet / Flight** | **B** | Скрыть до железа. Если когда-то пункт в меню — только «**В скором времени**», не «недоступно». |
| **S09 Панель родителя** | **A** (default меха, если не оспорено) | Тёмный градиент + золото как Удобный режим, без белых полей. |
| **S18 / S43 / S51 Snowball** | **B** | Палитра Snowball **сразу в коде**, красиво на 100%. Без «отложить риски». Отдельный токен-набор ALADDIN×Snowball; не плодить третий случайный стиль. |
| **S30 Места** | **Гибрид 100%** | Пресеты Дом/Школа/Работа/Другое + **строка поиска с автодополнением адреса** (Apple `MKLocalSearchCompleter`) + частые из реальной истории. См. §2.4. |
| **S05 / S72–73 Antifake copy** | **C + короткий A** | Вердикт чистый. У кнопки одна честная строка («может ошибаться / решайте сами»). Голос 30 с. Просто и понятно. |
| **S67–69 Фильтр / Safari** | **C** | Один экран: статус вкл/выкл честно + «Как включить». RU/EN простой. Без «Extensions content blocked». |
| **S63 Мягкое напоминание** | **A** | Скрыто навсегда флагом (ключи не удалять — локализация не поедет). |
| **S22 BT + Motion** | **A** | Не копировать L360 BT для маячков. Motion — только для уже существующего SOS/fall (если включено). BT **не** запрашивать без маячков/продукта. См. ответ §2.5. |
| **S21 BG Refresh** | **B** | Экран-объяснение в приложении + кнопка в системные Settings. |
| **S61–62 Play маршрута** | **A** | Делаем сейчас. Паритет Life360: play по полилинии реальной поездки, время/км/макс скорость из `DrivingReport`. Без mock точек. |
| **S75 / S78 Блокировки** | **C** | Сейчас ничего нового; Call Filter + Safari. Без scrape. |
| **S07 / S76 Имя** | **A** | Везде **ALADDIN X AI** (= Phone → Blocking). |

### 2.3 Фичи тарифов (черновик → код copy, без выдумки)

| Тариф | Пишем |
|-------|--------|
| **Семья** | Карта семьи · SOS / «нужна помощь» · лимиты ребёнка · Antifake по тарифу · **тихая зона** · поездки Start→Stop (канон B) |
| **Премиум** | То же + безлимит Antifake (текст/док/голос/видео/звонок **по действию**) · длиннее история мест |
| **Индивидуальный** | Защита одного · Antifake по лимиту |
| **Не писать** | Прослушка звонков в фоне · умные устройства (если нет) · веб+приложение (если не ship) |

**Безопасность внедрения:** менять только `Localizable.strings` + UI таблицы/карточек; не трогать IAP product IDs, Receipt, trial entitlement logic без отдельного GO.

### 2.4 S30 — автодополнение адреса (канон)

| Вопрос | Ответ |
|--------|--------|
| Можем? | **Да.** Apple `MKLocalSearchCompleter` + `MKLocalSearch` (как Maps). |
| Нужно | `MapKit` · поле поиска · список подсказок · выбор → координата + сохранение места в наш store/API. Интернет. Не нужен отдельный Google/Yandex key для completer. |
| Наилучшее | Гибрид: пресеты сверху · строка «Введите адрес» с подсказками по мере ввода · «Сохранить» на карте · частые из реальных визитов. RU/EN сразу. |

### 2.5 S22 — BT / Motion и Apple (канон ответа)

| Вопрос | Ответ |
|--------|--------|
| BT только для маячков? | У Life360 BT в основном **proximity / Tile-like / «рядом»**, не для обычной GPS-карты. |
| Нам запрашивать BT у Apple? | **Нет**, пока нет маячков/продукта «рядом по BT». Лишний permission = отказ App Review и недоверие. |
| Motion? | Уже есть `NSMotionUsageDescription` для **срочного сигнала / fall** — не расширять «для карты как L360» без пользы. |
| Итог | **A:** карта = GPS/Always; SOS = motion по opt-in; BT = не просим. |

### 2.6 Локализация — аудит 88 экранов (честно)

| Вопрос | Ответ |
|--------|--------|
| Политика на **все** S01–S80 + S19a–h? | **Да.** G3: любой UI-текст только через `localized()` + ключ в **RU и EN** `Localizable.strings` **до** merge. Сырой ключ на экране = баг. |
| Все 88 строк уже заранее написаны в матрице? | **Нет на 100%.** В `SCREEN_MATRIX_88` ~50 строк с «—» в колонке «Текст» (нет отдельной фразы, но экран часто уже на общих ключах). |
| Значит локализация «не продумана»? | **Продумана как правило + волны.** Закрытые волны (R0–R6, R8, R10, R5.5, voice 30s) — ключи в strings. Открытые волны — ключи **сначала в §2.7–2.8**, потом код. |
| LocManager mega-file? | Только точечный StrReplace при необходимости; канон = **strings first**. `./scripts/verify_localization_manager_integrity.sh` если трогали mega-file. |
| Проверка «нет сырых ключей» | Device/sim: grep UI на `map_`/`family_`/`antifake_` латиницей; RU и EN переключатель. |

**Правило волны:** перед UI-кодом — таблица ключей RU|EN в этом чеклисте → запись в оба `.strings` → код → смоук языка.

### 2.7 WAVE next: S30 Places completer (сначала)

**Порядок владельца:** 1) S30 completer → 2) метки-круги B. Сборка только после GO.

| Шаг | Что делаем |
|-----|------------|
| 1 | В `GeofencesSettingsModal` / sheet мест: поле поиска |
| 2 | `MKLocalSearchCompleter` → список подсказок |
| 3 | Выбор → пин на карте → имя (пресет или своё) → сохранить в текущий place/geofence store |
| 4 | Пресеты Дом/Школа/Работа/Другое (ключи уже частично есть) |
| 5 | «Частые» только из реальных сохранений |
| 6 | RU+EN · пустая сеть · «ничего не найдено» |

**Ключи S30 (добавить в ru+en.strings до кода UI):**

| Key | RU | EN |
|-----|----|----|
| `map_places_search_placeholder` | Введите адрес… | Enter an address… |
| `map_places_search_hint` | Начните печатать — появятся подсказки | Start typing for suggestions |
| `map_places_search_empty` | Ничего не нашли. Проверьте адрес или поставьте точку на карте | No matches. Check the address or drop a pin on the map |
| `map_places_search_offline` | Нужен интернет для подсказок адреса | Internet is required for address suggestions |
| `map_places_suggest_other` | Другое | Other |
| `map_places_frequent_title` | Частые места | Frequent places |
| `map_places_frequent_empty` | Пока нет сохранённых мест | No saved places yet |
| `map_places_save_cta` | Сохранить место | Save place |
| `map_places_name_placeholder` | Название места | Place name |
| `map_places_use_map_pin` | Взять точку с карты | Use map pin |

Уже есть (не дублировать): `map_places_title`, `map_places_add_*`, `map_places_suggest_home/school/work`, `map_member_save_place`, geofence_* статусы.

**GATES S30:** G1 поиск виден · G2 подсказка→пин реальный · G3 RU+EN · G4 сохранить в тот же flow мест · G5 нет Google key · G6 навигацию sheet не ломать.

### 2.8 WAVE next+1: Круги-метки B (после S30)

| Шаг | Что делаем |
|-----|------------|
| 1 | Модель локально+API позже: `{id, title, memberIds[]}` привязана к **текущему** `family_id` |
| 2 | UI: Семья → «Группы» (слово «Круг» в copy ок) → создать/редактировать |
| 3 | Выбор людей **только из текущего roster** |
| 4 | Карта: фильтр «вся семья» / «группа X» |
| 5 | До/после: count members + `family_id` неизменны |

**Не делаем:** второй roster, отдельный invite «в круг», leave circle ≠ leave family.

**Ключи Circles B (ru+en до кода):**

| Key | RU | EN |
|-----|----|----|
| `family_groups_title` | Группы семьи | Family groups |
| `family_groups_subtitle` | Метки внутри одной семьи — без второго списка людей | Labels inside one family — not a second member list |
| `family_groups_create` | Создать группу | Create group |
| `family_groups_name_placeholder` | Например: Школа, Бабушка | e.g. School, Grandma |
| `family_groups_pick_members` | Кто в группе | Who’s in the group |
| `family_groups_empty` | Пока нет групп. Создайте первую | No groups yet. Create one |
| `family_groups_save` | Сохранить | Save |
| `family_groups_delete` | Удалить группу | Delete group |
| `family_groups_filter_all` | Вся семья | Whole family |
| `family_groups_filter_group` | Группа: %@ | Group: %@ |
| `family_groups_map_filter` | Показать на карте | Show on map |

### 2.9 WAVE Densitiy A (S19b–f + карта) — OWNER 2026-11-09

**Канон:** A — densitiy карточек на реальных метриках; мини-карта/линия **только** при реальных координатах; иначе короткий честный плейсхолдер. **Без** mock mid-points. Loc: короткие RU/EN, без простыней, без сырых ключей.

| Key | RU | EN |
|-----|----|----|
| `trip_drive_mode` | За рулём | Driving |
| `trip_arrived` | Прибыли | Arrived |
| `trip_no_map_track` | Маршрут на карте — когда сохранится GPS-трек | Map route when a GPS track is saved |
| `trip_open_detail` | Открыть поездку | Open trip |
| `map_unit_meters` | %d м | %d m |
| `dens_places_day_title` | Места за день | Places today |
| `dens_places_day_empty` | Пока нет остановок за сегодня | No stops today yet |
| `dens_map_pin_time` | С %@ | Since %@ |
| `location_history_30d_subtitle` | *(укоротить)* Полная история — в семейном тарифе | Full history on Family plan |
| `map_drive_unlock_cta` | *(укоротить)* Отчёт о поездках за неделю | This week’s trip report |
| `map_drive_locks_hint` | *(укоротить)* На Family и Premium после пробного | On Family & Premium after trial |
| `driving_play_no_track` | *(укоротить)* Нет GPS-трека. Показаны время, км и скорость | No GPS track. Showing time, km, and speed |

**GATES densitiy:** G1 trip row: дата · HH:mm–HH:mm · адрес→адрес · км · max · риск · За рулём · Прибыли · G2 нет fake polyline · G3 RU+EN short · G4 sheet member weekly/unlock/history 30d · G5 S03 pin time через ключ · G6 без симулятора до GO.

### 2.10 WAVE S33–S39 notif copy (OWNER A) — 2026-11-09

**Канон:** короткие RU/EN под уже готовый R10; pet/weather = soon/N/A; без простыней; ключи в `Localizable.strings`.

| Key | RU | EN |
|-----|----|----|
| `battery_critical_push_title` | Батарея почти села | Battery almost empty |
| `battery_critical_push_body` | Заряд %d%%. … | Battery at %d%%. … |
| `week_digest_push_*` | Сводка недели семьи | Family week summary |
| `trip_week_push_*` | Поездки за неделю | Trips this week |
| `notif_s33_*` | Места семьи | Family places |
| `notif_s34_*` | Батарея близкого | Family battery |
| `notif_s35_*` | Поездки | Trips |
| `notif_s36_*` | Безопасность | Safety |
| `notif_s37_*` | Погода — скоро | Family weather — soon |
| `notif_s38_*` | События семьи | Family events |
| `notif_s39_*` | Питомцы — later | Pets — later |
| `family_urgent_signal_*` | укорочен | Urgent family signal |
| `shield_ask_parent_push_body` | укорочен | Child asked to unlock… |

**Wire:** battery/habit/week_digest/urgent/need_help/geofence/shield → strings; R10 + habits/limits/trips types.

### Push routing (R10) — обязательно

| Тип | Куда |
|-----|------|
| Срочный / Нужна помощь | Карта + member SOS sheet |
| Я ок | Карта / presence |
| Батарея | Карта / member |
| Geofence / no-show | Карта + место |
| Привычки | Семья → habits |
| Лимиты / shield | Семья → limits |
| Угроза / bypass / AV | Network Protection / Antifake |
| Тарифы | Tariffs |
| Post-call / companion / focus | Свои экраны |
| Без type | Fallback **карта семьи**, не Удобный режим |

---

## 3. Чеклист простым языком — по каждому скрину

Легенда статуса кода: ✅ сделано · 🟡 частично · 📋 в плане · ⛔ N/A (не копируем Life360 as-is) · ⏳ device

### Онбординг и карта

| # | Было | Станет | Для ALADDIN / семьи | Код |
|---|------|--------|---------------------|-----|
| **S01–S02** (+все 8 OB) | После Fit — поля/letterbox на 8 экранах | Full-bleed hybrid Fill+zoom как build 17; текст внизу без лишних полей; ничего не обрезать | Родитель сразу видит героя «во весь экран» — доверие с первой секунды | ✅ R0 · ⏳ device |
| **S03** «Как мам» | Не Life360-вид | Badge «С HH:MM» у пина (реальный fix) | Родитель видит «где близкий и с какого времени» | ✅ pin time · ⏳ device |
| **S04** | Смежный map | Тот же стек карты | Единый опыт «Где семья» | 🟡 |
| **S19 + S19a–h** | Слабый sheet; 8 скринов досланы | Sheet + densitiy A trip cards / places day / 30d history; map endpoints only if real coords | Тап по аватару = полный контроль за близким | 🟡 densitiy A code ✅ · polyline 📋 · ⏳ device |

### Antifake

| # | Было | Станет | Для семьи | Код |
|---|------|--------|-----------|-----|
| **S05** | Длинная простыня «может ошибаться» | 3 коротких варианта → выбран короткий баннер | Понятно без страха | ✅ R2 |
| **S05 тех** | Timeout то работает то нет (текст/док/голос/видео/звонок) | Честный timeout + Retry во всех каналах; без вечного спиннера | Семья не зависает в «проверяем…» | 🟡 code ✅ Retry · ⏳ device smoke |
| **S06** | «Вердикт неверный» + юр. простыня | Убрать disclaimer везде | Чистый результат проверки | ✅ R2 |
| **S72 голос** | 5с → было 10с | **30 секунд** запись; одинаковый шрифт/цвет; 3 коротких текста | Хватает фразы для проверки без фоновой прослушки | ✅ **30 с сейчас** |
| **S73** | Непонятный copy | Короткий RU/EN | Ясный Antifake | ✅ R2 |

### Call Filter / система

| # | Было | Станет | Для семьи | Код |
|---|------|--------|-----------|-----|
| **S07 / S15 / S76** | Путаница Call Filter / Call Directory / ALADDIN X AI; обрезка «зв…»; чёрный текст | В Settings iPhone: **ALADDIN X AI**; в приложении понятные RU/EN подписи; deep link максимально близко к Call Blocking; контраст | Родитель включает блок спама без путаницы имён | 🟡 R3 · ⏳ device |
| **S67–S68** | Системный фильтр «нельзя»; простыни | Filter hub + system toggle | Понятно что включить | ✅ code · ⏳ device |
| **S69** Safari | «Extensions content blocked» | Honesty + how-to → AdvancedProtection | Семья включает блок контента | ✅ code · ⏳ device |

### Удобный режим / родитель / скорость / haptic

| # | Было | Станет | Для семьи | Код |
|---|------|--------|-----------|-----|
| **S08** | «Ребёнок» чёрный; простыня про паузы; человечки смещены | Золотой заголовок; убрать простыню; аватарки по центру | Читаемый вход ребёнка | ✅ R1 |
| **S09** | Белые поля / сомнение «работает?» | Snowball dark+gold · без borderedProminent white | Родитель видит панель как остальные экраны | ✅ code · ⏳ device |
| **S10** | 181 км/ч фейк; haptic только на чипах | Только **реальная** скорость; SelectionHaptic на скролл карточек; очередь haptic на другие разделы **без mass rewrite** | Доверие к данным + тактильный отклик | ✅ gate/haptic base · 📋 rollout очередь |
| **S59–S60** | Золотой ободок; «Доба/вит»; PM PA | Контраст; без переноса «Добавить»; пояснить/убрать PM PA | Аккуратный Удобный режим | 🟡 |
| **S63** | «Мягкое напоминание» простыня | Убрать; не ломая ключи | Меньше шума | ✅ hide prose |
| **S70** | Чёрный нечитаемый time limits | Светлый контраст как другие | Родитель видит лимиты | ✅ |
| **S80** | Чёрный семейный список | Золотой/читаемый как везде | Читаемый roster | ✅ |

### Тарифы / trial

| # | Было | Станет | Для семьи | Код |
|---|------|--------|-----------|-----|
| **S13 / S54** | Два «бесплатно»; trial вверху; переносы | Auto trial после онбординга; trial-карту убрали | Новый пользователь сразу в trial без путаницы | ✅ code · ⏳ device |
| **S14** | Слабые bullets; EN Subscribe; лишний текст | Honest feature strings §2.3 + gates rows | Честное сравнение тарифов | ✅ code · ⏳ device |
| **S16** | Таблица «непонятные слова» | honestGatesComparisonTable (не 3 визуальных варианта) | Выбор тарифа без головной боли | 🟡 таблица есть · 📋 3 варианта UI |

### Карта / шапка / поездки / места

| # | Было | Станет | Для семьи | Код |
|---|------|--------|-----------|-----|
| **S17 / S29** | Фото обрезается в пине/аватаре | Crop pan внутри фигуры | Красивый аватар без обрезов | ✅ AvatarCrop · 📋 pin crop densitiy |
| **S18 / S43 / S51** | Слабый дизайн vs Life360 | Токены Snowball в коде (ParentDashboard/play); не все экраны; FIG-L отдельно | Приятный «дорогой» UI | 🟡 tokens ✅ · map/trips rollout ✅ · FIG-L 📋 |
| **S20 / S27 / S42 / S44** | Тихая зона | FAB + радиус (quiet zone). Copy: **Тихая зона** | В зоне точку семье не шлём | ✅ UI · 📋 проверить все пути upload в коде B |
| **S21** | BG refresh ? | Sheet Always Allow + Settings (гайд) | Стабильные обновления локации | ✅ code · ⏳ device |
| **S22** | Нет BT+Motion как L360 | **A:** BT не просим; Motion только SOS — copy в Always sheet | Честно: зачем нам / зачем им | ✅ policy+copy · ⏳ device |
| **S23–S28 / S58 / S61–62** | Слабее L360 journal/trips | densitiy + **play пин по нашему треку** (слой1) / старт→финиш (слой2) · без чужого API | Родитель видит реальные поездки | ✅ play stack · ⏳ device |
| **S30** | Мало мест | Гибрид + completer §2.7 · код ✅ | Семья сохраняет дом/школу по адресу | ✅ code · ⏳ device |
| **S53 / S71 / S77** | 5 карточек / иконки / скорость | Красивые chips; иконки размера L360; online vs max speed честно | Карта = главный инструмент | 🟡 |

### Круг / события / уведомления / inbox

| # | Было | Станет | Для семьи | Код |
|---|------|--------|-----------|-----|
| **S11** | QR ? TTL; «Родитель А»×2 | Проверить QR; TTL **72h**; имя 1 раз | Быстрый инвайт | ✅ TTL · ⏳ QR device |
| **S12** | «Без скрытого отслеживания» | Убрать spy-тон; честный Always Allow | Доверие, не «шпион» | ✅ |
| **S31–S32** | События | Как L360: имя/место/дата/кто увидит | Семейные встречи | 🟡 R7 min ✅ local create+who · shared later |
| **S33–S39** | Матрица нотифов | Аудит какие есть/нет; тексты; pet=N/A или soon; **все пуши → правильный экран (R10)** | Важное не теряется в Удобном режиме | 🟡 R10 ✅ · тексты ✅ §2.10 · ⏳ device |
| **S40** | Доступ локации | Честный copy + Settings path | Понятно зачем Always | 🟡 |
| **S41 / S55–S57** | Круг vs семья | **B** метки §2.8 · код ✅ | Фильтр групп на карте | ✅ code · ⏳ device |
| **S45–S47** | Activity share / leave / profile | Паритет + crop | Контроль круга и профиля | 🟡 S45 share+stop ✅ · S46 leave device ✅ · S47 crop ✅ |
| **S48–S50** | Flights / pets | Подготовка без маячков; не обещать GPS-ошейник | Честный roadmap | ⛔/📋 soon |
| **S52** | Inbox | Красивый «ящик» как L360 | Уведомления в одном месте | 🟡 R7 min ✅ empty+family persist+R10 tap |

### Мониторинг / фильтры / Yandex / список

| # | Было | Станет | Для семьи | Код |
|---|------|--------|-----------|-----|
| **S64–S66** | Чипы не как map; monitoring не тапается; truncate дня | Chip-nav как «Где семья»; кликабельные карточки или честный disable; day strip sync с map | Понятный родительский контроль | 🟡 R8 |
| **S74** | Roadside в Network | Скрыть (есть в Где семья) | Без дубля | ✅ |
| **S75 / S78** | Yandex web block DB | **Не scrape**; свои списки / официальные API если появятся | Легальная защита | ✅ policy |
| **S79** | Caller ID features | Что есть/добавить в ALADDIN X AI | Спам-звонки | 📋 |

---

## 4. Подзадачи — счётчик

| Блок | Кол-во | Статус |
|------|--------|--------|
| Экранные S01–S80 + S19a–h | **88** | в плане |
| Экранные подзадачи | **~116** | mix ✅/🟡/📋 |
| Push routes | **10** | ✅ R10 код |
| R10 атомы | **7** | ✅ код |
| Voice 30s | **1** | ✅ код + strings |
| Device evidence | **+88** | ⏳ после GO сборки |
| Figma FIG-L | отдельный долг | 📋 |

**≈133 атомарных до device** · **не 100% кода закрыто**.

---

## 5. Что сделано vs что осталось (топ)

### Сделано в коде (не путать с device PASS)

- R0 onboarding full-bleed · R1 contrast/copy · R2 antifake short + disclaimer off · **voice 30s**  
- R3 Call Filter naming foundation · R4 trial/antifake bullets partial · R5 speed gate + haptic base + crop  
- R6 hat FAB · R8 monitoring/roadside/day strip · R10 push→map · R5.5 C1/C2/B1 + SOS focus  
- FILE_INDEX + 8 S19 скринов · тексты A1/B1/C1/C2  

### Закрыто кодом по OWNER GO §2.2 (ещё не device)

S13/S54 Trial A · S14 Tariffs copy/gates · S16 таблица (1 вариант) · S30 completer · S41 Circles B · S09 A · S18 tokens (частично) · S61–62 Play scrubber · S67–69 Filter hub · S21 BG sheet · S22 BT A policy  

### Осталось до «100% кода» (честно)

1. **S61–62 полный** — play **на карте** по реальной полилинии (нужен GPS-трек в `DrivingReport`; сейчас scrubber без mock точек)  
2. **S03 / S19b–f / S23–S28 / S53** — densitiy карты/поездок/journal как Life360  
3. **S16** — «3 топ-варианта» красивой таблицы (сейчас одна honest table)  
4. **S18/S43/S51** — Snowball на **все** целевые экраны + 60+ · FIG-L  
5. **S31–S32 / S45–S47 / S52** — R7 события / share / leave / inbox  
6. **S33–S39 тексты** — R10 route ✅, copy нотифов 📋  
7. **S48–50** — audit «В скором времени» везде / скрыть лишнее  
8. **S07/S15/S76** — device truth Call Filter name  
9. Haptic очередь rollout · antifake timeout smoke 5 каналов  
10. **~50** строк матрицы с «—» — ключи по волнам  
11. Device evidence **+88** после **GO на сборку**  
12. FIG-L — отдельный GO  

---

## 6. Гибридные решения (где лучше всего)

| Тема | Гибрид |
|------|--------|
| Онбординг | Fill+zoom (build 17 feel) + Figma-якоря текста |
| Карта | Life360 density + ALADDIN stormGlass + реальный GPS |
| Тихая зона | Life360 quiet zone UX · copy «Тихая зона» · канон B |
| Antifake | Наш продукт; UX короткий; timeout честный |
| Круги | Не ломать ALADDIN семью; круги = опциональные метки/роли поверх |
| Pet/Flight | Soon sheets / подготовка, без фейковых маячков |
| Haptic | Один helper; включать экран за экраном |
| Push | Deep link map; cold start не «Удобный режим» как финал |

---

## 7. Навигация и реальные данные

- Новые sheet/push: как `WhereIsPhone` / `SimpleHome` sheets; не ломать стеки.  
- Скорость, поездки, батарея, локация — только с устройства/API; **запрет mock в проде**.  
- Локализация: сначала `Localizable.strings` RU+EN; verify integrity если трогали LocManager.

---

## 8. Журнал

| Дата | Что |
|------|-----|
| 2026-11-09 | Полный TZ чеклист создан; промпт §1; вердикт ≠100% кода |
| 2026-11-09 | Voice **30 с** код + RU/EN |
| 2026-11-09 | R10 + A1/B1/C1/C2 + S19a–h indexed |
| 2026-11-09 | OWNER GO §2.2–2.5: Trial A · Tariffs C · Circles B · Pet B · Snowball B · Places+completer · Play A · BT A · BG B · Filter C · Call A |
| 2026-11-09 | Loc audit §2.6 + WAVE S30 §2.7 keys + Circles B §2.8 keys · матрица 88: ~50 «—» закрываем по волнам · next: S30 затем B |
| 2026-11-09 | **S30 code:** §2.7 keys in ru+en.strings · `PlaceAddressSearchCompleter` · UI in `GeofencesSettingsModal` + WhereIsPhone chips Other · сборка ⛔ · next Circles B |
| 2026-11-09 | **Circles B code:** §2.8 keys · `FamilyGroupLabelStore` + `FamilyGroupsModal` · Family together entry + map filter chips · no second roster · сборка ⛔ |
| 2026-11-09 | **WAVE TrialA→BG B:** loc strings SSOT (tariffs+play+filter+bg) · hide trial card · honest gates · trip playback · Snowball palette · S09 dashboard · filter hub · BG refresh sheet · сборка ⛔ |
| 2026-11-09 | **Densitiy A:** OWNER lock · §2.9 keys short RU/EN · trip cards + pin time + places day/30d · endpoints map only if real coords · сборка ⛔ |
| 2026-11-09 | **S33–39 A:** §2.10 notif keys RU/EN · battery/habit/week_digest strings · R10 habits/limits/trips · сборка ⛔ |
| 2026-11-09 | **R7 min:** S31/32 create+who local · S52 inbox empty+family persist+R10 tap · сборка ⛔ |
| 2026-11-09 | **Snowball rollout:** WhereIsPhone + DrivingReports canvas tokens · haptic/AF Retry static ✅ · сборка ⛔ |
| 2026-11-09 | **S45–47:** share duration+stop · leave family on device · profile AvatarCrop · сборка ⛔ |
| 2026-11-09 | **GPS track:** `routePoints` decode + local sample on explicit trip · polyline when ≥2 real pts · no mock · сборка ⛔ |

---

## 9. Следующий шаг меха (без сборки)

1. ~~Densitiy A · S33–39 · R7 min · Snowball · haptic/AF · S45–47 · GPS · journal S23–28 polish~~ ✅  
2. FIG-L — только после **отдельного GO**. Call Filter — **device**.  
3. **GO на сборку** → device 88.
