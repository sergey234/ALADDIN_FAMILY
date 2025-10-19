# 📁 СТРУКТУРА ПРОЕКТА ALADDIN

## 🗂️ ОСНОВНЫЕ ФАЙЛЫ

```
ALADDIN_iOS/
├── ALADDINApp.swift                    ← Точка входа приложения
├── Screens/
│   └── 01_MainScreen.swift            ← Главный экран (ПРОБЛЕМНЫЙ)
├── ALADDIN.xcodeproj/
│   └── project.pbxproj                ← Конфигурация проекта
└── ALADDIN/
    └── Screens/
        └── 01_MainScreen.swift        ← Копия для компиляции
```

## 🔧 КОНФИГУРАЦИЯ ПРОЕКТА

### ALADDINApp.swift
```swift
import SwiftUI

@main
struct ALADDINApp: App {
    var body: some Scene {
        WindowGroup {
            MainScreen()  // Вызывает MainScreen
        }
    }
}
```

### project.pbxproj
- Компилирует: `ALADDIN/Screens/01_MainScreen.swift`
- Путь: `"ALADDIN/Screens/01_MainScreen.swift"`
- Включен в: `PBXSourcesBuildPhase`

## 📱 ТЕКУЩЕЕ СОСТОЯНИЕ

- ✅ Приложение запускается
- ✅ Показывает синий экран с градиентом
- ❌ Layout НЕ исправлен
- ❌ Элементы в неправильных позициях

## 🎯 ФАЙЛЫ ДЛЯ ИЗУЧЕНИЯ

1. **Screens/01_MainScreen.swift** - основной файл для редактирования
2. **ALADDIN/Screens/01_MainScreen.swift** - файл для компиляции
3. **ALADDINApp.swift** - точка входа
4. **ALADDIN.xcodeproj/project.pbxproj** - конфигурация

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

- Изменения нужно делать в `Screens/01_MainScreen.swift`
- Затем копировать в `ALADDIN/Screens/01_MainScreen.swift`
- Пересобирать проект командой `xcodebuild`
- Устанавливать на симулятор

