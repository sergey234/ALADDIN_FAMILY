# 📋 ПЛАН РЕАЛИЗАЦИИ: Умные уведомления о подписке

**Дата:** 14 ноября 2025  
**Статус:** 🚀 **В РАБОТЕ**  
**Время:** 2-3 часа

---

## 🎯 ЦЕЛЬ

Реализовать умные уведомления о приближающемся окончании подписки:
- ✅ За 3 дня до окончания
- ✅ За 1 день до окончания

---

## 📋 ЗАДАЧИ

### ✅ Backend (Python) - 70% работы

#### Задача 1.1: Добавить метод `check_expiring_subscriptions()` в `SubscriptionManager`

**Файл:** `/Users/sergejhlystov/ALADDIN_NEW/security/managers/subscription_manager.py`

**Что делать:**
1. Добавить метод `check_expiring_subscriptions()` который:
   - Проверяет все активные подписки
   - Вычисляет количество дней до окончания
   - Возвращает список подписок, заканчивающихся через 3 и 1 день

**Код:**
```python
async def check_expiring_subscriptions(self) -> List[Dict[str, Any]]:
    """
    Проверка подписок, заканчивающихся через 3 и 1 день
    
    Returns:
        Список подписок с информацией о днях до окончания
    """
    expiring_subscriptions = []
    now = datetime.now()
    
    for subscription in self.subscriptions.values():
        if subscription.status != SubscriptionStatus.ACTIVE:
            continue
            
        if not subscription.end_date:
            continue
            
        days_until_expiry = (subscription.end_date - now).days
        
        if days_until_expiry in [3, 1]:
            expiring_subscriptions.append({
                "subscription_id": subscription.subscription_id,
                "family_id": subscription.family_id,
                "tier": subscription.tier.value,
                "days_until_expiry": days_until_expiry,
                "end_date": subscription.end_date.isoformat()
            })
    
    return expiring_subscriptions
```

**Время:** 15 минут

---

#### Задача 1.2: Интегрировать с `FamilyNotificationManagerEnhanced`

**Файл:** `/Users/sergejhlystov/ALADDIN_NEW/security/managers/subscription_manager.py`

**Что делать:**
1. Добавить метод `send_subscription_renewal_notification()`
2. Импортировать `FamilyNotificationManagerEnhanced`
3. Отправлять уведомления через `family_notification_manager_enhanced`

**Код:**
```python
from security.family.family_notification_manager_enhanced import (
    family_notification_manager_enhanced,
    NotificationType,
    NotificationPriority,
    NotificationChannel
)

async def send_subscription_renewal_notification(
    self,
    family_id: str,
    days_until_expiry: int,
    tier: SubscriptionTier
) -> bool:
    """
    Отправка уведомления о приближающемся окончании подписки
    
    Args:
        family_id: ID семьи
        days_until_expiry: Дней до окончания (3 или 1)
        tier: Тарифный план
        
    Returns:
        True если уведомление отправлено успешно
    """
    try:
        # Определяем текст уведомления
        if days_until_expiry == 3:
            title = "Подписка заканчивается через 3 дня"
            message = f"Ваша подписка {tier.value} заканчивается через 3 дня. Продлите подписку, чтобы продолжить пользоваться сервисом."
        elif days_until_expiry == 1:
            title = "Подписка заканчивается завтра"
            message = f"Ваша подписка {tier.value} заканчивается завтра. Продлите подписку сейчас, чтобы не потерять доступ к функциям."
        else:
            return False
        
        # Отправляем уведомление
        await family_notification_manager_enhanced.send_family_alert(
            family_id=family_id,
            notification_type=NotificationType.SUBSCRIPTION_EXPIRING,
            priority=NotificationPriority.HIGH,
            title=title,
            message=message,
            channels=[NotificationChannel.IN_APP],
            metadata={
                "days_until_expiry": days_until_expiry,
                "subscription_tier": tier.value,
                "type": "subscription_renewal"
            },
            action_required=True,
            action_url="/tariffs"  # Ссылка на экран тарифов
        )
        
        logger.info(f"Отправлено уведомление о подписке для семьи {family_id}, дней до окончания: {days_until_expiry}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления о подписке: {e}")
        return False
```

**Время:** 20 минут

---

#### Задача 1.3: Создать метод для автоматической проверки и отправки

**Файл:** `/Users/sergejhlystov/ALADDIN_NEW/security/managers/subscription_manager.py`

**Что делать:**
1. Добавить метод `check_and_send_renewal_notifications()`
2. Объединить проверку и отправку уведомлений

**Код:**
```python
async def check_and_send_renewal_notifications(self) -> Dict[str, Any]:
    """
    Проверка подписок и отправка уведомлений о приближающемся окончании
    
    Returns:
        Статистика отправленных уведомлений
    """
    try:
        expiring_subscriptions = await self.check_expiring_subscriptions()
        
        sent_count = 0
        failed_count = 0
        
        for subscription_info in expiring_subscriptions:
            success = await self.send_subscription_renewal_notification(
                family_id=subscription_info["family_id"],
                days_until_expiry=subscription_info["days_until_expiry"],
                tier=SubscriptionTier(subscription_info["tier"])
            )
            
            if success:
                sent_count += 1
            else:
                failed_count += 1
        
        logger.info(f"Проверка подписок завершена: отправлено {sent_count}, ошибок {failed_count}")
        
        return {
            "success": True,
            "checked": len(expiring_subscriptions),
            "sent": sent_count,
            "failed": failed_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка проверки и отправки уведомлений: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

**Время:** 15 минут

---

#### Задача 1.4: Создать cron job / scheduled task (опционально)

**Файл:** Создать новый файл или добавить в существующий scheduler

**Что делать:**
1. Создать scheduled task для ежедневной проверки
2. Запускать в определенное время (например, 9:00 утра)

**Код:**
```python
# Пример для использования с APScheduler или аналогичным
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def daily_subscription_check():
    """Ежедневная проверка подписок и отправка уведомлений"""
    result = await subscription_manager.check_and_send_renewal_notifications()
    logger.info(f"Ежедневная проверка подписок: {result}")

# Настройка scheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(
    daily_subscription_check,
    trigger='cron',
    hour=9,
    minute=0
)
scheduler.start()
```

**Время:** 20 минут (опционально, можно сделать позже)

---

### ✅ iOS (Swift) - 30% работы

#### Задача 2.1: Добавить метод `scheduleRenewalNotifications()` в `NotificationManager`

**Файл:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/Core/Notifications/NotificationManager.swift`

**Что делать:**
1. Добавить метод `scheduleRenewalNotifications(subscriptionEndDate:)`
2. Планировать уведомления за 3 и 1 день
3. Использовать категорию `.subscription` (нужно добавить, если нет)

**Код:**
```swift
// Добавить в enum NotificationCategory (если нет)
enum NotificationCategory: String {
    case general = "general"
    case security = "security"
    case family = "family"
    case vpn = "vpn"
    case ai = "ai"
    case subscription = "subscription"  // НОВОЕ
}

/**
 * Планирование уведомлений о приближающемся окончании подписки
 */
func scheduleRenewalNotifications(subscriptionEndDate: Date) {
    // Отменяем предыдущие уведомления о подписке (если есть)
    cancelRenewalNotifications()
    
    // За 3 дня
    let threeDaysBefore = subscriptionEndDate.addingTimeInterval(-3 * 24 * 60 * 60)
    if threeDaysBefore > Date() {
        scheduleNotification(
            date: threeDaysBefore,
            title: "Подписка заканчивается через 3 дня",
            body: "Продлите подписку, чтобы продолжить пользоваться сервисом",
            category: .subscription,
            userInfo: [
                "type": "subscription_renewal",
                "days": 3,
                "subscription_end_date": ISO8601DateFormatter().string(from: subscriptionEndDate)
            ]
        )
    }
    
    // За 1 день
    let oneDayBefore = subscriptionEndDate.addingTimeInterval(-24 * 60 * 60)
    if oneDayBefore > Date() {
        scheduleNotification(
            date: oneDayBefore,
            title: "Подписка заканчивается завтра",
            body: "Продлите подписку сейчас, чтобы не потерять доступ к функциям",
            category: .subscription,
            userInfo: [
                "type": "subscription_renewal",
                "days": 1,
                "subscription_end_date": ISO8601DateFormatter().string(from: subscriptionEndDate)
            ]
        )
    }
    
    print("✅ Уведомления о подписке запланированы: за 3 дня и за 1 день")
}

/**
 * Отмена запланированных уведомлений о подписке
 */
func cancelRenewalNotifications() {
    notificationCenter.getPendingNotificationRequests { requests in
        let renewalIdentifiers = requests
            .filter { request in
                let userInfo = request.content.userInfo
                return userInfo["type"] as? String == "subscription_renewal"
            }
            .map { $0.identifier }
        
        if !renewalIdentifiers.isEmpty {
            self.notificationCenter.removePendingNotificationRequests(withIdentifiers: renewalIdentifiers)
            print("✅ Отменены предыдущие уведомления о подписке: \(renewalIdentifiers.count)")
        }
    }
}

/**
 * Планирование уведомления на конкретную дату
 */
private func scheduleNotification(
    date: Date,
    title: String,
    body: String,
    category: NotificationCategory,
    userInfo: [String: Any]
) {
    let content = UNMutableNotificationContent()
    content.title = title
    content.body = body
    content.sound = .default
    content.categoryIdentifier = category.rawValue
    content.userInfo = userInfo
    
    let trigger = UNCalendarNotificationTrigger(
        dateMatching: Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: date),
        repeats: false
    )
    
    let request = UNNotificationRequest(
        identifier: "subscription_renewal_\(Int(date.timeIntervalSince1970))",
        content: content,
        trigger: trigger
    )
    
    notificationCenter.add(request) { error in
        if let error = error {
            print("❌ Ошибка планирования уведомления: \(error)")
        } else {
            print("✅ Уведомление запланировано: \(title) на \(date)")
        }
    }
}
```

**Время:** 30 минут

---

#### Задача 2.2: Вызывать при покупке подписки

**Файл:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/ViewModels/TariffsViewModel.swift`

**Что делать:**
1. После успешной покупки получить `subscriptionEndDate`
2. Вызвать `NotificationManager.shared.scheduleRenewalNotifications()`

**Код:**
```swift
// В методе purchaseTariff после успешной покупки
if transaction != nil {
    isPurchaseSuccessful = true
    isLoading = false
    print("✅ IAP Purchase successful: \(tariff.title)")
    
    // Планируем уведомления о подписке
    if let endDate = calculateSubscriptionEndDate() {
        NotificationManager.shared.scheduleRenewalNotifications(subscriptionEndDate: endDate)
    }
    
    // ... остальной код
}

private func calculateSubscriptionEndDate() -> Date? {
    // Вычисляем дату окончания подписки (30 дней от текущей даты)
    return Calendar.current.date(byAdding: .day, value: 30, to: Date())
}
```

**Время:** 15 минут

---

#### Задача 2.3: Вызывать при продлении подписки

**Файл:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/ViewModels/TariffsViewModel.swift` или соответствующий ViewModel

**Что делать:**
1. После успешного продления обновить уведомления
2. Вызвать `scheduleRenewalNotifications()` с новой датой

**Время:** 10 минут

---

#### Задача 2.4: Вызывать при загрузке профиля пользователя

**Файл:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/ViewModels/ProfileViewModel.swift` или соответствующий файл

**Что делать:**
1. При загрузке профиля проверить `subscriptionEndDate`
2. Если есть активная подписка, запланировать уведомления

**Код:**
```swift
// При загрузке профиля
func loadProfile() {
    // ... загрузка профиля
    
    if let profile = userProfile,
       let endDateString = profile.subscriptionEndDate,
       let endDate = ISO8601DateFormatter().date(from: endDateString),
       endDate > Date() {
        // Есть активная подписка, планируем уведомления
        NotificationManager.shared.scheduleRenewalNotifications(subscriptionEndDate: endDate)
    }
}
```

**Время:** 15 минут

---

## 📊 ИТОГОВАЯ ОЦЕНКА ВРЕМЕНИ

| Задача | Время |
|--------|-------|
| Backend: check_expiring_subscriptions() | 15 мин |
| Backend: Интеграция с FamilyNotificationManager | 20 мин |
| Backend: check_and_send_renewal_notifications() | 15 мин |
| Backend: Cron job (опционально) | 20 мин |
| iOS: scheduleRenewalNotifications() | 30 мин |
| iOS: Вызов при покупке | 15 мин |
| iOS: Вызов при продлении | 10 мин |
| iOS: Вызов при загрузке профиля | 15 мин |
| **ИТОГО** | **~2.5 часа** |

---

## ✅ КРИТЕРИИ ЗАВЕРШЕНИЯ

- [ ] Backend: Метод `check_expiring_subscriptions()` реализован и протестирован
- [ ] Backend: Интеграция с `FamilyNotificationManagerEnhanced` работает
- [ ] Backend: Метод `check_and_send_renewal_notifications()` работает
- [ ] iOS: Метод `scheduleRenewalNotifications()` реализован
- [ ] iOS: Уведомления планируются при покупке подписки
- [ ] iOS: Уведомления планируются при продлении подписки
- [ ] iOS: Уведомления планируются при загрузке профиля
- [ ] Тестирование: Уведомления приходят за 3 и 1 день до окончания

---

## 🚀 НАЧИНАЕМ РЕАЛИЗАЦИЮ!

**Порядок выполнения:**
1. Backend: Задача 1.1 (check_expiring_subscriptions)
2. Backend: Задача 1.2 (интеграция)
3. Backend: Задача 1.3 (объединенный метод)
4. iOS: Задача 2.1 (scheduleRenewalNotifications)
5. iOS: Задачи 2.2, 2.3, 2.4 (вызовы метода)

---

**Дата создания:** 14 ноября 2025  
**Статус:** 🚀 **ГОТОВ К РЕАЛИЗАЦИИ**



