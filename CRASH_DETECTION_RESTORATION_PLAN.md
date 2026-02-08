# 📋 **ДЕТАЛЬНЫЙ ПЛАН ВОССТАНОВЛЕНИЯ CRASH DETECTION ФУНКЦИОНАЛЬНОСТИ**

## 🎯 **КОНТЕКСТ ЗАДАЧИ:**

**Текущий статус проекта ALADDIN iOS:**
- ✅ Проект компилируется без ошибок
- ✅ Основная логика Crash Detection работает (~70%)
- 🚫 Geofencing отключено (0% готовности)
- 🚫 Settings Modal отключен (0% готовности)
- 🚫 Emergency actions не реализованы (0% готовности)

**Цель:** Восстановить полную функциональность Crash Detection до 100% готовности.

---

## 📊 **АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ:**

### **Что работает:**
1. **CrashDetectionManager** - обнаружение аварий по G-force
2. **Battery optimization** - мониторинг только при скорости >50km/h
3. **Sensitivity settings** - программная настройка (low/medium/high)
4. **Emergency contacts** - система хранения контактов
5. **Emergency notifications** - настройки уведомлений

### **Что отключено/не работает:**
1. **Geofencing** - геозонный мониторинг отключен
2. **Settings Modal** - UI настройки отключены
3. **Emergency calls** - реальные действия при аварии отсутствуют

---

## 🚀 **ДЕТАЛЬНЫЙ ПЛАН ВОССТАНОВЛЕНИЯ**

### **ЭТАП 1: ВОССТАНОВЛЕНИЕ SETTINGS MODAL (ПРИОРИТЕТ 1)**
**Оценка времени:** 15-20 минут  
**Сложность:** Низкая  
**Зависимости:** Xcode, Swift compiler

#### **1.1 Анализ текущего состояния:**
- Файл `Shared/Components/Modals/CrashDetectionSettingsModal.swift` существует
- Полностью функционален с интеграцией CrashDetectionManager
- Раскомментирован в `NetworkProtectionScreen.swift`
- НЕТ ошибок компиляции в самом модале

#### **1.2 Необходимые действия:**
```swift
// В NetworkProtectionScreen.swift - раскомментировать:
.sheet(isPresented: $showCrashDetectionSettings) {
    CrashDetectionSettingsModal(
        componentId: "crash_detection_agent",
        isPresented: $showCrashDetectionSettings
    )
    .environmentObject(localizationManager)
}
```

#### **1.3 Исправить UI интеграцию:**
```swift
// В SecurityFeatureRow для crash_detection_agent:
// Изменить: hasSettings: false
// На: hasSettings: true
//
// Добавить: onSettingsTap: { showCrashDetectionSettings = true }
```

#### **1.4 Тестирование:**
- Запустить приложение
- Перейти в Network Protection
- Нажать на Crash Detection
- Проверить наличие кнопки "Настроить"
- Открыть модал и проверить все опции

---

### **ЭТАП 2: ВОССТАНОВЛЕНИЕ GEOFENCING (ПРИОРИТЕТ 2)**
**Оценка времени:** 30-45 минут  
**Сложность:** Средняя  
**Зависимости:** CoreLocation framework, LocationManager

#### **2.1 Анализ проблемы:**
- `GeofenceItem` не определен как тип
- В `CrashDetectionManager.swift` закомментирован код геозоны
- `GeofenceModels.swift` имеет ссылки на несуществующий тип

#### **2.2 Вариант решения A: Определить GeofenceItem (Рекомендуемый)**
```swift
// Добавить в Core/Models/GeofenceModels.swift:
struct GeofenceItem: Identifiable, Codable {
    let id: UUID
    let identifier: String
    let center: CLLocationCoordinate2D
    let radius: Double
    let type: GeofenceType

    enum GeofenceType: String, Codable {
        case crashDetection
        case home
        case work
        // другие типы
    }

    init(identifier: String, center: CLLocationCoordinate2D, radius: Double, type: GeofenceType = .crashDetection) {
        self.id = UUID()
        self.identifier = identifier
        self.center = center
        self.radius = radius
        self.type = type
    }
}
```

#### **2.3 Вариант решения B: Использовать CLCircularRegion напрямую**
```swift
// В CrashDetectionManager заменить GeofenceItem на CLCircularRegion
let region = CLCircularRegion(
    center: location.coordinate,
    radius: geofenceRadius,
    identifier: "crash_detection_zone"
)
locationManager.startMonitoring(for: region)
```

#### **2.4 Раскомментировать код в CrashDetectionManager:**
```swift
// Раскомментировать блок в startMonitoring():
do {
    let geofence = GeofenceItem(
        identifier: "crash_detection_zone",
        center: location.coordinate,
        radius: geofenceRadius,
        type: .crashDetection
    )

    try locationManager.startMonitoring(geofence: geofence, center: location.coordinate)
    print("✅ CrashDetectionManager: Геозона настроена")
} catch {
    print("⚠️ CrashDetectionManager: Ошибка настройки геозоны: \(error.localizedDescription)")
    // Продолжаем без геозоны
}
```

#### **2.5 Тестирование геозоны:**
- Запустить приложение на реальном устройстве
- Включить геолокацию
- Проверить логи о настройке геозоны
- Проверить мониторинг входа/выхода из зоны

---

### **ЭТАП 3: РЕАЛИЗАЦИЯ EMERGENCY ACTIONS (ПРИОРИТЕТ 3)**
**Оценка времени:** 60-90 минут  
**Сложность:** Высокая  
**Зависимости:** CallKit, MessageUI, URL schemes

#### **3.1 Анализ текущего состояния:**
- `CrashDetectionAlertModal` только показывает UI
- Нет реальных действий (звонки, SMS, отправка данных)
- Отсутствует интеграция с EmergencyContactsView

#### **3.2 Реализация звонка экстренным службам:**
```swift
// В CrashDetectionAlertModal добавить:
Button("🚨 112") {
    isPresented = false

    // Звонок экстренным службам
    if let url = URL(string: "tel://112") {
        UIApplication.shared.open(url, options: [:], completionHandler: nil)
    }

    // Отправить уведомление в систему
    sendEmergencyNotification()
}
```

#### **3.3 Реализация отправки SMS контактам:**
```swift
// Добавить функцию в CrashDetectionAlertModal:
private func sendEmergencySMS() {
    // Получить контакты из EmergencyContactsView
    let emergencyContacts = getEmergencyContacts()

    for contact in emergencyContacts {
        if contact.channels.contains("sms") {
            sendSMS(to: contact.phone, message: getEmergencyMessage())
        }
    }
}
```

#### **3.4 Реализация отправки данных на сервер:**
```swift
// Добавить в CrashDetectionManager:
func sendCrashDataToServer(_ crashData: CrashData) async {
    do {
        // Отправить данные аварии на сервер
        let endpoint = AppConfig.Endpoint.crashReport ?? "/api/crash-report"

        let report = CrashReport(
            timestamp: Date(),
            location: currentLocation,
            gForce: crashData.gForce,
            speed: crashData.speed,
            deviceInfo: getDeviceInfo()
        )

        try await APIService.shared.sendCrashReport(report)
        print("✅ Crash data sent to server")

    } catch {
        print("❌ Failed to send crash data: \(error.localizedDescription)")
    }
}
```

#### **3.5 Интеграция с EmergencyContactsView:**
```swift
// Добавить в CrashDetectionAlertModal:
private func getEmergencyContacts() -> [EmergencyContact] {
    // Получить контакты из UserDefaults или через API
    // Интегрировать с EmergencyContactsView логикой
}

private func notifyEmergencyContacts() {
    let contacts = getEmergencyContacts()

    for contact in contacts {
        // Отправить push уведомление или SMS
        sendEmergencyNotification(to: contact)
    }
}
```

#### **3.6 Тестирование emergency actions:**
- Симулировать аварию в тестовой среде
- Проверить звонок (без реального вызова)
- Проверить SMS отправку (с тестовыми номерами)
- Проверить отправку данных на сервер
- Проверить уведомления контактам

---

## 📋 **TODO ЛИСТ ДЛЯ ВЫПОЛНЕНИЯ**

### **ФАЗА 1: Подготовка (5 минут)**
- [ ] Проверить текущий статус компиляции
- [ ] Создать бэкап перед изменениями
- [ ] Открыть Xcode проект

### **ФАЗА 2: Settings Modal (15 минут)**
- [ ] Раскомментировать код в NetworkProtectionScreen.swift
- [ ] Изменить hasSettings: false → true для crash_detection_agent
- [ ] Добавить onSettingsTap обработчик
- [ ] Скомпилировать и проверить открытие модала
- [ ] Протестировать все настройки чувствительности

### **ФАЗА 3: Geofencing (30 минут)**
- [ ] Выбрать вариант реализации (GeofenceItem vs CLCircularRegion)
- [ ] Добавить определение типа в GeofenceModels.swift
- [ ] Раскомментировать код в CrashDetectionManager
- [ ] Проверить интеграцию с LocationManager
- [ ] Скомпилировать и протестировать на устройстве

### **ФАЗА 4: Emergency Actions (60 минут)**
- [ ] Реализовать звонок экстренным службам (tel://112)
- [ ] Добавить отправку SMS контактам
- [ ] Реализовать отправку данных на сервер
- [ ] Интегрировать с EmergencyContactsView
- [ ] Добавить логирование всех действий

### **ФАЗА 5: Тестирование (30 минут)**
- [ ] Тест Settings Modal - все опции работают
- [ ] Тест Geofencing - мониторинг зон работает
- [ ] Тест Emergency Actions - симуляция без реальных звонков
- [ ] Тест полной интеграции - от обнаружения до действий
- [ ] Проверка на разных устройствах/симуляторах

### **ФАЗА 6: Финализация (10 минут)**
- [ ] Очистить отладочный код
- [ ] Добавить финальные комментарии
- [ ] Создать документацию изменений
- [ ] Финальное тестирование

---

## 🎯 **КРИТЕРИИ ГОТОВНОСТИ:**

### **Settings Modal (100% готовность):**
- ✅ Модал открывается из Network Protection
- ✅ Все 3 уровня чувствительности (Low/Medium/High)
- ✅ Сохранение настроек работает
- ✅ Локализация на русском/английском

### **Geofencing (100% готовность):**
- ✅ Геозона создается при старте мониторинга
- ✅ Мониторинг входа/выхода работает
- ✅ Интеграция с Crash Detection логика
- ✅ Обработка ошибок разрешений геолокации

### **Emergency Actions (100% готовность):**
- ✅ Звонок экстренным службам (tel://112)
- ✅ SMS отправка emergency контактам
- ✅ Отправка crash data на сервер
- ✅ Push уведомления контактам
- ✅ Полная интеграция с EmergencyContactsView

---

## ⚠️ **ВОЗМОЖНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ:**

### **Проблема 1: Ошибки компиляции**
**Решение:** Проверять каждое изменение компиляцией

### **Проблема 2: Разрешения iOS**
**Решение:** Добавить в Info.plist разрешения на звонки, SMS, геолокацию

### **Проблема 3: Тестирование на симуляторе**
**Решение:** Основное тестирование на реальном устройстве

### **Проблема 4: Безопасность данных**
**Решение:** Шифрование контактов, безопасная отправка данных

---

## 📈 **ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:**

После выполнения плана Crash Detection будет иметь:
- **100% Settings Modal** - полная настройка через UI
- **100% Geofencing** - геозонный мониторинг
- **100% Emergency Actions** - реальные действия при аварии

**Итоговый статус: Crash Detection - 100% готов к продакшену!** 🚗✅

---

*План составлен: 8 февраля 2026*  
*Оценка времени выполнения: 2.5-3 часа*  
*Приоритет выполнения: Settings Modal → Geofencing → Emergency Actions* 📋✅