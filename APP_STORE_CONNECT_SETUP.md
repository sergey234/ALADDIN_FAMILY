# 🚀 App Store Connect Test Accounts Setup
## Для тестирования платежей ALADDIN

---

## 🎯 ЦЕЛЬ
Создать тестовые аккаунты App Store Connect для тестирования in-app покупок в sandbox окружении.

---

## 📋 НЕОБХОДИМЫЕ ШАГИ

### 1. ДОСТУП К APP STORE CONNECT

**Требуется:**
- Apple Developer Program аккаунт ($99/год)
- Admin или App Manager роль в App Store Connect
- Доступ к приложению ALADDIN

**URL:** https://appstoreconnect.apple.com/

---

### 2. СОЗДАНИЕ ТЕСТОВЫХ АККАУНТОВ

#### **В App Store Connect:**

1. **Перейдите в раздел "Users and Access"**
   - https://appstoreconnect.apple.com/access/users

2. **Выберите вкладку "Sandbox"**
   - Это специальный раздел для тестовых аккаунтов

3. **Нажмите "+" для создания тестового аккаунта**

#### **Создайте следующие аккаунты:**

##### **Тестовый аккаунт 1: Basic User**
```
First Name: Test
Last Name: User
Email: testuser_aladdin@icloud.com
Password: TestPass123!
Confirm Password: TestPass123!
Secret Question: What is your favorite color?
Secret Answer: Blue
Date of Birth: 01/01/1990
```

##### **Тестовый аккаунт 2: Premium User**
```
First Name: Premium
Last Name: Tester
Email: premiumtester_aladdin@icloud.com
Password: PremiumTest123!
Confirm Password: PremiumTest123!
Secret Question: What is your pet's name?
Secret Answer: Max
Date of Birth: 15/05/1985
```

##### **Тестовый аккаунт 3: Family Plan**
```
First Name: Family
Last Name: Account
Email: familyaccount_aladdin@icloud.com
Password: FamilyTest123!
Confirm Password: FamilyTest123!
Secret Question: What city were you born in?
Secret Answer: Moscow
Date of Birth: 20/10/1992
```

---

### 3. НАСТРОЙКА ПРОДУКТОВ ПОДПИСКИ

#### **Проверьте существующие продукты:**

1. **Перейдите в "My Apps" → ALADDIN**
2. **Выберите вкладку "In-App Purchases"**
3. **Убедитесь, что созданы продукты:**

##### **Требуемые продукты подписки:**

| ID | Название | Тип | Цена | Период |
|----|----------|-----|------|--------|
| `aladdin_trial_14` | ALADDIN Trial | Free Trial | Free (14 дней) | 1 месяц |
| `aladdin_personal_monthly` | ALADDIN Personal Monthly | Paid | $4.99 | 1 месяц |
| `aladdin_family_monthly` | ALADDIN Family Monthly | Paid | $9.99 | 1 месяц |
| `aladdin_premium_monthly` | ALADDIN Premium Monthly | Paid | $14.99 | 1 месяц |

#### **Проверка настроек продуктов:**

Для каждого продукта проверьте:
- ✅ **Product ID** соответствует таблице выше
- ✅ **Reference Name** понятное название
- ✅ **Type** - Subscription
- ✅ **Subscription Group** - ALADDIN_SUBSCRIPTIONS
- ✅ **Subscription Duration** - 1 Month
- ✅ **Price** - соответствует таблице
- ✅ **Status** - Ready to Submit

---

### 4. ТЕСТИРОВАНИЕ НАСТРОЕК

#### **Проверка в Xcode:**

1. **Откройте проект ALADDIN в Xcode**
2. **Перейдите в Signing & Capabilities**
3. **Убедитесь что In-App Purchase capability включена**

#### **Тестовые покупки:**

```swift
// В StoreManager добавить тестовый режим
#if DEBUG
    // Использовать sandbox environment
    let payment = SKMutablePayment(product: product)
    payment.simulatesAskToBuyInSandbox = true
    SKPaymentQueue.default().add(payment)
#endif
```

---

### 5. ДОКУМЕНТАЦИЯ ДЛЯ КОМАНДЫ

#### **Файл: TEST_ACCOUNTS.md**
Создайте файл с информацией о тестовых аккаунтах:

```
# ALADDIN Test Accounts

## Sandbox Test Accounts

### Basic User
- Email: testuser_aladdin@icloud.com
- Password: TestPass123!
- Purpose: Basic subscription testing

### Premium User
- Email: premiumtester_aladdin@icloud.com
- Password: PremiumTest123!
- Purpose: Premium features testing

### Family Account
- Email: familyaccount_aladdin@icloud.com
- Password: FamilyTest123!
- Purpose: Family plan testing

## Testing Guidelines

1. Use sandbox environment for all tests
2. Test all subscription levels
3. Verify receipt validation
4. Test restore purchases functionality
5. Test subscription cancellation/refund flows
```

---

### 6. ПРОБЛЕМЫ И РЕШЕНИЯ

#### **Проблема: "Sandbox account not recognized"**
**Решение:**
1. Убедитесь, что аккаунт создан в Sandbox разделе
2. Используйте @icloud.com email
3. Подождите 24 часа после создания

#### **Проблема: "Product not available"**
**Решение:**
1. Проверьте Product ID в коде
2. Убедитесь, что продукт в статусе "Ready to Submit"
3. Проверьте Subscription Group

#### **Проблема: "Payment failed"**
**Решение:**
1. Используйте тестовые кредитные карты
2. Проверьте настройки региона
3. Убедитесь, что приложение в Development mode

---

## ✅ ПОСЛЕ НАСТРОЙКИ

После создания аккаунтов:
1. **Протестируйте** покупку каждого уровня подписки
2. **Проверьте** валидацию receipts
3. **Убедитесь** в корректной активации функций
4. **Задокументируйте** процесс для команды

---

## 📞 КОНТАКТЫ

**App Store Connect Support:**
- https://developer.apple.com/support/app-store-connect/
- Phone: 1-800-633-2152

**Техническая поддержка ALADDIN:**
- Создайте issue в репозитории
- Отправьте логи с ошибками