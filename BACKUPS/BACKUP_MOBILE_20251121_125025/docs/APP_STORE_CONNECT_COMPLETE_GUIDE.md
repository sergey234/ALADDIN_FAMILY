# 📋 ПОЛНЫЙ ГАЙД: ЧТО РАЗМЕЩАТЬ В APP STORE CONNECT

**Дата:** 16 ноября 2025  
**Статус:** ✅ **ВСЯ ДОКУМЕНТАЦИЯ ГОТОВА**

---

## 🎯 ОБЗОР

Вся документация для публикации в App Store **ГОТОВА**! Ниже полный список того, что нужно будет разместить в App Store Connect после оплаты Apple Developer Program.

---

## 📊 СТАТИСТИКА ДОКУМЕНТАЦИИ

**Всего документов:** 8 основных документов  
**Статус:** ✅ Все готовы к использованию

---

## 📁 СПИСОК ВСЕХ ДОКУМЕНТОВ

### 1. ✅ Описание приложения
**Файл:** `docs/APP_STORE_DESCRIPTION.md`  
**Где размещать:** App Store Connect → App → App Information → Description

**Содержит:**
- ✅ Краткое описание (Subtitle) - 26 символов (RU), 28 символов (EN)
- ✅ Промо-текст (Promotional Text) - 169 символов (RU/EN)
- ✅ Полное описание (Description) - ~3,850 символов (RU/EN)

**Инструкция:** `docs/APP_STORE_DESCRIPTION_USAGE.md`

---

### 2. ✅ Ключевые слова
**Файл:** `docs/APP_STORE_KEYWORDS.md`  
**Где размещать:** App Store Connect → App → App Information → Keywords

**Содержит:**
- ✅ Ключевые слова для русского (99 символов)
- ✅ Ключевые слова для английского (99 символов)

**Рекомендуемый вариант:**
- RU: `безопасность, защита, семья, VPN, родительский контроль, AI, киберугрозы, мошенники, шифрование, приватность`
- EN: `security, protection, family, VPN, parental control, AI, cyber threats, scammers, encryption, privacy`

---

### 3. ✅ Review Notes (Заметки для ревьюера)
**Файл:** `docs/REVIEW_NOTES_TEMPLATE.md`  
**Где размещать:** App Store Connect → App → App Review Information → Notes

**Содержит:**
- ✅ Тестовый аккаунт (нужно создать)
- ✅ Описание функциональности
- ✅ Объяснение QR-оплаты
- ✅ Объяснение скидок за предоплату
- ✅ Пошаговые инструкции для ревьюера
- ✅ Контактная информация

**Статус:** ✅ Готов, нужно только создать тестовый аккаунт

---

### 4. ✅ App Privacy (Приватность)
**Файл:** `docs/APP_PRIVACY_DATA.md`  
**Где размещать:** App Store Connect → App → App Privacy

**Содержит:**
- ✅ Полный список собираемых данных (все "НЕТ" персональных данных)
- ✅ Цели использования данных
- ✅ Информация о передаче данных (НЕТ)
- ✅ Использование для отслеживания (НЕТ)

**Статус:** ✅ Все данные готовы, нужно только заполнить форму в App Store Connect

---

### 5. ✅ IAP (In-App Purchases)
**Файл:** `docs/IAP_PRODUCT_IDS_COMPLETE.md`  
**Где размещать:** App Store Connect → App → In-App Purchases

**Содержит:**
- ✅ 13 продуктов (1 Free + 12 Subscriptions)
- ✅ 3 Subscription Groups
- ✅ Product ID для всех тарифов и периодов
- ✅ Цены по регионам (US, RU, EU, GB)
- ✅ Описания для каждого продукта

**Статус:** ✅ Все данные готовы, нужно только зарегистрировать в App Store Connect

---

### 6. ✅ Категория и Age Rating
**Файл:** `docs/CATEGORY_AND_AGE_RATING.md`  
**Где размещать:** App Store Connect → App → App Information

**Содержит:**
- ✅ Рекомендуемые категории:
  - Primary: Productivity или Utilities
  - Secondary: Education или Lifestyle
- ✅ Age Rating: 4+ (нужно пройти анкету)

**Статус:** ✅ Рекомендации готовы, нужно выбрать в App Store Connect

---

### 7. ✅ Privacy Policy и Terms of Service (URL)
**Файл:** `docs/PUBLIC_URLS_INFO.md`  
**Где размещать:** App Store Connect → App → App Information → Privacy Policy URL / Terms of Service URL

**Содержит:**
- ✅ Информация о том, где разместить HTML файлы
- ✅ Требования к публичным URL

**HTML файлы:**
- `20_full_privacy_policy.html` - Privacy Policy
- `20_terms_of_service.html` - Terms of Service

**Статус:** ⚠️ Файлы готовы, нужно загрузить на сервер и получить публичные URL

---

### 8. ✅ Privacy Policy (Полный текст)
**Файл:** `docs/PRIVACY_POLICY_FULL_152FZ.md`  
**Где размещать:** В HTML файле на сервере

**Содержит:**
- ✅ Полная политика конфиденциальности (152-ФЗ)
- ✅ Политика для VPN
- ✅ Информация о шифровании

**Статус:** ✅ Готов, нужно разместить на сервере

---

## 📋 ПОЛНЫЙ ЧЕКЛИСТ ДЛЯ APP STORE CONNECT

### Раздел 1: App Information (Основная информация)

#### 1.1. Название приложения
- [ ] Название: "ALADDIN AI"
- [ ] Подзаголовок (Subtitle): `ALADDIN AI - защита семьи` (26 символов)
- [ ] Промо-текст: `🛡️ ALADDIN AI - ваш персональный агент безопасности!...` (169 символов)

**Источник:** `docs/APP_STORE_DESCRIPTION.md`

---

#### 1.2. Описание приложения
- [ ] Полное описание (RU): ~3,850 символов
- [ ] Полное описание (EN): ~3,850 символов

**Источник:** `docs/APP_STORE_DESCRIPTION.md`

---

#### 1.3. Ключевые слова
- [ ] Ключевые слова (RU): `безопасность, защита, семья, VPN...` (99 символов)
- [ ] Ключевые слова (EN): `security, protection, family, VPN...` (99 символов)

**Источник:** `docs/APP_STORE_KEYWORDS.md`

---

#### 1.4. Категория
- [ ] Primary Category: Productivity или Utilities
- [ ] Secondary Category: Education или Lifestyle

**Источник:** `docs/CATEGORY_AND_AGE_RATING.md`

---

#### 1.5. Age Rating
- [ ] Пройти анкету Age Rating
- [ ] Ожидаемый рейтинг: 4+

**Источник:** `docs/CATEGORY_AND_AGE_RATING.md`

---

#### 1.6. Privacy Policy URL
- [ ] Загрузить `20_full_privacy_policy.html` на сервер
- [ ] Получить публичный URL
- [ ] Указать URL в App Store Connect

**Источник:** `docs/PUBLIC_URLS_INFO.md`, `docs/PRIVACY_POLICY_FULL_152FZ.md`

---

#### 1.7. Terms of Service URL
- [ ] Загрузить `20_terms_of_service.html` на сервер
- [ ] Получить публичный URL
- [ ] Указать URL в App Store Connect

**Источник:** `docs/PUBLIC_URLS_INFO.md`

---

### Раздел 2: App Privacy (Приватность)

#### 2.1. Типы собираемых данных
- [ ] Заполнить форму App Privacy
- [ ] Указать, что персональные данные НЕ собираются
- [ ] Указать обезличенные данные (User ID, Device ID, Analytics)

**Источник:** `docs/APP_PRIVACY_DATA.md`

---

#### 2.2. Цели использования
- [ ] App Functionality
- [ ] Analytics
- [ ] НЕ используется для рекламы
- [ ] НЕ используется для отслеживания

**Источник:** `docs/APP_PRIVACY_DATA.md`

---

### Раздел 3: Pricing and Availability (Цены и доступность)

#### 3.1. Ценовая категория
- [ ] Выбрать: Free (бесплатно)
- [ ] Указать страны доступности

---

### Раздел 4: In-App Purchases (Внутриигровые покупки)

#### 4.1. Subscription Groups
- [ ] Создать `ALADDIN_PERSONAL_SUBSCRIPTIONS`
- [ ] Создать `ALADDIN_FAMILY_SUBSCRIPTIONS`
- [ ] Создать `ALADDIN_PREMIUM_SUBSCRIPTIONS`

**Источник:** `docs/IAP_PRODUCT_IDS_COMPLETE.md`

---

#### 4.2. Products - Personal (4 продукта)
- [ ] `family.aladdin.ios.subscription.personal.1m` (1 месяц)
- [ ] `family.aladdin.ios.subscription.personal.3m` (3 месяца, скидка 10%)
- [ ] `family.aladdin.ios.subscription.personal.6m` (6 месяцев, скидка 15%)
- [ ] `family.aladdin.ios.subscription.personal.12m` (12 месяцев, скидка 20%)

**Для каждого:**
- [ ] Установить цены по регионам
- [ ] Добавить описание (RU/EN)
- [ ] Настроить автоматическое продление

**Источник:** `docs/IAP_PRODUCT_IDS_COMPLETE.md`

---

#### 4.3. Products - Family (4 продукта)
- [ ] `family.aladdin.ios.subscription.family.1m`
- [ ] `family.aladdin.ios.subscription.family.3m`
- [ ] `family.aladdin.ios.subscription.family.6m`
- [ ] `family.aladdin.ios.subscription.family.12m`

**Источник:** `docs/IAP_PRODUCT_IDS_COMPLETE.md`

---

#### 4.4. Products - Premium (4 продукта)
- [ ] `family.aladdin.ios.subscription.premium.1m`
- [ ] `family.aladdin.ios.subscription.premium.3m`
- [ ] `family.aladdin.ios.subscription.premium.6m`
- [ ] `family.aladdin.ios.subscription.premium.12m`

**Источник:** `docs/IAP_PRODUCT_IDS_COMPLETE.md`

---

### Раздел 5: App Review Information (Информация для ревью)

#### 5.1. Review Notes
- [ ] Создать тестовый аккаунт
- [ ] Вставить текст Review Notes

**Источник:** `docs/REVIEW_NOTES_TEMPLATE.md`

---

#### 5.2. Контактная информация
- [ ] Email: sergey21-02-84@list.ru
- [ ] Телефон: +7 (927) 005-15-77

**Источник:** `docs/REVIEW_NOTES_TEMPLATE.md`

---

### Раздел 6: Version Information (Информация о версии)

#### 6.1. Скриншоты
- [ ] iPhone 6.7" (iPhone 14 Pro Max) - 7 экранов
- [ ] iPhone 6.5" (iPhone 11 Pro Max) - 7 экранов

**Экраны:**
1. Главный экран
2. VPN экран
3. Семейный экран
4. Профиль
5. Настройки
6. Тарифы (с выбором периода 12 месяцев)
7. QR оплата

**Статус:** ⚠️ Нужно сделать скриншоты

---

#### 6.2. Иконка приложения
- [ ] Проверить размер: 1024x1024
- [ ] Проверить формат: PNG без прозрачности
- [ ] Загрузить в App Store Connect

**Статус:** ✅ Иконка готова (нужно проверить текст "ALADDIN AI")

---

## 📊 ИТОГОВАЯ ТАБЛИЦА ГОТОВНОСТИ

| Раздел | Документ | Статус | Где размещать |
|--------|----------|--------|---------------|
| **Описание** | APP_STORE_DESCRIPTION.md | ✅ Готов | App Information → Description |
| **Ключевые слова** | APP_STORE_KEYWORDS.md | ✅ Готов | App Information → Keywords |
| **Review Notes** | REVIEW_NOTES_TEMPLATE.md | ✅ Готов | App Review Information → Notes |
| **App Privacy** | APP_PRIVACY_DATA.md | ✅ Готов | App Privacy |
| **IAP** | IAP_PRODUCT_IDS_COMPLETE.md | ✅ Готов | In-App Purchases |
| **Категория** | CATEGORY_AND_AGE_RATING.md | ✅ Готов | App Information → Category |
| **Privacy Policy URL** | PUBLIC_URLS_INFO.md | ⚠️ Нужен сервер | App Information → Privacy Policy URL |
| **Terms URL** | PUBLIC_URLS_INFO.md | ⚠️ Нужен сервер | App Information → Terms URL |
| **Скриншоты** | - | ⚠️ Нужно сделать | Version Information → Screenshots |
| **Иконка** | Assets.xcassets | ✅ Готов | Version Information → App Icon |

---

## ✅ ЧТО УЖЕ ГОТОВО (8/10)

1. ✅ Описание приложения (RU/EN)
2. ✅ Ключевые слова (RU/EN)
3. ✅ Review Notes (нужен тестовый аккаунт)
4. ✅ App Privacy данные
5. ✅ IAP Product ID и цены
6. ✅ Категория и Age Rating рекомендации
7. ✅ Privacy Policy текст
8. ✅ Terms of Service текст

---

## ⚠️ ЧТО НУЖНО СДЕЛАТЬ (2/10)

1. ⚠️ **Скриншоты** - нужно сделать 14 скриншотов (7 экранов × 2 размера)
2. ⚠️ **Публичные URL** - загрузить HTML файлы на сервер

---

## 🎯 ПОРЯДОК ДЕЙСТВИЙ

### Шаг 1: Подготовка (можно сделать сейчас)
1. ✅ Все тексты готовы
2. ⚠️ Сделать скриншоты (2-3 часа)
3. ⚠️ Загрузить HTML файлы на сервер (30 минут)

### Шаг 2: После оплаты Developer Program
1. Войти в App Store Connect
2. Создать новое приложение
3. Заполнить все разделы по чеклисту выше
4. Загрузить скриншоты
5. Загрузить иконку
6. Создать Archive и загрузить build

### Шаг 3: Отправка на ревью
1. Заполнить Review Notes
2. Выбрать build для ревью
3. Нажать "Submit for Review"

---

## 📁 СТРУКТУРА ДОКУМЕНТОВ

```
docs/
├── APP_STORE_DESCRIPTION.md          ✅ Описание приложения
├── APP_STORE_DESCRIPTION_USAGE.md    ✅ Инструкция по использованию
├── APP_STORE_KEYWORDS.md             ✅ Ключевые слова
├── REVIEW_NOTES_TEMPLATE.md          ✅ Заметки для ревьюера
├── APP_PRIVACY_DATA.md               ✅ Данные для App Privacy
├── IAP_PRODUCT_IDS_COMPLETE.md       ✅ IAP продукты
├── CATEGORY_AND_AGE_RATING.md        ✅ Категория и рейтинг
├── PUBLIC_URLS_INFO.md               ✅ Информация о URL
└── PRIVACY_POLICY_FULL_152FZ.md      ✅ Полная политика
```

---

## 🎉 ВЫВОД

**Вся документация для App Store Connect ГОТОВА!**

✅ **8 из 10 разделов** полностью готовы  
⚠️ **2 раздела** требуют действий (скриншоты и публичные URL)

После оплаты Apple Developer Program можно сразу приступать к заполнению App Store Connect - все тексты, данные и инструкции готовы!

---

**Дата создания:** 16 ноября 2025  
**Статус:** ✅ **ПОЛНЫЙ ГАЙД ГОТОВ**



