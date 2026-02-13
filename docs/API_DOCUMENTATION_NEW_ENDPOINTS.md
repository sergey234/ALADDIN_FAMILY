# 📚 НОВЫЕ API ENDPOINT'Ы - ДОПОЛНЕНИЕ К ДОКУМЕНТАЦИИ

**Дата:** 2026-02-11  
**Версия:** 2.0.0  
**Всего новых endpoint'ов:** 96

---

## 🎮 GAMIFICATION API

### GET /api/gamification/balance/{userId}
Получить баланс единорогов пользователя.

**Ответ:**
```json
{
  "userId": "user_123",
  "balance": 245,
  "lastUpdated": "2026-02-11T10:00:00Z"
}
```

### POST /api/gamification/balance/add
Добавить единорогов к балансу.

**Запрос:**
```json
{
  "userId": "user_123",
  "amount": 10,
  "reason": "За выполнение задания"
}
```

### POST /api/gamification/balance/subtract
Списать единорогов с баланса.

**Запрос:**
```json
{
  "userId": "user_123",
  "amount": 5,
  "reason": "Покупка награды"
}
```

### GET /api/gamification/balance/history
Получить историю операций с балансом.

**Параметры:**
- `userId` (required)
- `limit` (optional, default: 10)

**Ответ:**
```json
[
  {
    "id": "op_1",
    "userId": "user_123",
    "amount": 10,
    "type": "add",
    "reason": "За выполнение задания",
    "timestamp": "2026-02-11T10:00:00Z"
  }
]
```

### GET /api/gamification/rewards
Получить список наград пользователя.

**Параметры:**
- `userId` (required)

**Ответ:**
```json
[
  {
    "id": "reward_1",
    "name": "Игрушка",
    "description": "Крутая игрушка",
    "cost": 50,
    "category": "toys"
  }
]
```

### POST /api/gamification/rewards/claim
Получить награду.

**Запрос:**
```json
{
  "userId": "user_123",
  "rewardId": "reward_1"
}
```

### GET /api/gamification/rewards/history
Получить историю наград.

**Параметры:**
- `userId` (required)
- `limit` (optional, default: 10)

### POST /api/gamification/rewards/give
Выдать награду пользователю.

**Запрос:**
```json
{
  "userId": "user_123",
  "rewardId": "reward_1",
  "reason": "За хорошее поведение"
}
```

### GET /api/gamification/rewards/shop
Получить магазин наград.

**Параметры:**
- `userId` (required)

### POST /api/gamification/rewards/purchase
Купить награду.

**Запрос:**
```json
{
  "userId": "user_123",
  "rewardId": "reward_1"
}
```

### GET /api/gamification/achievements
Получить список достижений.

**Параметры:**
- `userId` (required)

**Ответ:**
```json
[
  {
    "id": "ach_1",
    "name": "Первые шаги",
    "description": "Выполните первое задание",
    "progress": 50,
    "maxProgress": 100,
    "isUnlocked": false
  }
]
```

### POST /api/gamification/achievements/unlock
Разблокировать достижение.

**Запрос:**
```json
{
  "userId": "user_123",
  "achievementId": "ach_1"
}
```

### GET /api/gamification/achievements/progress
Получить прогресс по достижениям.

**Параметры:**
- `userId` (required)

### GET /api/gamification/achievements/{achievementId}
Получить информацию о достижении.

**Параметры:**
- `achievementId` (path)
- `userId` (query, required)

### POST /api/gamification/achievements/claim
Получить награду за достижение.

**Запрос:**
```json
{
  "userId": "user_123",
  "achievementId": "ach_1"
}
```

### GET /api/gamification/tournaments
Получить список турниров.

**Параметры:**
- `status` (optional): `active`, `upcoming`, `finished`

**Ответ:**
```json
[
  {
    "id": "tour_1",
    "name": "Семейный турнир",
    "status": "active",
    "startDate": "2026-02-01T00:00:00Z",
    "endDate": "2026-02-28T23:59:59Z",
    "participants": 15
  }
]
```

### POST /api/gamification/tournaments/join
Присоединиться к турниру.

**Запрос:**
```json
{
  "userId": "user_123",
  "tournamentId": "tour_1",
  "deviceId": "device_123"
}
```

### GET /api/gamification/tournaments/{tournamentId}
Получить информацию о турнире.

**Параметры:**
- `tournamentId` (path)

### GET /api/gamification/tournaments/leaderboard
Получить таблицу лидеров.

**Параметры:**
- `tournamentId` (required)
- `limit` (optional, default: 10)

**Ответ:**
```json
[
  {
    "userId": "user_123",
    "name": "Иван",
    "score": 1500,
    "rank": 1
  }
]
```

### POST /api/gamification/tournaments/leave
Покинуть турнир.

**Запрос:**
```json
{
  "userId": "user_123",
  "tournamentId": "tour_1"
}
```

### GET /api/gamification/tournaments/history
Получить историю турниров.

**Параметры:**
- `userId` (required)
- `limit` (optional, default: 10)

### GET /api/gamification/settings
Получить настройки игр.

**Параметры:**
- `userId` (required)

**Ответ:**
```json
{
  "userId": "user_123",
  "soundEnabled": true,
  "notificationsEnabled": true,
  "deviceId": "device_123"
}
```

### POST /api/gamification/settings/update
Обновить настройки игр.

**Запрос:**
```json
{
  "userId": "user_123",
  "soundEnabled": true,
  "deviceId": "device_123"
}
```

### GET /api/gamification/settings/notifications
Получить настройки уведомлений игр.

**Параметры:**
- `userId` (required)

### POST /api/gamification/settings/notifications/update
Обновить настройки уведомлений игр.

**Запрос:**
```json
{
  "userId": "user_123",
  "achievementUnlocked": true,
  "tournamentStarted": true,
  "deviceId": "device_123"
}
```

### GET /api/gamification/progress
Получить прогресс игр.

**Параметры:**
- `userId` (required)

**Ответ:**
```json
{
  "userId": "user_123",
  "totalExperience": 1500,
  "currentLevel": 5,
  "experienceToNextLevel": 500
}
```

### POST /api/gamification/progress/update
Обновить прогресс игр.

**Запрос:**
```json
{
  "userId": "user_123",
  "gameId": "game_1",
  "experience": 100,
  "deviceId": "device_123"
}
```

### GET /api/gamification/progress/stats
Получить статистику прогресса.

**Параметры:**
- `userId` (required)

### GET /api/gamification/progress/level
Получить текущий уровень.

**Параметры:**
- `userId` (required)

### POST /api/gamification/progress/reset
Сбросить прогресс игры.

**Запрос:**
```json
{
  "userId": "user_123",
  "gameId": "game_1"
}
```

---

## 🛡️ PARENTAL CONTROL SYNC API

### GET /api/parental-control/settings/{familyId}
Получить настройки родительского контроля.

**Параметры:**
- `familyId` (path)
- `childId` (query, required)

**Ответ:**
```json
{
  "familyId": "family_123",
  "childId": "child_123",
  "isContentFilterEnabled": true,
  "isAppBlockingEnabled": true,
  "lastUpdated": "2026-02-11T10:00:00Z"
}
```

### POST /api/parental-control/settings/update
Обновить настройки родительского контроля.

**Запрос:**
```json
{
  "familyId": "family_123",
  "childId": "child_123",
  "isContentFilterEnabled": true,
  "deviceId": "device_123"
}
```

### GET /api/parental-control/settings/history
Получить историю изменений настроек.

**Параметры:**
- `familyId` (required)
- `childId` (required)

### POST /api/parental-control/settings/sync
Синхронизировать настройки.

**Запрос:**
```json
{
  "familyId": "family_123",
  "childId": "child_123",
  "deviceId": "device_123"
}
```

### GET /api/parental-control/settings/conflicts
Получить конфликты настроек.

**Параметры:**
- `familyId` (required)
- `childId` (required)

### GET /api/parental-control/time-limits/{childId}
Получить лимиты времени.

**Параметры:**
- `childId` (path)

**Ответ:**
```json
{
  "childId": "child_123",
  "dailyLimitMinutes": 120,
  "currentUsageMinutes": 45,
  "lastReset": "2026-02-11T00:00:00Z"
}
```

### POST /api/parental-control/time-limits/update
Обновить лимиты времени.

**Запрос:**
```json
{
  "childId": "child_123",
  "dailyLimitMinutes": 120,
  "deviceId": "device_123"
}
```

### GET /api/parental-control/time-limits/history
Получить историю лимитов времени.

**Параметры:**
- `childId` (required)

### POST /api/parental-control/time-limits/reset
Сбросить лимиты времени.

**Запрос:**
```json
{
  "childId": "child_123",
  "deviceId": "device_123"
}
```

### GET /api/parental-control/schedules/{childId}
Получить расписания.

**Параметры:**
- `childId` (path)

**Ответ:**
```json
[
  {
    "id": "sched_1",
    "childId": "child_123",
    "dayOfWeek": "monday",
    "startTime": "09:00",
    "endTime": "17:00",
    "isActive": true
  }
]
```

### POST /api/parental-control/schedules/update
Обновить расписание.

**Запрос:**
```json
{
  "childId": "child_123",
  "scheduleId": "sched_1",
  "startTime": "09:00",
  "endTime": "17:00",
  "deviceId": "device_123"
}
```

### GET /api/parental-control/schedules/history
Получить историю расписаний.

**Параметры:**
- `childId` (required)

### POST /api/parental-control/schedules/delete
Удалить расписание.

**Запрос:**
```json
{
  "scheduleId": "sched_1",
  "deviceId": "device_123"
}
```

### GET /api/parental-control/geofences/{childId}
Получить геозоны.

**Параметры:**
- `childId` (path)

**Ответ:**
```json
[
  {
    "id": "geo_1",
    "childId": "child_123",
    "name": "Дом",
    "latitude": 55.7558,
    "longitude": 37.6173,
    "radius": 100
  }
]
```

### POST /api/parental-control/geofences/add
Добавить геозону.

**Запрос:**
```json
{
  "childId": "child_123",
  "name": "Дом",
  "latitude": 55.7558,
  "longitude": 37.6173,
  "radius": 100,
  "deviceId": "device_123"
}
```

### POST /api/parental-control/geofences/update
Обновить геозону.

**Запрос:**
```json
{
  "geofenceId": "geo_1",
  "name": "Дом Обновленный",
  "deviceId": "device_123"
}
```

### DELETE /api/parental-control/geofences/{geofenceId}
Удалить геозону.

**Параметры:**
- `geofenceId` (path)

### GET /api/parental-control/app-blocks/{childId}
Получить заблокированные приложения.

**Параметры:**
- `childId` (path)

**Ответ:**
```json
{
  "childId": "child_123",
  "blockedApps": ["app_1", "app_2"]
}
```

### POST /api/parental-control/app-blocks/update
Обновить заблокированные приложения.

**Запрос:**
```json
{
  "childId": "child_123",
  "blockedApps": ["app_1", "app_2"],
  "deviceId": "device_123"
}
```

### POST /api/parental-control/app-blocks/sync
Синхронизировать заблокированные приложения.

**Запрос:**
```json
{
  "childId": "child_123",
  "deviceId": "device_123"
}
```

---

## 👤 USER PROFILE SYNC API

### POST /api/user/profile/sync
Синхронизировать профиль пользователя.

**Запрос:**
```json
{
  "userId": "user_123",
  "deviceId": "device_123"
}
```

**Ответ:**
```json
{
  "userId": "user_123",
  "name": "Иван Иванов",
  "email": "ivan@example.com",
  "phone": "+79001234567",
  "lastUpdated": "2026-02-11T10:00:00Z"
}
```

### POST /api/user/profile/update
Обновить профиль пользователя.

**Запрос:**
```json
{
  "userId": "user_123",
  "name": "Иван Петров",
  "deviceId": "device_123"
}
```

### GET /api/user/profile/history
Получить историю изменений профиля.

**Параметры:**
- `userId` (required)
- `limit` (optional, default: 10)

### GET /api/user/profile/privacy
Получить настройки приватности.

**Параметры:**
- `userId` (required)

**Ответ:**
```json
{
  "userId": "user_123",
  "profileVisibility": "private",
  "showEmail": false,
  "showPhone": false
}
```

### POST /api/user/profile/privacy/update
Обновить настройки приватности.

**Запрос:**
```json
{
  "userId": "user_123",
  "profileVisibility": "private",
  "deviceId": "device_123"
}
```

---

## 💳 SUBSCRIPTION SYNC API

### POST /api/subscription/sync
Синхронизировать подписку.

**Запрос:**
```json
{
  "userId": "user_123",
  "deviceId": "device_123"
}
```

**Ответ:**
```json
{
  "userId": "user_123",
  "subscriptionType": "family",
  "status": "active",
  "endDate": "2026-12-31T23:59:59Z"
}
```

### POST /api/subscription/update
Обновить подписку.

**Запрос:**
```json
{
  "userId": "user_123",
  "subscriptionType": "family",
  "deviceId": "device_123"
}
```

### GET /api/subscription/purchase-history
Получить историю покупок.

**Параметры:**
- `userId` (required)
- `limit` (optional, default: 10)

### GET /api/subscription/status
Получить статус подписки.

**Параметры:**
- `userId` (required)

### POST /api/subscription/status/update
Обновить статус подписки.

**Запрос:**
```json
{
  "userId": "user_123",
  "status": "active",
  "deviceId": "device_123"
}
```

### GET /api/subscription/auto-renewal
Получить настройки автопродления.

**Параметры:**
- `userId` (required)

### POST /api/subscription/auto-renewal/update
Обновить настройки автопродления.

**Запрос:**
```json
{
  "userId": "user_123",
  "enabled": true,
  "deviceId": "device_123"
}
```

### POST /api/subscription/cancel
Отменить подписку.

**Запрос:**
```json
{
  "userId": "user_123",
  "reason": "Не использую",
  "deviceId": "device_123"
}
```

---

## ⚙️ APP SETTINGS SYNC API

### POST /api/settings/sync
Синхронизировать настройки приложения.

**Запрос:**
```json
{
  "userId": "user_123",
  "deviceId": "device_123"
}
```

**Ответ:**
```json
{
  "userId": "user_123",
  "theme": "dark",
  "language": "ru",
  "notificationsEnabled": true,
  "biometryEnabled": true
}
```

### POST /api/settings/update
Обновить настройки приложения.

**Запрос:**
```json
{
  "userId": "user_123",
  "theme": "dark",
  "deviceId": "device_123"
}
```

### GET /api/settings/theme
Получить тему приложения.

**Параметры:**
- `userId` (required)

**Ответ:**
```json
{
  "userId": "user_123",
  "theme": "dark"
}
```

### POST /api/settings/theme/update
Обновить тему приложения.

**Запрос:**
```json
{
  "userId": "user_123",
  "theme": "light",
  "deviceId": "device_123"
}
```

### GET /api/settings/language
Получить язык приложения.

**Параметры:**
- `userId` (required)

### POST /api/settings/language/update
Обновить язык приложения.

**Запрос:**
```json
{
  "userId": "user_123",
  "language": "en",
  "deviceId": "device_123"
}
```

### GET /api/settings/notifications
Получить настройки уведомлений.

**Параметры:**
- `userId` (required)

### POST /api/settings/notifications/update
Обновить настройки уведомлений.

**Запрос:**
```json
{
  "userId": "user_123",
  "enabled": true,
  "deviceId": "device_123"
}
```

### GET /api/settings/biometry
Получить настройки биометрии.

**Параметры:**
- `userId` (required)

### POST /api/settings/biometry/update
Обновить настройки биометрии.

**Запрос:**
```json
{
  "userId": "user_123",
  "enabled": true,
  "type": "face",
  "deviceId": "device_123"
}
```

---

## 📍 LOCATION & GEOFENCES SYNC API

### POST /api/location/geofences/sync
Синхронизировать геозоны.

**Запрос:**
```json
{
  "userId": "user_123",
  "deviceId": "device_123"
}
```

### POST /api/location/geofences/update
Обновить геозону.

**Запрос:**
```json
{
  "userId": "user_123",
  "name": "Дом",
  "latitude": 55.7558,
  "longitude": 37.6173,
  "radius": 100,
  "deviceId": "device_123"
}
```

### DELETE /api/location/geofences/{geofenceId}
Удалить геозону.

**Параметры:**
- `geofenceId` (path)

### GET /api/location/movement-history
Получить историю перемещений.

**Параметры:**
- `userId` (required)
- `limit` (optional, default: 10)

### POST /api/location/movement-history/update
Обновить историю перемещений.

**Запрос:**
```json
{
  "userId": "user_123",
  "entries": [],
  "deviceId": "device_123"
}
```

### GET /api/location/status
Получить статус геолокации.

**Параметры:**
- `userId` (required)

**Ответ:**
```json
{
  "userId": "user_123",
  "enabled": true
}
```

### POST /api/location/status/update
Обновить статус геолокации.

**Запрос:**
```json
{
  "userId": "user_123",
  "enabled": true,
  "deviceId": "device_123"
}
```

---

## 💬 OFFLINE CHAT SYNC API

### POST /api/chat/offline-messages/sync
Синхронизировать офлайн сообщения.

**Запрос:**
```json
{
  "userId": "user_123",
  "familyId": "family_123",
  "deviceId": "device_123"
}
```

**Ответ:**
```json
{
  "messages": [
    {
      "id": "msg_1",
      "senderId": "user_123",
      "recipientId": "child_123",
      "content": "Привет!",
      "timestamp": "2026-02-11T10:00:00Z",
      "status": "sent"
    }
  ],
  "conflicts": []
}
```

### POST /api/chat/offline-messages/send
Отправить офлайн сообщение.

**Запрос:**
```json
{
  "userId": "user_123",
  "recipientId": "child_123",
  "familyId": "family_123",
  "content": "Привет!",
  "deviceId": "device_123"
}
```

### POST /api/chat/offline-messages/resolve-conflicts
Разрешить конфликты сообщений.

**Запрос:**
```json
{
  "userId": "user_123",
  "familyId": "family_123",
  "conflicts": [],
  "deviceId": "device_123"
}
```

---

## 💾 OFFLINE STORAGE SYNC API

### POST /api/offline-storage/sync
Синхронизировать офлайн хранилище.

**Запрос:**
```json
{
  "userId": "user_123",
  "deviceId": "device_123"
}
```

### GET /api/offline-storage/data
Получить данные из офлайн хранилища.

**Параметры:**
- `userId` (required)

### POST /api/offline-storage/data/update
Обновить данные в офлайн хранилище.

**Запрос:**
```json
{
  "userId": "user_123",
  "dataType": "settings",
  "data": {},
  "deviceId": "device_123"
}
```

### DELETE /api/offline-storage/data/{dataId}
Удалить данные из офлайн хранилища.

**Параметры:**
- `dataId` (path)
- `userId` (query, required)

### POST /api/offline-storage/resolve-conflicts
Разрешить конфликты в офлайн хранилище.

**Запрос:**
```json
{
  "userId": "user_123",
  "conflicts": [],
  "resolutionStrategy": "last-write-wins",
  "deviceId": "device_123"
}
```

---

## 🚨 CRASH DETECTION SYNC API

### POST /api/crash-detection/sync
Синхронизировать отчеты о крашах.

**Запрос:**
```json
{
  "userId": "user_123",
  "deviceId": "device_123"
}
```

### POST /api/crash-detection/report
Отправить отчет о краше.

**Запрос:**
```json
{
  "userId": "user_123",
  "deviceId": "device_123",
  "crashType": "accident",
  "severity": "high",
  "location": {
    "latitude": 55.7558,
    "longitude": 37.6173
  }
}
```

### GET /api/crash-detection/notifications
Получить уведомления о крашах.

**Параметры:**
- `userId` (required)
- `limit` (optional, default: 10)

### POST /api/crash-detection/notifications/send
Отправить уведомление о краше.

**Запрос:**
```json
{
  "userId": "user_123",
  "reportId": "report_1",
  "deviceId": "device_123"
}
```

---

## 👴 ELDERLY INTERFACE SYNC API

### POST /api/elderly/medications/sync
Синхронизировать лекарства.

**Запрос:**
```json
{
  "userId": "user_123",
  "deviceId": "device_123"
}
```

**Ответ:**
```json
{
  "medications": [
    {
      "id": "med_1",
      "name": "Аспирин",
      "dosage": "1 таблетка",
      "frequency": "daily",
      "nextDose": "2026-02-11T12:00:00Z"
    }
  ]
}
```

### POST /api/elderly/medications/update
Обновить лекарства.

**Запрос:**
```json
{
  "userId": "user_123",
  "name": "Аспирин",
  "dosage": "1 таблетка",
  "frequency": "daily",
  "deviceId": "device_123"
}
```

### POST /api/elderly/appointments/sync
Синхронизировать встречи.

**Запрос:**
```json
{
  "userId": "user_123",
  "deviceId": "device_123"
}
```

**Ответ:**
```json
{
  "appointments": [
    {
      "id": "appt_1",
      "title": "Врач",
      "dateTime": "2026-02-15T10:00:00Z",
      "location": "Поликлиника №1"
    }
  ]
}
```

### POST /api/elderly/appointments/update
Обновить встречу.

**Запрос:**
```json
{
  "userId": "user_123",
  "title": "Врач",
  "dateTime": "2026-02-15T10:00:00Z",
  "deviceId": "device_123"
}
```

---

## 📊 СТАТИСТИКА

**Всего новых endpoint'ов:** 96

- **Gamification API:** 30 endpoint'ов
- **Parental Control Sync API:** 20 endpoint'ов
- **User Profile Sync API:** 5 endpoint'ов
- **Subscription Sync API:** 8 endpoint'ов
- **App Settings Sync API:** 10 endpoint'ов
- **Location & Geofences Sync API:** 7 endpoint'ов
- **Offline Chat Sync API:** 3 endpoint'а
- **Offline Storage Sync API:** 5 endpoint'ов
- **Crash Detection Sync API:** 4 endpoint'а
- **Elderly Interface Sync API:** 4 endpoint'а

---

## 🔄 МЕХАНИЗМ СИНХРОНИЗАЦИИ

Все endpoint'ы синхронизации используют общий механизм:

1. **Last-Write-Wins:** Последнее изменение имеет приоритет
2. **Optimistic Locking:** Версионирование данных для предотвращения конфликтов
3. **Conflict Resolution:** Автоматическое разрешение конфликтов с возможностью ручного вмешательства

### Формат синхронизации:

**Запрос:**
```json
{
  "userId": "user_123",
  "deviceId": "device_123",
  "timestamp": "2026-02-11T10:00:00Z",
  "version": 1
}
```

**Ответ с конфликтами:**
```json
{
  "data": { ... },
  "conflicts": [
    {
      "field": "name",
      "localValue": "Иван",
      "serverValue": "Петр",
      "lastModified": "2026-02-11T09:00:00Z"
    }
  ]
}
```
