# 🛠️ КОМАНДЫ ДЛЯ ML СИСТЕМЫ

## 🚀 БЫСТРЫЙ СТАРТ

### 1. ПЕРЕХОД В ПАПКУ ПРОЕКТА:
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
```

### 2. ОТКРЫТЬ ПРОЕКТ В XCODE:
```bash
open ALADDIN.xcodeproj
```

### 3. ПРОВЕРИТЬ СТАТУС ПРОЕКТА:
```bash
# Проверка компиляции
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build

# Проверка ошибок
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep -E "(error:|warning:)" | head -20
```

---

## 🔧 ИСПРАВЛЕНИЕ КРИТИЧЕСКИХ ОШИБОК

### 1. ИСПРАВИТЬ ОШИБКИ SPACING/CORNERRADIUS:
```bash
# Файл: Screens/RewardsQuickModal.swift
# Добавить в начало файла:
echo "import SwiftUI" >> temp_import.txt
```

### 2. УДАЛИТЬ ДУБЛИКАТЫ:
```bash
# Удалить MainScreen из ContentView.swift
sed -i '' '/struct MainScreen/,/^}/d' ContentView.swift

# Удалить дубликат VPNViewModel
grep -n "struct VPNViewModel" ViewModels/VPNViewModel.swift
```

### 3. ИСПРАВИТЬ NOTIFICATIONMANAGER:
```bash
# Добавить import в NotificationSettingsScreen.swift
echo "import Foundation" >> temp_import.txt
```

---

## 📁 СОЗДАНИЕ ПАПОК В XCODE

### РУЧНОЕ СОЗДАНИЕ (РЕКОМЕНДУЕТСЯ):
1. **Открыть Xcode**
2. **Правый клик на ALADDIN** → New Group → "Shared"
3. **Правый клик на Shared** → New Group → "Styles"
4. **Правый клик на Shared** → New Group → "Components"
5. **Правый клик на Core** → New Group → "Notifications"

### АВТОМАТИЧЕСКОЕ СОЗДАНИЕ (ОПЦИОНАЛЬНО):
```bash
# Создать папки через Finder
mkdir -p "Shared/Styles"
mkdir -p "Shared/Components"
mkdir -p "Core/Notifications"
```

---

## 🎯 ДОБАВЛЕНИЕ ФАЙЛОВ В TARGET MEMBERSHIP

### РУЧНОЕ ДОБАВЛЕНИЕ (РЕКОМЕНДУЕТСЯ):
1. **Выбрать файл в Project Navigator**
2. **File Inspector (⌥⌘1)**
3. **Target Membership → поставить галочку ALADDIN**

### ФАЙЛЫ ДЛЯ ДОБАВЛЕНИЯ:
```bash
# Список файлов для добавления в Target Membership
echo "Файлы для добавления в Target Membership:"
echo "1. Shared/Styles/Spacing.swift"
echo "2. Shared/Styles/Colors.swift"
echo "3. Shared/Styles/Fonts.swift"
echo "4. Shared/Styles/DesignSystem.swift"
echo "5. Shared/Components/ALADDINNavigationBar.swift"
echo "6. Shared/Extensions/LinearGradient+Extensions.swift"
echo "7. Core/Notifications/NotificationManager.swift"
```

---

## 🧪 ТЕСТИРОВАНИЕ

### 1. ОЧИСТКА ПРОЕКТА:
```bash
# Очистка build папки
xcodebuild clean -project ALADDIN.xcodeproj -scheme ALADDIN

# Удаление DerivedData
rm -rf ~/Library/Developer/Xcode/DerivedData/ALADDIN-*
```

### 2. СБОРКА ПРОЕКТА:
```bash
# Сборка для симулятора
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build

# Сборка с подробным выводом
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build -verbose
```

### 3. ЗАПУСК В СИМУЛЯТОРЕ:
```bash
# Запуск приложения
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' -derivedDataPath ./build

# Запуск с тестами
xcodebuild test -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13'
```

---

## 📊 АНАЛИЗ ПРОЕКТА

### 1. ПРОВЕРКА СТРУКТУРЫ:
```bash
# Показать все Swift файлы
find . -name "*.swift" | sort

# Показать только экраны
find Screens -name "*.swift" | sort

# Показать только компоненты
find Shared -name "*.swift" | sort
```

### 2. ПРОВЕРКА ОШИБОК:
```bash
# Найти все ошибки компиляции
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep "error:"

# Найти все предупреждения
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep "warning:"

# Подсчитать ошибки
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep -c "error:"
```

### 3. ПРОВЕРКА РАЗМЕРОВ:
```bash
# Размер проекта
du -sh .

# Размер папки Screens
du -sh Screens/

# Размер папки Shared
du -sh Shared/
```

---

## 🔄 РЕЗЕРВНОЕ КОПИРОВАНИЕ

### 1. СОЗДАТЬ РЕЗЕРВНУЮ КОПИЮ:
```bash
# Создать backup папку
mkdir -p ../backup_$(date +%Y%m%d_%H%M%S)

# Копировать весь проект
cp -r . ../backup_$(date +%Y%m%d_%H%M%S)/

# Копировать только project.pbxproj
cp ALADDIN.xcodeproj/project.pbxproj ALADDIN.xcodeproj/project.pbxproj.backup_$(date +%Y%m%d_%H%M%S)
```

### 2. ВОССТАНОВИТЬ ИЗ РЕЗЕРВНОЙ КОПИИ:
```bash
# Восстановить project.pbxproj
cp ALADDIN.xcodeproj/project.pbxproj.backup_* ALADDIN.xcodeproj/project.pbxproj

# Восстановить весь проект
cp -r ../backup_*/* .
```

---

## 📱 РАБОТА С СИМУЛЯТОРОМ

### 1. СПИСОК ДОСТУПНЫХ СИМУЛЯТОРОВ:
```bash
# Показать все симуляторы
xcrun simctl list devices

# Показать только iPhone
xcrun simctl list devices | grep iPhone

# Показать только доступные
xcrun simctl list devices | grep "Booted\|Shutdown"
```

### 2. ЗАПУСК СИМУЛЯТОРА:
```bash
# Запустить iPhone 13
xcrun simctl boot "iPhone 13"

# Открыть симулятор
open -a Simulator
```

### 3. УСТАНОВКА ПРИЛОЖЕНИЯ:
```bash
# Установить приложение в симулятор
xcrun simctl install "iPhone 13" ./build/Products/Debug-iphonesimulator/ALADDIN.app

# Запустить приложение
xcrun simctl launch "iPhone 13" com.aladdin.app
```

---

## 🐛 ОТЛАДКА

### 1. ПОДРОБНЫЙ ВЫВОД:
```bash
# Сборка с подробным выводом
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build -verbose 2>&1 | tee build_log.txt

# Показать только ошибки
grep "error:" build_log.txt
```

### 2. ПРОВЕРКА ЗАВИСИМОСТЕЙ:
```bash
# Показать все импорты
grep -r "import " . --include="*.swift" | sort | uniq

# Показать все struct
grep -r "struct " . --include="*.swift" | sort

# Показать все class
grep -r "class " . --include="*.swift" | sort
```

### 3. ПРОВЕРКА ДУБЛИКАТОВ:
```bash
# Найти дубликаты struct
grep -r "struct " . --include="*.swift" | cut -d: -f2 | cut -d' ' -f2 | sort | uniq -d

# Найти дубликаты class
grep -r "class " . --include="*.swift" | cut -d: -f2 | cut -d' ' -f2 | sort | uniq -d
```

---

## 📈 МОНИТОРИНГ ПРОГРЕССА

### 1. СЧЕТЧИКИ:
```bash
# Количество Swift файлов
find . -name "*.swift" | wc -l

# Количество экранов
find Screens -name "*.swift" | wc -l

# Количество компонентов
find Shared -name "*.swift" | wc -l

# Количество ViewModels
find ViewModels -name "*.swift" | wc -l
```

### 2. СТАТУС КОМПИЛЯЦИИ:
```bash
# Проверить статус сборки
if xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build > /dev/null 2>&1; then
    echo "✅ Сборка успешна"
else
    echo "❌ Ошибки сборки"
    xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build 2>&1 | grep -c "error:"
fi
```

---

## 🎯 ФИНАЛЬНЫЕ КОМАНДЫ

### 1. ПОЛНАЯ ПРОВЕРКА:
```bash
# Очистка
xcodebuild clean -project ALADDIN.xcodeproj -scheme ALADDIN

# Сборка
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build

# Запуск
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' -derivedDataPath ./build
```

### 2. СОЗДАНИЕ ОТЧЕТА:
```bash
# Создать отчет о статусе
echo "=== ОТЧЕТ О СТАТУСЕ ПРОЕКТА ===" > project_status.txt
echo "Дата: $(date)" >> project_status.txt
echo "Количество Swift файлов: $(find . -name "*.swift" | wc -l)" >> project_status.txt
echo "Количество экранов: $(find Screens -name "*.swift" | wc -l)" >> project_status.txt
echo "Количество компонентов: $(find Shared -name "*.swift" | wc -l)" >> project_status.txt
echo "Статус сборки: $(if xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -destination 'platform=iOS Simulator,name=iPhone 13' build > /dev/null 2>&1; then echo "✅ Успешно"; else echo "❌ Ошибки"; fi)" >> project_status.txt
```

---

**🚀 ВСЕ КОМАНДЫ ГОТОВЫ! ML СИСТЕМА МОЖЕТ НАЧИНАТЬ РАБОТУ!**
