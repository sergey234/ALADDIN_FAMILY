# TF2 — Crash + EN loc + 19 screens (SSOT)

**Дата:** 2026-10-10  
**Канон:** merge-only TodoWrite ids `tf2-*`  
**Constraint:** iOS commits only on `master` · no push without GO · no `xcodebuild` without «GO на сборку»  
**Crash log:** `~/Downloads/ALADDIN-2026-10-10-145258.ips` (TF build **5**, `ai.aladdin`)

---

## ПЛАН–ФАКТ (сверка ×3 · 2026-10-10)

| # | План (что просили) | Факт (что в коде) | Было → Стало | Улучшение (предложение) |
|---|--------------------|-------------------|--------------|-------------------------|
| 1 | Найти краш рефки по `.ips`, план+чеклист | ✅ EXC_BAD_ACCESS: `String(format:)` + `−20%` | Share падал → `{CODE}` + safe replace | Unit-тест на шаблон с `%` |
| 2 | Все скрины / красные галочки / сырые ключи / ошибки | ✅ Registry + ключи EN/RU | Сырые ключи / RU на EN → human EN/RU | Новый TF после GO на сборку |
| 3 | EN layout: план локализации по каждому скрину | ✅ §3 таблицы + `.strings` | Key на экране → перевод | Аудит оставшихся ViewModels (Driving/Parental) |
| 4 | Auto Connect VPN: что/зачем + тогглы | ✅ Объяснено; sync Wi‑Fi/Mobile → сервер | Непонятный тогл → «Auto-connect VPN» | Карточка «When to connect» Wi‑Fi/Cellular |
| 5 | Toast «Компонент обновлён» по языку | ✅ `component_toast_*` | RU на EN → «Component updated» | — |
| 6 | Coverage: коды CYB/MOB, тапы, quick check | ✅ Без кодов; navigate по route | `CYB-07…` → «Fake apps» + короткий hint | CTA «Check now» + human error при fail |
| 7 IoT | Smart Home сырой ключ | ✅ `device_hub_iot_toggle_hint` | `iotThreats -> agent` → «Protect smart devices…» | — |
| 7b | Скрины 5–6 = как §6 + сервер | ✅ Те же coverage + routes | Коды / мёртвые тапы → human + route | Device QA навигации (GO) |
| 8 | HTTP 504 причина + RU на EN + везде | ✅ 504=timeout; `network_error_*` | «HTTP ошибка: 504» RU → «Server is busy» | Retry на баннере; без raw code юзеру |
| 9 | Last time 100% EN/RU | ✅ prefix + locale guard + draft scrub | RU body на EN → default EN | API Accept-Language для recap |
| 9b | Unicorn полный PNG | ✅ `unicorn_master.png` в пикере | Обрезанный 🦄 → PNG circle | Production `.riv` без fake face |
| 10/15 | Profile keys 100% | ✅ LM + strings + envObject | `profile_edit_*` → Cancel/Save/… | Device QA switch EN↔RU |
| 11/14 | AI без tech + 3 варианта клавиатуры | ✅ KB human + sanitizer; 3 варианта в registry | `### family_chat_e2ee_*` → простой текст | **Hybrid keyboard** допилить на device |
| 13 | Roadside key | ✅ Call for help / Вызвать помощь | raw key → перевод | — |
| 16 | Invite crash + красная ошибка | ✅ crash fixed; banner = server gate | Crash → stable share | Smoke invite API (ops GO) |
| 17 | device_detail raw + ISO | ✅ empty key + `formattedLastActive` | key + `2026-…Z` → «No threats» + local time | — |
| 18/19 | privacy_error_* | ✅ load_failed + auth_required | raw key / RU auth → EN/RU | Корневая причина load fail на сервере |
| — | ×3 проверка | ✅ grep hot-path clean | — | GO сборка → визуальный QA |

**Не закрыто без владельца:** Device/Simulator QA · commit · push · hybrid keyboard polish на железе.

---

## GATES (до «готово»)

| # | Gate | Evidence |
|---|------|----------|
| G1 | Invite / Share referral **не крашит** | `.ips` EXC_BAD_ACCESS → `String(format:)` + `−20%`; fix `{CODE}` + safe replace |
| G2 | EN layout → **0** сырых ключей на отмеченных экранах | keys в `LocalizationManager` **и** `en.lproj/Localizable.strings` |
| G3 | EN layout → **0** утечек RU в тостах/ошибках сети | `NetworkError` + component toasts → `L.localized` |
| G4 | Coverage UI без CYB/MOB/IOT/FRD кодов | `DeviceHubThreatCoverageView` + `IdentityHubThreatCoverageView` |
| G5 | AI Assistant без `### key` в пузыре | KB JSON human + `AIAssistantResponseSanitizer` |
| G6 | Triple-pass grep clean | см. § Triple-pass ниже |

---

## 1 · Crash referral (Invite a family)

| | |
|--|--|
| **Анализ** | `.ips` 14:52:56 · EXC_BAD_ACCESS в Share sheet. `referral_text_template` содержит `−20%`. `String(format:)` трактует `%` как спецификатор → crash. |
| **План** | 1) Template с `{CODE}` 2) `referralText` без `String(format:)` 3) sequential replace для legacy `%@` 4) history formatters не передают Int в `%@` |
| **Чеклист** | [x] Root cause из `.ips` [x] `{CODE}` в RU/EN template [x] `21_ReferralScreen.referralText` safe [x] Invite share path uses safe text [ ] Device QA после GO на сборку |
| **Улучшение** | Любой user-facing `%` в шаблонах → `%%` или `{TOKEN}`; unit-тест на `−20%` + share. |

---

## 2 · Все скрины (красные галочки) — сводка

| # | Скрин | Проблема | Статус кода |
|---|-------|----------|-------------|
| 1 | Network / VPN toggles | Auto Connect VPN смысл + toggles | ✅ см. §4 |
| 2 | Component toast RU on EN | «Компонент обновлен» | ✅ localized toasts |
| 3/5/6 | Threats coverage | CYB/MOB codes, taps, quick check | ✅ human titles; Identity FRD codes removed |
| 4 | IoT Smart Home | `iotThreats -> iot_security_agent` | ✅ `device_hub_iot_toggle_hint` |
| 7 | HTTP 504 RU on EN | «Ошибка: HTTP ошибка: 504» | ✅ `network_error_http_504` EN |
| 8/9 | Companion | Last time RU + unicorn clip | ✅ locale guard + PNG thumb |
| 10/15 | Profile edit | raw `profile_edit_*` | ✅ EN/RU dict + `.strings` + sheet env |
| 11/14 | AI Assistant | `### family_chat_e2ee_*` + keyboard | ✅ KB + sanitizer; keyboard hybrid §11 |
| 13 | Roadside | `roadside_assistance_call` | ✅ EN/RU |
| 16 | Invite crash + red banner | crash + server error | ✅ crash; banner already EN copy |
| 17 | Device detail | `device_detail_threats_empty` + ISO time | ✅ keys + `formattedLastActive` |
| 18/19 | Privacy | `privacy_error_load_failed` | ✅ keys + auth localized |

---

## 3 · EN layout — план локализации по экрану

| Экран | Ключи | EN | RU | Чеклист |
|-------|-------|----|----|---------|
| Profile edit | `profile_edit_*` | Cancel/Save/… | Отмена/Сохранить/… | [x] LM [x] strings [x] sheet `.environmentObject` |
| Privacy | `privacy_error_load_failed`, `privacy_error_auth_required` | Couldn’t load… / Sign in… | Не удалось… / Нужен вход… | [x] |
| Roadside | `roadside_assistance_call` | Call for help | Вызвать помощь | [x] |
| Device detail | `device_detail_threats_empty`, `device_detail_last_activity`, `device_detail_status_pending` | No threats… / Last activity… | Нет угроз… | [x] |
| Network errors | `network_error_*` | Server is busy… | Сервер занят… | [x] |
| Component toast | `component_toast_*` | Component updated | Компонент обновлён | [x] |
| IoT hint | `device_hub_iot_toggle_hint` | Protect smart devices… | Защита умных… | [x] |
| Companion recap | `wellness_recap_prefix`, `wellness_recap_default` | Last time: … | В прошлый раз: … | [x] locale mismatch guard |

**Правило SSOT:** EN missing → raw key (видно в DEBUG), **никогда** silent RU fallback.

---

## 4 · Auto Connect VPN (скрин 1)

| | |
|--|--|
| **Что это** | `network_security.auto_connect_vpn` / Wi‑Fi & Mobile toggles в Network Protection settings: автоматически поднимать VPN при появлении сети. |
| **Зачем** | Wi‑Fi часто публичный → auto ON по умолчанию; Mobile — опционально (батарея/трафик). |
| **Код** | `NetworkSecuritySettingsScreen` → `autoConnectVPN`; `03_NetworkProtectionScreen` → `autoConnectWiFi` / `autoConnectMobile` → sync на сервер. |
| **Чеклист** | [x] Labels localized EN/RU [x] onChange sync server [ ] Device: toggle persists after reopen (GO QA) |
| **Улучшение** | Одна карточка «When to connect» с 2 понятными строками (Wi‑Fi / Cellular), без слова «agent». |

---

## 5 · Toast «Компонент обновлен» на EN

| | |
|--|--|
| **Анализ** | Hardcoded RU в `NetworkProtectionViewModel` toast. |
| **План** | `component_toast_updated` / `_local` / `component_toast_error_format` |
| **Чеклист** | [x] Replace hardcodes [x] EN/RU keys [ ] Grep clean after rebuild |

---

## 6 · Coverage cards (скрин 3 / 5 / 6)

| | |
|--|--|
| **Анализ** | Старый TF показывал `CYB-07 Fake applications` + tech pipelines. Коды — внутренний каталог (`cyb-07`…), не для UI. |
| **Что делают карточки** | Tap → `DeviceThreatRoute` (Device Hub tab / Antifake). Не «скан сами по себе»; ведут в нужную проверку. |
| **Quick check fail** | Часто 504 / timeout / empty agent → «Не удалось выполнить проверку» — нужно human EN + retry. |
| **План** | Human title (`tariffs_threat_*`) + short pipeline (`device_hub_*_pipeline`); section headers «Cyber / Mobile / Smart home»; Identity без FRD codes. |
| **Чеклист** | [x] DeviceHub: no `id.uppercased()` [x] IdentityHub: no FRD badge [x] Pipelines human EN/RU [ ] Device: each card navigates (GO) |
| **Лучшее UX** | Список «Что проверить» → 1 тап → экран проверки с кнопкой «Проверить сейчас» и понятной ошибкой («Сервер занят» / «Нет сети»), без кодов. |

---

## 7 · IoT Smart Home raw key

| | |
|--|--|
| **Было** | `iotThreats -> iot_security_agent` |
| **Стало** | Title: Smart home / Умный дом · Hint: `device_hub_iot_toggle_hint` |
| **Чеклист** | [x] Hint keys [x] Scan button localized [ ] Server scan returns human errors |

---

## 8 · HTTP 504 + RU on EN (скрин 7)

| | |
|--|--|
| **Причина 504** | Gateway timeout: app → API `:8002` / edge не ответил вовремя (нагрузка, VPN path, cold worker). |
| **RU leak** | `NetworkError.localizedDescription` был hardcoded RU / «Ошибка: …». |
| **План** | `network_error_http_504` EN/RU; banner uses `NetworkError` only; no hardcoded «Ошибка:». |
| **Чеклист** | [x] NetworkError localized [x] encoding/filesystem/unknown localized [ ] Server SLO / timeout tuning (ops, отдельный GO) |
| **Улучшение** | Retry с backoff + «Try again» на баннере; не показывать raw HTTP code пользователю (только support log). |

---

## 9 · Companion Last time + unicorn (8/9)

| | |
|--|--|
| **Last time** | Prefix localized; body с сервера мог быть RU → guard + `wellness_recap_default`. Draft RU scrub на EN. |
| **Unicorn** | Emoji 🦄 обрезался в Capsule → PNG `unicorn_master` 22pt circle. Full asset: `Resources/Companion/unicorn_master.png`. |
| **Чеклист** | [x] Recap locale guard [x] Draft locale scrub [x] Picker PNG [ ] Visual QA App Review (GO) |
| **Улучшение** | Позже: production `.riv` unicorn без placeholder face overlay. |

---

## 10 / 15 · Profile edit keys

| | |
|--|--|
| **Анализ** | TF build без EN keys / sheet без env → raw keys. |
| **План** | Полный набор `profile_edit_*` EN+RU в LM + Localizable.strings; `.environmentObject(localizationManager)`. |
| **Чеклист** | [x] Keys [x] strings [x] sheet env [ ] Device EN/RU switch |

---

## 11 / 14 · AI Assistant tech + keyboard

| | |
|--|--|
| **Tech text** | KB doc клал `### family_chat_e2ee_*` как заголовки. |
| **Fix** | Human KB JSON + sanitizer resolves/strips key headings. |
| **Клавиатура — 3 варианта** | **A)** Composer в `safeAreaInset` + scroll-on-focus (уже) **B)** `scrollDismissesKeyboard` + toolbar Done **C) Hybrid (рекомендуем):** A + dismiss on drag + при focus прятать QuickActions + scroll to last bubble; при «пустом» экране — `resignFirstResponder` watchdog 0.3s если keyboard frame >0 но composer offscreen. |
| **Чеклист** | [x] KB EN/RU human [x] Sanitizer [x] safeAreaInset composer [ ] Hybrid keyboard polish (optional) Device QA |

---

## 13 · Roadside assistance key

| | |
|--|--|
| **Чеклист** | [x] `roadside_assistance_call` EN/RU [x] title/subtitle already localized |

---

## 16 · Invite family crash + red error

| | |
|--|--|
| **Crash** | §1 fixed. |
| **Red banner** | «This action isn't available on the server…» — сервер/feature gate; не crash. |
| **Чеклист** | [x] Share text safe [ ] API invite endpoint smoke (GO / ops) |

---

## 17 · Device detail

| | |
|--|--|
| **Чеклист** | [x] `device_detail_threats_empty` [x] `formattedLastActive` ISO→local [x] pending status localized |

---

## 18 / 19 · Privacy errors

| | |
|--|--|
| **Чеклист** | [x] `privacy_error_load_failed` format [x] auth → `privacy_error_auth_required` (no hardcoded RU) |

---

## Triple-pass verify (×3)

### Pass 1 — crash / share
```bash
grep -n 'referralText\|{CODE}\|String(format:.*referral' Screens/21_ReferralScreen.swift
grep -n 'referral_text_template' Core/Localization/LocalizationManager.swift
```

### Pass 2 — raw keys / RU hardcodes
```bash
grep -n 'Требуется авторизация\|Компонент обновл\|Ошибка: HTTP\|Ошибка подготовки' ViewModels Core --include='*.swift'
grep -n 'profile_edit_cancel\|privacy_error_load_failed\|roadside_assistance_call\|device_detail_threats_empty' Resources/Localization/en.lproj/Localizable.strings
grep -n 'uppercased()' Shared/Components/*ThreatCoverage*.swift
```

### Pass 3 — AI / companion / network
```bash
grep -n 'family_chat_e2ee_decrypt_failed' docs/kb/kb_v1/documents/family_chat_e2ee*.json
grep -n 'markdownKeyHeading\|companionRecapBodyMatchingLocale\|formattedLastActive' Core/AI Screens --include='*.swift'
grep -n 'network_error_http_504\|component_toast_updated' Core/Localization/LocalizationManager.swift | head
```

---

## Рекомендуемый порядок ship

1. Static greps (triple-pass) ✅ в этой сессии  
2. Commit TF2 iOS-only на `master` — **по запросу владельца**  
3. «GO на сборку» → Simulator/Device QA по чеклистам  
4. «GO на push» → origin master  

**Не делать без GO:** MDM wipe, APNs remote lock, bot в iOS commit, VPN secrets push.
