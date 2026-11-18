# ALADDIN × Life360 — тарифы, рост и реализация (SSOT)

**Дата:** 2026-11-18 · **Статус:** план утверждён владельцем, код **ещё не менялся**
**Cursor TODO:** id `l360-*` (только `merge: true`, задачи не удалять)
**Рабочий корень:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS` · ветка `master`
**Вход для бизнеса:** [`ML_SYSTEM_BUSINESS_START_HERE.md`](ML_SYSTEM_BUSINESS_START_HERE.md)

> Для другой ML-системы: сначала прочитай §0 (решения) и §1 (правила), затем бери задачи из §6 по порядку §7. Каждая задача содержит: файл → строки → было → станет → критерий готовности.

---

## 0. Решения владельца (зафиксировано)

| # | Решение | Статус |
|---|---|---|
| D1 | Делаем этапы **0 + 1 + 1Б** (код без деплоя, кроме 1Б.3) | ✅ GO 2026-11-18 |
| D2 | Бесплатная семья — **до 4 человек** (этап 2) | ✅ решено |
| D3 | Тариф **Личный остаётся, цена 100 ₽** (не скрывать с витрины) | ✅ решено |
| D4 | Новый смысл Личного: **«антифрод и защита для себя»**; Семейный — защита всей семьи | ✅ решено |
| D5 | Лимит дорогих ИИ-проверок (голос, видео, документ, анализ звонка) для Личного — **30 в месяц**; номера, ссылки, SMS, текст — без лимита | ✅ решено |
| D6 | Семейный и Премиум — Антифейк **без лимита** (как уже обещано и как работает сервер; только защита от спама) | ✅ «да» владельца 2026-11-18 (после доработок §11) |
| D7 | Тексты карточек RU/EN — §5 | ✅ «да» владельца 2026-11-18 (после доработок §11) |
| D11 | Семейный/Премиум/пробный владельца дают Антифейк **всем участникам** семьи (без лимита); Личный — только себе | ✅ следует из D4 (§11 G1) |
| D12 | Пробный период на этапе 2 — **6 мест** (как Семейный), не меньше бесплатных 4 | ✅ следует из D2 (§11 G2) |
| D8 | Личный на этапе 2 — **не меньше 4 мест** (не может быть хуже бесплатного) | ✅ следует из D2 |
| D9 | Цена года на сайте ниже App Store (960/2784/4704 против 1000/2784/4900) — **оставить** (нет комиссии Apple) | ✅ |
| D10 | Тест цены Личного новым SKU (149/199 ₽) — **не делаем**; тестируем только витрину (A/B) | ✅ следует из D3 |

---

## 1. Правила исполнения (обязательно)

- **Сборка** (`xcodebuild`, симулятор, Archive) — только после фразы владельца «GO на сборку». Rule `ask-before-ios-build.mdc`.
- **Деплой** на 🇷🇺 MAIN — FirstVDS / Аладдин · запас · Россия (`…180`, `/opt/aladdin-backend`) и на сайт — отдельный GO, по `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` (бэкап → `scp` → `py_compile` → restart → `curl /api/health`).
- **Коммит** только на `master`, только по просьбе владельца; `git push` — по фразе «GO на push». Без `telegram_stars_shop_bot/**` и `.env`.
- **Локализация:** новые строки — **только** в `Resources/Localization/{ru,en}.lproj/Localizable.strings` (они читаются раньше словаря). `Core/Localization/LocalizationManager.swift` (~21k строк) **не переписывать**. После правок: `./scripts/verify_localization_manager_integrity.sh` → `OK`, `plutil -lint` обоих `.strings`.
- **Большие файлы** (`SubscriptionManager.swift` 3317 строк, `02_FamilyScreen.swift`, `WhereIsPhoneScreen.swift`) — только точечные правки.
- **Без mock** на parental / family / antifake. Rule `prod-no-mock-bypass.mdc`.
- **Не трогать** файлы `*.tmp`, `*backup*`, `*_Old*` в `Screens/` — это мусор, не часть сборки.

---

## 2. Почему так (выжимка анализа Life360)

| Факт Life360 (Q3 2026) | Что берём |
|---|---|
| Капитализация $3,61 млрд, выручка 2026 ~$670 млн, 107,7 млн MAU, 3,4 млн платящих семей, ~$144 в год с семьи | ориентир масштаба |
| 2008–2012 — **полностью бесплатно**, порог «10 млн активных»; 2013 первый Premium $4,99; 2014 — 50 тыс. платящих; 2016 — $5,3 млн выручки; первая годовая прибыль — 2025 | копируем **принцип**, а не «ноль выручки»: у нас нет VC-денег |
| «Ядро бесплатно навсегда, платят за безопасность» | бесплатная семья и карта, платный антифрод |
| Семья 3–4 человека конвертирует лучше всех; главный показатель — первые 7 дней | этап 1 (аналитика) и этап 3 (онбординг) |
| Дешёвое отдают щедро, дорогое — в старших тарифах | лимит 30 ИИ-проверок в Личном |
| Переводят оплату на сайт (нет комиссии Apple) | Platega и код активации у нас уже есть |

Россия и СНГ: лидер — «Где мои дети» (продажи через операторов). iOS ~31% в РФ. Ущерб от мошенников за 2025 год — 29,3 млрд ₽ (ЦБ). **Свободная ниша ALADDIN:** семейная карта + антифрод + защита пожилых в одном продукте.

Источники: Life360 [Q3'26](https://investors.life360.com/static-files/fdc3babd-fdf0-4c39-bf27-b4248e7380aa) · [отчётность 2016–2018](https://s3.documentcloud.org/documents/21115710/02104288-1.pdf) · [TechCrunch 2013](https://techcrunch.com/2013/07/10/life360-the-family-locator-with-more-users-than-foursquare-raises-10-million-series-b/) · [Forbes 2014](https://www.forbes.com/sites/aarontilley/2014/12/10/the-app-that-tracks-your-kids/) · [Sub Club / Hulls](https://subclub.com/episode/freemium-done-right-lessons-from-a-multi-billion-dollar-app-chris-hulls-life360) · [RevenueCat](https://www.revenuecat.com/blog/growth/freemium-at-scale-how-life360-built-trust-and-hit-1-8b) · [ЦБ](https://www.cbr.ru/press/event/?id=28300).

---

## 3. Что сейчас в коде (факты на 2026-11-18)

### 3.1 Продукты App Store (`ALADDIN/StoreKit/ALADDINSubscriptions.storekit`, группа «ALADDIN Premium»)

| Product ID | Цена | Период | Уровень в группе |
|---|---|---|---|
| `ai.aladdin.subscription.individual.v2` | 100 ₽ | месяц | 1 |
| `ai.aladdin.subscription.family` | 290 ₽ | месяц | 2 |
| `ai.aladdin.subscription.premium` | 490 ₽ | месяц | 3 |
| `….individual.v2.yearly` | 1000 ₽ (−17%) | год | 1 |
| `….family.yearly` | 2784 ₽ (−20%) | год | 2 |
| `….premium.yearly` | 4900 ₽ (−17%) | год | 3 |
| `….basic.v2` | — | нет в ASC | легаси в коде |

Пробный период — **наш**, серверный, 14 дней (не App Store intro offer). Оплата на сайте → код активации → `Screens/26_ActivationCodeScreen.swift`. В сборке App Store экран QR-оплаты заблокирован (`NavigationManager.swift:405`, `AppStoreBuildPolicy`) — это правильно.

### 3.2 Где решается «кому что доступно» — 6 мест

| # | Что решает | Файл : строки | Сейчас | Проблема |
|---|---|---|---|---|
| **A** | Сколько людей в семье (главный замок) | `app/services/family_roster_reconcile.py:14-20` (`_DEFAULT_LEVEL_MAX`) | trial 3 · free **1** · personal 2 · family 6 · premium 15 | фоллбэк `app/routers/family.py:61-62` при ошибке импорта возвращает 1 для всех |
| **B** | Копия лимита для экрана | `Core/Managers/SubscriptionManager.swift:812-825` (`familyMemberLimitStatic`) | 1 · 3 · 2 · 6 · 15 | ✅ совпадает с A |
| **C** | Лимит устройств | `Core/Models/SubscriptionModels.swift:947-1000` (`freeLimits` … `premiumLimits`) | free 1 · trial 3 · personal 2 · family 6 · premium **10** | ❌ премиум 10, сервер 15 |
| **D** | Разделы защиты, род. контроля, доп. функций | `Shared/Models/ThreatProtectionCategory.swift:16-24` (`featureAccessTier`), `:91-141` (конфиг категорий); `Shared/Models/ParentalControlFeature.swift`; `Shared/Models/AdditionalFeature.swift` | уровни: free 1 · personal 2 · family 3 · premium 4 · trial 4 | категория `deepfakes` = premium |
| **E** | Вход в Антифейк | `Core/Security/AntifakeAccessPolicy.swift:31-52` | trial **или** `currentTariff == .premium` **или** категория `deepfakes` (= premium) | ❌ Личный и Семейный не пускает; сервер пускает |
| **F** | Живая карта | `Screens/FamilySafetyRemainderHub.swift:306-330` (`FamilyMapLiveAccess`) | trial, family, premium (+ тариф владельца семьи) | бесплатная — только последняя точка |
| — | Каталог `FeatureRegistry` | `Core/Models/SubscriptionModels.swift:1109+` | `location_tracking`, `panic_button`, `family_chat` = `.family` | **почти не блокирует**: реально вызывается только для `location_bubble_agent`, `dark_web_monitoring_agent` и превью `FeatureGateView` |

Три параллельных типа тарифа: `StoreManager.ProductID`, `TariffType` (`TariffManager`), `SubscriptionLevel` (`SubscriptionModels`).

### 3.3 Сервер Антифейка (`app/routers/antifake.py`, `app/services/antifake_premium.py`)

- Доступ: `PREMIUM_LEVELS` (`antifake_premium.py:12-22`) = premium, trial, trial_premium, **family, personal**, premium_3m, premium_6m. То есть **Личный и Семейный сервер уже пускает**.
- Лимитов по тарифам **нет**, только защита от спама (`antifake.py:72-74`): текст и ссылки — 60 в минуту, медиа — 10 в час, жалобы — 5 в час.
- Дорогие (ИИ) эндпоинты: `POST /check/audio` (`:703`), `/check/video` (`:723`), `/check/document` (`:743`), `/call/analyze` (`:762`). Дешёвые: `/check/text` (`:451`), `/check/url` (`:483`).

### 3.4 Аналитика

- `Core/Analytics/AnalyticsManager.swift:54-75` — `trackEvent` в релизе **ничего не отправляет** (только `print` в DEBUG).
- `Core/Analytics/FamilyReferralAnalytics.swift` пишет в этот же «пустой» `AnalyticsManager` → реферальная воронка не измеряется.
- **Рабочий канал уже есть:** `SubscriptionManager.trackEvent` (`SubscriptionManager.swift:2883`) → очередь → `APIService.sendSubscriptionEventsBatch` (`APIService.swift:2406`) → `POST /api/subscription/events/batch` (`app/routers/subscription_events.py`). Сервер принимает **любой** `eventType` (3–64 символа) и `metadata: Dict[str,str]`, таблица `subscription_event_ingest`, отчёт `GET /api/subscription/events/stats/summary`. **Деплой не нужен.**
- `Core/ABTesting/ABTestingService.swift` (273 строки) — готовый A/B-сервис, **нигде не используется**.

---

## 4. Расхождения (что видит пользователь)

| # | Что видит | Где | Почему ошибка | Задача |
|---|---|---|---|---|
| 1 | Личный и Семейный: «Antifake» в списке, а при нажатии — экран тарифов | замок E | обещано, но не выдаётся | 1Б.2 |
| 2 | Личный: «Защита одного устройства» и «До 2 участников» | `tariffs_personal_features_1` + строка лимита | противоречие | 0.2 |
| 3 | Личный и Семейный: «Antifake по лимиту тарифа / по тарифу» и «Antifake: без лимита» | `tariffs_personal_features_3`, `tariffs_family_features_5` + `tariffs_antifake_paid` | две строки спорят | 0.2 |
| 4 | Премиум: «Безлимит Antifake…» и «Antifake: без лимита…» | `tariffs_premium_features_3` + `tariffs_antifake_paid` | повтор | 0.2 |
| 5 | Премиум: «Расширенные лимиты устройств», «Живая карта для всей семьи» | `tariffs_premium_features_6`, `_7` | первое дублирует «До 15», второе есть и в Семейном | 0.2 |
| 6 | Лимит устройств Премиума 10 | `SubscriptionModels.swift:992-1000` | сервер 15 | 0.1 |
| 7 | Описания в `StoreManager`: Премиум «до 15» в `description` и «до 10» в `features`; Индивидуальный «1 устройство» и «до 2 участников»; только русский | `Core/Store/StoreManager.swift:102-131` | вшиты в код, спорят | 0.4 |
| 8 | «До N участников…» | `Screens/10_TariffsScreen.swift:134-140` | RU/EN вшиты в код | 0.3 |
| 9 | Ключ `tariffs_gates_check` дважды | RU `Localizable.strings:1846` и `:1866`; EN `:1960` и `:1980` | дубль, побеждает последний | 0.5 |
| 10 | Сайт: Личный 4 устройства, Премиум 10 и «Безлимитные устройства», JSON-LD «до 5 устройств» | `landing/index.html:185-275`, `:2022` | сервер 2 / 15 / 6 | С.1 |
| 11 | Таблица сравнения: «Антифейк без лимита» — только у Премиума | `10_TariffsScreen.swift` `honestGatesComparisonTable` | D6: Семейный тоже без лимита | 0.2 (найдено при реализации) |
| 12 | Таблица сравнения: «Длинная история» — только у Премиума | там же, `tariffs_gates_history_long` | неправда, у всех 7 дней (G9) | 0.2 (строка убрана) |
| 13 | `tariffs_premium_simple`: «Всё из Семейного · длиннее история…» | `Localizable.strings` RU/EN | та же неправда | 0.2 |
| 14 | Тост пробного: «3 места» вшито числом | `10_TariffsScreen.swift` (`tariffs_trial_activated_slots`, 3) | после 2.2c станет 6 | 0.7 |

---

## 5. Тексты карточек RU / EN (утверждаются владельцем — D7)

Правило: одна мысль — одна строка; никаких «по лимиту» и «без лимита» в одной карточке.

### 5.1 Личный, 100 ₽

| # | Ключ | RU | EN |
|---|---|---|---|
| 1 | `tariffs_personal_features_3` (новое значение) | Антифрод для себя: звонки, SMS, ссылки, переводы | Anti-fraud for you: calls, texts, links, transfers |
| 2 | `tariffs_personal_voice_video_limit` (**новый**, `%d`, показывать только после деплоя 1Б.3) | Проверка голоса и видео — %d в месяц | Voice & video checks — %d per month |
| 3 | `tariffs_member_limit_format` (**новый**, `%d`) | До %d участников в семье | Up to %d family members |
| 4 | `tariffs_personal_ai` (**новый**) | ИИ-помощник по безопасности | AI safety assistant |
| 5 | `tariffs_personal_features_6` (как есть) | Только по вашему действию — без фоновой записи | Only when you act — no background recording |

Убрать из карточки: `tariffs_personal_features_1`, `_4`, `_5`, `tariffs_antifake_paid`.

### 5.2 Семейный, 290 ₽

| # | Ключ | RU | EN |
|---|---|---|---|
| 1 | `tariffs_family_features_1` (как есть) | Карта семьи и места | Family map and places |
| 2 | `tariffs_member_limit_format` | До %d участников в семье | Up to %d family members |
| 3 | `tariffs_family_features_5` (новое значение) | Антифрод для каждого в семье | Anti-fraud for everyone in the family |
| 4 | `tariffs_family_scam_alert` (**новый**) | Оповещение родных о звонке мошенника | Alert your family about scam calls |
| 5 | `tariffs_family_features_3` (как есть) | Лимиты и контроль ребёнка | Child limits and parental controls |
| 6 | `tariffs_family_features_4` (как есть) | SOS / «нужна помощь» | SOS / “help needed” |
| 7 | `tariffs_family_features_6` (как есть) | Поездки и тихая зона | Trips and quiet zone |

Убрать из карточки: `tariffs_antifake_paid`, `tariffs_antifake_action_only`.
Перед публикацией строки 4 проверить, что оповещение семьи работает на Семейном (`Core/Security/FamilyScamCallFunnel.swift`, `Core/Family/AntifakeFamilyPushRegistrar.swift`).

### 5.3 Премиум, 490 ₽

| # | Ключ | RU | EN |
|---|---|---|---|
| 1 | `tariffs_premium_features_1` (новое значение) | Всё из Семейного | Everything in Family |
| 2 | `tariffs_member_limit_format` | До %d участников в семье | Up to %d family members |
| 3 | `tariffs_premium_features_3` (новое значение) | Антифрод без лимита: текст, голос, видео, звонок | Unlimited anti-fraud: text, voice, video, call |
| 4 | `tariffs_premium_features_5` (как есть) | Приоритетная поддержка семьи | Priority family support |

Убрать из карточки: `tariffs_premium_features_4` («Длиннее история мест» — **проверено: неправда**, у всех 7 дней на телефоне, `GeofenceEventStore.swift:18`; вернуть на этапе 4), `_6`, `_7`, `_8`, `tariffs_antifake_paid`.

### 5.4 Сообщения лимита (1Б.3)

| Ключ | RU | EN |
|---|---|---|
| `premium_nudge_antifake_title` (**уже есть**, переиспользован вместо нового `antifake_quota_exhausted_title`) | Нужно больше проверок? | Need more checks? |
| `antifake_quota_exhausted_body` (**новый**, `%d` = лимит с сервера) | %d проверок голоса и видео в этом месяце уже использованы. Лимит обновится 1-го числа. | You’ve used all %d voice & video checks this month. The limit resets on the 1st. |
| `premium_nudge_cta` (**уже есть**, переиспользован вместо нового `antifake_quota_upgrade_cta`) | как в строках | Смотреть тарифы | See plans |

Факт реализации: при 429 `monthly_quota_exceeded` показывается существующая карточка `Shared/Components/AntifakeInlinePremiumGateCard.swift` (`requiresPremiumUpgrade`) с текстом `antifake_quota_exhausted_body`; отдельного экрана и ключей `_title`/`_cta` не заводили — меньше новых строк на App Review.

Число «30» в iOS не вшивать: брать `limit` из ответа сервера (429 или `GET /api/antifake/quota`), чтобы менять лимит без новой сборки.

### 5.5 Кнопка перехода (1Б.4)

| Ключ | RU | EN |
|---|---|---|
| `tariffs_upgrade_personal_to_family_cta` | Защитить всю семью — +190 ₽ в месяц | Protect your whole family — +190 ₽/month |
| `tariffs_upgrade_personal_to_family_note` | Остаток оплаты App Store пересчитает сам | App Store prorates what you’ve already paid |

Цену «+190 ₽» не хардкодить: считать из StoreKit (`family.displayPrice − individual.displayPrice`); если цены не загружены, показывать текст без суммы.

### 5.6 Бесплатный (этап 2)

| Ключ | Сейчас RU | Станет RU | Станет EN |
|---|---|---|---|
| `tariffs_free_features_1` | 1 участник в семье | Семья до 4 человек | Family of up to 4 |
| `tariffs_free_features_3` | Карта — 1 last-point… | Живая карта семьи | Live family map |
| `tariffs_free_features_9` | Live-карта в реальном времени (в списке «не входит») | убрать из «не входит» | — |
| `tariffs_free_features_10` | Несколько участников и полный Family-пакет | Больше 4 человек и антифрод | More than 4 members and anti-fraud |
| `tariffs_gates_free_note` | Free: 1 участник · 1 last-point… | Бесплатно: семья до 4, живая карта, SOS. Антифрод — с Личного. | Free: family of up to 4, live map, SOS. Anti-fraud from Personal. |
| `tariffs_free_simple` | 1 устройство · … | Семья до 4 · живая карта · SOS | Family of up to 4 · live map · SOS |

---

## 6. Задачи — что, где, как

Формат: **ID · TODO id · где · было → станет · готово когда**. Деплой: «нет» = только iOS.

### Этап 0 — порядок в тарифах (деплой: нет)

**0.1 · `l360-0-1` · лимит устройств Премиума**
- Где: `Core/Models/SubscriptionModels.swift:992-1000` (`premiumLimits.maxDevices`).
- Было `10` → станет `15`. Остальные (1/3/2/6) уже совпадают с сервером.
- Готово: значения = §3.2 A; `rg "maxDevices: 10"` в `Core/` пусто.

**0.2 · `l360-0-2` · тексты карточек**
- Где: `Resources/Localization/ru.lproj/Localizable.strings` и `en.lproj` (значения из §5.1–5.3); состав карточек — `Screens/10_TariffsScreen.swift:58-100` (`features(localizationManager:)`).
- Новые ключи — рядом с блоком `tariffs_personal_features_*` (RU ~`:4024`, EN ~`:4114`).
- `tariffs_personal_voice_video_limit` в карточку **не добавлять** до 1Б.3.
- Готово: в каждой карточке одна строка про антифрод; нет «1 устройства» рядом с «до N»; RU и EN одинаковое число строк.

**0.3 · `l360-0-10` · строка «До N участников»**
- Где: `Screens/10_TariffsScreen.swift:134-140` (`familyMemberLimitFeatureText`).
- Было: `if currentLanguage == .russian { "До \(limit)…" } else { "Up to…" }` → станет: `String(format: localizationManager.localized("tariffs_member_limit_format"), limit)`.
- Готово: в Swift нет вшитых «До … участников» / «Up to … family members».

**0.4 · `l360-0-9` · описания в StoreManager**
- Где: `Core/Store/StoreManager.swift:102-131` (`displayName`, `description`, `features`); используются в `ViewModels/TariffsViewModel.swift:191-197` → `Tariff.features`.
- Было: русский текст в коде («До 10 участников», «1 устройство…») → станет: те же ключи, что и карточки (`tariffs_personal`, `tariffs_family`, `tariffs_premium` + списки из §5) через `LocalizationManager.shared.localized`. Лимит — через `familyMemberLimitStatic`.
- Готово: в `StoreManager.swift` нет русских строк с числами участников.

**0.5 · `l360-0-8` · дубль ключа**
- Где: RU `Localizable.strings:1846` и `:1866`, EN `:1960` и `:1980` — `tariffs_gates_check`.
- Оставить одну запись: последнюю, она сейчас и показывается — «Проверить Antifake (звонок/текст/видео)» / «Antifake Check (call/text/video)».
- Готово: `rg -c '^"tariffs_gates_check"'` = 1 в каждом файле; `plutil -lint` OK.

**0.6a · `l360-0-3` · легаси `basic.v2`**
- Где: `StoreManager.swift:52` и switch'и `:104/:113/:122`; ссылки `TariffsViewModel.swift:571, 584, 657`.
- Не удалять (на него ссылаются маппинги) → добавить `@available(*, deprecated, message: "Not in App Store Connect")` или однострочный комментарий-ограничение.
- Готово: сборка не ломается (проверит владелец на GO-сборке).

**0.6b · `l360-0-4` · устаревший комментарий**
- Где: `ViewModels/TariffsViewModel.swift:255-259`. Было «В России → PaymentQRScreen…» → станет: «App Store build: IAP only; оплата на сайте — через код активации».

**0.7 · `l360-0-5` · одна таблица тарифов**
- Новый файл: `Core/Store/TariffEntitlements.swift` (~60 строк):
  ```swift
  enum TariffEntitlements {
      static func level(for tariff: TariffType) -> SubscriptionLevel
      static func familyMemberLimit(_ level: SubscriptionLevel) -> Int   // = сервер §3.2 A
      static func maxDevices(_ level: SubscriptionLevel) -> Int
      static func canUseAntifake(_ level: SubscriptionLevel) -> Bool     // personal, family, premium, trial
      static func hasLiveMap(_ level: SubscriptionLevel) -> Bool         // этап 2: true для всех
      static func antifakeMonthlyHeavyQuota(_ level: SubscriptionLevel) -> Int? // personal = 30, иначе nil
  }
  ```
- Перевести на неё (точечно, тело функции → вызов): `SubscriptionManager.familyMemberLimitStatic` (B), `SubscriptionLimits.*.maxDevices` (C), `AntifakeAccessPolicy` (E), `FamilyMapLiveAccess.isEntitled` (F). Замок D (`featureAccessTier`) оставить, но сверить с `level(for:)` комментарием-ограничением.
- `FeatureRegistry` **не трогать** (каталог) — только пометить в шапке: «не источник правды по доступу, см. `TariffEntitlements`».
- Файл добавить в target `ALADDIN` в `ALADDIN.xcodeproj` (иначе не соберётся).
- Готово: числа лимитов и правила доступа к Антифейку и живой карте задаются только в `TariffEntitlements.swift`.

### Этап 1Б.2 — открыть Антифейк с Личного (деплой: нет)

**1Б.2 · `l360-0-7`**
- Где: `Core/Security/AntifakeAccessPolicy.swift:49-51`.
- Было: `if manager.currentTariff == .premium { return true }; return manager.isCategoryAvailable(.deepfakes)` → станет: `return TariffEntitlements.canUseAntifake(subs.getCurrentLevel())` (оставив проверки trial выше без изменений).
- Категорию `deepfakes` в `ThreatProtectionCategory.swift:116-117` оставить Премиумом: это каталог «100 видов защиты», а не вход в Антифейк.
- Комментарий в шапке (`:3-5`) привести к факту: «Personal, Family, Premium, Trial — как сервер `PREMIUM_LEVELS`».
- Готово: на тестовом аккаунте personal/family раздел открывается и проверка проходит (сервер уже пускает); free — экран тарифов.

### Этап 1 — аналитика активации (деплой: нет)

**1.1 · `l360-1-1` · пересылка событий роста**
- Где: `Core/Managers/SubscriptionManager.swift:74-104` (`enum SubscriptionEvent`) — добавить кейсы:
  `family_created`, `family_invite_sent`, `family_member_joined`, `app_open_day`, `paywall_shown`, `paywall_upgrade_tap`, `referral_a_*` (8 значений из `FamilyReferralAnalytics.Stage`), `ab_assignment`.
- Где: `Core/Analytics/AnalyticsManager.swift:54` — если `SubscriptionEvent(rawValue: eventName)` существует → `Task { @MainActor in SubscriptionManager.shared.trackEvent(event, metadata: safeMeta) }`. Новую систему **не делать**.
- Готово: одно событие → одна запись в `subscription_event_ingest`.

**1.2 · `l360-1-2` · где ставить события**

| Событие | Место |
|---|---|
| `family_created` | `ViewModels/FamilyRegistrationViewModel.swift:426` (`createFamily`, ветка success) |
| `family_member_joined` | `FamilyRegistrationViewModel.swift:1065` (`joinFamilySanitized`, success) и `Shared/Components/Modals/InvitationCodeInputModal.swift:325` |
| `family_invite_sent` | места `FamilyReferralAnalytics.track(.inviteTap…)`: `Screens/02_FamilyScreen.swift:3741`, `Screens/11_ProfileScreen.swift:721, 743`, `Screens/21_ReferralScreen.swift:201, 1165` + `APIService.createFamilyInvite` (`:202`, success) |
| `app_open_day` | `ALADDINApp.swift`, `scenePhase == .active`: не чаще 1 раза в календарный день; `metadata.day_index` = дни с первой установки (дату первого запуска хранить в `UserDefaults`, если её нет) |
| `paywall_shown` | `Screens/10_TariffsScreen.swift`, `.onAppear`, `metadata.source` |
| покупка | уже есть: `upgradeCompleted` в `SubscriptionManager` — не дублировать |

**1.3 · `l360-1-3` · без персональных данных**
- В `metadata` пропускать только ключи: `source, method, tier, status, days, code_len, day_index, variant, experiment, product_id, plan`. Значения — `String`, ≤64 символов. Имена, телефоны, коды приглашений, координаты — **никогда**.
- Готово: проверить `pendingEvents` в DEBUG — нет лишних ключей.

**1.5 · отчёт (на сервере, только чтение, после GO на SSH)**
```sql
-- семьи, где за 7 дней после создания вступили ≥2 человека
SELECT COUNT(DISTINCT user_id) FROM subscription_event_ingest WHERE event_type='family_created';
SELECT COUNT(DISTINCT user_id) FROM subscription_event_ingest WHERE event_type='app_open_day'
  AND json_extract(metadata_json,'$.day_index') = '7';
```
Сводка без SQL: `GET /api/subscription/events/stats/summary?days=7`.

### Этап 1Б — «Личный: антифрод для себя»

**1Б.1 · `l360-1b-1`** — тексты §5.1 (входит в 0.2).

**1Б.3 · `l360-1b-3` · лимит 30 в месяц (деплой: да, MAIN, отдельный GO)**
- Новый сервис `app/services/antifake_personal_quota.py`: таблица `antifake_monthly_usage(user_id, month, heavy_count)` (`CREATE TABLE IF NOT EXISTS`), атомарный `INSERT … ON CONFLICT … DO UPDATE … WHERE heavy_count < :limit RETURNING`. Месяц — по Москве (UTC+3). Лимит — env `ANTIFAKE_PERSONAL_MONTHLY_HEAVY_LIMIT` (по умолчанию 30; `0` = выключить лимит без нового деплоя кода).
- `app/routers/antifake.py` `_enqueue_media_job` (`:608`): `job_type` уже приходит из `/check/audio`, `/check/video`, `/check/document`, `/call/analyze` — правки эндпоинтов не нужны. Списывать **после** проверки файла (`validate_media_upload`) и до `create_job`: битый файл не съедает лимит. Превышение → `HTTP 429`, `detail = {"error":"monthly_quota_exceeded","limit":30,"used":30,"resets_at":"YYYY-MM-01"}`.
- Новый `GET /api/antifake/quota` → `{"limited":bool,"limit":int|null,"used":int,"resets_at":str|null}` — для строки «осталось N».
- Лимит только у **своего** Личного. Если человек ещё и участник семьи с Семейным/Премиумом владельца — без лимита (D11). Family, Premium, Trial — без изменений (D6). Переход на Семейный снимает лимит сразу (уровень проверяется на каждом запросе).
- Тесты: `backend_tests/test_antifake_personal_quota.py` (pytest, без БД).
- iOS: обработать `monthly_quota_exceeded` → тексты §5.4 + кнопка 1Б.4; только после этого включить строку `tariffs_personal_voice_video_limit` в карточке.
- Готово: на personal 31-я проверка голоса → 429 и понятный экран; на family ограничений нет; `/api/health` 200.

**1Б.6 · `l360-1b-6` · Антифейк участникам семьи по тарифу владельца (деплой: да, MAIN, вместе с 1Б.3)** — §11 G1
- Сервер: новый `app/services/antifake_family_entitlement.py` (⚠️ не `antifake_family_share.py` — это уже существующий модуль «поделиться вердиктом с семьёй», его не трогать) → `family_owner_grants_antifake(db, user_id)`: последние членства в `family_members` → `families.owner_user_id` → `subscription_trial_snapshot_from_db` + `effective_level_from_parts` → уровень владельца ∈ {family, premium, trial, trial_premium, premium_3m, premium_6m}. Вызвать в конце `user_has_antifake_access_resolved` (`app/services/antifake_web_premium.py:69`). Личный владельца **не** делится (D4).
- iOS: `AntifakeAccessPolicy.canSubmitChecks` — дополнительно `TariffEntitlements.ownerTierSharesFamilyPerks(FamilyMapLiveAccess.cachedOwnerTier)` (кэш уже пишется из `/api/family/stats.ownerSubscriptionTier`).
- Тесты: в `backend_tests/test_antifake_personal_quota.py` (существующий `test_antifake_family_share.py` проверяет другой модуль и должен оставаться зелёным).
- Готово: у бесплатного участника семьи с Семейным владельца проверка проходит; у участника семьи с Личным владельца — экран тарифов.

**1Б.7 · `l360-1b-7` · события ценности Антифейка (деплой: нет)** — §11 G8
- `antifake_quota_hit` (metadata `source=antifake_check`) — при 429 `monthly_quota_exceeded`; `paywall_upgrade_tap` (metadata `source=personal_upsell`, `plan=family`) — нажатие кнопки 1Б.4.
- Факт: `source=antifake_quota` для `paywall_upgrade_tap` **не** сделан — экран лимита ведёт в общий экран тарифов; связку «лимит → покупка» считать по `antifake_quota_hit` → `paywall_shown` → `upgrade_completed` у того же пользователя.

**1Б.4 · `l360-1b-4` · кнопка «+190 ₽»**
- Где: `Screens/10_TariffsScreen.swift` — для активного `individual.v2` показывать CTA §5.5 → покупка `family` (StoreKit сам делает апгрейд в группе: уровень 1 → 2). Плюс в экране лимита §5.4.
- Готово: у подписчика Личного кнопка видна, у остальных — нет.

**1Б.5 · `l360-1b-5` · тест витрины A/B**
- Где: ~~`Core/ABTesting/ABTestingService.swift`~~ — **проверено: файла нет в Xcode-target** (не компилируется), поэтому эксперимент живёт в `Core/Store/TariffEntitlements.swift` → `enum TariffShowcaseExperiment`: `tariff_showcase_v1`, варианты `control` / `family_first`, 50/50, вариант хранится в `UserDefaults` `ab_test_tariff_showcase_v1_variant`.
- Факт: `family_first` меняет **порядок** карточек (Семейный первым); бейдж «Рекомендуем» у Семейного уже есть в обоих вариантах. Компактной карточки Личного нет — тексты §5.1 и так короткие.
- `control`: как сейчас. `family_first`: Семейный — «Рекомендуем» (уже `recommended` в `10_TariffsScreen.swift:116`) и первым, Личный — компактная карточка с текстами §5.1.
- Назначение варианта → событие `ab_assignment` (`metadata.experiment`, `variant`) через канал 1.1. Сейчас `trackExperimentAssignment` пишет в `ProductionMonitoringService` — добавить вызов канала 1.1.
- Метрики (3–6 недель): выручка на 1000 `paywall_shown`; доля покупок Личный / Семейный; отток на 2-м месяце.

### Этап 2 — бесплатная семья (деплой: да, MAIN, отдельный GO)

| ID | TODO | Где | Было → станет |
|---|---|---|---|
| 2.1 | `l360-2-1` | `app/services/family_roster_reconcile.py:16` | `"free": 1` → `4` |
| 2.2 | `l360-2-2` | там же `:17` + `TariffEntitlements.familyMemberLimit` | `"personal": 2` → `4` |
| 2.2b | `l360-2-2` | `app/routers/family.py:61-62` (фоллбэк) | вернуть значения из той же таблицы, а не всегда 1 |
| 2.2c | `l360-2-2` | `family_roster_reconcile.py:15` `"trial": 3` + `TariffEntitlements.familyMemberLimit(.trial)` + `backend_tests/test_family_roster_reconcile.py` | 3 → **6** (D12: пробный не хуже бесплатного) |
| 2.2d | `l360-2-5` | `app/routers/family.py:1093-1111` | понижение тарифа: уже вступившие участники **остаются**, блокируется только добавление нового (409). Проверить кодом, не обещать в тексте, пока не проверено |
| 2.3 | `l360-2-3` | `TariffEntitlements.hasLiveMap` → `FamilySafetyRemainderHub.swift:306-330` | только family/premium/trial → все |
| 2.4 | `l360-2-4` | `Localizable.strings` RU/EN | тексты §5.6 |
| 2.5 | — | тестовые аккаунты | у текущих подписчиков ничего не пропало; 5-й человек в бесплатной семье получает 409 `open_tariffs_or_free_seat` |

Выкатывать сервер (2.1, 2.2) и iOS-тексты (2.4) **одновременно**, иначе экран пообещает 4 места при серверных 1.

### Сайт (деплой: да, сайт, отдельный GO)

**С.1 · `l360-site-1`** — `landing/index.html`:

| Строка | Было | Станет |
|---|---|---|
| `:214` Personal `devices` | 4 | 2 (после этапа 2 → 4) |
| `:226-231` Personal `perks` | «Фильтрация сайтов и защита семьи», «Мониторинг 4 устройств» … | тексты §5.1 |
| `:259` Premium `devices` | 10 | 15 |
| `:271-275` Premium `perks` | «Безлимитные устройства в семье» | «До 15 участников в семье» + §5.3 |
| `:2022` JSON-LD | «до 5 устройств» | «до 6 участников» |

Цены года на сайте не трогать (D9).

### Этапы 3–5 (после этапов 0–2, отдельные GO)

- **3 — онбординг «собери семью»:** шаг «Пригласите 2 близких» (`Shared/Components/InviteOGComposer.swift`); пуш на 2–3 день; экран тарифов в момент ценности (3-е место, история, лимит Антифейка), а не сразу. Метрика: семьи 3+ за 7 дней.
- **4 — платная глубина:** история перемещений на сервере (сейчас только локально: `Core/Family/GeofenceEventStore.swift:18`, 7 дней на телефоне) — 24 ч бесплатно / 7 дней Семейный / 30 дней Премиум; напоминания за 3–7 дней до окончания оплаты на сайте.
- **5 — рынки:** коды операторов через `app/routers/promo.py` + `Screens/PromoActivationScreen.swift`; Казахстан (тенге, казахский язык); решение по Android.

---

## 7. Порядок работы

```
0.1 → 0.5 → 0.3 → 0.4 → 0.2 → 0.6 → 0.7 → 1Б.2 → 1Б.6 (iOS) → 1.1 → 1.2 → 1.3 → 1Б.7 → 1Б.5 → 1Б.4
→ сервер 1Б.3 + 1Б.6 — код и pytest локально (без деплоя)
→ verify (`l360-verify`) + сверка план/факт (§12) → сборку делает владелец сам
→ [GO деплой MAIN] 1Б.3 + 1Б.6 — **до** отправки сборки в App Store (иначе участник семьи увидит 403)
→ [GO деплой] этап 2 (+2.2c, 2.2d) + С.1
```

## 8. Проверки перед словом «готово» (`l360-verify`)

1. `./scripts/verify_localization_manager_integrity.sh` → `OK`.
2. `plutil -lint Resources/Localization/ru.lproj/Localizable.strings Resources/Localization/en.lproj/Localizable.strings` → OK.
3. Каждый новый ключ есть **и** в RU, **и** в EN: `rg -c` по ключам §5.
4. `git diff --stat` — без тысяч удалённых строк; нет `telegram_stars_shop_bot/`, `.env`.
5. `rg -n 'maxDevices: 10' Core` и `rg -n 'участников в семейном доступе' Screens` → пусто.
6. Сборка, симулятор, Device QA — **только после «GO на сборку»**. Сценарии: free / personal / family / premium / trial — карточки, вход в Антифейк, живая карта, лимит семьи.

## 9. Риски

| Риск | Что делаем |
|---|---|
| Личный за 100 ₽ «съедает» Семейный | тест 1Б.5, решение по данным через 3–6 недель |
| Безлимитные ИИ-проверки на Личном до деплоя 1Б.3 | временно; защита от спама 10 медиа в час уже есть на сервере |
| Экран обещает 4 места при серверной 1 | 2.1, 2.2 и 2.4 выкатываются вместе |
| Аналитика забивает очередь | только whitelist событий; лимит очереди 1000 уже есть (`SubscriptionManager.swift:2914`) |
| Правка mega-file локализации | только `.strings` + verify-скрипт |

## 11. Доработки после ревью плана (2026-11-18)

Что не хватало первой версии и куда это внесено.

| # | Дыра | Почему важно | Куда внесено |
|---|---|---|---|
| G1 | Сервер Антифейка смотрит только **свой** тариф. Бесплатный участник семьи с Семейным владельца получит 403, хотя карточка обещает «антифрод для каждого в семье» | главное обещание Семейного не выполнялось бы | 1Б.6, D11 |
| G2 | После этапа 2 пробный (3 места) хуже бесплатного (4) | пробный не может быть хуже бесплатного | 2.2c, D12 |
| G3 | Не описано, что будет при понижении тарифа (было 6 человек — стал Личный) | страх «семью удалят» → отток | 2.2d |
| G4 | Лимит 30 был вшит в текст; нет выключателя; не ясно, какой месяц и что списывается | менять лимит без сборки; не наказывать за битый файл | 1Б.3, §5.4 |
| G5 | Нет цифр успеха и правила решения | без них A/B ничего не решит | §13 |
| G6 | Нет тестов на новые правила сервера | лимиты и доступ — деньги и доверие | 1Б.3, 1Б.6 (pytest) |
| G7 | Описания подписок в App Store Connect не совпадут с новыми карточками | расхождение витрины и App Store, вопросы App Review | §14 (владелец) |
| G8 | Не измеряем, получает ли Личный ценность и как часто упирается в лимит | без этого нельзя решить про цену Личного | 1Б.7 |
| G9 | «Длиннее история мест» на Премиуме — неправда (у всех 7 дней) | ложное обещание в платном тарифе | §5.3 — строка убрана до этапа 4 |
| G10 | Порядок выката: iOS пускает участников раньше, чем сервер | 403 у пользователей | §7 — сервер до App Store |

Осталось как риск: у Премиума мало отличий от Семейного (15 мест и поддержка). Настоящее отличие появится на этапе 4 (история 30 дней).

## 12. Сверка план / факт

Сверка 2026-11-18, после реализации. Сборку Xcode делает владелец; агент `xcodebuild` не запускал. Деплой MAIN и сайта — сделаны (строки ниже); коммит — после решения по этапам 4–5.

| Задача | Файлы (факт) | Статус | Доказательство |
|---|---|---|---|
| 0.1 Премиум 15 устройств | `Core/Models/SubscriptionModels.swift` → `TariffEntitlements.maxDevices` | ✅ | `rg 'maxDevices: 10'` → пусто |
| 0.2 Тексты карточек §5.1–5.3 | `Screens/10_TariffsScreen.swift` `features`; RU/EN `.strings` | ✅ | ключи RU=1 EN=1; `plutil -lint` OK |
| 0.2+ Таблица сравнения (§4 №11–13) | `10_TariffsScreen.swift` `honestGatesComparisonTable`; `tariffs_premium_simple` | ✅ | строка history_long удалена; antifake_limit: Семейный ✓ |
| 0.3 «До N участников» | `tariffs_member_limit_format` | ✅ | `rg 'участников в семейном доступе'` → пусто |
| 0.4 StoreManager без вшитого русского | `Core/Store/StoreManager.swift` → `ProductID.tariffType` | ✅ | diff: `displayName/description/features` из `TariffType` |
| 0.5 Дубль `tariffs_gates_check` | RU/EN `.strings` | ✅ | `rg -c` → 1 и 1 |
| 0.6a / 0.6b | `StoreManager.swift` комментарий `basic`; `TariffsViewModel.swift` комментарий | ✅ | diff |
| 0.7 Одна таблица замков B/C/E/F | новый `Core/Store/TariffEntitlements.swift` (в target, `project.pbxproj` A360E001/2) | ✅ | `familyMemberLimitStatic`, `maxDevices`, `AntifakeAccessPolicy`, `FamilyMapLiveAccess`, тост trial читают его |
| 0.7 замок D (каталог `deepfakes` = premium) | `ThreatProtectionCategory.swift` | ⏸ намеренно не тронут | это каталог, не вход в Антифейк (1Б.2) |
| 1Б.1 Тексты Личного | `.strings` §5.1 | ✅ | — |
| 1Б.2 Антифейк с Личного | `Core/Security/AntifakeAccessPolicy.swift` | ✅ | DEBUG-override пробного не открывает доступ |
| 1Б.3 Лимит 30 голос/видео — сервер | `app/services/antifake_personal_quota.py`, `app/routers/antifake.py` (`_enqueue_media_job`, `GET /quota`) | ✅ код · ⏳ деплой MAIN (GO) | pytest 15/15 |
| 1Б.3 iOS | `PremiumGateHandler.swift` (`AntifakeMonthlyQuota`), `NetworkManager.swift`, `APIService.getAntifakeQuota`, `SecurityVerdictModels.swift`, `AppConfig`, `AntifakeTLSRouting` | ✅ | строка «%d в месяц» появится сама после деплоя (из `/quota`) |
| 1Б.4 Кнопка «+190 ₽» | `10_TariffsScreen.swift` `personalToFamilyUpgradeCard`; `TariffsViewModel.personalToFamilyUpgradeDelta` | ✅ | разница цен из StoreKit, не вшита; на экране лимита — общая кнопка «Смотреть тарифы» |
| 1Б.5 A/B витрины | `TariffEntitlements.swift` `TariffShowcaseExperiment` | ✅ (порядок карточек) | `ABTestingService` вне target — см. 1Б.5 |
| 1Б.6 Антифейк участникам — сервер | новый `app/services/antifake_family_entitlement.py`; `antifake_web_premium.py` | ✅ код · ⏳ деплой MAIN (GO) | pytest; `test_antifake_family_share.py` (старый модуль) зелёный |
| 1Б.6 iOS | `AntifakeAccessPolicy` + `FamilyMapLiveAccess.cachedOwnerTier` | ✅ | — |
| 1Б.7 События | `PremiumGateHandler` (`antifake_quota_hit`), `10_TariffsScreen` (`paywall_upgrade_tap`) | ✅ (без `source=antifake_quota`) | — |
| 1.1 Канал событий на сервер | `Core/Analytics/AnalyticsManager.swift` → `SubscriptionManager.trackEvent` → `/api/subscription/events/batch` | ✅ | whitelist событий и ключей, без PII, ≤64 символа |
| 1.2 События активации | `FamilyRegistrationViewModel` (created/joined), `APIService.createFamilyInvite` (invite_sent), `ALADDINApp` (`app_open_day`), `10_TariffsScreen` (`paywall_shown`) | ✅ | покупки уже шли через `SubscriptionManager` |
| 1.3 / 1.4 Реферальная воронка без PII | `FamilyReferralAnalytics` (8 этапов) → тот же канал | ✅ | имена этапов = `SubscriptionEvent` |
| Деплой 1Б.3 + 1Б.6 | 🇷🇺 MAIN — FirstVDS / Аладдин · запас · Россия (…180), бэкап `/opt/aladdin-backend/backups/l360_20261118_173643` | ✅ 2026-11-18 | `/api/health` 200; `GET /api/antifake/quota` 200 с токеном, `personal_monthly_limit` 30 |
| Этап 2 сервер (2.1, 2.2, 2.2b, 2.2c) | `family_roster_reconcile.py` `_DEFAULT_LEVEL_MAX` free 4 / trial 6 / personal 4 / family 6 / premium 15; `family.py` `_FALLBACK_LEVEL_MAX`; бэкап `…/backups/l360_stage2_20261118_174554` | ✅ деплой MAIN | pytest `test_family_roster_reconcile.py` (+ `test_trial_never_below_free`); `aladdin-family-prod-smoke` PASS |
| 2.2d понижение тарифа | `family.py` add-gate | ✅ проверено кодом | участники не удаляются, блокируется только добавление (409); iOS список не обрезает |
| 2.3 Живая карта всем | `TariffEntitlements.hasLiveMap` → true; новый `hasDrivingInsights` (trial/family/premium) для поездок: `DrivingReportsModal`, `WhereIsPhoneScreen` | ✅ iOS | поездки не открылись вместе с картой |
| 2.4 Тексты Free | RU/EN `.strings` §5.6; `10_TariffsScreen` `freeExcludedFeatures` [8, 10], строки таблицы | ✅ iOS | `plutil` OK |
| 2.5 Проверка на проде | тестовая семья на MAIN (устройство `ALADDIN-L360-ROSTER-SMOKE-*`) | ✅ | на проде: пробный — 6 мест, 7-й → 409; бесплатный 4 / 5-й → 409 — pytest |
| С.1 Сайт | `landing/cms/tariffs.json`, `landing/index.html`, `landing/i18n-strings.js`; бэкап `/var/www/backups/l360_site_20261118_175144` | ✅ деплой | снаружи: 4 / 4 / 6 / 15, «чел. в семье», кэш `?v=20261118l360` |
| 1.5 Отчёт активации | MAIN, только чтение — см. §12.1 | ✅ | — |
| 3 «Собери семью» | новый `Core/Family/FamilyGrowthNudgeScheduler.swift` (в target, A360E003/4) ← `SubscriptionManager.applyFamilyRosterQuotaFromFamilyStats`; ключи `family_growth_nudge_*` RU/EN; тест `FamilyGrowthNudgeSchedulerTests` | ✅ код (сборку делает владелец) | логика прогнана отдельным `swiftc`: 6/6 сценариев |
| 3 шаг в онбординге | — | ⏸ не делался | онбординг OB_* меняется только с синхронизацией Figma (правило `onboarding-figma-ios-sync-mandatory`); вместо шага — напоминания на 2-й и 3-й день и экран семьи |
| 3 экран тарифов в момент ценности | уже есть: 409 при полной семье и 429 лимита Антифейка ведут на тарифы | ✅ без новых правок | — |
| Этап 4 история мест | см. §12.3 | ✅ | — |
| Этап 4 напоминания об оплате сайта, этап 5 | — | ⏳ нужны решения владельца | см. §12.2 |

### 12.1 Отчёт активации (1.5), MAIN, 2026-11-18

Смоук-аккаунты и тестовые владельцы (больше 20 семей у одного владельца) исключены: из 7702 семей настоящих — 227, из 1628 пользователей — 322.

| Метрика | Значение |
|---|---|
| Настоящие пользователи: всего / новые за 30 дней / за 7 дней | 322 / 46 / 9 |
| Тариф пользователей (все, включая тестовых) | free 1595, trial 33, платных нет |
| Настоящие семьи: всего · с 2+ людьми · с 3+ людьми | 227 · 64 (28,2%) · 8 (3,5%) |
| Семьи за последние 30 дней: всего · 2+ · 3+ | 17 · 6 (35,3%) · 0 |
| События на сервере (`payments.db` → `subscription_event_ingest`, 30 дней) | `sync_completed` 2816, `sync_failed` 208, `trial_activated` 13, `feature_blocked` 7, `app_open_day` 1 |

Выводы:
- Канал событий 1.1 работает: первое `app_open_day` уже пришло со сборки с новым кодом. События хранятся в SQLite `payments.db` (асинхронная сессия этого роутера), не в Postgres.
- Базовая линия для §13: семьи 3+ — **3,5%** (за 30 дней — 0 из 17). Цель этапа 3 считаем от неё.
- Платных подписчиков в базе нет — поэтому лимит Личного и доступ участников семьи на проде проверены только тестами и тестовыми аккаунтами.

### 12.3 Этап 4 — история мест на сервере (GO владельца 2026-11-18)

Находка до начала работ: сервер **уже** хранил точки (`POST /api/parental-control/location/report` → `location_history`) **без срока** — 1983 точки с апреля, 21 человек; удаление аккаунта их не стирало; координаты писались в лог.

| Что | Где | Статус | Доказательство |
|---|---|---|---|
| Сроки 24 ч / 7 дней / 30 дней; срок = больший из своего тарифа и тарифа владельца семьи (Личный владельца не продлевает); потолок 30 дней | новый `app/services/family_location_history.py`; iOS-зеркало `TariffEntitlements.locationHistoryHours` | ✅ деплой MAIN | pytest `test_family_location_history.py` 10/10 |
| Удаление по сроку | после каждой точки — по человеку; раз в час — по всем | ✅ | на проде: удалено 730 (старше 30 дней) + 951 (по тарифу), осталось 302, старше 7 дней — 0 |
| Индекс `(user_id, timestamp)` | `ix_location_history_user_ts` | ✅ | `pg_indexes` |
| Координаты не пишутся в лог | `security/api/routers/parental_control_router.py` | ✅ | diff |
| Удаление аккаунта стирает историю и последнюю точку | `app/routers/user.py` (+ `family_where_phone_signal/point`) | ✅ | смоук: после удаления 0 точек |
| Чтение истории | `GET /api/family/location-history?member_id=` в `family.py`; ребёнок — себя и родителей, чужие — 404 | ✅ | смоук: своя 200 (168 ч, 2 точки), посторонний 404; семейный смоук PASS |
| iOS-экран | новый `Screens/FamilyLocationHistoryView.swift` (A360E005/6) ← «Где семья» → человек → «История мест»; `APIService.getFamilyLocationHistory`; `AppConfig.familyLocationHistory` | ✅ код (сборку делает владелец) | `swiftc -typecheck` iOS 15.2 с заглушками — без ошибок |
| Политика в приложении | `18_PrivacyPolicyScreen.swift` + `privacy_policy_section_family_location_content_6/7` RU/EN | ✅ только добавлено | `plutil` OK |
| Системный запрос геолокации | `Info.plist`, `{ru,en}.lproj/InfoPlist.strings` — дописана фраза про историю | ✅ только добавлено | `plutil` OK |
| Политика на сайте | `landing/privacy.html`, `legal/privacy.{ru,en}.html` (+ серверная копия `legal/privacy.html`): блок «Сколько храним историю мест» + строка в «11. Сроки хранения»; бэкап `/var/www/backups/l360_privacy_20261118_183534` | ✅ деплой | против живого сайта: удалено 0 строк, добавлено 10 в каждом файле |
| Ответ App Review + App Privacy | `docs/AppStore/REVIEW_NOTES_CURRENT.md` → «L360 — Notes» | ✅ текст готов | отправляет владелец |

Бэкап сервера: `/opt/aladdin-backend/backups/l360_stage4_20261118_183217`. `user.py` выкачен как серверная версия + 3 строки (чужие невыкаченные правки локального `user.py` на прод не попали).

### 12.2 Что ждёт решения владельца

- ~~**Этап 4, история перемещений на сервере.**~~ Сделано — §12.3.
- **Этап 4, напоминания об окончании оплаты на сайте.** Нужно выбрать канал: пуш в приложении, e-mail или бот.
- **Этап 5.** Коды операторов: сервер уже умеет (`POST /api/promo/admin/create`), нужны договорённости с операторами. Казахстан: цена в тенге и нужен ли казахский язык. Android: делать ли вообще.

Проверки (`l360-verify`):
- `verify_localization_manager_integrity.sh` → OK (21788 = HEAD; `LocalizationManager.swift` не тронут).
- `plutil -lint` RU/EN `.strings` и `project.pbxproj` → OK.
- pytest: `test_antifake_personal_quota.py` + `test_antifake_family_share.py` + `test_antifake_effective_trial_gate.py` + `test_family_roster_reconcile.py` → 31 passed. Весь `test_antifake*.py`: 254 passed, 10 failed — все 10 падали и до правок (golden URL `yandex.ru`, `ml_lazy`, `web_trial_abuse`; проверено на версии из HEAD).
- `py_compile` всех изменённых `.py` → OK.
- Бот / `.env` / VPN-handoff в изменениях этой задачи — нет.
- Уже существовавшие FAIL (не от этой задачи): `verify_antifake_bypass_off.py`, `verify_antifake_release_readiness.py` ищут `bypassPremiumGate: Bool = false`, а в коде вычисляемое `#if DEBUG`.

Инцидент при реализации: `antifake_family_share.py` по плану был «новым», но такой файл уже есть (поделиться вердиктом с семьёй). Он был перезаписан и **восстановлен из git**; новая логика — в `antifake_family_entitlement.py`.

## 13. Цифры успеха и правило решения

| Метрика | Откуда | Сейчас | Цель |
|---|---|---|---|
| Семьи с 3+ людьми за 7 дней после создания | `family_created` + `family_member_joined` | замерить 2 недели после выката 1.x | +30% к замеру |
| Конверсия экрана тарифов в покупку | `paywall_shown` → `upgrade_completed` | замер | +15% |
| Выручка на 1000 показов экрана тарифов | то же + цены | замер | вариант A/B с большей выручкой |
| Доля Личного среди покупок | `upgrade_completed.product_id` | замер | не растёт за счёт Семейного |
| Личный упирается в лимит | `antifake_quota_hit` / активные Личные | — | 5–20% (меньше — лимит не ограничивает, больше — злит) |
| Отток на 2-м месяце | App Store Connect | замер | не хуже замера |

Правило A/B (1Б.5): решаем не раньше **1000 показов экрана тарифов на вариант** или 6 недель. Победитель — по выручке на 1000 показов, если отток не хуже.

## 14. Действия владельца вне кода

- App Store Connect → подписки → локализации RU/EN: описания Личного/Семейного/Премиума привести к §5 (после деплоя 1Б.3).
- В заметке для App Review указать: Личный — проверки для себя; голос/видео — 30 в месяц.
- `retain_premium` / `retain_individual` в ASC; ротация секрета Platega; SberPay.

## 10. Журнал

| Дата | Что |
|---|---|
| 2026-11-18 | Анализ Life360 и рынков РФ/СНГ; аудит тарифов в коде (6 замков, 10 расхождений); решения D1–D10; создан этот файл и TODO `l360-*`. Код не менялся. |
| 2026-11-18 | Ревью плана: добавлены §11 (G1–G10), D11–D12, §13, §14. Реализованы этапы 0, 1, 1Б (iOS + сервер локально), сверка §12. Не сделано: деплой MAIN 1Б.3+1Б.6, этап 2, сайт, 1.5 — ждут GO. |
| 2026-11-18 | GO владельца. Деплой на 🇷🇺 MAIN — FirstVDS / Аладдин · запас · Россия (…180): 1Б.3 + 1Б.6, затем этап 2; семейный смоук PASS. Сайт выкачен. Отчёт активации §12.1. Этап 3: напоминания «пригласите близких» (iOS). Этапы 4–5 — ждут решений §12.2. |
| 2026-11-18 | Этап 4 (история мест): сроки по тарифу, удаление, чтение для семьи, iOS-экран, политика в приложении и на сайте (только дополнения), Notes для App Review — §12.3. Деплой MAIN + сайт. Остались: напоминания об оплате на сайте и этап 5 (§12.2). |
