# Регистрация новых пользователей и карточка «семья + тариф» на главном экране

Документ для разработчиков и ML-систем: как устроена стабилизация первичной регистрации семьи на iOS, какие есть серверные вызовы, и как на главном экране связаны цвет прямоугольника, название тарифа и лимит участников семьи.

**Полный канон (iOS + прод-сервер, матрицы расхождений, чеклисты):** `docs/REGISTRATION_AND_TARIFF_MAIN_SCREEN_ML_REFERENCE.md`.  
**Смоук семьи (тестовая сеть / прод):** `docs/FAMILY_API_SMOKE_REGIMEN.md`. **ТЗ бэкенду (POST join, gate add):** `docs/server/BACKEND_FAMILY_JOIN_AND_ADD_GATE.md`.

---

## 1. Точки входа в UI

### 1.1. Маршрут `mainWithRegistration`

В `ALADDINApp.swift` экран `MainScreenWithRegistration` показывается **отдельным корнем**, вне `NavigationView`, вместе с остальными приложениями через общий слой `applyRootChrome` (те же `environmentObject`: навигация, локализация, подписка, `MainViewModel` и т.д.).

Это сделано, чтобы прогрессивная регистрация не наслаивалась на стек навигации и чтобы уменьшить шум от системной навигационной панели на первом входе. Основное приложение после онбординга живёт внутри `NavigationView` с `.navigationBarHidden(true)` на контейнере экранов.

### 1.2. Обёртка `MainScreenWithRegistration`

Файл: `Screens/MainScreenWithRegistration.swift`.

- При появлении (`.task`) через ~0.5 с вызывается `registrationVM.startRegistration()` — открывается цепочка модалок.
- **Отмена** (кнопка в углу): `completeRegistration(isSuccess: false)` — **не** выставляет `hasCompletedOnboarding`, затем переход на экран семьи через `navigationManager.switchToFamilyScreen()`.
- **Успех**: `hasCompletedOnboarding = true` только при реальном успехе регистрации (`completeRegistration(isSuccess: true)`).

DEBUG-only: опциональная панель Apple / magic link (флаг `isAlternativeRegistrationAuthVisible`).

---

## 2. Логика регистрации на клиенте (`FamilyRegistrationViewModel`)

Файл: `ViewModels/FamilyRegistrationViewModel.swift`.

### 2.1. Шаги

1. Согласие (`acceptConsent` → UserDefaults ключи версии согласия).
2. Роль: `parent`, `child`, `teenager`, `elderly` (локальная модель `FamilyRole`).
3. Возрастная группа (`AgeGroup`) с маппингом в строки, ожидаемые сервером (`serverValue`, например подросток → `"13-17"`).
4. Буква для имени вида «Родитель A» (если не режим admin-add — имя пишется в `current_user_name`).
5. Вызов `createFamily()` (или ветка добавления участника — см. ниже).

### 2.2. Маппинг «подросток» на сервер

Сервер принимает роли вроде `parent` / `child` / `elderly`. Локальная роль `.teenager` отправляется как **`child`**, а возрастная группа подростка даёт **`age_group: "13-17"`** (`AgeGroup.teen.serverValue`).

### 2.3. Режим `admin_add_mode`

Если пользователь уже в семье и с главного / семьи включено добавление участника:

- В `UserDefaults` может быть `admin_add_mode == true` и непустой `family_id`.
- Тогда вместо `POST /api/family/create` вызывается **`addFamilyMember`** (лимит проверяется через `SubscriptionManager.shared.canAddFamilyMember`).
- **`your_member_id`** и роль «текущего пользователя» при admin-add **не перезаписываются** (остаётся сессия родителя).

Защита от ошибочного состояния: если `admin_add_mode` true, но **`family_id` на устройстве пустой**, флаг сбрасывается и выполняется обычное создание семьи (иначе возможны 404 при «добавлении» без семьи).

### 2.4. Восстановление после ошибки «семья не найдена»

Если в режиме admin-add `addFamilyMember` падает с признаками «family not found» / 404, клиент сбрасывает `admin_add_mode` и **повторно вызывает `createFamily()`** (fallback на первичное создание).

### 2.5. Успешный ответ `createFamily`

- `family_id` → `FamilyLocalStore.familyIdKey`, сброс кэшей при смене семьи (`FamilyLocalStore.resetPersistedCachesIfFamilyChanged`).
- `creator_member_id` → `FamilyLocalStore.persistFamilyCreatorMemberId` (для правил «кто создатель» на экране семьи).
- `your_member_id` → `UserDefaults` (`your_member_id`), кроме admin-add.
- JWT из ответа: если оба токена валидны — сохранение; иначе fallback **`loginByRecoveryCode`**.
- Recovery code может сохраняться в Keychain через `RecoveryCodeStorageManager`.
- Локально дописывается создатель в список участников (см. продолжение файла VM).

---

## 3. Сетевой слой: `POST /api/family/create`

Файл: `Core/Network/APIService.swift`, метод `createFamily` → внутренний `performCreateFamily`.

- Эндпоинт по умолчанию: **`AppConfig.Endpoint.createFamily`** → `/api/family/create`, **`requiresAuth: true`**.
- При **401 / истёкший токен / reauth**: один раз выполняется **`bootstrapDeviceTokenIfNeeded(forceRefresh: true)`** и запрос **повторяется** (стабилизация первого запуска, когда JWT ещё не успел появиться).
- При ответе, интерпретируемом как **notFound** у шлюза: fallback на legacy путь **`/family/create`** (обратная совместимость окружений).

Аналогичная схема есть для `joinFamily` (`/api/family/join` и fallback `/family/join`).

Тело запроса: `CreateFamilyRequest` с полями в духе `role`, `age_group`, `personal_letter`, `device_type` (точные имена полей — в модели запроса рядом с VM).

---

## 4. Сервер (ожидаемое поведение с точки зрения iOS)

В этом репозитории лежит **клиент**; бэкенд не дублируется здесь. С точки зрения приложения сервер:

1. Принимает создание семьи по защищённому маршруту с JWT устройства.
2. Возвращает идентификаторы семьи и участника, опционально пару access/refresh или сценарий восстановления по recovery code.
3. Отдельно от семьи отдаёт **подписку и триал** (например `GET /api/subscription/status` или данные внутри JWT после bootstrap) — это источник правды для **лимита членов семьи** и уровня плана после синхронизации.

Любая правка контрактов на сервере должна сопровождаться обновлением моделей в iOS и `APIResponseValidator`, если ответы валидируются централизованно.

---

## 5. Подписка, триал и лимит семьи (`SubscriptionManager`)

Файл: `Core/Managers/SubscriptionManager.swift`.

### 5.1. Лимит участников по уровню (`familyMemberLimit`)

Одна таблица для UI и для проверок «можно ли добавить»:

| Уровень (`SubscriptionLevel`) | Макс. участников семьи |
|--------------------------------|-------------------------|
| `free`                         | 1                       |
| `trial`                          | 3                       |
| `personal`                       | 2                       |
| `family`                       | 6                       |
| `premium`                      | 10                      |

### 5.2. Кап для лимита vs «план в JWT» (`subscriptionLevelForFamilyMemberCap`)

Сервер может оставить `plan_level` = free, пока активен триал. Для **лимита роста семьи** используется не только `status.level`, но и активный триал:

- Если в `SubscriptionStatus` есть активный `trialInfo` → для капа уровень считается **`trial`** (3 места).
- Дополнительно: если в статусе триала нет, но локально `trialStatus?.isActive` → тоже **`trial`**.
- Иначе кап следует за `status.level`.

При обновлении статуса (`updateSubscriptionStatus`) пересчитываются `currentFamilyLimit`, `currentFamilyRemaining`, UserDefaults `family_limit` / `family_remaining`, шлётся `SubscriptionUpdated` при реальном изменении, вызываются `reconcileTariffManagerWithSubscription` и **`bumpSubscriptionDisplayEpoch()`**.

### 5.3. Порядок обновления триала и подписки (`updateTrialStatus`)

После присвоения `trialStatus` при активном локальном `currentSubscription` вызывается **`updateSubscriptionStatus(sub)`** заново, чтобы лимит и градиент главной не застревали на free (1) и «золотом», если триал уже активен, а план в снимке ещё free.

### 5.4. Отображаемый уровень для UI (`getCurrentLevel`)

- Активный локальный триал → **`.trial`**.
- Если подписка уже **free** и триал **не** активен → **`.free`** (важно после cancel: не показывать trial по устаревшему JWT).
- Иначе согласование уровня из `currentSubscription` и `currentToken` (ветки для рассинхрона JWT и Keychain).

### 5.5. Downgrade на free (`downgradeToFree`)

Серверный cancel, очистка триала из Keychain, локальный снимок free, `forceSync`, уведомление `SubscriptionUpdated`.

### 5.6. Повторный тап «Пробный» на тарифах (`activateTrialIfNeeded`)

Если триал уже активен — повторный вызов **не игнорируется полностью**: пересчитывается статус подписки и **`bumpSubscriptionDisplayEpoch()`**, чтобы главная перерисовала лимиты и цвет.

### 5.7. Синк после экрана тарифов

`syncSubscriptionAfterTariffsDismiss()` — **без** троттлинга главного экрана, сразу `forceSync` + bump epoch (см. `10_TariffsScreen`).

---

## 6. Главный экран: прямоугольник семьи и цвет тарифа

Файл: `Screens/01_MainScreen.swift`.

### 6.1. Где рисуется «цветной» блок

Блок с заголовком семьи, слотами «X из Y», бейджем защиты, строкой тарифа и кнопками «Управлять» / «Добавить» обёрнут в:

- `RoundedRectangle` + **`LinearGradient`** от `currentTariffColor` к `currentTariffColor.opacity(0.85)`.
- Обводка и тень тоже от `currentTariffColor`.

### 6.2. Соответствие тарифа и цвета (`currentTariffColor`)

Логика привязана к **`subscriptionManager.getCurrentLevel()`**:

| Уровень   | Цвет |
|----------|------|
| `free`   | `Color.secondaryGold` (жёлто-золотой акцент) |
| `trial`  | `Color(red: 0.22, green: 0.78, blue: 0.72)` — **бирюзовый / teal**, отличимый от free |
| `personal` | синий |
| `family`   | фиолетовый |
| `premium`  | оранжевый |

Название тарифа в тексте: `currentTariffDisplayName` через ключи локализации `tariffs_*` и fallback `level.displayName`.

Иконка рядом с названием: `tariffIconForCurrentLevel()` (SF Symbol).

### 6.3. Почему иногда UI «не менялся» после смены тарифа

Добавлены:

- **`subscriptionDisplayEpoch`** в `SubscriptionManager` — инкремент при значимых обновлениях подписки/триала.
- **`.id(...)`** у строки тарифа, у карточки семьи и у сегментов чата на главной, включающие `subscriptionDisplayEpoch` и стабильный **`tariffRowViewIdentity`** (`getCurrentLevel()`, флаг активного триала, язык).

Это принудительно заставляет SwiftUI пересобрать градиент и тень на реальных устройствах, где кэширование иногда не подхватывало смену `Color`.

### 6.4. Число членов семьи «из Y» в шапке карточки

Текст строится из локализованной строки `main_family_header_member_slots` с аргументами:

- первый: `min(mainViewModel.familyMembers, max(0, subscriptionManager.currentFamilyLimit))`
- второй: `max(0, subscriptionManager.currentFamilyLimit)`

То есть отображается **фактическое число участников**, ограниченное сверху лимитом тарифа, и **лимит по тарифу** (после учёта триала через кап, см. раздел 5.2).

### 6.5. Обновление данных после действий на других экранах

На `homeContent` подписаны уведомления, в т.ч.:

- `MainFamilyStatsForceRefresh`, `FamilyMembersUpdated`, `FamilyDevicesDidChange` → debounced refresh `MainViewModel`, при необходимости `subscriptionManager.forceSync()`.
- `SubscriptionUpdated`, `tariffPurchased`, `onChange(of: subscriptionManager.currentSubscription)` → обновление дашборда / синк.

---

## 7. Связанные стабилизации вокруг семьи (кратко)

- **`FamilyLocalStore`**: снимок `family_id` с сервера (`X-Resolved-Family-Id`), валидация кэша ростера при смене семьи, API ручной очистки локального кэша.
- **`FamilyAccessPolicy`**: безопасные дефолты прав родителя, когда `your_member_id` / `family_id` ещё пустые или в процессе reconcile.
- **`02_FamilyScreen`**: проверка кэша при загрузке, диалог очистки локального кэша ростера.
- **`FamilyRegistrationViewModel` / чат**: при записи `family_members_list` — сохранение снимка `family_id` для согласованности.

Эти части не рисуют прямоугольник на главной, но влияют на корректность списка участников и отсутствие «битого» состояния после регистрации.

---

## 8. Чеклист для проверки вручную

1. Новый пользователь: онбординг → `mainWithRegistration` → полный флоу → на главной появляется карточка, **`your_member_id`** не пустой после create.
2. Активный триал при `plan_level` free на сервере: на главной **бирюзовый** градиент, лимит **3**, не жёлтый и не «1 из 1» из-за старого порядка обновления trial/subscription.
3. Отмена триала / переход на free: **золотой** градиент, лимит **1**, уведомления триала отменены.
4. Смена тарифа с экрана тарифов: после закрытия экрана главная подтягивает статус (синк без троттлинга появления главной).

---

## 9. Основные файлы (индекс)

| Тема | Файлы |
|------|--------|
| Корень приложения, ветка регистрации | `ALADDINApp.swift` |
| UI регистрации поверх заглушки главной | `Screens/MainScreenWithRegistration.swift` |
| Бизнес-логика шагов и API create/add | `ViewModels/FamilyRegistrationViewModel.swift` |
| HTTP create/join + bootstrap JWT | `Core/Network/APIService.swift`, `Core/Config/AppConfig.swift` |
| Подписка, лимиты, epoch, trial order | `Core/Managers/SubscriptionManager.swift` |
| Карточка семьи, цвет, слоты, id для refresh | `Screens/01_MainScreen.swift` |
| После тарифов | `Screens/10_TariffsScreen.swift` |
| Локальное состояние семьи | `Core/Managers/FamilyLocalStore.swift` |

---

*Документ составлен по состоянию кодовой базы iOS-клиента ALADDIN. Контракты бэкенда уточняйте в репозитории сервера и OpenAPI.*
