# ALADDIN AI — полный ответ App Review (Guideline 2.1)

**Дата:** 2026-09-15  
**Статус:** готово к копированию в Reply + Notes  
**IAP:** 3 тарифа владелец загружает/привязывает **при отправке** версии; до этого «Products not loaded» на TF — ожидаемо (не баг).

Заполните перед отправкой плейсхолдеры `[ЗАПОЛНИТЬ …]`.

---

## A. Русский текст (Reply в App Store Connect)

Здравствуйте, команда App Review!

Спасибо за запрос дополнительной информации. Ниже ответы по всем пунктам. Приложение ALADDIN AI готово к проверке на физических устройствах.

### 1. Запись экрана

Приложена непрерывная запись экрана с физического iPhone (актуальная публичная iOS).

В записи показано:

- запуск приложения с домашнего экрана;
- выбор языка и onboarding;
- просмотр и принятие Privacy Policy и Terms of Use;
- создание псевдонимной технической сессии без обязательного email/пароля;
- создание / вход в семейную группу;
- родительский контроль: правила, задания, достижения, вознаграждения;
- Antifake — проверка тестового подозрительного текста;
- семейный чат: отправка сообщения, **Report** (жалоба), **Restrict** (ограничение отправителя родителем), удаление собственного сообщения;
- детский образовательный раздел;
- AI-ассистент и компаньоны (Единорог, Аладдин, Джин) с пояснением, что ответы создаёт ИИ;
- экран тарифов (SaaS / In-App Purchase) и точка входа в покупку / Restore;
- удаление аккаунта в приложении.

Устройство: `[ЗАПОЛНИТЬ: модель iPhone]`  
Версия iOS: `[ЗАПОЛНИТЬ]`  
Версия приложения / Build: `[ЗАПОЛНИТЬ]`  
Имя файла видео: `[ЗАПОЛНИТЬ]`

### 2. Назначение и аудитория

ALADDIN AI — семейная платформа цифровой безопасности и воспитания для родителей, детей, подростков и пожилых.

Проблема: цифровые риски, мошенничество в сети, отсутствие понятных семейных правил и обучения безопасности.

Ценность: Antifake-проверки; родительский контроль (правила, задания, награды); закрытый семейный чат с модерацией; детское обучение; AI-ассистент и три семейных компаньона (Единорог, Аладдин, Джин). Монетизация — SaaS-подписка через Apple In-App Purchase (StoreKit 2) с Restore Purchases.

### 3. Как настроить доступ и проверить функции

Email и пароль для старта не нужны. После onboarding и принятия Privacy Policy / Terms приложение создаёт псевдонимную JWT-сессию устройства.

Порядок для ревьюера:

1. Запуск → язык → onboarding → Privacy Policy / Terms → «Начать».  
2. Семья → создать семью или ввести review recovery code.  
3. Родительский контроль → правила / задания.  
4. Защита → Antifake (тестовый текст ниже).  
5. Семейный чат → сообщение → Report / Restrict / Delete own.  
6. Детский раздел / AI / компаньоны.  
7. Тарифы → UI планов; покупка через системный лист Apple после привязки IAP-продуктов к этой версии (см. блок IAP).  
8. Профиль → Безопасность → Удалить аккаунт.

Тестовая семья (только для App Review):

- Family / recovery code: `[ЗАПОЛНИТЬ]`  
- Родитель: `[ЗАПОЛНИТЬ]`  
- Ребёнок: `[ЗАПОЛНИТЬ]`

Тестовый текст для Antifake:

> Срочно сообщите пароль и код из SMS, иначе ваш аккаунт будет заблокирован.

### Подписки (In-App Purchase) — важно для ревью

Цифровой доступ к расширенным функциям оплачивается **только** через Apple In-App Purchase (StoreKit 2). Есть Restore Purchases.

Три auto-renewable subscription product ID (создаются / привязываются к **этой** версии приложения в App Store Connect при отправке):

1. `ai.aladdin.subscription.individual.v2` — Individual / Personal  
2. `ai.aladdin.subscription.family` — Family  
3. `ai.aladdin.subscription.premium` — Premium  

Пока продукты не привязаны к версии и не доступны для сборки, экран «Тарифы» может показывать временное состояние «Products not loaded» / перезагрузку. Это **ожидаемое** состояние до согласования и привязки тарифов, а не дефект приложения. После привязки трёх продуктов к версии на проверке открывается системный лист покупки Apple.

В видео показан UI тарифов и точки входа в покупку; живой StoreKit sheet доступен ревьюеру после привязки указанных Product ID к этой submission.

### 4. Внешние сервисы

- Backend ALADDIN (`https://aladdin-ai.ru`) — устройство, семья, Antifake, модерация чата, AI  
- Apple StoreKit 2 — подписка и Restore  
- Apple Push Notification Service  
- Apple Safari Content Blocker, Call Directory, Speech Recognition, Maps  
- AI через backend (Hermes) с маршрутизацией OpenRouter / DeepSeek и fallback Google Gemini  
- STT: Apple Speech; серверный fallback Yandex SpeechKit, затем OpenAI Whisper  
- TTS: Apple AVSpeech; premium ElevenLabs Flash v2.5  

Рекламных SDK нет. Данные не используются для рекламного трекинга.

### 5. Региональные различия

Основная функциональность одинакова во всех поддерживаемых регионах.  
Цена и валюта подписки определяются storefront App Store.  
Интерфейс: русский и английский.

### 6. Регулируемые отрасли / материалы третьих лиц

ALADDIN AI — потребительское приложение для семейной цифровой безопасности. Мы не оказываем лицензируемые медицинские, банковские, страховые или юридические услуги и не заменяем государственные экстренные службы.

Antifake даёт информационную оценку риска.  
Персонажи Единорог, Аладдин и Джин и связанные материалы созданы для ALADDIN.

### Семейный чат и UGC (Guideline 1.2)

Закрытый семейный чат (без публичной ленты). Реализованы:

- **Report** — жалоба на сообщение другого участника (metadata-only на сервер);  
- **Restrict** — родитель может ограничить отправку сообщений участнику;  
- **Delete own** — удаление собственного сообщения.

Эти действия показаны в видео.

Готовы предоставить дополнительную информацию по запросу.

С уважением,  
Команда ALADDIN AI  
Контакт: `[ЗАПОЛНИТЬ email]`

---

## B. English text (Reply + paste into Notes)

Hello App Review team,

Thank you for requesting additional information. Below are answers to all items. ALADDIN AI is ready for review on physical devices.

### 1. Screen recording

We attached a continuous screen recording captured on a physical iPhone running a current public iOS version.

The recording shows:

- launching the app from the Home Screen;
- language selection and onboarding;
- viewing and accepting the Privacy Policy and Terms of Use;
- creating a pseudonymous technical session without required email/password;
- creating / joining a family group;
- parental control: rules, tasks, achievements, rewards;
- Antifake check of a safe sample suspicious text;
- family chat: send a message, **Report**, **Restrict** (parent), delete own message;
- children’s education section;
- AI assistant and companions (Unicorn, Aladdin, Genie) with AI disclosure;
- Tariffs screen (SaaS / In-App Purchase entry) and Restore entry point;
- in-app account deletion.

Device: `[FILL iPhone model]`  
iOS: `[FILL]`  
App version / Build: `[FILL]`  
Video file name: `[FILL]`

### 2. Purpose and audience

ALADDIN AI is a family digital safety and parenting platform for parents, children, teenagers, and elderly family members.

Problem solved: digital risks, online fraud/scams, and the lack of clear family rules and safety education.

Value: Antifake checks; parental control (rules, tasks, rewards); private moderated family chat; children’s education; AI assistant plus three family companions (Unicorn, Aladdin, Genie). Monetization is a SaaS subscription via Apple In-App Purchase (StoreKit 2) with Restore Purchases.

### 3. Setup and access

No email/password is required to start. After onboarding and accepting Privacy Policy / Terms, the app creates a pseudonymous device JWT session.

Reviewer path:

1. Launch → language → onboarding → Privacy Policy / Terms → Start.  
2. Family → create a family or enter the review recovery code.  
3. Parental Control → rules / tasks.  
4. Protection → Antifake (sample text below).  
5. Family Chat → message → Report / Restrict / Delete own.  
6. Child section / AI / companions.  
7. Tariffs → plan UI; Apple purchase sheet after IAP products are linked to this version (see IAP note).  
8. Profile → Security → Delete Account.

Review-only family:

- Family / recovery code: `[FILL]`  
- Parent: `[FILL]`  
- Child: `[FILL]`

Safe Antifake sample text:

> Urgently send your password and the SMS code, or your account will be blocked.

### In-App Purchase note (important)

Paid digital features use **Apple In-App Purchase (StoreKit 2) only**, with Restore Purchases.

Three auto-renewable subscription Product IDs (created / linked to **this** app version in App Store Connect at submission):

1. `ai.aladdin.subscription.individual.v2` — Individual / Personal  
2. `ai.aladdin.subscription.family` — Family  
3. `ai.aladdin.subscription.premium` — Premium  

Until these products are linked and available for the build under review, the Tariffs screen may show a temporary “Products not loaded” / reload state. This is **expected** before the tariffs are attached for this submission, not an application defect. After the three products are linked to the version under review, the system Apple purchase sheet works normally.

The recording shows the Tariffs UI and purchase entry points; the live StoreKit sheet is available to reviewers once the Product IDs above are linked to this submission.

### 4. External services

- ALADDIN backend (`https://aladdin-ai.ru`) — device, family, Antifake, chat moderation, AI  
- Apple StoreKit 2 — subscription and Restore  
- Apple Push Notification Service  
- Apple Safari Content Blocker, Call Directory, Speech Recognition, Maps  
- AI via backend (Hermes) with OpenRouter / DeepSeek routing and Google Gemini fallback  
- STT: Apple Speech; server fallback Yandex SpeechKit, then OpenAI Whisper  
- TTS: Apple AVSpeech; premium ElevenLabs Flash v2.5  

No advertising SDKs. Data is not used for ad tracking.

### 5. Regional differences

Core features are the same across supported regions.  
Subscription price and currency follow the App Store storefront.  
UI languages: Russian and English.

### 6. Regulated industries / third-party material

ALADDIN AI is a consumer family digital-safety app. We do not provide licensed medical, banking, insurance, or legal services and do not replace official emergency services.

Antifake provides an informational risk assessment.  
Unicorn, Aladdin, and Genie characters and related assets were created for ALADDIN.

### Family chat / UGC (Guideline 1.2)

Private family chat only (no public feed). Implemented:

- **Report** — report another member’s message (metadata-only to server);  
- **Restrict** — parent can restrict a member from sending;  
- **Delete own** — user can delete their own message.

These actions are shown in the video.

We are happy to provide any further information you need.

Kind regards,  
ALADDIN AI Team  
Contact: `[FILL email]`

---

## C. Short Notes field (English, compact)

```text
ALADDIN AI — family digital safety & parenting (parents, kids, teens, elderly).
SaaS via Apple IAP (StoreKit 2) + Restore.

Product IDs (link with this version at submit):
- ai.aladdin.subscription.individual.v2
- ai.aladdin.subscription.family
- ai.aladdin.subscription.premium
Until linked, Tariffs may show temporary “Products not loaded” (expected, not a bug).

No email/password to start (pseudonymous JWT after onboarding).
Review family code: [FILL] | Parent: [FILL] | Child: [FILL]

Path: Launch → onboarding → Family → Parental Control → Antifake →
Family Chat (Report/Restrict/Delete own) → Tariffs UI → Delete Account.

Services: aladdin-ai.ru; StoreKit; APNs; Content Blocker; Call Directory;
Speech; Maps; AI Hermes/OpenRouter/DeepSeek/Gemini; STT/TTS as in full reply.

Video: [NAME] | Device/iOS/build: [FILL]
```
