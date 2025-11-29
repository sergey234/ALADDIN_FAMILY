# 📋 СЛЕДУЮЩИЕ ШАГИ - ЧЕКЛИСТ

**Дата:** 15 ноября 2025  
**Статус:** 🔄 **В ПРОЦЕССЕ**

---

## ✅ ВЫПОЛНЕНО

- [x] Release конфигурация настроена
- [x] Версия установлена (1.0.0, Build 1)
- [x] Все debug print() обернуты в #if DEBUG
- [x] Mock API отключен в Release
- [x] Документы подготовлены

---

## 🔄 ТЕКУЩАЯ ЗАДАЧА: Code Signing

### Шаг 1: Проверить Code Signing в Xcode ⏳

**Инструкции:** `docs/CODE_SIGNING_INSTRUCTIONS.md`

**Что нужно сделать:**
1. Открыть проект в Xcode
2. Project → Target → General
   - [ ] Bundle Identifier: `family.aladdin.ios`
   - [ ] Version: `1.0.0`
   - [ ] Build: `1`
3. Project → Target → Signing & Capabilities
   - [ ] Team: выбрать вашу команду
   - [ ] Signing Certificate: валидный
   - [ ] Provisioning Profile: для App Store Distribution
   - [ ] "Automatically manage signing" включено
4. Проверить Capabilities:
   - [ ] Push Notifications (если используется)
   - [ ] VPN / Network Extensions (если используется)
   - [ ] Keychain Sharing (если используется)

**После проверки:**
- [ ] Отметить задачу `release_signing` как completed
- [ ] Перейти к созданию Archive

---

## ⏭️ СЛЕДУЮЩИЕ ЗАДАЧИ

### Шаг 2: Создать Archive ⏳

**В Xcode:**
1. Выбрать схему: `ALADDIN`
2. Выбрать устройство: `Any iOS Device (arm64)` (НЕ симулятор!)
3. Product → Scheme → Edit Scheme...
   - [ ] Run → Build Configuration: `Release`
   - [ ] Archive → Build Configuration: `Release`
4. Product → Archive
5. Дождаться завершения
6. Проверить в Organizer:
   - [ ] Archive создан
   - [ ] Версия: 1.0.0
   - [ ] Build: 1

**После создания:**
- [ ] Отметить задачу `release_archive` как completed
- [ ] Перейти к Upload

---

### Шаг 3: Upload в App Store Connect ⏳

**В Organizer:**
1. Выбрать созданный Archive
2. Нажать "Validate App"
   - [ ] Выбрать метод: "Automatically manage signing"
   - [ ] Дождаться валидации
   - [ ] Проверить, что нет ошибок
3. Нажать "Distribute App"
   - [ ] Выбрать: "App Store Connect"
   - [ ] Выбрать: "Upload"
   - [ ] Следовать инструкциям
4. Проверить в App Store Connect:
   - [ ] Build появился в TestFlight или App Store
   - [ ] Статус: "Processing" или "Ready to Submit"

**После Upload:**
- [ ] Отметить задачу `release_upload` как completed
- [ ] Перейти к Review Notes

---

### Шаг 4: Подготовить Review Notes ⏳

**Документ:** `docs/REVIEW_NOTES_TEMPLATE.md`

**Что нужно сделать:**
1. Создать тестовый аккаунт:
   - [ ] Email: `review@aladdin.family` (или ваш)
   - [ ] Password: `ReviewTest2025!` (или ваш)
2. Заполнить Review Notes по шаблону:
   - [ ] Тестовый аккаунт
   - [ ] Описание функциональности
   - [ ] Объяснение QR-оплаты
   - [ ] Пошаговые инструкции для ревьюера
3. Загрузить в App Store Connect:
   - [ ] App Store Connect → App → App Review Information
   - [ ] Вставить текст Review Notes
   - [ ] Сохранить

**После подготовки:**
- [ ] Отметить задачи `review_account`, `review_notes`, `review_upload` как completed
- [ ] Перейти к App Privacy

---

### Шаг 5: Заполнить App Privacy ⏳

**Документ:** `docs/APP_PRIVACY_DATA.md`

**Что нужно сделать:**
1. Зайти в App Store Connect → App → App Privacy
2. Заполнить форму по данным из документа:
   - [ ] Типы собираемых данных (все "НЕТ")
   - [ ] Цели использования данных
   - [ ] Информация о передаче данных
3. Сохранить

**После заполнения:**
- [ ] Отметить задачи `privacy_prepare`, `privacy_fill`, `privacy_check` как completed
- [ ] Перейти к Public URLs

---

### Шаг 6: Подготовить Public URLs ⏳

**Документ:** `docs/PUBLIC_URLS_INFO.md`

**Что нужно сделать:**
1. Загрузить HTML файлы на сервер:
   - [ ] `20_full_privacy_policy.html` → публичный URL
   - [ ] `20_terms_of_service.html` → публичный URL
2. Проверить доступность URL:
   - [ ] Privacy Policy URL открывается
   - [ ] Terms of Service URL открывается
3. Указать URL в App Store Connect:
   - [ ] App Store Connect → App → App Information
   - [ ] Privacy Policy URL: указать URL
   - [ ] Terms of Service URL: указать URL
   - [ ] Сохранить

**После подготовки:**
- [ ] Отметить задачи `url_upload`, `url_connect` как completed
- [ ] Перейти к IAP Registration

---

### Шаг 7: Зарегистрировать IAP ⏳

**Документ:** `docs/IAP_REGISTRATION_DATA.md`

**Что нужно сделать:**
1. Создать Subscription Group в App Store Connect:
   - [ ] App Store Connect → App → In-App Purchases
   - [ ] Создать Subscription Group: "ALADDIN Subscriptions"
2. Зарегистрировать тарифы:
   - [ ] Free: Product ID `aladdin.free`
   - [ ] Personal: Product ID `aladdin.personal.monthly`
   - [ ] Family: Product ID `aladdin.family.monthly`
3. Установить цены по регионам
4. Протестировать в Sandbox:
   - [ ] Создать Sandbox тестовый аккаунт
   - [ ] Протестировать покупку каждого тарифа

**После регистрации:**
- [ ] Отметить задачи `iap_prepare`, `iap_register`, `iap_test` как completed
- [ ] Перейти к Category and Age Rating

---

### Шаг 8: Выбрать Category and Age Rating ⏳

**Документ:** `docs/CATEGORY_AND_AGE_RATING.md`

**Что нужно сделать:**
1. Выбрать категории в App Store Connect:
   - [ ] Primary Category: Productivity или Utilities
   - [ ] Secondary Category: Education или Lifestyle
2. Пройти анкету Age Rating:
   - [ ] Ответить на все вопросы
   - [ ] Рейтинг должен быть: 4+
3. Сохранить

**После выбора:**
- [ ] Отметить задачи `category_select`, `category_rating` как completed
- [ ] Все готово к отправке на ревью!

---

## 🎯 ИТОГОВЫЙ ЧЕКЛИСТ ПЕРЕД ОТПРАВКОЙ

- [ ] Code Signing проверен
- [ ] Archive создан
- [ ] Upload выполнен
- [ ] Review Notes загружены
- [ ] App Privacy заполнена
- [ ] Public URLs указаны
- [ ] IAP зарегистрированы
- [ ] Category и Age Rating выбраны
- [ ] Скриншоты загружены (если готовы)
- [ ] Описание приложения заполнено
- [ ] Ключевые слова указаны

---

**Дата создания:** 15 ноября 2025  
**Текущий шаг:** Code Signing (в Xcode)




