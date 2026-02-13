# 📱 План обновления UI для синхронизации с сервером

## 🎯 Цель
Обновить существующие UI экраны геймификации для синхронизации данных с сервером вместо использования только локальных данных.

---

## 📋 Экраны для обновления (4 экрана)

### 1. **ChildRewardsScreen.swift** - Экран наград для детей
**Что нужно обновить:**
- ✅ Заменить локальные данные наградами с сервера
- ✅ Использовать `apiService.getGamificationRewards()` для получения списка наград
- ✅ Использовать `apiService.claimGamificationReward()` при получении награды
- ✅ Использовать `apiService.getGamificationRewardsShop()` для магазина
- ✅ Использовать `apiService.purchaseGamificationReward()` при покупке
- ✅ Синхронизировать баланс единорогов с сервером (`getGamificationBalance()`)
- ✅ Показывать индикатор загрузки при запросах
- ✅ Обрабатывать ошибки сети

**Ключевые изменения:**
```swift
// Вместо локальных данных:
// let rewards = localRewards

// Использовать:
apiService.getGamificationRewards(userId: userId) { result in
    switch result {
    case .success(let response):
        self.rewards = response.rewards
    case .failure(let error):
        // Обработка ошибки
    }
}
```

---

### 2. **GamesSettingsManager.swift** - Менеджер настроек игр
**Что нужно обновить:**
- ✅ Загружать настройки с сервера при запуске (`getGamificationSettings()`)
- ✅ Сохранять изменения на сервер (`updateGamificationSettings()`)
- ✅ Синхронизировать настройки уведомлений (`getGamificationNotificationSettings()`, `updateGamificationNotificationSettings()`)
- ✅ Использовать оптимистичную блокировку (version) для предотвращения конфликтов
- ✅ Кэшировать настройки локально для офлайн режима
- ✅ Синхронизировать при восстановлении соединения

**Ключевые изменения:**
```swift
// При загрузке:
func loadSettings() {
    apiService.getGamificationSettings(userId: userId) { result in
        // Обновить локальные настройки
    }
}

// При сохранении:
func saveSettings() {
    apiService.updateGamificationSettings(...) { result in
        // Обновить версию и синхронизировать
    }
}
```

---

### 3. **FamilyTournamentView.swift** - Экран семейных турниров
**Что нужно обновить:**
- ✅ Загружать активные турниры с сервера (`getGamificationTournaments()`)
- ✅ Использовать `joinGamificationTournament()` при присоединении
- ✅ Использовать `getGamificationTournamentLeaderboard()` для таблицы лидеров
- ✅ Использовать `getGamificationTournamentsHistory()` для истории
- ✅ Использовать `leaveGamificationTournament()` при выходе
- ✅ Обновлять данные в реальном времени (polling или WebSocket)
- ✅ Показывать статус турнира (upcoming, active, finished)

**Ключевые изменения:**
```swift
// Загрузка турниров:
apiService.getGamificationTournaments(status: "active") { result in
    // Обновить список турниров
}

// Присоединение:
apiService.joinGamificationTournament(userId: userId, tournamentId: id) { result in
    // Обновить UI
}
```

---

### 4. **UnicornPetView.swift** - Виджет единорога (баланс)
**Что нужно обновить:**
- ✅ Синхронизировать баланс единорогов с сервером (`getGamificationBalance()`)
- ✅ Обновлять баланс при добавлении/вычитании (`addGamificationBalance()`, `subtractGamificationBalance()`)
- ✅ Показывать историю операций (`getGamificationBalanceHistory()`)
- ✅ Автоматически обновлять баланс при изменении (pull или push уведомления)
- ✅ Кэшировать баланс локально для офлайн режима
- ✅ Показывать анимацию при изменении баланса

**Ключевые изменения:**
```swift
// Загрузка баланса:
func loadBalance() {
    apiService.getGamificationBalance(userId: userId) { result in
        switch result {
        case .success(let response):
            self.balance = response.balance
        case .failure:
            // Использовать кэшированное значение
        }
    }
}

// При изменении:
func addBalance(amount: Int) {
    apiService.addGamificationBalance(userId: userId, amount: amount) { result in
        // Обновить UI
    }
}
```

---

---

## 🔄 Общие улучшения для всех экранов

### 1. **Обработка офлайн режима**
- Кэшировать данные локально
- Показывать индикатор офлайн режима
- Синхронизировать при восстановлении соединения

### 2. **Обработка ошибок**
- Показывать понятные сообщения об ошибках
- Retry логика для сетевых ошибок
- Fallback на локальные данные при ошибках

### 3. **Индикаторы загрузки**
- Показывать спиннеры при загрузке
- Skeleton screens для лучшего UX
- Оптимистичные обновления UI

### 4. **Синхронизация данных**
- Автоматическая синхронизация при открытии экрана
- Pull-to-refresh для ручного обновления
- Фоновая синхронизация

### 5. **Конфликты данных**
- Использовать версионирование (version field)
- Last-Write-Wins стратегия
- Уведомления о конфликтах

---

## 📊 Приоритет обновлений

### 🔴 Критично (сначала):
1. **UnicornPetView.swift** - Баланс единорогов (основа геймификации)
2. **ChildRewardsScreen.swift** - Награды (основной функционал)

### 🟡 Важно (затем):
3. **GamesSettingsManager.swift** - Настройки (синхронизация между устройствами)
4. **FamilyTournamentView.swift** - Турниры (социальный функционал)


---

## ✅ Критерии готовности

Каждый экран считается готовым, когда:
- ✅ Данные загружаются с сервера
- ✅ Изменения сохраняются на сервер
- ✅ Обрабатываются ошибки сети
- ✅ Работает офлайн режим (кэш)
- ✅ Показываются индикаторы загрузки
- ✅ Тестирование на реальных устройствах

---

## 🧪 Тестирование UI

После обновления каждого экрана нужно протестировать:
1. Загрузку данных с сервера
2. Сохранение изменений
3. Офлайн режим
4. Обработку ошибок
5. Синхронизацию между устройствами
6. Производительность (нет ли лагов)

---

## 📝 Примечания

- Все экраны уже имеют локальную реализацию
- Нужно добавить интеграцию с API без ломания существующего функционала
- Сохранить обратную совместимость
- Использовать существующие паттерны проекта (MVVM, Combine, etc.)
