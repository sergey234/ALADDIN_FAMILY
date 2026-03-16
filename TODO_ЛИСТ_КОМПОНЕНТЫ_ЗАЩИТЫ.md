# ✅ TODO ЛИСТ: КОМПОНЕНТЫ ЗАЩИТЫ

**Дата создания:** 2026-03-14  
**Статус:** 🔴 В РАБОТЕ  
**Приоритет:** ВЫСОКИЙ

---

## 📋 ЗАДАЧА 1: ИСПРАВИТЬ ЛОКАЛИЗАЦИЮ ОШИБОК

### ✅ 1.1. Добавить отсутствующие ключи локализации

**Файл:** `Core/Localization/LocalizationManager.swift`

**Статус:** ⚠️ TODO

**Что сделать:**
- [ ] Добавить ключ `dark_web_error_temporary` в русский словарь
- [ ] Добавить ключ `dark_web_error_temporary` в английский словарь
- [ ] Проверить все остальные ключи локализации для ошибок
- [ ] Убедиться что все ключи используются правильно

**Ключи для добавления:**

**Русский:**
```swift
"dark_web_error_temporary": "Временная ошибка: %@",
```

**Английский:**
```swift
"dark_web_error_temporary": "Temporary error: %@",
```

---

### ✅ 1.2. Добавить обработку unauthorized во всех ViewModels

**Статус:** ⚠️ TODO

**Что сделать:**

#### 1.2.1. DarkWebMonitoringViewModel

**Файл:** `ViewModels/DarkWebMonitoringViewModel.swift`

- [ ] Добавить проверку токена перед загрузкой
- [ ] Добавить обработку `NetworkError.unauthorized`
- [ ] Показывать понятное сообщение на русском языке

**Код для добавления:**
```swift
func loadData(status: String? = nil, severity: String? = nil) async {
    // ✅ ИСПРАВЛЕНИЕ: Проверяем токен перед загрузкой
    guard AppConfig.authToken != nil else {
        errorMessage = "Требуется авторизация. Войдите в аккаунт для просмотра данных."
        return
    }
    
    isLoading = true
    errorMessage = nil
    
    do {
        // ... существующий код ...
    } catch {
        let networkError = NetworkError.from(error)
        
        // ✅ ИСПРАВЛЕНИЕ: Обрабатываем ошибку авторизации отдельно
        if case .unauthorized = networkError {
            errorMessage = "Требуется авторизация. Войдите в аккаунт для просмотра данных."
            return
        }
        
        // ... остальная обработка ошибок ...
    }
}
```

---

#### 1.2.2. IdentityTheftViewModel

**Файл:** `ViewModels/IdentityTheftViewModel.swift`

- [ ] Добавить проверку токена перед загрузкой
- [ ] Добавить обработку `NetworkError.unauthorized`
- [ ] Показывать понятное сообщение на русском языке

---

#### 1.2.3. PrivacyReportsViewModel

**Файл:** `ViewModels/PrivacyReportsViewModel.swift`

- [ ] Добавить проверку токена перед загрузкой в `loadLocationData()`
- [ ] Добавить проверку токена перед загрузкой в `loadCleanupData()`
- [ ] Добавить проверку токена перед загрузкой в `loadTrackerData()`
- [ ] Добавить обработку `NetworkError.unauthorized` во всех методах
- [ ] Показывать понятное сообщение на русском языке

---

#### 1.2.4. AICategoriesViewModel

**Файл:** `ViewModels/AICategoriesViewModel.swift`

- [ ] Добавить проверку токена перед загрузкой
- [ ] Добавить обработку `NetworkError.unauthorized`
- [ ] Показывать понятное сообщение на русском языке

---

## 📋 ЗАДАЧА 2: ПОДКЛЮЧИТЬ ВСЕ КОМПОНЕНТЫ К БД

### ✅ 2.1. Создать таблицы в PostgreSQL

**Файл:** `app/database/migrations/create_component_tables.sql` (новый файл)

**Статус:** ⚠️ TODO

**Что сделать:**
- [ ] Создать файл миграции
- [ ] Создать таблицу `dark_web_leaks`
- [ ] Создать таблицу `dark_web_scans`
- [ ] Создать таблицу `identity_theft_attempts`
- [ ] Создать таблицу `location_requests`
- [ ] Создать таблицу `data_cleanup_records`
- [ ] Создать таблицу `tracker_blocks`
- [ ] Создать таблицу `ai_category_reports`
- [ ] Создать индексы для всех таблиц
- [ ] Применить миграцию на сервере

---

### ✅ 2.2. Подключить Dark Web endpoints к БД

**Файл:** `app/security/api/routers/dark_web_monitoring_router.py`

**Статус:** ⚠️ TODO

**Что сделать:**
- [ ] Добавить `db: Session = Depends(get_db)` в `get_dark_web_stats()`
- [ ] Добавить `db: Session = Depends(get_db)` в `get_leaks()`
- [ ] Добавить `db: Session = Depends(get_db)` в `get_scans()`
- [ ] Добавить `db: Session = Depends(get_db)` в `resolve_leak()`
- [ ] Реализовать SQL запросы для получения статистики
- [ ] Реализовать SQL запросы для получения утечек
- [ ] Реализовать SQL запросы для получения сканирований
- [ ] Реализовать SQL запросы для обновления статуса утечки
- [ ] Добавить graceful degradation (возвращать пустой список если таблицы нет)
- [ ] Убрать mock данные

---

### ✅ 2.3. Подключить Identity Theft endpoints к БД

**Файл:** `app/security/api/routers/identity_theft_protection_router.py`

**Статус:** ⚠️ TODO

**Что сделать:**
- [ ] Добавить `db: Session = Depends(get_db)` в `get_identity_stats()`
- [ ] Добавить `db: Session = Depends(get_db)` в `get_identity_attempts()`
- [ ] Добавить `db: Session = Depends(get_db)` в `allow_attempt()`
- [ ] Добавить `db: Session = Depends(get_db)` в `block_attempt()`
- [ ] Реализовать SQL запросы для получения статистики
- [ ] Реализовать SQL запросы для получения попыток
- [ ] Реализовать SQL запросы для обновления статуса попытки
- [ ] Добавить graceful degradation
- [ ] Убрать mock данные

---

### ✅ 2.4. Подключить Location Bubble endpoints к БД

**Файл:** `app/security/api/routers/location_bubble_router.py`

**Статус:** ⚠️ TODO

**Что сделать:**
- [ ] Добавить `db: Session = Depends(get_db)` в `get_location_stats()`
- [ ] Добавить `db: Session = Depends(get_db)` в `get_location_requests()`
- [ ] Добавить `db: Session = Depends(get_db)` в `allow_location()`
- [ ] Добавить `db: Session = Depends(get_db)` в `block_location()`
- [ ] Реализовать SQL запросы для получения статистики
- [ ] Реализовать SQL запросы для получения запросов
- [ ] Реализовать SQL запросы для сохранения действий
- [ ] Добавить graceful degradation
- [ ] Убрать mock данные

---

### ✅ 2.5. Подключить Data Cleanup endpoints к БД

**Файл:** `app/security/api/routers/data_cleanup_router.py`

**Статус:** ⚠️ TODO

**Что сделать:**
- [ ] Добавить `db: Session = Depends(get_db)` в `get_cleanup_stats()`
- [ ] Добавить `db: Session = Depends(get_db)` в `get_cleanup_records()`
- [ ] Добавить `db: Session = Depends(get_db)` в `start_cleanup()`
- [ ] Реализовать SQL запросы для получения статистики
- [ ] Реализовать SQL запросы для получения записей
- [ ] Реализовать SQL запросы для сохранения новой очистки
- [ ] Добавить graceful degradation
- [ ] Убрать mock данные

---

### ✅ 2.6. Подключить Anti Tracker endpoints к БД

**Файл:** `app/security/api/routers/anti_tracker_router.py`

**Статус:** ⚠️ TODO

**Что сделать:**
- [ ] Добавить `db: Session = Depends(get_db)` в `get_tracker_stats()`
- [ ] Добавить `db: Session = Depends(get_db)` в `get_top_trackers()`
- [ ] Добавить `db: Session = Depends(get_db)` в `add_to_whitelist()`
- [ ] Реализовать SQL запросы для получения статистики
- [ ] Реализовать SQL запросы для получения топ трекеров
- [ ] Реализовать SQL запросы для обновления белого списка
- [ ] Добавить graceful degradation
- [ ] Убрать mock данные

---

### ✅ 2.7. Подключить AI Categories endpoints к БД

**Файл:** `app/security/api/routers/ai_categories_router.py`

**Статус:** ⚠️ TODO

**Что сделать:**
- [ ] Добавить `db: Session = Depends(get_db)` в `get_ai_stats()`
- [ ] Добавить `db: Session = Depends(get_db)` в `get_ai_reports()`
- [ ] Добавить `db: Session = Depends(get_db)` в `allow_category()`
- [ ] Добавить `db: Session = Depends(get_db)` в `block_category()`
- [ ] Реализовать SQL запросы для получения статистики
- [ ] Реализовать SQL запросы для получения отчетов
- [ ] Реализовать SQL запросы для обновления статуса категории
- [ ] Добавить graceful degradation
- [ ] Убрать mock данные

---

## 📋 ЗАДАЧА 3: РЕАЛИЗОВАТЬ РЕАЛЬНУЮ ФУНКЦИОНАЛЬНОСТЬ

**Статус:** ⚠️ TODO (низкий приоритет)

**Примечание:** Можно оставить mock данные для демо, реальная функциональность может быть реализована позже.

---

## 📊 ПРОГРЕСС ВЫПОЛНЕНИЯ

### **ЗАДАЧА 1: ИСПРАВИТЬ ЛОКАЛИЗАЦИЮ ОШИБОК**
- [ ] 1.1. Добавить отсутствующие ключи локализации
- [ ] 1.2.1. DarkWebMonitoringViewModel - обработка unauthorized
- [ ] 1.2.2. IdentityTheftViewModel - обработка unauthorized
- [ ] 1.2.3. PrivacyReportsViewModel - обработка unauthorized
- [ ] 1.2.4. AICategoriesViewModel - обработка unauthorized

**Прогресс:** 0/5 (0%)

---

### **ЗАДАЧА 2: ПОДКЛЮЧИТЬ ВСЕ КОМПОНЕНТЫ К БД**
- [ ] 2.1. Создать таблицы в PostgreSQL
- [ ] 2.2. Подключить Dark Web endpoints к БД
- [ ] 2.3. Подключить Identity Theft endpoints к БД
- [ ] 2.4. Подключить Location Bubble endpoints к БД
- [ ] 2.5. Подключить Data Cleanup endpoints к БД
- [ ] 2.6. Подключить Anti Tracker endpoints к БД
- [ ] 2.7. Подключить AI Categories endpoints к БД

**Прогресс:** 0/7 (0%)

---

### **ЗАДАЧА 3: РЕАЛИЗОВАТЬ РЕАЛЬНУЮ ФУНКЦИОНАЛЬНОСТЬ**
- [ ] 3.1. Dark Web Monitoring - реальная интеграция
- [ ] 3.2. Identity Theft Protection - реальная интеграция
- [ ] 3.3. Location Bubble - реальная генерация пузырей
- [ ] 3.4. Data Cleanup - реальная очистка данных
- [ ] 3.5. Anti Tracker - реальная блокировка трекеров
- [ ] 3.6. AI Categories - реальная категоризация

**Прогресс:** 0/6 (0%)

---

## 📊 ОБЩИЙ ПРОГРЕСС

**Всего задач:** 18  
**Выполнено:** 0  
**В работе:** 0  
**Осталось:** 18  

**Прогресс:** 0/18 (0%)

---

## ✅ ПРИМЕЧАНИЯ

1. ✅ **ViewModels УЖЕ СУЩЕСТВУЮТ** - отдельные ViewModels для Location Bubble, Data Cleanup, Anti Tracker НЕ НУЖНЫ
2. ✅ **Локализация ошибок НЕ ПОЛНАЯ** - нужно добавить отсутствующие ключи
3. ✅ **Обработка unauthorized НЕ ВЕЗДЕ** - нужно добавить в остальные ViewModels
4. ✅ **Подключение к БД НЕ РЕАЛИЗОВАНО** - нужно создать таблицы и подключить endpoints
5. ✅ **Реальная функциональность НЕ РЕАЛИЗОВАНА** - можно оставить mock данные для демо

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

1. ✅ Начать с задачи 1.1 - добавить отсутствующие ключи локализации
2. ✅ Затем задача 1.2 - добавить обработку unauthorized во всех ViewModels
3. ✅ Затем задача 2.1 - создать таблицы в PostgreSQL
4. ✅ Затем задачи 2.2-2.7 - подключить endpoints к БД

---

**Последнее обновление:** 2026-03-14
