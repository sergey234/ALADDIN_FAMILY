# 📚 API ДОКУМЕНТАЦИЯ - ALADDIN iOS

**Версия:** 2.0.0  
**Дата:** 2026-02-11  
**Базовый URL:** `https://aladdin-ai.ru/api`  
**Обновлено:** Добавлено 96 новых endpoint'ов для синхронизации данных

---

## 📋 ОГЛАВЛЕНИЕ

1. [Общая информация](#общая-информация)
2. [Аутентификация](#аутентификация)
3. [VPN API](#vpn-api)
4. [Family API](#family-api)
5. [Analytics API](#analytics-api)
6. [AI Assistant API](#ai-assistant-api)
7. [User API](#user-api)
8. [Notifications API](#notifications-api)
9. [Subscription API](#subscription-api)
10. [Protection API](#protection-api)
11. [Parental Control API](#parental-control-api)
12. [Device API](#device-api)
13. [IoT API](#iot-api)
14. [Referral API](#referral-api)
15. [Payment API](#payment-api)
16. [Gamification API](#gamification-api)
17. [Parental Control Sync API](#parental-control-sync-api)
18. [User Profile Sync API](#user-profile-sync-api)
19. [Subscription Sync API](#subscription-sync-api)
20. [App Settings Sync API](#app-settings-sync-api)
21. [Location & Geofences Sync API](#location--geofences-sync-api)
22. [Offline Chat Sync API](#offline-chat-sync-api)
23. [Offline Storage Sync API](#offline-storage-sync-api)
24. [Crash Detection Sync API](#crash-detection-sync-api)
25. [Elderly Interface Sync API](#elderly-interface-sync-api)
26. [Коды ошибок](#коды-ошибок)

---

## 🔐 ОБЩАЯ ИНФОРМАЦИЯ

### Базовый URL
```
https://aladdin-ai.ru/api
```

### Формат запросов
- **Content-Type:** `application/json`
- **Accept:** `application/json`
- **Кодировка:** UTF-8

### Аутентификация
Большинство endpoints требуют JWT токен в заголовке:
```
Authorization: Bearer {access_token}
```

### Формат ответов
Все ответы возвращаются в формате JSON:

**Успешный ответ:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Операция выполнена успешно"
}
```

**Ошибка:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Описание ошибки"
  }
}
```

---

## 🔑 АУТЕНТИФИКАЦИЯ

### POST /auth/login
Авторизация пользователя.

**Запрос:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "refresh_token_here",
    "expires_in": 3600,
    "token_type": "Bearer"
  }
}
```

### POST /auth/logout
Выход из системы.

**Запрос:**
```json
{}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

### POST /auth/refresh
Обновление access token.

**Запрос:**
```json
{
  "refresh_token": "refresh_token_here"
}
```

**Ответ:**
```json
{
  "access_token": "new_access_token",
  "refresh_token": "new_refresh_token",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

---

## 🌐 VPN API

### GET /vpn/status
Получить статус VPN подключения.

**Ответ:**
```json
{
  "isConnected": true,
  "serverLocation": "Москва, Россия",
  "ipAddress": "185.123.45.67",
  "ping": 23,
  "downloadSpeed": "125.5 Mbps",
  "uploadSpeed": "98.3 Mbps",
  "sessionTime": "02:34:15",
  "threatsBlocked": 47
}
```

### POST /vpn/connect
Подключиться к VPN.

**Запрос:**
```json
{}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

### POST /vpn/disconnect
Отключиться от VPN.

**Запрос:**
```json
{}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

### GET /vpn/servers
Получить список VPN серверов.

**Ответ:**
```json
[
  {
    "id": "server_1",
    "country": "Россия",
    "city": "Москва",
    "flag": "🇷🇺",
    "ping": 12,
    "load": 45,
    "status": "optimal"
  },
  {
    "id": "server_2",
    "country": "Германия",
    "city": "Франкфурт",
    "flag": "🇩🇪",
    "ping": 34,
    "load": 67,
    "status": "loaded"
  }
]
```

### GET /vpn/config
Получить конфигурацию VPN.

**Ответ:**
```json
{
  "encryption": {
    "algorithm": "AES-256-GCM",
    "keySize": 256,
    "recommendedLevel": "maximum"
  },
  "servers": [ ... ],
  "features": {
    "killSwitch": true,
    "autoConnect": false,
    "dnsLeakProtection": true,
    "splitTunneling": false
  },
  "settings": {
    "autoDisconnectEnabled": true,
    "autoDisconnectTimeout": 1800,
    "batteryOptimizationEnabled": true
  }
}
```

### POST /vpn/stats
Отправить статистику VPN.

**Запрос:**
```json
{
  "bytesIn": 1024000,
  "bytesOut": 512000,
  "packetsIn": 1500,
  "packetsOut": 1200,
  "today": 2048000,
  "thisMonth": 104857600,
  "sessionTime": 3600,
  "threatsBlocked": 12
}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

---

## 👨‍👩‍👧‍👦 FAMILY API

### GET /family/members
Получить список участников семьи.

**Ответ:**
```json
[
  {
    "id": "member_1",
    "name": "Иван Иванов",
    "role": "parent",
    "avatar": "👨‍💼",
    "status": "protected",
    "threatsBlocked": 23,
    "lastActive": "Сейчас",
    "devices": 2
  },
  {
    "id": "member_2",
    "name": "Мария Иванова",
    "role": "child",
    "avatar": "👧",
    "status": "protected",
    "threatsBlocked": 5,
    "lastActive": "5 минут назад",
    "devices": 1
  }
]
```

### POST /family/add
Добавить участника семьи.

**Запрос:**
```json
{
  "name": "Петр Иванов",
  "role": "teenager"
}
```

**Ответ:**
```json
{
  "id": "member_3",
  "name": "Петр Иванов",
  "role": "teenager",
  "avatar": "🧑",
  "status": "protected",
  "threatsBlocked": 0,
  "lastActive": "Сейчас",
  "devices": 0
}
```

### GET /family/stats
Получить статистику семьи.

**Ответ:**
```json
{
  "totalMembers": 4,
  "totalDevices": 6,
  "totalThreats": 45,
  "protectionLevel": 95,
  "familyStatus": "protected",
  "familyStatusMessage": "Вся семья под защитой"
}
```

---

## 💬 FAMILY CHAT API

### GET /family/chat/messages
Получить сообщения семейного чата.

**Ответ:**
```json
[
  {
    "id": "msg_1",
    "senderId": "member_1",
    "senderName": "Иван Иванов",
    "message": "Привет, как дела?",
    "timestamp": "2025-11-25T10:30:00Z"
  }
]
```

### POST /family/chat/send
Отправить сообщение в семейный чат.

**Запрос:**
```json
{
  "message": "Всем привет!",
  "familyId": "family_123"
}
```

**Ответ:**
```json
{
  "id": "msg_2",
  "senderId": "member_1",
  "senderName": "Иван Иванов",
  "message": "Всем привет!",
  "timestamp": "2025-11-25T10:35:00Z"
}
```

---

## 📊 ANALYTICS API

### GET /analytics?period={period}
Получить аналитику за период.

**Параметры:**
- `period`: `day`, `week`, `month`

**Ответ:**
```json
{
  "period": "week",
  "threatsDetected": 127,
  "threatsBlocked": 125,
  "itemsScanned": 15420,
  "protectionLevel": 98,
  "topThreats": [
    {
      "id": "threat_1",
      "name": "Фишинговые сайты",
      "count": 45,
      "icon": "🎣",
      "severity": "high"
    }
  ],
  "threatsByType": [
    {
      "type": "web",
      "count": 80,
      "percentage": 63.0
    },
    {
      "type": "app",
      "count": 30,
      "percentage": 23.6
    }
  ]
}
```

### GET /analytics/top-threats
Получить топ угроз.

**Ответ:**
```json
[
  {
    "id": "threat_1",
    "name": "Фишинговые сайты",
    "count": 45,
    "icon": "🎣",
    "severity": "high"
  }
]
```

---

## 🤖 AI ASSISTANT API

### POST /ai/message
Отправить сообщение AI ассистенту.

**Запрос:**
```json
{
  "message": "Как защитить ребенка от мошенников?",
  "userId": "user_123",
  "timestamp": "2025-11-25T10:40:00Z"
}
```

**Ответ:**
```json
{
  "message": "Для защиты ребенка от мошенников рекомендую...",
  "timestamp": "2025-11-25T10:40:05Z",
  "suggestions": [
    "Настроить родительский контроль",
    "Включить защиту от фишинга"
  ]
}
```

---

## 👤 USER API

### GET /user/profile
Получить профиль пользователя.

**Ответ:**
```json
{
  "id": "user_123",
  "name": "Иван Иванов",
  "email": "ivan@example.com",
  "phone": "+79001234567",
  "registrationDate": "2025-01-15",
  "subscriptionType": "family",
  "subscriptionEndDate": "2026-01-15",
  "threatsBlocked": 234,
  "familyMembers": 4,
  "devices": 3
}
```

### POST /user/update
Обновить профиль пользователя.

**Запрос:**
```json
{
  "name": "Иван Петров",
  "email": "ivan.new@example.com",
  "phone": "+79001234568"
}
```

**Ответ:**
```json
{
  "id": "user_123",
  "name": "Иван Петров",
  "email": "ivan.new@example.com",
  "phone": "+79001234568",
  ...
}
```

### DELETE /user/delete
Удалить аккаунт.

**Запрос:**
```json
{
  "confirmationCode": "DELETE123"
}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

---

## 🔔 NOTIFICATIONS API

### GET /notifications
Получить список уведомлений.

**Ответ:**
```json
[
  {
    "id": "notif_1",
    "title": "Обнаружена угроза",
    "message": "Заблокирован фишинговый сайт",
    "type": "threat",
    "timestamp": "2025-11-25T10:00:00Z",
    "isRead": false
  }
]
```

### POST /notifications/read
Отметить уведомление как прочитанное.

**Запрос:**
```json
{
  "notificationId": "notif_1"
}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

---

## 💳 SUBSCRIPTION API

### GET /subscription/tariffs
Получить список тарифов.

**Ответ:**
```json
[
  {
    "id": "free",
    "name": "Бесплатный",
    "price": 0,
    "period": "month",
    "features": [ ... ]
  },
  {
    "id": "personal",
    "name": "Личный",
    "price": 299,
    "period": "month",
    "features": [ ... ]
  }
]
```

### POST /subscription/subscribe
Подписаться на тариф.

**Запрос:**
```json
{
  "tariffId": "family"
}
```

**Ответ:**
```json
{
  "status": "active",
  "tariffId": "family",
  "startDate": "2025-11-25",
  "endDate": "2026-11-25"
}
```

### POST /subscription/activate
Активировать подписку по коду (старый метод, для обратной совместимости).

**Запрос:**
```json
{
  "code": "ABC123XYZ"
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "status": "active",
    "tariffId": "family",
    "startDate": "2025-11-25",
    "endDate": "2026-11-25"
  }
}
```

**Примечание:** Рекомендуется использовать новые методы `/subscription/activation/verify` и `/subscription/activation/activate` для активации кодов.

### POST /subscription/activation/verify
Проверить код активации.

**Запрос:**
```json
{
  "code": "ABC123XYZ",
  "familyId": "family_123",
  "deviceId": "device_456"
}
```

**Ответ:**
```json
{
  "valid": true,
  "tariffId": "family",
  "tariffName": "Семейный",
  "duration": 12,
  "price": 2990
}
```

### POST /subscription/activation/activate
Активировать код.

**Запрос:**
```json
{
  "code": "ABC123XYZ",
  "familyId": "family_123",
  "deviceId": "device_456"
}
```

**Ответ:**
```json
{
  "success": true,
  "subscription": {
    "status": "active",
    "tariffId": "family",
    "startDate": "2025-11-25",
    "endDate": "2026-11-25"
  }
}
```

---

## 🛡️ PROTECTION API

### GET /protection/settings
Получить настройки защиты.

**Ответ:**
```json
{
  "categories": [
    {
      "id": "phishing",
      "name": "Фишинг",
      "enabled": true,
      "level": "high"
    }
  ],
  "globalLevel": 95
}
```

### POST /protection/settings
Обновить настройки защиты.

**Запрос:**
```json
{
  "categories": [
    {
      "id": "phishing",
      "enabled": true,
      "level": "high"
    }
  ],
  "globalLevel": 95
}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

### GET /protection/status
Получить статус защиты.

**Ответ:**
```json
{
  "isProtected": true,
  "level": 95,
  "threatsBlocked": 234,
  "lastScan": "2025-11-25T10:00:00Z"
}
```

### GET /protection/threat-scenarios
Получить сценарии угроз.

**Ответ:**
```json
[
  {
    "id": "scenario_1",
    "name": "Фишинговая атака",
    "description": "...",
    "severity": "high"
  }
]
```

### POST /protection/enable
Включить категорию защиты.

**Запрос:**
```json
{
  "categoryId": "phishing"
}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

### POST /protection/disable
Отключить категорию защиты.

**Запрос:**
```json
{
  "categoryId": "phishing"
}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

### GET /protection/stats
Получить статистику защиты.

**Ответ:**
```json
{
  "totalThreats": 234,
  "blockedThreats": 230,
  "byCategory": {
    "phishing": 120,
    "malware": 80,
    "scam": 30
  }
}
```

### POST /protection/sync
Синхронизировать настройки защиты.

**Запрос:**
```json
{
  "categories": [ ... ],
  "globalLevel": 95
}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

---

## 👨‍👩‍👧 PARENTAL CONTROL API

### POST /api/v1/parental-control/blocking
Применить блокировку контента.

**Запрос:**
```json
{
  "childId": "child_123",
  "type": "website",
  "enabled": true
}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

### POST /api/v1/parental-control/rules
Применить правила родительского контроля.

**Запрос:**
```json
{
  "childId": "child_123",
  "ageGroup": "teenager",
  "rules": {
    "screenTime": 120,
    "bedtime": "22:00",
    "allowedApps": [ ... ]
  }
}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

### GET /api/v1/parental-control/access-requests
Получить запросы доступа.

**Параметры:**
- `childId` (опционально): ID ребенка

**Ответ:**
```json
[
  {
    "id": "request_1",
    "childId": "child_123",
    "childName": "Мария",
    "requestType": "website",
    "url": "https://example.com",
    "timestamp": "2025-11-25T10:00:00Z",
    "status": "pending"
  }
]
```

### POST /api/v1/parental-control/access-requests/{requestId}
Обработать запрос доступа.

**Запрос:**
```json
{
  "requestId": "request_1",
  "action": "accept",
  "reason": "Разрешаю доступ"
}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

### GET /api/v1/parental-control/stats
Получить статистику родительского контроля.

**Параметры:**
- `childId` (опционально): ID ребенка

**Ответ:**
```json
{
  "screenTime": 120,
  "appsUsed": 15,
  "websitesVisited": 45,
  "blockedAttempts": 12
}
```

### GET /parental/bypass/stats
Получить статистику защиты от обхода.

**Параметры:**
- `childId` (опционально): ID ребенка

**Ответ:**
```json
{
  "incognitoAttempts": 5,
  "torAttempts": 2,
  "proxyAttempts": 3,
  "blockedAttempts": 10
}
```

### POST /parental/bypass/apply
Применить защиту от обхода.

**Запрос:**
```json
{
  "childId": "child_123",
  "incognito": true,
  "tor": true,
  "proxy": true
}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

---

## 📱 DEVICE API

### GET /devices
Получить список устройств.

**Ответ:**
```json
[
  {
    "id": "device_1",
    "name": "iPhone 13 Pro",
    "type": "iphone",
    "owner": "Иван Иванов",
    "status": "online",
    "lastSeen": "2025-11-25T10:00:00Z"
  }
]
```

### GET /devices/{deviceId}
Получить детали устройства.

**Ответ:**
```json
{
  "id": "device_1",
  "name": "iPhone 13 Pro",
  "type": "iphone",
  "owner": "Иван Иванов",
  "status": "online",
  "lastSeen": "2025-11-25T10:00:00Z",
  "threatsBlocked": 23,
  "protectionLevel": 95
}
```

### POST /devices
Добавить устройство.

**Запрос:**
```json
{
  "name": "iPad Pro",
  "type": "ipad",
  "owner": "Мария Иванова"
}
```

**Ответ:**
```json
{
  "id": "device_2",
  "name": "iPad Pro",
  "type": "ipad",
  "owner": "Мария Иванова",
  "status": "online",
  "lastSeen": "2025-11-25T10:30:00Z"
}
```

### POST /devices/register-ios
Зарегистрировать iOS устройство для push-уведомлений.

**Запрос:**
```json
{
  "deviceToken": "apns_token_here",
  "platform": "iOS",
  "appVersion": "1.0.0"
}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

---

## 🏠 IoT API

### GET /iot/status/{homeId}
Получить статус IoT безопасности.

**Ответ:**
```json
{
  "homeId": "home_123",
  "isProtected": true,
  "devicesCount": 12,
  "threatsCount": 3,
  "lastScan": "2025-11-25T10:00:00Z"
}
```

### GET /iot/devices/{homeId}
Получить список IoT устройств.

**Ответ:**
```json
{
  "devices": [
    {
      "id": "iot_device_1",
      "name": "Умная камера",
      "type": "camera",
      "status": "online",
      "isSecure": true,
      "threats": []
    }
  ]
}
```

### GET /iot/threats/{homeId}
Получить список угроз IoT.

**Ответ:**
```json
{
  "threats": [
    {
      "id": "threat_1",
      "deviceId": "iot_device_1",
      "deviceName": "Умная камера",
      "type": "weak_password",
      "severity": "high",
      "description": "Слабый пароль"
    }
  ]
}
```

### POST /iot/device/{deviceId}/block
Заблокировать IoT устройство.

**Запрос:**
```json
{}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

### POST /iot/scan/{homeId}
Запустить сканирование IoT устройств.

**Запрос:**
```json
{}
```

**Ответ:**
```json
{
  "success": true,
  "data": "scan_id_123"
}
```

### POST /iot/fix/{threatId}
Исправить угрозу IoT.

**Запрос:**
```json
{}
```

**Ответ:**
```json
{
  "success": true,
  "data": true
}
```

---

## 🎁 REFERRAL API

### GET /referral/code
Получить реферальный код.

**Ответ:**
```json
{
  "code": "IVAN2025",
  "link": "https://aladdin-ai.ru/ref/IVAN2025",
  "totalReferrals": 5,
  "totalRewards": 1500
}
```

### GET /referral/stats
Получить статистику реферальной программы.

**Ответ:**
```json
{
  "totalReferrals": 5,
  "activeReferrals": 3,
  "totalRewards": 1500,
  "availableRewards": 500
}
```

### GET /referral/history
Получить историю рефералов.

**Ответ:**
```json
[
  {
    "id": "ref_1",
    "referralName": "Петр Петров",
    "date": "2025-11-20",
    "status": "active",
    "reward": 300
  }
]
```

### GET /referral/rewards
Получить награды реферальной программы.

**Ответ:**
```json
{
  "availableRewards": 500,
  "totalEarned": 1500,
  "rewardsHistory": [ ... ]
}
```

---

## 💰 PAYMENT API

### POST /payments/qr/create
Создать QR-код для оплаты.

**Запрос:**
```json
{
  "tariffId": "family",
  "duration": 12,
  "amount": 2990,
  "currency": "RUB"
}
```

**Ответ:**
```json
{
  "paymentId": "payment_123",
  "qrCode": "data:image/png;base64,iVBORw0KGgo...",
  "amount": 2990,
  "currency": "RUB",
  "expiresAt": "2025-11-25T11:00:00Z"
}
```

### GET /payments/qr/status/{paymentId}
Проверить статус оплаты.

**Ответ:**
```json
{
  "paymentId": "payment_123",
  "status": "completed",
  "amount": 2990,
  "paidAt": "2025-11-25T10:45:00Z"
}
```

---

## ❌ КОДЫ ОШИБОК

### Общие ошибки

| Код | Описание |
|-----|----------|
| `UNAUTHORIZED` | Требуется аутентификация |
| `FORBIDDEN` | Доступ запрещен |
| `NOT_FOUND` | Ресурс не найден |
| `BAD_REQUEST` | Неверный запрос |
| `INTERNAL_ERROR` | Внутренняя ошибка сервера |

### Специфичные ошибки

| Код | Описание |
|-----|----------|
| `INVALID_TOKEN` | Неверный токен |
| `TOKEN_EXPIRED` | Токен истек |
| `INVALID_CREDENTIALS` | Неверные учетные данные |
| `SUBSCRIPTION_EXPIRED` | Подписка истекла |
| `DEVICE_NOT_FOUND` | Устройство не найдено |
| `FAMILY_NOT_FOUND` | Семья не найдена |

### Пример ошибки

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Требуется аутентификация",
    "details": "Токен отсутствует или неверен"
  }
}
```

---

## 📝 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Swift (iOS)

```swift
import Foundation

// Создание запроса
let url = URL(string: "https://aladdin-ai.ru/api/vpn/status")!
var request = URLRequest(url: url)
request.httpMethod = "GET"
request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

// Выполнение запроса
URLSession.shared.dataTask(with: request) { data, response, error in
    if let data = data {
        let vpnStatus = try? JSONDecoder().decode(VPNStatusResponse.self, from: data)
        print(vpnStatus)
    }
}.resume()
```

### cURL

```bash
# Получить статус VPN
curl -X GET "https://aladdin-ai.ru/api/vpn/status" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Подключиться к VPN
curl -X POST "https://aladdin-ai.ru/api/vpn/connect" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 🔒 БЕЗОПАСНОСТЬ

### SSL Pinning
Приложение использует SSL pinning для защиты от MITM атак.

### Rate Limiting
API имеет ограничения на количество запросов:
- **Обычные endpoints:** 100 запросов/минуту
- **Аутентификация:** 5 запросов/минуту

### Валидация данных
Все входные данные валидируются на сервере. Неверные данные возвращают ошибку `BAD_REQUEST`.

---

## 📞 ПОДДЕРЖКА

При возникновении проблем с API:
- **Telegram:** [@aladdin_support_bot](https://t.me/aladdin_support_bot)
- **Телефон:** +7 (927) 005-15-77
- **FAQ:** https://aladdin-ai.ru/help-faq.html

---

**Версия документа:** 1.0.0  
**Последнее обновление:** 2025-11-25

