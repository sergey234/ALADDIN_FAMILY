# 🔍 АНАЛИЗ ЛОГОВ ИЗ XCODE
## Детальный анализ логов запуска приложения

**Дата анализа:** 2026-03-09 22:14:58  
**Источник:** Xcode Console  
**Проблема:** Краш в TestFlight при переходе на главную страницу

---

## 📊 ПОСЛЕДОВАТЕЛЬНОСТЬ ЗАПУСКА

### **Этап 1: Инициализация (22:14:58.480 - 22:14:58.706)**

```
✅ VisualLogger инициализирован (0 восстановленных логов)
✅ SubscriptionManager начинает инициализацию
✅ Токены загружаются из Keychain
✅ TokenHealthMonitor инициализирован
✅ ALADDINApp.init() вызван
```

**Статус:** ✅ Все успешно

---

### **Этап 2: Обработка токенов (22:14:58.706 - 22:14:59.239)**

```
⚠️ KeychainAutoRecoveryService: удалён повреждённый auth_token
❌ KeychainManager: Failed to load data for key refresh_token. Status: -25300
❌ KeychainManager: Failed to load data for key auth_token. Status: -25300
❌ KeychainManager: Failed to load data for key refresh_token. Status: -25300
✅ Debug токены не обнаружены
```

**Анализ:**
- ⚠️ **ПРОБЛЕМА:** Ошибки загрузки токенов из Keychain (статус -25300 = errSecItemNotFound)
- ✅ **РЕШЕНИЕ:** KeychainAutoRecoveryService удаляет поврежденные токены
- ✅ **РЕЗУЛЬТАТ:** Токены успешно загружаются позже

**Вывод:** Это нормально - токены восстанавливаются автоматически.

---

### **Этап 3: Инициализация менеджеров (22:14:59.239 - 22:14:59.921)**

```
✅ LocalizationManager инициализирован
✅ StoreManager инициализирован
✅ NetworkManager создан
✅ UserProfileManager инициализирован
✅ NotificationManager инициализирован
```

**Статус:** ✅ Все успешно

**Детали NetworkManager:**
```
✅ SSL Pinning: DISABLED (DISABLE_SSL_PINNING env = 1)
✅ Сертификаты загружены: 2 шт
✅ URLSession создан
```

---

### **Этап 4: Навигация (22:14:59.921 - 22:14:59.945)**

```
🛠️ Первый запуск - сбрасываем состояние
🛠️ Начинаем инициализацию...
🛠️ onboardingDone = false
🔴 ONBOARDING: Первый запуск - показываем онбординг
✅ App initialization completed in 0.06 seconds
```

**Статус:** ✅ Успешно - показывается онбординг

---

### **Этап 5: ALADDINApp.onAppear (22:14:59.945)**

```
🎯 ALADDIN_APP: onAppear triggered
🛠️ Уже инициализировано, пропускаем
🚀 Starting SubscriptionManager initialization Task
✅ Инициализация завершена
```

**Статус:** ✅ Успешно

---

### **Этап 6: SubscriptionManager.initializeOnAppStart() (22:15:00.474 - 22:15:02.381)**

```
✅ Health monitoring started
✅ Token validation: VALID (18 hours remaining)
✅ Circuit Breaker: CLOSED
✅ App start initialization completed
```

**Статус:** ✅ Все успешно

---

## 🔍 ВЫЯВЛЕННЫЕ ПРОБЛЕМЫ

### **1. ⚠️ Ошибки Keychain (не критично)**

```
❌ KeychainManager: Failed to load data for key refresh_token. Status: -25300
❌ KeychainManager: Failed to load data for key auth_token. Status: -25300
```

**Анализ:**
- Статус -25300 = `errSecItemNotFound` (элемент не найден)
- Это нормально при первом запуске или после очистки
- KeychainAutoRecoveryService автоматически восстанавливает токены
- Токены успешно загружаются позже

**Вывод:** ✅ Не является причиной краша

---

### **2. ⚠️ SSL Pinning отключен**

```
🔐 SSL PINNING: DISABLE_SSL_PINNING env = 1
🔐 SSL PINNING: Final decision = DISABLED
```

**Анализ:**
- SSL Pinning отключен через переменную окружения
- Это может быть проблемой в RELEASE сборке
- В TestFlight может быть другая конфигурация

**Вывод:** ⚠️ Проверить конфигурацию SSL Pinning в RELEASE

---

### **3. ✅ Все инициализации успешны**

Все менеджеры инициализируются успешно:
- ✅ SubscriptionManager
- ✅ LocalizationManager
- ✅ StoreManager
- ✅ NetworkManager
- ✅ UserProfileManager
- ✅ NotificationManager

**Вывод:** ✅ Инициализация не является причиной краша

---

## 🎯 ГИПОТЕЗЫ О ПРИЧИНЕ КРАША В TESTFLIGHT

### **Гипотеза 1: Проблема при переходе на MainScreen**

**Анализ:**
- В логах нет перехода на MainScreen (показывается онбординг)
- Краш происходит при переходе на главную страницу
- Значит проблема в `MainScreen.onAppear()` или `MainViewModel.onAppear()`

**Что может вызывать краш:**
1. **Инициализация @StateObject MainViewModel** - может крашиться в RELEASE
2. **Загрузка данных из API** - может быть проблема с сетью
3. **Обработка ответов API** - может быть проблема с парсингом
4. **Инициализация ObservableObject** - может быть проблема с потоками

---

### **Гипотеза 2: Проблема с потоками (Thread Safety)**

**Анализ:**
- В логах видно что многие операции выполняются на разных потоках
- `[MAIN]` и `[BACKGROUND]` указывают на разные потоки
- В RELEASE сборке оптимизации компилятора могут вызывать проблемы

**Что проверить:**
- Все обновления UI должны быть на main thread
- Все обращения к UserDefaults должны быть thread-safe
- Все обращения к Keychain должны быть thread-safe

---

### **Гипотеза 3: Проблема с памятью**

**Анализ:**
- В симуляторе больше памяти
- В TestFlight на реальном устройстве может быть нехватка памяти
- Множественные инициализации могут вызывать проблемы

**Что проверить:**
- Утечки памяти
- Слишком большие объекты
- Циклические ссылки

---

### **Гипотеза 4: Проблема с оптимизацией компилятора**

**Анализ:**
- В RELEASE сборке компилятор оптимизирует код
- Могут быть удалены проверки на nil
- Могут быть проблемы с force unwrap

**Что проверить:**
- Все force unwrap (`!`)
- Все optional binding
- Все проверки на nil

---

## 📋 ЧТО НУЖНО ПРОВЕРИТЬ В MAINSCREEN

### **1. Инициализация MainViewModel**

```swift
@StateObject private var mainViewModel = MainViewModel()
```

**Проблемы:**
- Может крашиться если MainViewModel.init() вызывает краш
- Может быть проблема с инициализацией в RELEASE

**Что проверить:**
- Логи в MainViewModel.init()
- Все инициализации в MainViewModel
- Все обращения к shared instances

---

### **2. Вызов mainViewModel.onAppear()**

```swift
mainViewModel.onAppear()
```

**Проблемы:**
- Может вызывать сетевые запросы
- Может обновлять UI не на main thread
- Может вызывать краш при обработке ответов

**Что проверить:**
- Логи в MainViewModel.onAppear()
- Все сетевые запросы
- Все обновления UI

---

### **3. Загрузка profileImage**

```swift
loadProfileImage()
profileImage = ProfileImageManager.shared.loadProfileImage(for: .main)
```

**Проблемы:**
- Может быть проблема с загрузкой изображения
- Может быть проблема с ProfileImageManager
- Может быть проблема с памятью

**Что проверить:**
- Логи в ProfileImageManager
- Проверка на nil
- Обработка ошибок

---

### **4. Проверка Member ID**

```swift
let memberId = UserDefaults.standard.string(forKey: "your_member_id")
```

**Проблемы:**
- Может быть nil в TestFlight
- Может вызывать краш если используется force unwrap
- Может быть проблема с UserDefaults в RELEASE

**Что проверить:**
- Все проверки на nil
- Все optional binding
- Все обращения к UserDefaults

---

## 🔍 РЕКОМЕНДАЦИИ ПО ДИАГНОСТИКЕ

### **1. Добавить больше логирования в MainScreen**

Добавить логи в:
- `MainScreen.init()` (если есть)
- `MainScreen.body` (начало)
- `MainScreen.onAppear()` (каждый шаг)
- `MainViewModel.init()`
- `MainViewModel.onAppear()`
- `loadProfileImage()`

### **2. Проверить Thread Safety**

Проверить что все обновления UI на main thread:
```swift
DispatchQueue.main.async {
    // Обновление UI
}
```

### **3. Проверить Optional Handling**

Проверить все force unwrap и optional binding:
```swift
// Плохо:
let value = someOptional!

// Хорошо:
guard let value = someOptional else { return }
```

### **4. Проверить Memory Management**

Проверить:
- Утечки памяти
- Циклические ссылки
- Слишком большие объекты

---

## 🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ ИЗ КОДА

### **Проблема 1: @ObservedObject для Singleton в MainScreen**

```swift
@ObservedObject private var tariffManager = TariffManager.shared
@ObservedObject private var antivirusManager = AntivirusManager.shared
```

**Анализ:**
- ⚠️ **КРИТИЧНО:** Использование `@ObservedObject` для singleton может вызывать проблемы
- ⚠️ Singleton может быть не инициализирован при первом обращении
- ⚠️ В RELEASE сборке может быть проблема с инициализацией

**Риск:** 🔴 ВЫСОКИЙ - может вызывать краш при инициализации View

---

### **Проблема 2: @EnvironmentObject может быть nil**

```swift
@EnvironmentObject private var localizationManager: LocalizationManager
@EnvironmentObject private var navigationManager: NavigationManager
```

**Анализ:**
- ⚠️ **КРИТИЧНО:** `@EnvironmentObject` может быть nil если не передан в родительский View
- ⚠️ В TestFlight может быть другая иерархия View
- ⚠️ Если EnvironmentObject не установлен - приложение крашится

**Риск:** 🔴 ВЫСОКИЙ - может вызывать краш при доступе к nil

**Что проверить:**
- Убедиться что `localizationManager` и `navigationManager` переданы в `.environmentObject()` в родительском View
- Добавить проверки на nil (но это невозможно с @EnvironmentObject)

---

### **Проблема 3: Инициализация @StateObject MainViewModel**

```swift
@StateObject private var mainViewModel = MainViewModel()
```

**Анализ:**
- ⚠️ **КРИТИЧНО:** `MainViewModel.init()` вызывает `logger.business()` который может вызывать проблемы
- ⚠️ `MainViewModel.init()` использует `APIService.shared` и `KeychainManager.shared`
- ⚠️ Если singleton не инициализирован - может быть краш

**Риск:** 🟡 СРЕДНИЙ - может вызывать краш если singleton не готов

**Что проверить:**
- Логи в `MainViewModel.init()` - должны быть в логах
- Проверить что `APIService.shared` и `KeychainManager.shared` инициализированы до создания MainViewModel

---

### **Проблема 4: loadProfileImage() может вызывать краш**

```swift
private func loadProfileImage() {
    profileImage = ProfileImageManager.shared.loadProfileImage(for: .main)
}
```

**Анализ:**
- ⚠️ **КРИТИЧНО:** `ProfileImageManager.shared` может быть не инициализирован
- ⚠️ `loadProfileImage()` может возвращать nil или вызывать краш
- ⚠️ Нет обработки ошибок

**Риск:** 🟡 СРЕДНИЙ - может вызывать краш если ProfileImageManager не готов

**Что проверить:**
- Логи в `ProfileImageManager.loadProfileImage()`
- Проверка на nil перед присваиванием
- Обработка ошибок

---

### **Проблема 5: mainViewModel.onAppear() может вызывать API запросы**

```swift
mainViewModel.onAppear()
```

**Анализ:**
- ⚠️ **КРИТИЧНО:** `mainViewModel.onAppear()` может вызывать `loadDashboardData()`
- ⚠️ `loadDashboardData()` делает API запросы
- ⚠️ API запросы могут вызывать краш если токен невалиден или сеть недоступна
- ⚠️ Обновления UI могут быть не на main thread

**Риск:** 🟡 СРЕДНИЙ - может вызывать краш при обработке ответов API

**Что проверить:**
- Логи в `MainViewModel.onAppear()` - должны быть в логах
- Проверить что все обновления UI на main thread
- Проверить обработку ошибок API

---

### **Проблема 6: UserDefaults доступ не thread-safe**

```swift
let memberId = UserDefaults.standard.string(forKey: "your_member_id")
let onboardingDone = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
```

**Анализ:**
- ⚠️ **КРИТИЧНО:** UserDefaults не thread-safe
- ⚠️ Если доступ происходит с разных потоков - может быть краш
- ⚠️ В RELEASE сборке может быть проблема с синхронизацией

**Риск:** 🟡 СРЕДНИЙ - может вызывать краш при одновременном доступе

**Что проверить:**
- Все обращения к UserDefaults должны быть на одном потоке
- Использовать `UserDefaults.standard.synchronize()` после записи

---

## 📊 ВЫВОДЫ

### **Что работает:**
- ✅ Инициализация всех менеджеров
- ✅ Загрузка токенов из Keychain
- ✅ Навигация до онбординга
- ✅ SubscriptionManager инициализация

### **Что может быть проблемой:**
- 🔴 **КРИТИЧНО:** @ObservedObject для Singleton (TariffManager, AntivirusManager)
- 🔴 **КРИТИЧНО:** @EnvironmentObject может быть nil (localizationManager, navigationManager)
- 🟡 **СРЕДНЕ:** Инициализация @StateObject MainViewModel
- 🟡 **СРЕДНЕ:** loadProfileImage() может вызывать краш
- 🟡 **СРЕДНЕ:** mainViewModel.onAppear() может вызывать API запросы
- 🟡 **СРЕДНЕ:** UserDefaults доступ не thread-safe

### **Рекомендации:**
1. ✅ **КРИТИЧНО:** Проверить что EnvironmentObject переданы в родительском View
2. ✅ **КРИТИЧНО:** Заменить @ObservedObject на прямое обращение к Singleton
3. ✅ Добавить детальное логирование в MainScreen.onAppear()
4. ✅ Добавить логирование в MainViewModel.init()
5. ✅ Проверить thread safety для UserDefaults
6. ✅ Добавить обработку ошибок в loadProfileImage()
7. ✅ Проверить что все обновления UI на main thread

---

## 🎯 ГИПОТЕЗА О ПРИЧИНЕ КРАША В TESTFLIGHT

**Наиболее вероятная причина:**

1. ✅ **@EnvironmentObject передан правильно** - проверено в `ALADDINApp.swift`, все экраны получают `localizationManager` и `navigationManager`
2. ⚠️ **@ObservedObject для Singleton** - использование `@ObservedObject` для `TariffManager.shared` и `AntivirusManager.shared` может вызывать проблемы в RELEASE сборке
3. ⚠️ **Инициализация MainViewModel** - если `APIService.shared` или `KeychainManager.shared` не готовы, может быть краш
4. ⚠️ **loadProfileImage()** - может вызывать краш если `ProfileImageManager.shared` не готов или файл поврежден
5. ⚠️ **mainViewModel.onAppear()** - может вызывать API запросы которые крашатся в RELEASE

**Что проверить в первую очередь:**
- ✅ EnvironmentObject переданы правильно (проверено)
- ⚠️ Проверить что `TariffManager.shared` и `AntivirusManager.shared` инициализированы до создания MainScreen
- ⚠️ Добавить логирование в `MainViewModel.init()` чтобы увидеть где именно краш
- ⚠️ Добавить обработку ошибок в `loadProfileImage()`
- ⚠️ Проверить что все обновления UI в `mainViewModel.onAppear()` на main thread

---

## 📝 ДОПОЛНИТЕЛЬНЫЕ НАБЛЮДЕНИЯ ИЗ ЛОГОВ

### **Что НЕ видно в логах:**
- ❌ Нет логов из `MainScreen.onAppear()` - значит переход на MainScreen не произошел
- ❌ Нет логов из `MainViewModel.init()` - значит MainViewModel не был создан
- ❌ Нет логов из `loadProfileImage()` - значит функция не была вызвана

### **Вывод:**
Краш происходит **ДО** вызова `MainScreen.onAppear()`, скорее всего при:
1. **Создании View** - при инициализации `@StateObject MainViewModel`
2. **Доступе к Singleton** - при обращении к `TariffManager.shared` или `AntivirusManager.shared`
3. **Рендеринге body** - при вычислении `body` свойства MainScreen

### **Рекомендация:**
Добавить логирование в:
- `MainScreen.init()` (если есть)
- Начало `MainScreen.body`
- При создании `@StateObject MainViewModel`
- При обращении к `TariffManager.shared` и `AntivirusManager.shared`

---

**Дата создания:** 2026-03-09  
**Автор:** AI Assistant  
**Версия:** 1.1
