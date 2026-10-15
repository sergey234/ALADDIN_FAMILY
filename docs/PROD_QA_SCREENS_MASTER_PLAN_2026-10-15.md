# PROD QA Screens — Master Plan (2026-10-15)

**Статус:** ✅ **СОГЛАСОВАНО владельцем** (2026-10-15 ~13:35) — реализуем всё по чеклисту.  
**База:** build **8** на `origin/master` (`119c2bf1`).  
**Сборка Xcode / TF:** только в **самом конце**, после отдельного **GO на сборку**.  
**Финал волны:** полный loc pass RU/EN, без сырых ключей (`prodqa-loc-pass`).

**Правила:** strings-first → точечный LocManager; `verify_localization_manager_integrity.sh`; iOS-коммит только `master`; bot/`.env` ∉ iOS.

---

## Решения владельца (зафиксировано)

| Тема | Решение |
|------|---------|
| **S03 Единорог** | Только **A** `unicorn_master.png` **везде**; B+C **удалены**; если Rive crop — PNG priority для unicorn |
| **S05 Focus** | В «Ещё» переименовать в **«Тихий час»** (не путать со Звонками); Звонки — под диктофоном; +6-я плитка «Расширенные настройки» |
| **S06 Blocklist** | Гибрид: локальный каталог сейчас + расширение; родители могут добавлять свои сайты |
| **S16 Календарь** | Тот же календарь для воды / телефон на ночь / лекарство / свои / челленджи / семейный список + **сразу sync с Календарём Apple** |
| **S26 Профиль / даты** | **NEW:** дата пробного/тарифа и «с нами с» — сразу после регистрации и выбора тарифа, без «после синхронизации» на часы |
| **Остальное** | Все пункты чеклиста S01–S25 (кроме оговорённого выше) — **GO** |
| **Сборка** | Только после завершения задач + GO |

---

## Волны внедрения (GO получен)

| Волна | Что | Риск |
|-------|-----|------|
| **W-P0** | S01, S02✅, S03 unicorn everywhere, S07, S13, S15✅, S17-contrast, S24✅, **S26 даты** | низкий/средний |
| **W-P1** | S04 model, S05, S08–11 Calls, S12, S18, S21/S23 | средний |
| **W-P2** | S06 blocklist+parent sites, **S16 calendar+EventKit**, S22, S25 | высокий |
| **W-LOC** | Полный RU/EN verify | — |
| **W-QA** | Xcode/TF — только с GO | — |

---

## S01 — Companion / роли: «Parent A» при русской раскладке

**Факт:** в UI остаётся `Parent A`, хотя язык приложения RU. В семейном чате formatter уже есть.  
**Причина:** `FamilyMemberDisplayNameFormatter` покрывает chat/cards/selector; имя при регистрации может сохраняться как EN (`Parent A`); Companion / другие экраны показывают **сырое** `member.name` без formatter.  
**Гибрид ★:**  
1) Единая точка: **все** отображения имени → `FamilyMemberDisplayNameFormatter.displayName`.  
2) При смене языка — не переписывать серверное имя; только presentation layer.  
3) Smoke: Parent/Child/Elderly/Teen × RU/EN.  
**Alt A:** миграция stored names на канон-роль+суффикс. **B:** только UI map. **C:** серверный locale (избыточно).  
**Loc:** уже `family_role_*_label` — проверить покрытие всех call-sites.  
**TODO:** `prodqa-s01-lang`

---

## S02 — Геозоны: «Почему нет уведомлений?» + мёртвая кнопка

**Факт:** блок FAQ с тех.объяснением; CTA «Включить уведомления» не нажимается / не даёт эффекта.  
**Причина (код):** `02_FamilyScreen` — кнопка вызывает `NotificationManager.requestAuthorizationIfNeeded()`; если permission уже `.denied`, iOS **не** показывает диалог повторно → «кнопка мёртвая». Весь FAQ-блок владелец просит убрать.  
**Гибрид ★:**  
1) **Удалить** title+body «Почему нет…».  
2) Оставить одну яркую кнопку «Включить уведомления».  
3) Логика: `notDetermined` → request; `denied` → **открыть Settings** + короткий toast «Разрешите уведомления в Настройках»; `authorized` → toast «Уже включены» + deep-link в inbox.  
**Alt A:** только Settings deep-link. **B:** оставить FAQ короче. **C:** баннер только если denied.  
**Loc:** переиспользовать `geofence_why_no_push_enable_notifications`; добавить toast keys RU/EN; body/title — deprecate.  
**TODO:** `prodqa-s02-push`

---

## S03 — Обрезанный единорог

**Факт:** на устройстве снова crop, хотя W3 build 8 запретил artboard `unicorn_master_crop_*`.  
**Причина (гипотезы по приоритету):**  
1) Rive `unicorn.riv` artboard `Hero360` сам кадрирует крупно (голова/шея) — PNG fallback не используется, если Rive OK.  
2) Старый TF-кэш / не та сборка.  
3) Другой экран тянет letterbox/broken asset.  

**Решение владельца (2026-10-15):**

| # | Файл | Решение |
|---|------|---------|
| **A ★** | `Resources/Companion/unicorn_master.png` (360×480) | **КАНОН** — целый единорог везде |
| B | `unicorn_master_letterboxed_backup.png` | **УДАЛЁН** |
| C | `unicorn_master_broken_lavender_overlay.png` | **УДАЛЁН** |
| D | `unicorn.riv` / `Hero360` | Если на device всё ещё crop — тогда re-export Rive (отдельный шаг) |

**Гибрид ★ (APPROVED):** PNG A **везде** для единорога (PNG priority, даже если Rive доступен — пока кадр Rive не пересобран full-body). B+C удалены.  
**TODO:** `prodqa-s03-unicorn` — **IN PROGRESS**

---

## S26 — Профиль: «Пробный период» + «Дата появится после синхронизации» (NEW P0)

**Факт:** >20 часов на устройстве — дата так и не появилась; от даты зависят сроки тарифов.  
**Причина:** `AccountRegistrationDateStore` ждёт серверный `registrationDate` / JWT; profile soft-pull может не заполнить; trial expiry отдельно от `trialStatus` / `subscription_expires_at_iso` — если sync не пришёл, UI вечно показывает pending.  
**Гибрид ★ (APPROVED — наилучшее):**  
1) **Сразу при регистрации / активации trial / выборе тарифа:**  
   - заморозить дату «с нами с» из JWT `issuedAt` или `registeredAt` (не ждать профиль);  
   - записать `trial.endDate` → UI «действует до …» + `subscription_expires_at_iso`.  
2) **При открытии Профиля:** принудительный `refreshSubscriptionStatus()` + `getUserProfile` (не только soft).  
3) **Fallback:** если trial active, а даты нет — взять `trial.startDate` / JWT; никогда не оставлять pending при живом токене.  
4) Copy pending оставить только на **реальный** offline без JWT.  
**Loc:** уточнить `profile_subscription_end_pending_sync` / `profile_registration_pending_sync` — короче, если сеть offline.  
**TODO:** `prodqa-s26-dates`

---

## S04 / S17 — Модель устройства + контраст карточки Info

**Факт:** «Модель» = имя профиля (`iPhone • Люди 60+ D`), не hardware; текст Владелец/Тип/Модель тёмный на тёмном; табы «Статистика»/«Настройки» рвутся.  
**Причина:** нет маппинга `utsname`/`hw.machine` → marketing name; цвета secondary слишком тёмные на navy.  
**Гибрид ★:**  
1) **Авто:** `UIDevice` + таблица `iPhone17,1` → «iPhone 16 Pro» (локальный словарь, без сети).  
2) **Ручной override** — уже есть выбор типа — оставить «Изменить модель» в настройках устройства.  
3) Display: `iPhone 16 · Ребёнок B` (модель + роль через formatter).  
4) Контраст: label/value → `Color.textPrimary` / `secondaryGold` (канон), запрет чёрного на dark.  
5) Табы: `minimumScaleFactor` / короткие loc (`Стат.` только если не влезает — лучше 2-line fixed height).  
**Alt A:** только авто. **B:** только ручной. **C:** авто+badge «уточните».  
**Loc:** `device_info_owner`, `device_info_type`, `device_info_model`, `device_model_iphone_*` (по мере таблицы).  
**TODO:** `prodqa-s04-17-model`

---

## S05 — Звонки + «Тихий час» + 6-я карточка (APPROVED)

**Простыми словами:** это **не звонки**. Мягкий таймер 25/60 мин (бывший Focus). Не блокирует приложения.

**3 названия на выбор владельца (под заголовком — расшифровка):**

| # | Название RU | EN | Расшифровка под текстом |
|---|-------------|-----|-------------------------|
| **1 ★ APPROVED** | **Спокойные минуты** | **Calm minutes** | **Помогает сосредоточиться!** / **Helps you focus!** (только это) |

**Также:** Звонки под диктофоном; 6-я плитка «Расширенные настройки».  
**TODO:** `prodqa-s05-focus-calls` — **IN PROGRESS**

---

## S06 / S19 / S20 — «Блокировка активна: 21 / 34 сайта» + диагностика

**Факт:** 34 сайта / 34 правила / 12 категорий; диагностика показывает base 34 → после теста 5 rules в storage; «21» на карточках фильтра.  
**Причина (код):** `ContentBlockerCategory` = **12** case; сумма `blockedDomains` ≈ **34** паттерна (не «мировой» blocklist). Счётчик UI = `rules.count`. «21» = активный **subset** категорий. Диагностика пишет 5 **тестовых** правил — это self-test, не прод-каталог.  
**Гибрид ★ (APPROVED) — как расширять список:**  

| Кто | Как |
|-----|-----|
| **Мы (ALADDIN)** | Обновляем встроенный каталог в обновлении приложения + позже подписанный remote pack (еженедельно) |
| **Родитель** | **Да** — в Родительском контроле / Блокировке: «Добавить сайт» (домен) → сразу в Content Blocker на устройстве ребёнка |
| **Семья** | Свои домены синхронятся на устройства детей через parental settings |

**Порядок внедрения:**  
1) Честный copy («правил / категорий»).  
2) Расширить базовый phishing/scam каталог.  
3) UI родителя «Добавить / удалить сайт».  
4) (Позже) remote pack без store-update.  

Диагностика — простым языком; после теста восстановить прод-правила.  
**TODO:** `prodqa-s06-19-20-block`

---

## S07 — Переносы «Подробнее» / «Лимиты»; EN threat words

**Факт:** слова рвутся на 2 строки; в «Блокировка угроз» — Phishing / Malware / Mobile network.  
**Гибрид ★:** `lineLimit(1)` + `minimumScaleFactor(0.85)` на чипах; заменить жаргон.  
**3 варианта каждого:**

| EN | V1 ★ | V2 | V3 |
|----|------|----|----|
| Phishing | Фишинг-ссылки | Поддельные сайты | Обманные страницы |
| Malware | Вредоносные программы | Опасные файлы | Вирусы и вредонос |
| Mobile network | Мобильная сеть | Сеть телефона | Интернет на телефоне |

**Loc:** `threat_kind_phishing`, `threat_kind_malware`, `threat_kind_mobile_network` (+EN).  
**TODO:** `prodqa-s07-wrap-threats`

---

## S08–S11 — Звонки: copy, «Звонок»/«Пробный», кнопка «Позвонить» мёртвая

**Факт:** техтекст про линию оператора; типы «Звонок»/«Пробный»; после «Начать» → «Позвонить» — ничего.  
**Причина (типичная для iOS):** `tel:` / `telprompt:` не открывается без валидного номера; симулятор не звонит; sheet закрывается до `openURL`; нет permission/contacts; post-call flow ждёт возврат в app.  
**Гибрид ★:**  
1) Copy: «Запись только с микрофона, если включён громкая связь. Линию оператора приложение не слышит.» → ещё короче (ниже 3 варианта).  
2) Типы: «Звонок» → «Исходящий»; «Пробный» → «Тренировка» / «Проверка записи».  
3) Починить dial: проверить номер → `UIApplication.shared.open(tel)` **после** dismiss sheet (delay 0.3 как Second Hand) → если нет номера — sheet «Введите номер или выберите контакт» → fallback «Открыть Телефон».  
4) Тумблеры «запись с динамика» + «понимаю условия» — gating: Start disabled until legal toggle ON + toast.  

**3 варианта текста вместо «не пишет линию»:**  
1) ★ «Мы записываем только звук с микрофона при громкой связи — не саму линию звонка.»  
2) «Запись — это диктофон рядом с телефоном. Собеседника слышно, если звук идёт из динамика.»  
3) «ALADDIN не подключается к звонку. Запись включается только с вашего согласия.»  

**3 решения dial:**  
1) ★ Hybrid: telprompt + contact picker + «Открыть Телефон» fallback.  
2) Только Contacts picker.  
3) Убрать dial — только «после звонка отметьте» (красный/зелёный).  

**TODO:** `prodqa-s08-11-calls`

---

## S12 — «Статус уточняется» / упрощённый режим / INC-…

**Факт:** «Угроз не найдено» + «Статус уточняется»; «Инцидент зарегистрирован» + ID; «Работает в упрощённом режиме».  
**Причина:** `ComponentStatusCopy` / `fallback_active` = локальный/упрощённый контур без полного server pipeline; INC = локальный id прогона теста реагирования (не «взлом»).  
**Гибрид ★:**  
1) «Статус уточняется» → «Проверяем защиту…» / скрыть если score уже есть.  
2) «Упрощённый режим» → «Базовая проверка на устройстве» (без слова fallback).  
3) INC: «Запись проверки: INC-…» + «Нужна только если поддержка спросит» — не пугать.  
**3 варианта заголовка инцидента:**  
1) ★ «Проверка сохранена»  
2) «Тест защиты записан»  
3) «Отчёт о проверке»  
**TODO:** `prodqa-s12-incident`

---

## S13 — Уведомления: контраст + ошибка API

**Факт:** secondary text почти нечитаем; баннер `ALADDIN.NotificationsAPIError, ошибка 0`; видны raw `ID: local-…`.  
**Причина:** тёмный secondary на navy; error.localizedDescription сырой; debug id в UI.  
**Гибрид ★:**  
1) Контраст: body → white 0.92 / gold accents; unread dot оставить.  
2) Ошибка: «Не удалось обновить список. Показаны сохранённые.» + Retry (реально дергает API).  
3) Скрыть `ID: local-…` из UI (оставить в debug/long-press).  
4) Sync «−13 с» → clamp ≥ 0 / «только что».  
**TODO:** `prodqa-s13-notif`

---

## S15 — Глубокое исследование себя

**Факт:** title без «себя!»; how-it-works дублируется 2×; текст про «стиль».  
**Гибрид ★:** title = «Глубокое исследование себя!»; один блок how-it-works.  

**3 варианта how-it-works:**  
1) ★ «Выберите тон разговора — герой подстроится под вас.»  
2) «Как вам удобнее говорить: поддержка, разбор или один вопрос.»  
3) «Один разговор — вы выбираете, как герой отвечает.»  

**Loc:** `companion_deep_dive_title`, `companion_deep_dive_how` (убрать дубль view).  
**TODO:** `prodqa-s15-deep`

---

## S16 — Календарь → все напоминания + Apple Calendar (APPROVED)

**Делаем сразу:**  
1) Общий UI-календарь (как в Режиме экзамена) для: вода / убрать телефон / лекарство / свои / челленджи / семейный список.  
2) **Синхрон с Календарём Apple (EventKit) сразу** — с запросом разрешения; события пишутся в выбранный календарь семьи/пользователя.  
3) В приложении остаётся свой список (офлайн) + зеркало в Apple Calendar.  
4) Toggle «сообщить родителям» сохраняем где уместно.  

**TODO:** `prodqa-s16-calendar`

---

## S18 — Родительский контроль: дети flicker, 429, Retry, тумблеры, панель

**Факт:** список детей то есть то «загрузка»; «Слишком много запросов»; Retry мёртв; тумблеры без toast; «Панель родителя» непонятна; внутри EN + raw `elderly_*` (см. S24).  
**Причина:** нет cache-first; Retry не сбрасывает cooldown; rate-limit без jitter; CTA panel без navigation destination / disabled hit area.  
**Гибрид ★:**  
1) Cache-first roster (последний успешный список сразу) + silent refresh.  
2) 429: countdown UI «Подождите :45» + Retry enabled when timer 0; экспоненциальный backoff.  
3) Тумблеры: optimistic UI + toast «Сохранено» / «Не удалось — откат».  
4) Проверить wiring: self-harm / grooming / predators / psych bot — real API vs noop.  
5) «Панель родителя» → явная кнопка «Открыть панель» (chevron card).  
**3 варианта панели:**  
1) ★ Карточка-кнопка на весь ряд → ParentDashboard.  
2) Toolbar «Панель».  
3) Убрать дубль — только «Защита детей» expandable.  
**TODO:** `prodqa-s18-parental`

---

## S21 / S23 — Местоположение: «недоступно» vs координаты / город

**Факт:** toggle ON + «геолокация недоступна» + «точность 50м»; иногда только lat/lon без города.  
**Причина:** конфликт статусов (auth vs lastKnown vs CLError); reverse geocode не вызван / failed / язык placemark.  
**Гибрид ★:**  
1) Единый status enum: Off / NeedPermission / Locating / Ready(place) / Stale / Unavailable.  
2) Если есть координаты — **не** писать «недоступно»; писать город/улицу.  
3) Reverse geocode с `Locale` app language (RU/EN city names от Apple Maps data).  
4) Apple: показывать approximate location если Precise off; не фоновый трекинг без Always + purpose string.  
**Можно добавить (Apple-friendly):** город, район, «обновлено N мин», точность, батарея устройства ребёнка (уже в SOS), вход/выход геозоны.  
**Нельзя:** скрытый трекинг, продажа geo, точный адрес в публичных шарах без согласия.  
**TODO:** `prodqa-s21-23-geo`

---

## S22 — Реферал: X + Instagram

**Факт:** Step1 упоминает WA/TG/VK; нет X/Instagram; код на скрине инструкций может быть выше fold.  
**Гибрид ★:** `UIActivityViewController` (система сама даёт X/IG если установлены) + явные кнопки-иконки: копировать / WA / TG / VK / X / IG Stories (IG — обычно share image+text, не чистый deep-link URL).  
**TODO:** `prodqa-s22-referral`

---

## S24 — Parent dashboard: Export/Delete EN + elderly_ raw keys

**Факт:** кнопки English на RU; категории 60+ = `elderly_content_safety` и т.д.  
**Причина:** `ParentDashboardView` hardcode `Button("Export child data")`; LocManager RU тоже EN; seed ids показываются как title без `localized()`.  
**Гибрид ★:**  
RU: «Скачать данные ребёнка» / «Удалить данные активного ребёнка»  
EN: оставить Export/Delete  
Map: `elderly_content_safety` → «Безопасность» / «Safety» и т.д.  
**TODO:** `prodqa-s24-loc`

---

## S25 — Участники семьи: SOS на родителе + модели + какие ещё алерты

**Факт:** «Нужна помощь · время · батарея» на карточке **Родитель A** (должно быть на источнике SOS — ребёнок/60+); raw ID/server tags; нет модели телефона.  
**Гибрид ★:** алерт всегда на **memberId отправителя**; parent видит badge на ребёнке/60+; модели как S04; сократить ID (long-press copy).  

**3 набора важных пушей от детей/60+:**  
1) ★ SOS / Я в порядке / Низкая батарея / Вошёл·вышел из геозоны / Попытка снятия защиты  
2) + Подозрительный звонок отмечен / Долгий «тишина» check-in  
3) Минимальный: только SOS + Я в порядке + геозона  

**TODO:** `prodqa-s25-family`

---

## Глобальный чеклист (не забыть)

- [x] Галочки владельца = P0 в каждой волне  
- [x] Каждое новое слово → `ru.lproj` + `en.lproj` **сначала** (wave keys 53/53 RU+EN, 2026-10-15)  
- [x] `./scripts/verify_localization_manager_integrity.sh` → OK  
- [x] Нет сырых ключей `elderly_*` / `fallback_*` в UI (маппинг human copy)  
- [x] Нет тех. error codes в Notifications (human string)  
- [x] Контраст: InfoRow / Notifications → white/gold (не `.primary` на navy)  
- [x] Retry / CTA: geofence push + parental retry wired  
- [x] bot/`.env` не в staging iOS  
- [x] Ветка `master` перед коммитом  
- [ ] Сборка/TF только после **GO на сборку** / bump  
- [ ] W9 visual QA после TF 

---

## План-Факт трекер (аудит 2026-10-15)

| ID | План (факт владельца) | Код (доказательство) | Loc RU/EN | Вердикт |
|----|----------------------|----------------------|-----------|---------|
| S01 | Parent A → роли по языку | `FamilyMemberDisplayNameFormatter` + Elderly cards | роли в strings+LocMgr | **DONE** |
| S02 | Убрать «почему нет»; CTA push | CTA `geofence_why_no_push_enable_*` → request/Settings | RU «Включить уведомления» / EN OK | **DONE** |
| S03 | Unicorn A везде; B/C удалены | `shouldUseRasterMaster` unicorn→PNG; только `unicorn_master.png` | — | **DONE** |
| S04/17 | Модель hw + контраст | `DeviceMarketingName` + `InfoRow` gold/textPrimary + tabs scale | owner/type/model strings OK | **DONE** |
| S05 | Спокойные минуты + tile6 | `focus_session_*` + `simple_home_tile_advanced_*` | RU/EN OK | **DONE** |
| S06 | Parent sites + честный copy | `ParentalCustomBlockedSitesSection` | keys в strings | **DONE** (remote pack later) |
| S07 | lineLimit Подробнее/Лимиты | AdvancedProtection `lineLimit(1)` | details/limits OK | **DONE** |
| S08–11 | dial + copy Исходящий/Тренировка | phone+`telprompt`+Contacts picker | disclaimer/card/phone OK | **DONE** |
| S12 | human INC/status | `shortIncidentLabel` + status strings | fallback/INC OK | **DONE** |
| S13 | contrast + human error | white text; `notifications_load_failed_human`; ID hidden | OK | **DONE** |
| S15 | Глубокое исследование | `wellness_deep_explore_*` | RU/EN OK | **DONE** |
| S16 | EventKit sync | toggle + `FamilyHabitEventKitSync` | eventkit strings OK | **DONE** |
| S18 | cache/toast/панель | cache-first; toast; dashboard card; 429 countdown 45s | dashboard/retry/wait OK | **DONE** |
| S21/23 | geo не «недоступно» при coords | `applyCachedLocationStatusIfAny` + preferredLocale | stale/unavailable OK | **DONE** |
| S22 | X + Instagram | MessengerType.x/instagram + share sheet | OK (brand names) | **DONE** |
| S24 | Export/Delete + elderly_ | ParentDashboard localized; elderly_content_* human | RU/EN OK | **DONE** |
| S25 | SOS на sender card | multi-id + displayName + local_self migrate | — | **DONE code** (device QA after build GO) |
| S26 | даты сразу | `persistSubscriptionExpiresAtIso` + registration capture | — | **DONE** (optional unwrap fix) |
| LOC | strings-first + integrity | `verify_localization_manager_integrity` OK | wave keys synced | **DONE** (pass 2026-10-15) |
| BUILD | Xcode/TF | — | — | **WAIT GO** |

---

## Следующий шаг (после этого документа)

1. Владелец: подтвердить единорог **A** (или B/D) + тексты ★ где есть 3 варианта.  
2. Агент: W-P0 (S01, S02, S07, S13, S15, S17-contrast, S24) без Xcode.  
3. Затем W-P1 логика.  
4. GO на сборку → TF → visual QA.

---

## Convenient-mode device QA (2026-10-15 ~15:00) — код-фикс

| Симптом в логах | Корневая причина | Фикс |
|-----------------|------------------|------|
| Back с «Расширенные» не возвращает | `dismiss()` при stack-навигации (не sheet) | `goBack()` если `currentScreen == .advancedProtection` |
| Open Phone noop | нет `tel`/`telprompt` в `LSApplicationQueriesSchemes`; пустой `tel://`; Simulator −10814 | schemes + toast + sim honesty |
| Contacts = белый лист | nested `CNContactPicker` sheet внутри prep sheet | picker на уровне hub |
| Check Updates «ничего» | `checkForUpdates()` = только `print` | App Store search + toast |
| GPS/ГЛОНАСС «тишина» в Xcode | VisualLogger ≠ console; iOS multi-GNSS нельзя форсировать | `print` + toast + честная note |
| 3 героя «тишина» | тумблер без Save; нет `print` | лог на toggle + toast на Save |
| `/api/family/presence` 404 | роутер не на проде | отдельный server GO (не mock) |

**Звонки / Apple:** линия оператора **не** записывается. ★ Гибрид C на экране: исходящие prep+mic · входящие «с динамика» · после — память. FAB по центру снизу.

### Hybrid C — ProtectionFeedback (код ✅, QA после GO на сборку)

| Область | Поведение |
|---------|-----------|
| P1 `ProtectionFeedback` | `show(on/off/needsAction)` + helpers Safari/threats/messages |
| P2 Safari | зелёная рамка **только** при Content Blocker `.enabled`; toast «В приложении включено» + жёлтый «Включите в Safari» + CTA; без ложного «защита подключена» |
| P3 Угрозы | статус/toast «Защита от угроз: N из M» + рамка green/orange/gray |
| P4 Сообщения | toast после успешного POST; честный subtitle (без ложного push) |
| P5 Loc | RU/EN strings-first; `verify_localization_manager_integrity.sh` OK |

**Presence 404:** роут в репо есть; прод не трогаем без явного «GO на деплой presence».
