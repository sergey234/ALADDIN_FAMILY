# 🛠️ КОМАНДЫ ДЛЯ РАБОТЫ С ПРОЕКТОМ

## 📍 РАБОЧАЯ ДИРЕКТОРИЯ
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
```

## 🔨 СБОРКА ПРОЕКТА
```bash
# Собрать проект
xcodebuild -project ALADDIN.xcodeproj -scheme ALADDIN -sdk iphonesimulator build

# Проверить результат
echo "BUILD SUCCEEDED" || echo "BUILD FAILED"
```

## 📱 РАБОТА С СИМУЛЯТОРОМ
```bash
# Запустить симулятор
xcrun simctl boot "iPhone 12"

# Установить приложение
xcrun simctl install booted /Users/sergejhlystov/Library/Developer/Xcode/DerivedData/ALADDIN-*/Build/Products/Debug-iphonesimulator/ALADDIN.app

# Запустить приложение
xcrun simctl launch booted family.aladdin.ios
```

## 📋 КОПИРОВАНИЕ ФАЙЛОВ
```bash
# Копировать исправленный MainScreen
cp Screens/01_MainScreen.swift ALADDIN/Screens/01_MainScreen.swift
```

## 🧹 ОЧИСТКА КЭША
```bash
# Очистить кэш Xcode
rm -rf ~/Library/Developer/Xcode/DerivedData/ALADDIN-*

# Перезагрузить симулятор
xcrun simctl shutdown all
xcrun simctl boot "iPhone 12"
```

## 📊 ПРОВЕРКА ЛОГОВ
```bash
# Проверить логи приложения
xcrun simctl spawn booted log stream --predicate 'processImagePath contains "ALADDIN"' --style compact
```

## 🎯 ПОСЛЕДОВАТЕЛЬНОСТЬ ДЕЙСТВИЙ

1. **Редактировать** `Screens/01_MainScreen.swift`
2. **Копировать** в `ALADDIN/Screens/01_MainScreen.swift`
3. **Собрать** проект
4. **Установить** на симулятор
5. **Запустить** приложение
6. **Проверить** результат

## ⚠️ ВАЖНО

- Всегда копировать файл после изменений
- Проверять результат сборки
- Устанавливать на симулятор после сборки

