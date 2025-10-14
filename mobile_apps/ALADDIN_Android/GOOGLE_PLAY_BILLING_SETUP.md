# 💰 Google Play Billing Setup

## 📋 Настройка продуктов в Google Play Console

### ✅ ШАГ 1: Создать продукты в Google Play Console

1. Перейдите: https://play.google.com/console
2. Выберите ваше приложение
3. **Monetization → Subscriptions**
4. Нажмите **Create subscription**

---

### ✅ ШАГ 2: Создать 4 подписки

#### 1️⃣ БАЗОВЫЙ ТАРИФ (FREE)

- **Product ID**: `family_aladdin_android_subscription_basic`
- **Name**: ALADDIN Базовая подписка
- **Description**: 1 устройство, базовая защита, ограниченная аналитика
- **Billing period**: 1 Month
- **Price**: **₽0** (Free)
- **Free trial**: 30 days

---

#### 2️⃣ ИНДИВИДУАЛЬНЫЙ ТАРИФ

- **Product ID**: `family_aladdin_android_subscription_individual`
- **Name**: ALADDIN Индивидуальная подписка
- **Description**: 1 устройство, полная защита, расширенная аналитика, AI помощник
- **Billing period**: 1 Month
- **Price**: **₽199/месяц**
- **Free trial**: 7 days

---

#### 3️⃣ СЕМЕЙНЫЙ ТАРИФ (РЕКОМЕНДУЕТСЯ) ⭐

- **Product ID**: `family_aladdin_android_subscription_family`
- **Name**: ALADDIN Семейная подписка
- **Description**: До 5 устройств, полная защита, AI помощник, родительский контроль
- **Billing period**: 1 Month
- **Price**: **₽499/месяц**
- **Free trial**: 14 days
- **Base plan**: Recommended ⭐

---

#### 4️⃣ ПРЕМИУМ ТАРИФ

- **Product ID**: `family_aladdin_android_subscription_premium`
- **Name**: ALADDIN Премиум подписка
- **Description**: До 10 устройств, все функции, приоритетная поддержка
- **Billing period**: 1 Month
- **Price**: **₽999/месяц**
- **Free trial**: 14 days

---

### ✅ ШАГ 3: Добавить зависимости в build.gradle.kts

В `app/build.gradle.kts` добавьте:

```kotlin
dependencies {
    // Google Play Billing
    implementation("com.android.billingclient:billing-ktx:6.1.0")
    
    // Coroutines (если ещё нет)
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}
```

**Sync Project with Gradle Files!**

---

### ✅ ШАГ 4: Настроить AndroidManifest.xml

Добавьте permission (если ещё нет):

```xml
<uses-permission android:name="com.android.vending.BILLING" />
```

---

## 🔧 Интеграция в код (УЖЕ ГОТОВА!)

✅ **BillingManager.kt** - управление покупками  
✅ **TariffsViewModel.kt** - интеграция с UI (нужно обновить)  
✅ **TariffsScreen.kt** - отображение тарифов  

---

## 🧪 Тестирование

### Локальное тестирование:

1. В Google Play Console создайте **License testers**
2. **Setup → License testing**
3. Добавьте ваш Google аккаунт
4. Выберите: **License Test Response: RESPOND_NORMALLY**
5. Покупки будут работать БЕЗ оплаты! ✅

### Тестирование в Internal Testing:

1. Создайте **Internal testing track**
2. Загрузите APK/AAB
3. Добавьте тестеров
4. Они смогут покупать подписки (будут отменены автоматически через 5 минут)

---

## 📊 Метрики покупок

BillingManager автоматически отслеживает:
- ✅ Какие продукты куплены
- ✅ Активные подписки
- ✅ Статус подписки (active/expired/cancelled)
- ✅ Восстановление покупок
- ✅ Pending purchases

**Готово к production!** 🚀

---

## ⚠️ ВАЖНО!

**Перед релизом в Google Play:**

1. ✅ Создайте все 4 подписки в Console
2. ✅ Настройте цены для всех стран
3. ✅ Добавьте описания на русском и английском
4. ✅ Настройте Grace period (3 дня)
5. ✅ Настройте Account hold (30 дней)
6. ✅ Включите восстановление подписки
7. ✅ Протестируйте на Internal track

**Без этого покупки не будут работать!**



