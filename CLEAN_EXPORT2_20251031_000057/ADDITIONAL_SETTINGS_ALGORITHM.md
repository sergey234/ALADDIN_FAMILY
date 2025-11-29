# 🎯 АЛГОРИТМ РАБОТЫ С ДОПОЛНИТЕЛЬНЫМИ НАСТРОЙКАМИ РОДИТЕЛЬСКОГО КОНТРОЛЯ

## 📋 ОБЩЕЕ ОПИСАНИЕ

Этот алгоритм описывает, как добавлять интерактивные дополнительные настройки в модальные окна SwiftUI с полным функционалом. Все изменения основаны на HTML wireframe `14_parental_control_screen.html`.

## 🏗️ СТРУКТУРА ИЗМЕНЕНИЙ

### 1. **ДОБАВЛЕНИЕ STATE ПЕРЕМЕННЫХ**

```swift
// В AdditionalModal добавляем новые @State переменные:
@State private var showingAccessRequests = false
@State private var isDeviceBlocked = false
@State private var isDataDeleted = false
@State private var accessRequests = [
    AccessRequest(app: "Instagram", time: "10 мин назад", status: .pending),
    AccessRequest(app: "YouTube", time: "5 мин назад", status: .pending)
]
```

**ПРИНЦИП:** Каждая интерактивная функция требует собственной @State переменной для отслеживания состояния.

### 2. **ОБНОВЛЕНИЕ КАРТОЧЕК С ДИНАМИЧЕСКИМ КОНТЕНТОМ**

```swift
// Удалённая блокировка - динамическая иконка и текст
additionalSettingCard(
    icon: isDeviceBlocked ? "🔓" : "🔒",
    title: "Удалённая блокировка",
    subtitle: isDeviceBlocked ? "Телефон разблокирован" : "Заблокировать телефон ребёнка",
    buttonText: isDeviceBlocked ? "Разблокирован" : "Блокировать",
    buttonColor: isDeviceBlocked ? .green : .red,
    action: { 
        if isDeviceBlocked {
            isDeviceBlocked = false
        } else {
            showingRemoteBlockAlert = true 
        }
    }
)
```

**ПРИНЦИП:** Используем тернарные операторы для изменения UI в зависимости от состояния.

### 3. **ДОБАВЛЕНИЕ РЕАЛЬНЫХ АЛЕРТОВ С ДЕЙСТВИЯМИ**

```swift
.alert("🔒 Удалённая блокировка", isPresented: $showingRemoteBlockAlert) {
    Button("Подтвердить", role: .destructive) {
        isDeviceBlocked = true
        // Здесь можно добавить реальную логику блокировки через API
        print("📱 Устройство заблокировано удалённо")
    }
    Button("Отмена", role: .cancel) { }
} message: {
    Text("Вы уверены, что хотите заблокировать телефон ребёнка? Это действие можно будет отменить только с вашего устройства.")
}
```

**ПРИНЦИП:** Каждый алерт должен изменять состояние и выполнять реальные действия.

### 4. **СОЗДАНИЕ СТРУКТУР ДАННЫХ**

```swift
// MARK: - Data Models
struct AccessRequest: Identifiable {
    let id = UUID()
    let app: String
    let time: String
    var status: RequestStatus
}

enum RequestStatus {
    case pending
    case approved
    case rejected
}
```

**ПРИНЦИП:** Создаем типизированные структуры для сложных данных.

### 5. **СОЗДАНИЕ МОДАЛЬНЫХ ОКОН С ПОЛНЫМ ФУНКЦИОНАЛОМ**

```swift
struct YouTubeSettingsModal: View {
    @Environment(\.dismiss) private var dismiss
    @State private var ageRestriction = "12+"
    @State private var isFilterEnabled = true
    @State private var showingSuccessAlert = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Toggle для включения/выключения
                    Toggle("Включить фильтрацию", isOn: $isFilterEnabled)
                    
                    if isFilterEnabled {
                        // Условный контент
                        Picker("Возраст", selection: $ageRestriction) {
                            Text("6+").tag("6+")
                            Text("12+").tag("12+")
                            Text("16+").tag("16+")
                            Text("18+").tag("18+")
                        }
                        .pickerStyle(SegmentedPickerStyle())
                    }
                    
                    // Кнопка сохранения с алертом
                    Button("Сохранить настройки") {
                        showingSuccessAlert = true
                        print("📺 YouTube настройки сохранены: \(ageRestriction)")
                    }
                }
            }
        }
        .alert("Настройки сохранены", isPresented: $showingSuccessAlert) {
            Button("OK") { }
        } message: {
            Text("Настройки YouTube фильтрации успешно сохранены!")
        }
    }
}
```

**ПРИНЦИП:** Каждое модальное окно должно быть полностью функциональным с сохранением настроек.

## 🔧 ДЕТАЛЬНЫЕ ПРИМЕРЫ РЕАЛИЗАЦИИ

### **ПРИМЕР 1: Удалённая блокировка**

**Что делаем:**
1. Добавляем @State переменную `isDeviceBlocked`
2. Создаем динамическую карточку с изменяемой иконкой и текстом
3. Добавляем алерт с подтверждением
4. Реализуем логику блокировки/разблокировки

**Код:**
```swift
// State
@State private var isDeviceBlocked = false
@State private var showingRemoteBlockAlert = false

// Динамическая карточка
additionalSettingCard(
    icon: isDeviceBlocked ? "🔓" : "🔒",
    title: "Удалённая блокировка",
    subtitle: isDeviceBlocked ? "Телефон разблокирован" : "Заблокировать телефон ребёнка",
    buttonText: isDeviceBlocked ? "Разблокирован" : "Блокировать",
    buttonColor: isDeviceBlocked ? .green : .red,
    action: { 
        if isDeviceBlocked {
            isDeviceBlocked = false
        } else {
            showingRemoteBlockAlert = true 
        }
    }
)

// Алерт с действием
.alert("🔒 Удалённая блокировка", isPresented: $showingRemoteBlockAlert) {
    Button("Подтвердить", role: .destructive) {
        isDeviceBlocked = true
        print("📱 Устройство заблокировано удалённо")
    }
    Button("Отмена", role: .cancel) { }
}
```

### **ПРИМЕР 2: Запросы доступа**

**Что делаем:**
1. Создаем структуру данных `AccessRequest`
2. Добавляем массив запросов в @State
3. Создаем модальное окно для обработки запросов
4. Реализуем функции одобрения/отклонения

**Код:**
```swift
// Структура данных
struct AccessRequest: Identifiable {
    let id = UUID()
    let app: String
    let time: String
    var status: RequestStatus
}

enum RequestStatus {
    case pending, approved, rejected
}

// State
@State private var accessRequests = [
    AccessRequest(app: "Instagram", time: "10 мин назад", status: .pending),
    AccessRequest(app: "YouTube", time: "5 мин назад", status: .pending)
]

// Динамический счетчик
subtitle: "\(accessRequests.filter { $0.status == .pending }.count) новых запроса на разблокировку",
buttonText: "\(accessRequests.filter { $0.status == .pending }.count)",

// Модальное окно
.sheet(isPresented: $showingAccessRequests) {
    AccessRequestsModal(accessRequests: $accessRequests)
}
```

### **ПРИМЕР 3: YouTube фильтрация**

**Что делаем:**
1. Создаем модальное окно с настройками
2. Добавляем Toggle для включения/выключения
3. Используем условный рендеринг для показа настроек
4. Добавляем Picker для выбора возраста
5. Реализуем сохранение с алертом

**Код:**
```swift
struct YouTubeSettingsModal: View {
    @State private var ageRestriction = "12+"
    @State private var isFilterEnabled = true
    @State private var showingSuccessAlert = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Основной переключатель
                    Toggle("Включить фильтрацию", isOn: $isFilterEnabled)
                    
                    // Условный контент
                    if isFilterEnabled {
                        Picker("Возраст", selection: $ageRestriction) {
                            Text("6+").tag("6+")
                            Text("12+").tag("12+")
                            Text("16+").tag("16+")
                            Text("18+").tag("18+")
                        }
                        .pickerStyle(SegmentedPickerStyle())
                    }
                    
                    // Кнопка сохранения
                    Button("Сохранить настройки") {
                        showingSuccessAlert = true
                        print("📺 YouTube настройки сохранены: \(ageRestriction)")
                    }
                }
            }
        }
        .alert("Настройки сохранены", isPresented: $showingSuccessAlert) {
            Button("OK") { }
        }
    }
}
```

### **ПРИМЕР 4: Режим домашнего задания**

**Что делаем:**
1. Создаем сложное модальное окно с множественными настройками
2. Добавляем DatePicker для времени
3. Используем LazyVGrid для выбора дней недели
4. Реализуем Set<String> для множественного выбора
5. Добавляем условный рендеринг для дополнительных настроек

**Код:**
```swift
struct HomeworkModeModal: View {
    @State private var isHomeworkModeEnabled = false
    @State private var homeworkStartTime = Date()
    @State private var homeworkEndTime = Date().addingTimeInterval(3600)
    @State private var selectedDays: Set<String> = []
    @State private var showingSuccessAlert = false
    
    let weekDays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Основной переключатель
                    Toggle("Включить режим", isOn: $isHomeworkModeEnabled)
                    
                    if isHomeworkModeEnabled {
                        // Время работы
                        DatePicker("Время начала", selection: $homeworkStartTime, displayedComponents: .hourAndMinute)
                        DatePicker("Время окончания", selection: $homeworkEndTime, displayedComponents: .hourAndMinute)
                        
                        // Дни недели с множественным выбором
                        LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 8) {
                            ForEach(weekDays, id: \.self) { day in
                                Button(action: {
                                    if selectedDays.contains(day) {
                                        selectedDays.remove(day)
                                    } else {
                                        selectedDays.insert(day)
                                    }
                                }) {
                                    Text(day)
                                        .background(selectedDays.contains(day) ? Color.green : Color.gray.opacity(0.3))
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
```

## 🎯 КЛЮЧЕВЫЕ ПРИНЦИПЫ

### **1. STATE MANAGEMENT**
- Каждая интерактивная функция = отдельная @State переменная
- Используем @Binding для передачи данных между модальными окнами
- Все изменения состояния должны быть реактивными

### **2. УСЛОВНЫЙ РЕНДЕРИНГ**
```swift
if isFilterEnabled {
    // Показываем настройки только если включено
}
```

### **3. ДИНАМИЧЕСКИЙ КОНТЕНТ**
```swift
icon: isDeviceBlocked ? "🔓" : "🔒"
buttonText: isDeviceBlocked ? "Разблокирован" : "Блокировать"
```

### **4. МОДАЛЬНЫЕ ОКНА**
- Каждое модальное окно = отдельная структура
- Используем @Environment(\.dismiss) для закрытия
- Добавляем алерты для подтверждения действий

### **5. СОХРАНЕНИЕ НАСТРОЕК**
- Все настройки должны сохраняться в @State
- Добавляем алерты успешного сохранения
- Выводим логи в консоль для отладки

## 🚀 ПОШАГОВЫЙ АЛГОРИТМ ДЛЯ НОВЫХ НАСТРОЕК

### **ШАГ 1: АНАЛИЗ HTML WIREFRAME**
1. Изучите HTML wireframe
2. Определите все интерактивные элементы
3. Создайте список необходимых @State переменных

### **ШАГ 2: ДОБАВЛЕНИЕ STATE**
```swift
@State private var newSettingEnabled = false
@State private var showingNewModal = false
@State private var newSettingValue = ""
```

### **ШАГ 3: ОБНОВЛЕНИЕ КАРТОЧКИ**
```swift
additionalSettingCard(
    icon: "🆕",
    title: "Новая настройка",
    subtitle: newSettingEnabled ? "Включено" : "Выключено",
    buttonText: newSettingEnabled ? "Настроено" : "Настроить",
    buttonColor: newSettingEnabled ? .green : .blue,
    action: { showingNewModal = true }
)
```

### **ШАГ 4: СОЗДАНИЕ МОДАЛЬНОГО ОКНА**
```swift
struct NewSettingModal: View {
    @Environment(\.dismiss) private var dismiss
    @State private var settingValue = ""
    @State private var showingSuccessAlert = false
    
    var body: some View {
        NavigationView {
            VStack {
                // Настройки
                TextField("Значение", text: $settingValue)
                
                Button("Сохранить") {
                    showingSuccessAlert = true
                    print("🆕 Новая настройка сохранена: \(settingValue)")
                }
            }
        }
        .alert("Сохранено", isPresented: $showingSuccessAlert) {
            Button("OK") { }
        }
    }
}
```

### **ШАГ 5: ПОДКЛЮЧЕНИЕ МОДАЛЬНОГО ОКНА**
```swift
.sheet(isPresented: $showingNewModal) {
    NewSettingModal()
}
```

## ⚠️ ВАЖНЫЕ МОМЕНТЫ

### **1. ИЗБЕГАЙТЕ ОШИБОК**
- Всегда проверяйте уникальность имен структур
- Используйте правильные типы данных для @State
- Не забывайте добавлять @Environment(\.dismiss)

### **2. ОПТИМИЗАЦИЯ**
- Используйте LazyVGrid для больших списков
- Применяйте условный рендеринг для экономии ресурсов
- Группируйте связанные настройки в отдельные секции

### **3. ПОЛЬЗОВАТЕЛЬСКИЙ ОПЫТ**
- Добавляйте алерты для всех важных действий
- Используйте понятные иконки и тексты
- Обеспечивайте обратную связь при сохранении

## 📝 ЧЕКЛИСТ ДЛЯ ПРОВЕРКИ

- [ ] Все @State переменные добавлены
- [ ] Карточки обновлены с динамическим контентом
- [ ] Модальные окна созданы и подключены
- [ ] Алерты добавлены для всех действий
- [ ] Сохранение настроек реализовано
- [ ] Логирование добавлено для отладки
- [ ] Нет ошибок компиляции
- [ ] Все функции протестированы

## 🎯 РЕЗУЛЬТАТ

После применения этого алгоритма вы получите:
- Полностью интерактивные дополнительные настройки
- Реальные действия при нажатии кнопок
- Красивые модальные окна с настройками
- Сохранение всех изменений
- Обратную связь для пользователя

**Этот алгоритм можно применять для любых дополнительных настроек в любых экранах приложения!**
