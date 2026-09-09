# ALADDIN X AI — handoff для следующей ML-системы по App Review Guideline 2.1

**Дата среза:** 9 сентября 2026, после privacy/Family Controls hardening
**Репозиторий:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`
**Ветка:** `master`
**Статус:** локальная реализация в работе; изменения не закоммичены целевым App Review-коммитом и не развёрнуты на production
**Главный принцип:** нельзя писать Apple «готово», пока проверяемая функция не находится в том же Archive/TestFlight build, который отправляется на review

## 1. Цель работы

Apple запросила дополнительную информацию по **Guideline 2.1 — Information Needed / New App Submission**. Задача состоит не только в подготовке письма, а в приведении фактической App Store-сборки, App Privacy, Review Notes и демонстрационного видео к одному непротиворечивому состоянию.

Финальный результат должен включать:

1. App Store Release-бинарник без внешней оплаты, VPN/Smart DNS и неподтверждённых системных Family Controls.
2. Рабочую UGC-модерацию семейного чата: report, restrict и удаление собственного сообщения.
3. Privacy Manifest и App Store Connect App Privacy, совпадающие с фактической обработкой данных.
4. Подтверждённый список реально активных production AI/STT/TTS-провайдеров.
5. Подписанный Archive с проверенными entitlements.
6. TestFlight-проверку на физическом iPhone.
7. Непрерывную запись экрана для Apple.
8. Финальное письмо без условных формулировок и полей `[ЗАПОЛНИТЬ]`.

## 2. Обязательные ограничения для следующей ML-системы

### 2.1. Рабочий корень

Перед любыми правками выполнить:

```bash
git rev-parse --show-toplevel
git branch --show-current
git status --short
```

Корень обязан совпадать с путём из шапки. Сейчас рабочее дерево очень грязное: `git status` выводит более двух тысяч строк, включая несвязанные изменения. Нельзя делать `git add .`, массовый commit или механический rollback.

### 2.2. Безопасность и staging

- Не читать, не печатать и не коммитить значения `.env`, токены, ключи, пароли и provisioning secrets.
- Никогда не добавлять в commit файл `aladdin_shop_vpn_api/deploy/VPN_SPEED_DEGRADATION_HANDOFF_RU.md`.
- Не включать `telegram_stars_shop_bot/**` в iOS App Review-коммит.
- Не использовать `git reset --hard`, `git checkout --` или иные разрушительные команды.
- Перед commit проверить staged paths и секреты; staging делать только явным allowlist файлов.

### 2.3. Production и внешние действия

Без отдельного явного **GO владельца** запрещены:

- SSH и deploy на **MAIN — Аладдин (…180), iOS API :8002**;
- production migration;
- restart backend/gunicorn/systemd;
- изменение production `.env`;
- загрузка TestFlight;
- отправка App Review;
- создание финального Archive, если владелец ещё не дал GO на релизную фазу.

Read-only health check разрешён правилами репозитория, но он не заменяет deploy/smoke.

## 3. Зафиксированные продуктовые решения

### 3.1. App Store payment policy

Для App Store используется compile-time флаг `APP_STORE_BUILD`.

В этой сборке:

- цифровые подписки покупаются только через Apple StoreKit 2;
- внешняя QR/СБП/SberPay/сайтовая оплата недоступна;
- `PaymentQRScreen` и activation-code flow исключены из App Store-навигации;
- deep links дополнительно отклоняются;
- присутствует Restore Purchases;
- российский альтернативный платёжный код может оставаться в репозитории, но не должен быть достижим или скомпилирован в пользовательский App Store-поток.

IAP:

- `ai.aladdin.subscription.individual.v2`;
- `ai.aladdin.subscription.family`;
- `ai.aladdin.subscription.premium`.

### 3.2. Network protection policy

В первой повторной App Store-отправке:

- полноценного VPN нет;
- Packet Tunnel target отсутствует;
- Smart DNS и `NEDNSSettingsManager` выключены для `APP_STORE_BUILD`;
- VPN-подобные серверы, connect button, uptime, трафик, Kill Switch и обещания скрытия IP исключены;
- остаются реальные функции: Safari Content Blocker, Antifake, Call Directory и локальные security tools.

### 3.3. Family Controls policy

До получения Apple Family Controls Distribution entitlement:

- `AppStoreBuildPolicy.allowsSystemFamilyControls = false`;
- системные Screen Time/Managed Settings вызовы fail closed;
- тарифы не должны продавать недоступные Family Controls;
- time control, monitoring и bypass protection UI не должны быть достижимы в App Store build;
- нельзя обещать блокировку сторонних приложений, просмотр их истории, сообщений, контактов, скриншотов, incognito/Tor/proxy detection.

Полноценный Family Controls rollout — отдельная будущая фаза после одобрения Apple и отдельного GO.

### 3.4. HealthKit policy

В первой App Store-сборке HealthKit отключён:

- `AppStoreBuildPolicy.allowsHealthKitIntegration = false`;
- импорты и вызовы в `WellnessHealthSleepReader.swift` и `ElderlyFallDetectionService.swift` compile-gated через `!APP_STORE_BUILD`;
- HealthKit entitlement в текущем App Store target не заявляется;
- вручную введённые wellness/mood/sleep/medication данные всё равно раскрываются в App Privacy как Health data.

## 4. Что уже реализовано

### 4.1. Единый policy App Store build

Основные файлы:

- `Core/Config/AppConfig.swift`
- `ALADDIN.xcodeproj/project.pbxproj`
- `ALADDIN.xcodeproj/xcshareddata/xcschemes/ALADDIN.xcscheme`
- `ALADDIN.entitlements`
- `Info.plist`

Реализовано:

- Release получает `APP_STORE_BUILD`;
- централизованные флаги запрещают alternative payments, Smart DNS, неподтверждённые Family Controls и HealthKit;
- Release APNs environment на уровне проекта настроен как production intent;
- signed Archive entitlements ещё не проверялись.

### 4.2. Оплата только через StoreKit

Затронуты:

- `Screens/10_TariffsScreen.swift`
- `ALADDINApp.swift`
- `Core/Navigation/NavigationManager.swift`
- `Screens/19_TermsOfServiceScreen.swift`
- `Screens/13_SupportScreen.swift`
- `Core/Localization/LocalizationManager.swift`

Реализовано:

- внешние payment destinations compile-gated;
- навигация fail closed;
- StoreKit path остаётся;
- добавлена доступная кнопка Restore Purchases;
- Terms/FAQ и активный App Store UI очищены от предложения внешней оплаты.

### 4.3. Удаление VPN/Smart DNS claims

Затронуты:

- `Core/Managers/DNSProtectionManager.swift`
- `Screens/02_FamilyScreen.swift`
- `Screens/03_NetworkProtectionScreen.swift`
- `Screens/05_SettingsScreen.swift`
- `Screens/SimpleHomeScreen.swift`
- `Shared/Models/AdditionalFeature.swift`
- privacy/terms/support localization.

Реализовано:

- `NetworkExtension` не импортируется в `APP_STORE_BUILD`;
- App Store DNS manager — безопасная no-op/fail-closed реализация;
- Smart DNS скрыт;
- Protection Center показывает реальные capabilities;
- legacy network privacy/terms tabs скрыты;
- tariff network/anonymity claims фильтруются.

### 4.4. UGC moderation backend

Основные файлы:

- `app/routers/family.py`
- `app/routers/family_chat_moderation.py`
- `app/database/migrations/create_family_chat_moderation.sql`
- `main.py`
- `backend_tests/test_family_chat_moderation.py`
- `backend_tests/test_family_chat_moderation_endpoints.py`
- `backend_tests/test_family_chat_moderation_admin.py`

Endpoint-контракт:

- `POST /chat/moderation/report`
- `POST /chat/moderation/restrict`
- существующий `DELETE /chat/send/{message_id}` для удаления собственного сообщения

Реализовано:

- JWT authentication;
- family membership и IDOR checks;
- report только на чужое сообщение;
- категории `spam`, `harassment`, `inappropriate`, `threat`, `other`;
- metadata-only очередь жалоб;
- plaintext сообщения, ciphertext и свободный текст note/reason не копируются в moderation storage;
- родитель/владелец может restrict активного участника;
- нельзя ограничить себя, владельца/родителя или уже покинувшего семью;
- rate limit на report/restrict;
- audit journal;
- report status constraint: `pending`, `reviewed`, `actioned`, `dismissed`;
- WebSocket периодически обновляет restriction state, чтобы уже открытое соединение перестало отправлять сообщения после restriction;
- bounded ciphertext upload и проверки доступа к media были усилены в той же серии изменений.

Важно: request models всё ещё принимают `note`/`reason` для валидации UX-контракта, но эти строки не сохраняются.

### 4.5. Операторская обработка жалоб

Файлы:

- `scripts/family_chat_moderation_admin.py`
- `backend_tests/test_family_chat_moderation_admin.py`

CLI умеет:

- вывести metadata-only reports по статусу;
- перевести жалобу в `reviewed`, `actioned` или `dismissed`;
- при `actioned` применить `restrict_member` или `remove_message`;
- записать audit event;
- не печатать plaintext/ciphertext, free-form note, токены и credentials.

CLI не является production deploy. Перед использованием на production нужен отдельный GO, правильный `DATABASE_URL` из secret manager/environment и runbook.

### 4.6. UGC moderation iOS

Основные файлы:

- `Core/Network/APIModels.swift`
- `Core/Network/APIClient.swift`
- `Screens/23_FamilyChatScreen.swift`
- `Shared/Components/Chat/MessageActionsMenu.swift`
- `Core/Localization/LocalizationManager.swift`
- `ALADDINApp.swift`
- `Tests/UnitTests/AppConfigTests.swift`
- `Tests/UITests/ALADDINUITests.swift`

Реализовано:

- «Пожаловаться» на чужое сообщение;
- выбор причины жалобы;
- privacy note, что plaintext E2EE сообщения не раскрывается;
- «Ограничить участника» только для parent/owner;
- delete для собственного сообщения;
- explicit `CodingKeys` у wire models;
- `current_user_role` вынесен в `AppConfig.UserDefaultsKeys`;
- role checks используют точные значения, не substring;
- устранена двойная презентация context menu/action sheet;
- добавлены accessibility identifiers;
- добавлен DEBUG fixture `-UITestFamilyChatModeration`;
- добавлены unit contract tests и два UI-сценария.

### 4.7. Privacy Manifest и App Privacy

Основные файлы:

- `PrivacyInfo.xcprivacy`
- `ALADDINCallDirectory/PrivacyInfo.xcprivacy`
- `ALADDINAntifakeShare/PrivacyInfo.xcprivacy`
- `ALADDINContentBlocker/PrivacyInfo.xcprivacy`
- `ALADDIN.xcodeproj/project.pbxproj`
- `docs/AppStore/APP_PRIVACY_ANSWERS_2026-09-09_RU.md`
- `docs/APP_PRIVACY_DATA.md`
- `docs/release/ANTIFAKE_APP_STORE_PRIVACY_LABELS.md`
- `scripts/verify_app_privacy.py`

Текущая консервативная декларация:

- Data Collection: Yes;
- Tracking: No;
- все server-linked категории — Linked: Yes;
- App Functionality для всех;
- Analytics только там, где это фактически уместно.

В main manifest включены:

- Name, Email Address, Phone Number, Physical Address, Contacts;
- Precise Location;
- Purchase History;
- Other User Content, Photos or Videos, Audio Data, Emails or Text Messages;
- User ID, Device ID;
- Product Interaction, Other Usage Data;
- Sensitive Info, Health, Fitness, Customer Support, Other Data Types;
- Crash Data, Performance Data, Other Diagnostic Data.

Required Reason APIs:

- UserDefaults `CA92.1`;
- App Group UserDefaults `1C8F.1`;
- File Timestamp `C617.1`;
- System Boot Time `35F9.1`.

Добавлен отдельный manifest для Safari Content Blocker и он включён в resources target. Extension manifests используют App Group reason `1C8F.1`.

### 4.8. Privacy Policy внутри приложения

Затронуты:

- `Screens/18_PrivacyPolicyScreen.swift`
- `Core/Localization/LocalizationManager.swift`

Исправлено:

- в `APP_STORE_BUILD` показывается короткая фактическая RU/EN политика;
- удалено активное ложное обещание «не собираем персональные данные»;
- описаны server processing, E2EE scope, StoreKit, Antifake, location, AI/STT/TTS и support recipients;
- версия обновлена до 2.2 от 9 сентября 2026;
- legacy подробные секции остаются только вне App Store branch и требуют отдельной будущей очистки, если этот канал будет публиковаться.

### 4.9. Family Controls и fake-statistics hardening

Затронуты:

- `Components/TariffCardView.swift`
- `Shared/Models/TariffCard.swift`
- `Screens/07_ParentalControlScreen.swift`
- `Screens/FamilyModals.swift`
- `Core/Managers/ParentalControlManager.swift`

Исправлено:

- parental feature counter и parental tariff section скрыты для App Store build;
- parental features возвращают пустой список в App Store build;
- monitoring/time/bypass cards gated;
- bypass modal больше не стартует с выдуманных значений `47`, `15`, `8`, `6`;
- при backend failure статистика обнуляется;
- unsupported toggles по умолчанию выключены.

### 4.10. AI/STT/TTS mapping

Файл:

- `scripts/check_ai_provider_flags.py`

По коду выявлена ожидаемая цепочка:

- AI backend: SFM/Hermes/OpenRouter;
- default direct model: DeepSeek V4 Flash;
- Gemini — optional fallback, default off;
- client/system STT: Apple Speech Recognition;
- server STT fallback: Yandex SpeechKit, затем OpenAI Whisper;
- local TTS: Apple AVSpeechSynthesizer;
- premium server TTS: ElevenLabs Flash.

Это ещё не доказательство production-активности. Наличие credentials и effective flags на production не проверено после этих изменений.

## 5. Уже выполненные проверки

Последний локально подтверждённый результат:

```text
PASS: App Privacy manifest and App Store Connect answers are consistent
APP_STORE_BUILD POLICY: PASS
UGC MODERATION: PASS
```

Команды:

```bash
python3 scripts/verify_app_privacy.py
python3 scripts/verify_app_store_build_policy.py
python3 scripts/verify_ugc_moderation.py
```

Plist/project validation:

```text
PrivacyInfo.xcprivacy: OK
ALADDINCallDirectory/PrivacyInfo.xcprivacy: OK
ALADDINAntifakeShare/PrivacyInfo.xcprivacy: OK
ALADDINContentBlocker/PrivacyInfo.xcprivacy: OK
ALADDIN.xcodeproj/project.pbxproj: OK
```

Команда:

```bash
plutil -lint \
  PrivacyInfo.xcprivacy \
  ALADDINCallDirectory/PrivacyInfo.xcprivacy \
  ALADDINAntifakeShare/PrivacyInfo.xcprivacy \
  ALADDINContentBlocker/PrivacyInfo.xcprivacy \
  ALADDIN.xcodeproj/project.pbxproj
```

`xcodebuild -project ALADDIN.xcodeproj -list` успешно увидел targets:

- ALADDIN;
- ALADDINUnitTests;
- ALADDINUITests;
- ALADDINContentBlocker;
- ALADDINAntifakeShare;
- ALADDINCallDirectory.

Пользователь отдельно подтвердил, что Xcode-проект собирался и Simulator iPhone 13 Pro Max / iOS 15.2 запускался до последнего privacy hardening.

Backend moderation tests ранее проходили локально в `.venv-appreview39` на совместимой версии Python.

## 6. Незавершённая проверка UI tests

Последняя команда:

```bash
xcodebuild test-without-building \
  -project ALADDIN.xcodeproj \
  -scheme ALADDIN \
  -configuration Debug \
  -destination 'platform=iOS Simulator,id=A900C6B0-6E81-4779-9305-E32CAA039BF6' \
  -only-testing:ALADDINUITests/ALADDINUITests/testFamilyChatModerationActionsForForeignMessage \
  -only-testing:ALADDINUITests/ALADDINUITests/testFamilyChatOwnMessageOffersDeleteButNotReport \
  -resultBundlePath /tmp/ALADDIN-AppReviewUITests-iOS15-2-r4.xcresult
```

Результат:

```text
Resolve Package Graph
Resolved RiveRuntime 6.20.5
BUILD INTERRUPTED
```

Это не assertion failure и не PASS. Процесс был внешне прерван. Результат не засчитывать.

После предыдущих UI-test ошибок уже были сделаны два исправления:

1. `app.otherElements` заменены на `app.staticTexts(...).firstMatch`.
2. Удалён дублирующий `.contextMenu`, оставлен единый action sheet.

Нужно заново собрать test products после последних Swift/privacy изменений и повторить targeted tests.

## 7. Что осталось сделать — строгий порядок

### P0-A. Завершить локальный Swift review

Предыдущий запуск обязательного `swift-reviewer` был прерван. Следующая ML-система должна:

1. Просмотреть uncommitted Swift diff только по App Review-файлам.
2. Проверить:
   - корректность `#if APP_STORE_BUILD`;
   - SwiftUI result-builder после добавления privacy sections;
   - отсутствие достижимого monitoring/bypass UI;
   - layout и accessibility;
   - отсутствие fake success/fake stats;
   - RU/EN локализацию.
3. Исправить только конкретные findings минимальным diff.
4. Повторить static gates.

### P0-B. Выполнить локальную сборку после последних изменений

Сборка, подтверждённая владельцем ранее, была до последних privacy/HealthKit/tariff правок. Поэтому требуется новая.

Рекомендуемый порядок:

1. Проверить booted simulator через `xcrun simctl list devices`.
2. Собрать Debug для выбранного simulator.
3. Собрать test products.
4. Запустить targeted unit tests:
   - `AppConfigTests`;
   - API moderation wire-contract tests.
5. Запустить два targeted UI tests из раздела 6.
6. Только после них запускать более широкий Unit/UI suite.

Не запускать несколько конкурирующих `xcodebuild` на одном simulator. Если CoreSimulatorService завис, сначала собрать evidence, затем выполнить один контролируемый restart simulator service.

### P0-C. Закрыть iOS moderation tests

Definition of Done:

- чужое сообщение найдено по accessibility identifier;
- action sheet содержит Report;
- parent/owner видит Restrict;
- причина report выбирается;
- success/error state проверяется без production network;
- собственное сообщение предлагает Delete;
- собственное сообщение не предлагает Report;
- нет duplicate matching UI elements;
- `.xcresult` сохранён и содержит PASS.

### P0-D. Повторить backend tests

Использовать `.venv-appreview39`, а не несовместимый system Python 3.12.

Запустить минимум:

```bash
.venv-appreview39/bin/python -m pytest \
  backend_tests/test_family_chat_moderation.py \
  backend_tests/test_family_chat_moderation_endpoints.py \
  backend_tests/test_family_chat_moderation_admin.py
```

Проверить отдельно:

- auth 401/403;
- cross-family IDOR;
- own-message report reject;
- non-manager restrict reject;
- departed-member reject;
- status transition;
- no note/reason persistence;
- rate-limit registration/behavior.

Если rate limit сейчас покрыт только статически, добавить отдельный интеграционный тест фактического `429`.

### P0-E. Финальный локальный compliance/security gate

Запустить:

```bash
python3 scripts/verify_app_store_build_policy.py
python3 scripts/verify_app_privacy.py
python3 scripts/verify_ugc_moderation.py
git diff --check
```

Дополнительно:

- проверить, что нет hardcoded secrets;
- проверить staged files allowlist;
- не включать Telegram bot;
- не включать `.env`;
- не включать VPN secrets handoff;
- выполнить Swift review;
- выполнить security review UGC/backend diff, если после предыдущего review изменялась auth/authorization/storage логика.

### P0-F. Тематический commit

Commit допустим только после зелёных P0-A…P0-E и в соответствии с текущим указанием владельца.

Из-за огромного грязного дерева:

- staging только по явному списку App Review-файлов;
- перед commit вывести `git diff --cached --name-only`;
- убрать любые случайные user/IDE/backup/bot файлы;
- не делать push без отдельного запроса.

Рекомендуется разделить минимум на два атомарных commit, если владелец согласует:

1. `feat(app-review): add family chat moderation`
2. `fix(app-review): align privacy and restricted capabilities`

Не переписывать историю и не смешивать unrelated work.

### P0-G. Production AI/STT/TTS truth check — только после GO

На **MAIN — Аладдин (…180), iOS API :8002**:

1. Сначала прочитать `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`.
2. Выполнить внешний health check по runbook.
3. После явного GO подключиться по approved SSH key.
4. Запустить `scripts/check_ai_provider_flags.py` в окружении backend так, чтобы выводились только boolean presence/effective names.
5. Не печатать значения credentials.
6. Сохранить только secret-safe JSON:
   - active AI backend/model;
   - fallback flags;
   - effective STT provider;
   - TTS feature flags/provider/model;
   - credential present true/false.
7. Обновить письмо Apple и App Privacy recipients по факту.

### P0-H. Backend deploy UGC — только после отдельного GO

Следовать серверному guide без отклонений:

1. Внешний health check.
2. Backup каждого заменяемого server file.
3. Deploy только нужных router/migration/main files.
4. `python3 -m py_compile` изменённых Python files.
5. Применить migration контролируемо и проверить constraints/indices.
6. Restart сервиса строго по runbook.
7. Локальный и внешний health check.
8. OpenAPI check новых endpoints.
9. Authenticated smoke:
   - report;
   - duplicate report;
   - restrict;
   - restricted WebSocket send;
   - own delete;
   - operator list/decision.
10. Проверить, что логи не содержат plaintext/ciphertext/token.

Rollback должен быть подготовлен до первого server write.

### P0-I. App Store Connect App Privacy

После production truth check и до Submit:

1. Открыть `docs/AppStore/APP_PRIVACY_ANSWERS_2026-09-09_RU.md`.
2. Вручную перенести ответы в App Store Connect.
3. Не использовать deprecated `docs/APP_PRIVACY_DATA.md`.
4. Убедиться:
   - Data Collection = Yes;
   - Tracking = No;
   - linked categories совпадают с manifest;
   - Health раскрывает вручную введённые wellness данные, даже при выключенном HealthKit;
   - E2EE chat content раскрыт консервативно как collected User Content;
   - diagnostics/customer support раскрыты;
   - Browsing History = No только потому, что Safari Content Blocker локальный, а monitoring UI выключен.
5. После Archive сгенерировать Xcode Privacy Report и повторно сверить SDK manifests.

### P0-J. Archive и signed entitlements — только после GO

Проверить именно подписанный `.app`, а не только source `.entitlements`.

Обязательно подтвердить:

- `aps-environment = production`;
- нет `com.apple.developer.networking.networkextension`;
- нет Family Controls entitlement;
- нет HealthKit entitlement;
- embedded только ожидаемые extensions:
  - Content Blocker;
  - Antifake Share;
  - Call Directory;
- каждый embedded extension содержит свой PrivacyInfo.xcprivacy;
- Release binary собран с `APP_STORE_BUILD`;
- external payment destinations отсутствуют/недостижимы;
- Smart DNS и HealthKit symbols/flows не активны;
- StoreKit products соответствуют App Store Connect.

### P0-K. Physical device/TestFlight QA — только после GO

На чистой установке:

1. Onboarding.
2. Privacy Policy и Terms.
3. Псевдонимная регистрация.
4. Создание/join тестовой семьи.
5. Родительский и детский профили.
6. Family Chat:
   - send;
   - report;
   - restrict;
   - delete own message.
7. Antifake safe sample.
8. AI disclosure и consent.
9. STT/TTS.
10. Location/emergency без реального вызова служб.
11. StoreKit products.
12. Purchase sheet cancel path.
13. Restore Purchases.
14. Delete Account.
15. APNs push через TestFlight.
16. Проверить, что нет VPN/Smart DNS/Family Controls/HealthKit permission prompts или обещаний.

### P0-L. Видео и финальное письмо

Видео:

- только физический iPhone;
- непрерывная запись от запуска с Home Screen;
- актуальная публичная iOS;
- та же TestFlight build, которая отправляется Apple;
- показать report/restrict/delete own;
- показать StoreKit sheet и Restore;
- не показывать secrets, реальные семейные данные и production credentials.

Финальное письмо:

- база: `docs/AppStore/APPLE_GUIDELINE_2_1_MASTER_RESPONSE_2026-09-09_RU.md`;
- удалить все `[ЗАПОЛНИТЬ]` и условные замечания;
- не писать, что Apple Family Controls используются;
- не писать VPN/Smart DNS;
- подставить фактические device/iOS/version/build;
- подставить одноразовый review family/recovery code;
- перечислить только providers, подтверждённые production truth check;
- приложить имя видео;
- согласовать App Review Notes с тем же build.

## 8. P1 после обязательных блокеров

Эти задачи важны, но не должны смешиваться с P0 без необходимости:

1. Полный runtime-аудит лишних `Info.plist` usage descriptions:
   - Apple Music;
   - HomeKit;
   - Calendar;
   - Bluetooth;
   - Reminders;
   - Siri;
   - другие неиспользуемые permission keys.
2. Удалить необоснованные keys либо документировать и проверить фактический flow.
3. Проверить rights/licenses:
   - персонажи;
   - иллюстрации;
   - музыка/звуки;
   - Rive assets;
   - отсутствие смешения с Disney.
4. Уточнить фактического поставщика и сценарий дорожной помощи.
5. Проверить экспортное шифрование и ответы export compliance.
6. Устранить low-severity per-connection WebSocket rate-limit limitation, если abuse model требует distributed/user-level limiter.

## 9. Отложенная фаза Family Controls

Не выполнять в текущем App Review hotfix без отдельного продуктового решения.

Для будущего релиза:

1. Определить минимальный реальный Screen Time scope.
2. Создать нужные extensions:
   - Device Activity Monitor;
   - Shield Configuration;
   - Shield Action, если нужен;
   - Device Activity Report, если нужен.
3. Зарегистрировать отдельные Bundle IDs.
4. Подать Family Controls Distribution requests для main app и каждого extension.
5. Получить одобрение Apple.
6. Пересоздать provisioning profiles.
7. Реализовать системные controls без mock/fallback.
8. Проверить минимум на двух физических устройствах parent/child.
9. Только после этого вернуть точные claims в тарифы, UI, metadata и письмо Apple.

## 10. Карта текущих TODO

### Выполнено локально

- `app-review-letter`
- `app-review-capabilities`
- `app-review-checklist`
- `appreview-network-audit`
- `appreview-appstore-config`
- `appreview-smartdns-off`
- `appreview-network-ui`
- `appreview-network-copy`
- `appreview-protection-hub`
- `appreview-storekit-only`
- `appreview-network-tests`
- `appreview-ugc-contract`
- `appreview-ugc-backend`
- `appreview-privacy-audit`
- `appreview-security-review`

### Реализовано, но требует финальной проверки/закрытия статуса

- `appreview-ugc-ios-tests`
- `appreview-ugc-backend-tests`
- `appreview-ugc-ios`
- `appreview-ugc-review-tools`
- `appreview-ai-providers`
- `appreview-privacy-manifest`
- `appreview-app-privacy`
- `appreview-family-claims`
- `appreview-compliance-tests`

Не переводить эти задачи в completed только по наличию кода. Нужны соответствующие tests/truth checks из раздела 7.

### Не выполнено и требует отдельного GO

- `appreview-device-qa`
- `appreview-backend-deploy`
- `appreview-final-archive`

## 11. Известные риски и ловушки

1. **Огромное грязное рабочее дерево.** Не принимать весь `git diff` за изменения текущей задачи.
2. **Старые документы противоречат новому SSOT.** Для privacy использовать только `APP_PRIVACY_ANSWERS_2026-09-09_RU.md`; для ответа Apple — master response после актуализации.
3. **Static PASS не равен Archive PASS.** Provisioning и merged privacy report видны только после Archive.
4. **Build interrupted не равен test failure.** Повторить UI tests и сохранить `.xcresult`.
5. **Код provider chain не равен production configuration.** Нужен secret-safe runtime check.
6. **Локальный backend code не равен deploy.** Не говорить Apple, что report/restrict доступен, до production smoke и TestFlight.
7. **E2EE не отменяет App Privacy disclosure.** Encrypted envelope всё равно считается collected user content при передаче на server.
8. **Metadata-only moderation.** Не добавлять plaintext/ciphertext/free-form complaint reason в report storage ради удобства оператора.
9. **Family Controls.** Не возвращать claims до Distribution entitlement и device QA.
10. **HealthKit.** Не добавлять entitlement/permission prompt в текущую submission без отдельной реализации и privacy/legal review.
11. **App Privacy conservative mapping.** Не уменьшать категории без endpoint/runtime evidence.
12. **Review video.** Нельзя снимать simulator и нельзя показывать другой build.

## 12. Рекомендуемый первый сеанс следующей ML-системы

1. Прочитать этот handoff.
2. Прочитать:
   - `docs/AppStore/APPLE_GUIDELINE_2_1_MASTER_RESPONSE_2026-09-09_RU.md`;
   - `docs/AppStore/APP_PRIVACY_ANSWERS_2026-09-09_RU.md`;
   - `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` только перед server phase.
3. Зафиксировать repo root/branch/status.
4. Не редактировать production и не делать commit.
5. Выполнить Swift review текущего App Review diff.
6. Исправить только blocking findings.
7. Запустить три static gates и `plutil -lint`.
8. Собрать Debug/test products один раз.
9. Запустить targeted unit/UI moderation tests.
10. Отчитаться владельцу:
    - что PASS;
    - что FAIL;
    - точные blockers;
    - какие действия требуют GO.

## 13. Definition of Done всей задачи

Работа по Guideline 2.1 завершена только когда одновременно выполнено:

- локальный App Review diff reviewed;
- backend tests PASS;
- iOS unit tests PASS;
- iOS UI moderation tests PASS;
- static policy/privacy/UGC gates PASS;
- production AI/STT/TTS truth подтверждён;
- UGC backend deployed и smoke PASS;
- App Store Connect App Privacy заполнен по финальному manifest/report;
- signed Archive entitlements проверены;
- TestFlight clean install PASS на физическом iPhone;
- IAP products/Restore PASS;
- APNs TestFlight push PASS;
- report/restrict/delete own PASS на реальном backend;
- account deletion PASS;
- физическое видео записано;
- письмо и Review Notes не содержат placeholder/условных claims;
- отправляется та же build, которая прошла все проверки.

До этого момента корректная формулировка статуса:

> «Локальная реализация существенно завершена; production deploy, signed Archive, TestFlight/device QA, video и App Review submission ещё не выполнены».
