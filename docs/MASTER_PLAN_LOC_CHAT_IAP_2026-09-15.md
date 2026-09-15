# Master plan + checklist — localization A/B/C/G/I · chat TF · IAP/ASC (2026-09-15)

**Режим:** план и трекинг. Код не правим, пока нет GO FIX.

---

## 0. Правила без дублей

1. **Один русский текст → один ключ → один пункт** (даже если 2+ call-site).
2. Зоны **не пересекаются по файлам**:
   - A = Companion consent / personality / memory (+ hero chip names)
   - B = ChildContent* only
   - C = Family / Member* / Rewards* / FamilyRegistration
   - G = SubscriptionModels / SubscriptionManager / PaymentQR / TariffCard
   - I = ALADDINWidgets only
3. Сначала **WIRE** (ключ уже есть), потом **NO_KEY**.
4. SSOT по фразам: `docs/LOCALIZATION_PRIORITY_DEDUPED_PLAN_ABC_GI_2026-09-15.md`

| Зона | Уникальных фраз | NO_KEY | WIRE | Файлы |
|------|----------------:|-------:|-----:|-------|
| A | 25 | 22 | 3 | Consent, Personality, Memory (+ 1 a11y wire) |
| B | 86 | 85 | 1 | ChildContentExperience, ChildContent |
| C | 78 | 57 | 21 | MemberSettings, Family, Rewards… |
| G | 26 | 25 | 1 | SubscriptionModels (+ alerts) |
| I | 12 | 8 | 4 | ALADDINWidgets |
| **Σ** | **227** | **197** | **30** | без наложений зон |

---

## 1. План локализации по зонам (порядок работ)

### Batch LOC-A (Мир героев) — 25 пунктов

**WIRE first (3):**
- [x] A-W1 «Единорог» → `companion_hero_unicorn` · Consent
- [x] A-W2 «Аладдин (13+)» → `companion_hero_aladdin`
- [x] A-W3 «Герой настороже» → `companion_a11y_hero_alert` (+ остальные a11y emotions)

**NO_KEY Consent / Personality / Memory:** ✅ wired 2026-09-15  
DoD A: English UI в companion settings — без RU-хардкода в Consent/Personality/Memory.

---

### Batch LOC-B (детский контент) — 86 уникальных

- [x] **Аудит A 2026-09-15:** все 86 пунктов — ключ RU+EN + call-site + 0 хардкода из списка B  
- [x] EN подправлены (детский тон)  
- ⚠️ Вне B: `page.narration` и куплеты karaoke ещё на RU — отдельный backlog  

**DoD B (кнопки/заголовки из чеклиста):** ✅ English UI без RU-хардкода по списку B-026…B-111.

---

### Batch LOC-C (семья / награды) — 78 уникальных

- [x] C-112…C-189 — пачки 1–5 (WIRE + NO_KEY) ✅ 2026-09-15
- Чеклист: `docs/LOCALIZATION_PRIORITY_DEDUPED_PLAN_ABC_GI_2026-09-15.md`

**DoD C:** MemberSettings section titles + Family roster/created + MemberStats section titles без RU-хардкода по чеклисту C. (StatCard labels внутри stats — вне C.)

---

### Batch LOC-G (тарифы) — 26 уникальных

- [x] G-190…G-215 ✅ 2026-09-15
- AppFeature checklist rows → `feature_*_name` / `feature_*_desc`; `displayName`/`fullDescription` → `localized`
- Auth errors → `subscription_auth_*`; Family title → `tariff_plan_family_title`
- WIRE: `tariff_devices_unlimited`

**DoD G:** чеклист G без RU-хардкода; остальные AppFeature вне списка — backlog.

---

### Batch LOC-I (виджеты) — 12 уникальных

- [x] I-216…I-227 ✅ 2026-09-15
- WIRE existing keys + `widget_label_*` NO_KEY
- Runtime: `ALADDINWidgets/WidgetL10n.swift` (appex; keys mirrored in LocalizationManager)

**DoD I:** чеклист I без RU-хардкода в entry views / display names.

---

## 2. Семейный чат: почему Simulator OK, TestFlight — ошибка

### Что за алерт (просто)

Приложение **шифрует** семейный чат (E2EE).  
Пока ключ на этом iPhone не готов — отправка блокируется сообщением «Secure chat is not set up…».

### Почему на симуляторе часто работает

В коде `FamilyE2EEManager.ensureLocalFamilyKey`:

- Если в семье **нет других устройств** с ключами → этот телефон **сам создаёт** семейный ключ → `isReady = true` → отправка OK.
- Симулятор часто = единственное «устройство» семьи / свежий familyId → ключ создаётся сразу.

### Почему на TestFlight часто ошибка

Если в семье на сервере **уже есть другое устройство** (старый iPhone, второй член, прошлое Install TestFlight с другим `deviceId`), а ключ ещё не пришёл на новый телефон:

→ код ждёт distribution с другого девайса  
→ иначе: *«open Family Chat on another family device first»*  
→ UI показывает локализованный `family_chat_e2ee_not_ready`.

Дополнительно на устройстве чаще:

- сбой `register` E2EE API (сеть, JWT, 500 → reset identity)
- Keychain после переустановки TF = новый deviceId, старый ключ на сервере «сирота»
- SSL pinning / prod API vs debug

**Это не баг перевода.** На English UI текст уже EN.

### План фикса чата (после GO FIX CHAT)

| ID | Задача | DoD |
|----|--------|-----|
| CHAT-1 | Логи bootstrap на TF: register / devices count / lastError | ✅ Console `🔐 FamilyE2EE.*` |
| CHAT-2 | UX: Send disabled пока `!isReady` + баннер setup | ✅ |
| CHAT-3 | Single-device create + orphan empty sender keys → create | ✅ |
| CHAT-4 | Кнопка «Пересоздать защиту чата» + force create | ✅ |
| CHAT-5 | QA матрица | ✅ doc `docs/FAMILY_CHAT_E2EE_QA_MATRIX_2026-09-15.md` (PASS на устройстве — владелец) |

---

## 3. IAP / тарифы + Report/Restrict (канон владельца 2026-09-15)

### Решение владельца (зафиксировано)

- На TestFlight **сейчас продукты StoreKit грузить не обязаны**.  
- Алерт «Products not loaded» на текущем TF **ожидаем**, пока 3 тарифа не загружены/не привязаны в ASC при отправке на Review.  
- Владелец **загрузит 3 тарифа при отправке** билда в App Store Connect.  
- В **Reply + Notes** явно пишем: IAP заработает после согласования/привязки продуктов к этой версии; до этого экран Тарифов показывает UI планов и временное состояние загрузки продуктов — это не баг приложения.

### Три Product ID (для письма и ASC)

| Тариф | Product ID |
|-------|------------|
| Individual / Personal | `ai.aladdin.subscription.individual.v2` |
| Family | `ai.aladdin.subscription.family` |
| Premium | `ai.aladdin.subscription.premium` |

Оплата только **Apple In-App Purchase (StoreKit 2)** + **Restore Purchases**.  
Цифровой контент не продаём в обход IAP.

### Что предложить сделать (рекомендация)

1. **В письме / Notes (обязательно)** — блок про подписки (черновик ниже).  
2. **При Submit** — создать/привязать 3 auto-renewable subscriptions к **этой** версии приложения (Guideline 3.1.1 «submitted alongside the app»).  
3. **Видео сейчас** — показать экран **Тарифы** (3 плана, trial/subscribe UI, Terms/Privacy, Restore если видно).  
   - **Не** требовать живой StoreKit sheet на текущем TF.  
   - В Notes: «IAP purchase sheet becomes available to reviewers after the three subscription products attached to this version are processed; Product IDs listed below.»  
4. **После привязки продуктов** (когда владелец загрузит тарифы) — опционально короткое доп. видео / уточнение в Reply, если Apple попросит увидеть sheet.  
5. **Не** чинить «Products not loaded» как баг приложения до загрузки тарифов в ASC.

### Черновик абзаца для Reply / Notes (EN)

```text
Monetization: SaaS subscription via Apple In-App Purchase (StoreKit 2) only,
with Restore Purchases.

Three auto-renewable subscription products (to be submitted / linked with this
app version in App Store Connect):

- ai.aladdin.subscription.individual.v2  (Individual / Personal)
- ai.aladdin.subscription.family         (Family)
- ai.aladdin.subscription.premium        (Premium)

Until these products are attached and available for this build, the Tariffs
screen may show a temporary “products loading / not loaded” state. This is
expected and not an application defect. After the products are approved for
the version under review, the system Apple purchase sheet works normally.

The screen recording shows the Tariffs UI and the intended purchase entry
points; the live StoreKit sheet is available once the three products above
are linked to this submission.
```

### Report + Restrict (без изменений по смыслу)

| Действие | Простыми словами | В коде? |
|----------|------------------|--------|
| **Report** | Пожаловаться на чужое сообщение | Да |
| **Restrict** | Родитель запрещает участнику писать | Да |
| Delete own | Удалить своё | Да |

Видео: показать Report + Restrict в семейном чате (нужен рабочий чат на TF → партия CHAT).

---

## 4. Чеклист трекинга (Cursor TODOs)

### Family chat TF
- [x] `chat-1` … `chat-4` (код)
- [x] `chat-5` (чеклист QA; PASS на TF — владелец)

### Localization
- [x] `loc-A` … `loc-I`
- [x] `loc-verify` — `python3 scripts/verify_loc_abcgi_user_visible.py` → PASS (0 user-visible RU hardcode in A/B/C/G/I)

### App Review / IAP (обновлено)

- [x] ~~iap-1 продукты обязаны грузиться на TF сейчас~~ — **снято** (канон владельца)
- [x] ~~iap-2 видео без Products not loaded~~ — **снято**
- [ ] `iap-3` Видео: Report + Restrict в семейном чате
- [ ] `iap-letter` Абзац IAP/3 Product ID в Reply + Notes (черновик §3)
- [ ] `iap-submit` При отправке: 3 тарифа созданы и **привязаны к этой версии** в ASC
- [ ] `asc-1` Reply + Notes пункты 1–6 готовы (включая IAP-абзац)

---

## 5. Порядок GO (обновлено)

1. **GO FIX CHAT** — чтобы на TF-видео работали сообщения + Report/Restrict  
2. **GO ASC REPLY TEXT** — письмо 1–6 + блок IAP «продукты с отправкой тарифов»  
3. При Submit — владелец загружает 3 тарифа (`iap-submit`)  
4. **GO FIX LOC-A** → C / G / I / B — отдельно от Review  

**Не** ставить GO «починить Products not loaded на TF» до загрузки тарифов в ASC.

