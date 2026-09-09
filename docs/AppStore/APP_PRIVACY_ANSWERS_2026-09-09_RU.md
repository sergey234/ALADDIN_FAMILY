# App Privacy — фактическая карта и ответы

Дата аудита: 2026-09-09. Канон для первой повторной App Store-отправки.

## Главные ответы App Store Connect

- Data Collection: **Yes**.
- Tracking: **No**.
- Data Used to Track You: **No** для всех категорий.
- Third-Party Advertising: **No**.
- Developer Advertising or Marketing: **No**.
- Большинство данных считать **Linked to the User: Yes**. Даже псевдонимный `user_id`, `family_id` или `device_id` связывает запись с аккаунтом/семьёй в смысле Apple.
- Основная цель: **App Functionality**. Для Device ID и Product Interaction дополнительно: **Analytics**.

Старые утверждения «ничего не собираем» и «всё не связано с пользователем» больше не использовать: они противоречат JWT-аккаунту, семейному чату, StoreKit, геолокации и серверным security-функциям.

## Что отметить как собираемые данные

### Contact Info

- Name — Yes; Linked: Yes; App Functionality. Семейное имя/псевдоним и имя выбранного контакта.
- Email Address — Yes; Linked: Yes; App Functionality. Профиль и добровольные проверки утечек/безопасности.
- Phone Number — Yes; Linked: Yes; App Functionality. Call Directory, проверки номера и добровольно отправленный контакт.
- Physical Address — Yes; Linked: Yes; App Functionality. Пользовательские названия/адреса geofence и семейных мест.
- Contacts — Yes; Linked: Yes; App Functionality. Только контакт, явно выбранный пользователем для отправки в семейный чат; массовой выгрузки адресной книги нет.

### Location

- Precise Location — Yes; Linked: Yes; App Functionality. Добровольная отправка геопозиции в чат, семейные запросы местоположения, geofence и emergency/crash сценарии.
- Coarse Location — No отдельно, если продукт отправляет точные координаты и уже отмечен Precise Location.

### Purchases

- Purchase History — Yes; Linked: Yes; App Functionality. Статус StoreKit-подписки и восстановление покупок. Платёжные реквизиты карты приложение не получает.

### User Content

- Other User Content — Yes; Linked: Yes; App Functionality. Семейные сообщения, ссылки, security-check ввод и metadata-only жалобы.
- Photos or Videos — Yes; Linked: Yes; App Functionality.
- Audio Data — Yes; Linked: Yes; App Functionality. Голосовые сообщения, STT и TTS-запросы.

Семейный чат использует E2EE. Сервер хранит зашифрованный envelope, но для консервативного и прозрачного App Privacy disclosure эти категории всё равно отмечаются как collected. Жалоба не копирует plaintext сообщения: сохраняются только ID, family/user linkage, категория и статус.

### Identifiers

- User ID — Yes; Linked: Yes; App Functionality.
- Device ID — Yes; Linked: Yes; App Functionality + Analytics.

### Usage Data

- Product Interaction — Yes; Linked: Yes; App Functionality + Analytics.
- Advertising Data — No.
- Other Usage Data — Yes; Linked: Yes; App Functionality + Analytics.

### Sensitive / Other

- Sensitive Info — Yes; Linked: Yes; App Functionality. Пользователь может добровольно передать security-check данные; они не используются для рекламы.
- Health — Yes; Linked: Yes; App Functionality + Product Personalization. Самостоятельно введённые wellness, mood, sleep, medication и assessment данные; HealthKit в первой App Store-сборке выключен.
- Fitness — Yes; Linked: Yes; App Functionality. Датчики движения/скорости в явно включённом emergency/crash сценарии.
- Emails or Text Messages — Yes; Linked: Yes; App Functionality. Содержимое семейного чата хранится как E2EE envelope.
- Customer Support — Yes; Linked: Yes; App Functionality. Добровольные обращения и переданные пользователем диагностические материалы.
- Other Data Types — Yes; Linked: Yes; App Functionality. Датчики движения/скорости в явно включённом emergency/crash сценарии.
- Browsing History — No: Safari Content Blocker работает локально; история браузера не загружается.
- Search History — No: ручная проверка конкретной ссылки/текста считается User Content, а не полной историей поиска.
- Financial Info — No: платёжные реквизиты обрабатывает Apple.
- Crash Data, Performance Data и Other Diagnostic Data — Yes; Linked: Yes; App Functionality + Analytics. Технические события и добровольно отправляемые диагностические материалы. Дорожное crash-detection событие не является crash log приложения.

## Внешние получатели

- Apple: StoreKit, APNs, Apple Speech Recognition, Apple Maps.
- Hermes/OpenRouter: AI/LLM routing; production default по коду — DeepSeek V4 Flash.
- Google Gemini: опциональный AI fallback, по умолчанию выключен.
- Yandex SpeechKit: серверный STT fallback.
- OpenAI Whisper: следующий STT fallback.
- ElevenLabs Flash: premium server TTS.
- ALADDIN backend: аккаунт, семья, E2EE envelopes, moderation metadata, security APIs.
- Telegram: только когда пользователь сам переходит в поддержку; SDK рекламного трекинга нет.
- RiveRuntime: локальный рендеринг анимаций, пользовательские данные ему не передаются.

Фактическая активность production AI/STT/TTS credentials и feature flags подтверждается отдельным read-only production check без вывода значений секретов.

## Privacy Manifest

`PrivacyInfo.xcprivacy` синхронизирован с этой консервативной картой:

- tracking выключен, tracking domains пусты;
- все серверно связанные категории имеют `Linked = true`;
- App Functionality указана для всех категорий;
- Analytics добавлена только для Device ID и Product Interaction;
- Required Reason APIs: UserDefaults `CA92.1` и App Group `1C8F.1`, File Timestamp `C617.1`, System Boot Time `35F9.1`.

## Перед нажатием Publish в App Store Connect

1. Перенести ответы выше в App Store Connect → App Privacy.
2. Не возвращать старые ответы из `docs/APP_PRIVACY_DATA.md`.
3. Сгенерировать Xcode Privacy Report для финального Archive и сверить bundled SDK manifests.
4. Если production runtime-check покажет другого активного AI/STT/TTS-провайдера, обновить это описание и письмо Apple до отправки.
