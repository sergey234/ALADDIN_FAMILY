# 🔍 ПОЛНЫЙ АНАЛИЗ ЛОГИКИ UserProfile НА ОНБОРДИНГЕ - BUILD 122

**Дата:** 17 марта 2026, 00:05  
**Build:** 122  
**Статус:** 🔍 **ДЕТАЛЬНЫЙ АНАЛИЗ ЛОГИКИ**

---

## 📋 ВОПРОСЫ ДЛЯ АНАЛИЗА

1. **Должен ли запрос профиля выполняться на онбординге?**
2. **Правильно ли это, что запрос идет сразу при входе?**
3. **Проверка всех 4 пунктов рекомендаций по очереди**

---

## 🔍 ПУНКТ 1: АНАЛИЗ ЛОГИКИ ВЫЗОВА getUserProfile

### Где вызывается getUserProfile:

1. **ProfileViewModel.loadProfile()** (строка 34-64):
   ```swift
   func loadProfile() {
       logger.business("Loading user profile")
       isLoading = true
       errorMessage = nil
       
       apiService.getUserProfile { [weak self] result in
           // Обработка результата
       }
   }
   ```

2. **UserProfileManager.loadProfile()** (ALADDINApp.swift, строка 61-78):
   ```swift
   func loadProfile(completion: ((Bool) -> Void)? = nil) {
       apiService.getUserProfile { [weak self] result in
           // Сохранение в кеш
       }
   }
   ```

3. **UserProfileManager.loadProfileInBackground()** (UserProfileManager.swift, строка 74-85):
   ```swift
   private func loadProfileInBackground() {
       DispatchQueue.global(qos: .background).async { [weak self] in
           guard let self = self else { return }
           
           if let token = AppConfig.authToken {
               self.loadProfileFromAPI(token: token)
           }
       }
   }
   ```

### Когда вызывается:

1. **UserProfileManager.init()** (строка 17-20):
   - Вызывается при создании singleton `UserProfileManager.shared`
   - Вызывает `loadProfileInBackground()`
   - ⚠️ **ПРОБЛЕМА:** Вызывается при первом обращении к singleton, даже на онбординге!

2. **ProfileViewModel.loadProfile()**:
   - Вызывается вручную из UI
   - Не вызывается автоматически при инициализации
   - ✅ **ПРАВИЛЬНО:** Не вызывается на онбординге

---

## 🎯 ПУНКТ 2: АНАЛИЗ ЛОГИКИ НА ОНБОРДИНГЕ

### Что происходит на онбординге:

1. **ALADDINApp инициализируется:**
   - Создается `SubscriptionManager.shared`
   - Вызывается `SubscriptionManager.initializeOnAppStart()`
   - ✅ **ПРАВИЛЬНО:** Инициализация токенов

2. **UserProfileManager.shared может быть создан:**
   - Если где-то в коде обращаются к `UserProfileManager.shared`
   - Вызывается `init()` → `loadProfileInBackground()`
   - ⚠️ **ПРОБЛЕМА:** Запрос профиля выполняется даже на онбординге!

3. **ProfileViewModel НЕ используется на онбординге:**
   - `OnboardingScreen` не использует `ProfileViewModel`
   - ✅ **ПРАВИЛЬНО:** Профиль не загружается из UI на онбординге

---

## ⚠️ ВЫЯВЛЕННАЯ ПРОБЛЕМА

### Проблема: UserProfileManager загружает профиль на онбординге

**Причина:**
- `UserProfileManager.shared` создается при первом обращении
- В `init()` вызывается `loadProfileInBackground()`
- Если есть токен → выполняется запрос `/api/user/profile`
- На онбординге токен уже есть (device token) → запрос выполняется!

**Это неправильно?**
- ❌ **ДА!** На онбординге пользователь еще не зарегистрирован
- ❌ Профиль не нужен на онбординге
- ❌ Запрос выполняется впустую и вызывает ошибку

---

## 🔍 ПУНКТ 3: ПРОВЕРКА РЕКОМЕНДАЦИЙ

### Рекомендация 1: Проверить доступность SFM на сервере

**Статус:** ⏳ ТРЕБУЕТСЯ ПРОВЕРКА

**Действие:**
- Проверить, запущен ли SFM на порту 8003
- Проверить, инициализирован ли `self._sfm` в SFM Adapter

**Проверка:**
```bash
# Проверить процесс SFM
ps aux | grep sfm

# Проверить порт 8003
curl http://localhost:8003/health
```

---

### Рекомендация 2: Проверить реализацию функции в SFM

**Статус:** ⏳ ТРЕБУЕТСЯ ПРОВЕРКА

**Действие:**
- Проверить, реализована ли функция `get_authentication_manager_profile` в SFM
- Проверить, правильно ли она работает

**Проверка:**
```bash
# Проверить функцию в authentication_manager.py
grep -r "get_authentication_manager_profile" /opt/aladdin-backend/app/security/
```

---

### Рекомендация 3: Обработать mock ответы на клиенте

**Статус:** ✅ РЕКОМЕНДУЕТСЯ

**Действие:**
- Добавить обработку mock ответов в `NetworkManager`
- Если ответ содержит `"source": "sfm_mock"` → использовать fallback данные
- Или пропустить запрос профиля для device-based пользователей

**Где обработать:**
- `Core/Network/NetworkManager.swift` - обработка декодирования
- `Core/Network/APIService.swift` - обработка ответа getUserProfile

---

### Рекомендация 4: Сделать профиль опциональным для device tokens

**Статус:** ✅ КРИТИЧНО

**Действие:**
- Device tokens могут не иметь профиля
- Сделать загрузку профиля опциональной
- Не показывать ошибку, если профиль недоступен
- **НЕ загружать профиль на онбординге!**

**Где изменить:**
- `Core/Managers/UserProfileManager.swift` - добавить проверку онбординга
- `ViewModels/ProfileViewModel.swift` - обработать отсутствие профиля

---

## 🎯 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ

### Исправление 1: Не загружать профиль на онбординге

**Файл:** `Core/Managers/UserProfileManager.swift`

**Изменение:**
```swift
private func loadProfileInBackground() {
    // ✅ BUILD 122: НЕ загружаем профиль на онбординге
    let hasCompletedOnboarding = UserDefaults.standard.bool(forKey: AppConfig.UserDefaultsKeys.hasCompletedOnboarding)
    guard hasCompletedOnboarding else {
        print("ℹ️ UserProfileManager: Онбординг не завершен - пропускаем загрузку профиля")
        return
    }
    
    DispatchQueue.global(qos: .background).async { [weak self] in
        guard let self = self else { return }
        
        if let token = AppConfig.authToken {
            self.loadProfileFromAPI(token: token)
        }
    }
}
```

---

### Исправление 2: Обработать mock ответы

**Файл:** `Core/Network/NetworkManager.swift`

**Изменение:**
```swift
// При декодировании ответа
if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
   let source = json["source"] as? String,
   source == "sfm_mock" {
    // Это mock ответ - не декодируем в UserProfile
    print("⚠️ NetworkManager: Получен mock ответ от SFM - пропускаем декодирование")
    completion(.failure(NetworkError.decodingError("Mock response from SFM")))
    return
}
```

---

### Исправление 3: Сделать профиль опциональным

**Файл:** `ViewModels/ProfileViewModel.swift`

**Изменение:**
```swift
func loadProfile() {
    logger.business("Loading user profile")
    isLoading = true
    errorMessage = nil
    
    apiService.getUserProfile { [weak self] result in
        DispatchQueue.main.async {
            self?.isLoading = false
            
            switch result {
            case .success(let profile):
                // Обработка успеха
            case .failure(let error):
                // ✅ BUILD 122: Не показываем ошибку для device tokens
                if let networkError = error as? NetworkError,
                   case .decodingError(let message) = networkError,
                   message.contains("sfm_mock") {
                    // Это mock ответ - не критично
                    print("ℹ️ ProfileViewModel: Mock ответ от SFM - используем значения по умолчанию")
                    // Используем значения по умолчанию
                } else {
                    self?.errorMessage = error.localizedDescription
                }
            }
        }
    }
}
```

---

## 📊 ВЫВОДЫ

### Основные проблемы:

1. **UserProfileManager загружает профиль на онбординге:**
   - ❌ Неправильно - профиль не нужен на онбординге
   - ❌ Вызывает ошибку декодирования
   - ✅ **РЕШЕНИЕ:** Добавить проверку онбординга

2. **SFM Adapter возвращает mock ответ:**
   - ⚠️ SFM недоступен или функция не реализована
   - ⚠️ Нужно проверить доступность SFM
   - ✅ **РЕШЕНИЕ:** Обработать mock ответы на клиенте

3. **Ошибка декодирования видна в логах:**
   - ⚠️ Не критично для работы приложения
   - ⚠️ Может влиять на пользовательский опыт
   - ✅ **РЕШЕНИЕ:** Сделать профиль опциональным

---

## 🎯 ПРИОРИТЕТ ИСПРАВЛЕНИЙ

1. **КРИТИЧНО:** Не загружать профиль на онбординге
2. **ВАЖНО:** Обработать mock ответы на клиенте
3. **РЕКОМЕНДУЕТСЯ:** Проверить доступность SFM на сервере
4. **РЕКОМЕНДУЕТСЯ:** Проверить реализацию функции в SFM

---

**Дата:** 17 марта 2026, 00:05  
**Статус:** 🔍 **АНАЛИЗ ЗАВЕРШЕН - ТРЕБУЮТСЯ ИСПРАВЛЕНИЯ**
