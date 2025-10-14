# 🔍 Проверка качества кода мобильных приложений ALADDIN

## 📋 Обзор

Для мобильных приложений используются специальные инструменты проверки кода, отличные от flake8 (который используется для Python):

### **iOS (Swift + Xcode):**
- **SwiftLint** - основной линтер для Swift
- **SwiftFormat** - форматирование кода
- **Xcode Analyzer** - встроенный анализатор

### **Android (Kotlin + Android Studio):**
- **Detekt** - основной линтер для Kotlin
- **ktlint** - форматирование Kotlin
- **Android Lint** - встроенный анализатор

## 🚀 Быстрый старт

### 1. Установка инструментов

```bash
# macOS (через Homebrew)
brew install swiftlint swiftformat ktlint

# Или через CocoaPods для iOS
cd mobile/ios
pod install
```

### 2. Запуск проверки

```bash
# Полная проверка (iOS + Android)
./mobile/scripts/quality_check_mobile.sh

# Только iOS
./mobile/ios/Scripts/swiftlint.sh

# Только Android
./mobile/android/scripts/detekt.sh
```

## 📊 Детальная настройка

### iOS (SwiftLint)

**Конфигурация:** `.swiftlint.yml`

```yaml
# Основные правила
disabled_rules:
  - trailing_whitespace
  - line_length

line_length:
  warning: 120
  error: 200

# Исключения
excluded:
  - Pods
  - DerivedData
```

**Команды:**
```bash
# Проверка
swiftlint lint

# Автоисправление
swiftlint --fix

# HTML отчет
swiftlint lint --reporter html > report.html
```

### Android (Detekt)

**Конфигурация:** `config/detekt.yml`

```yaml
# Основные настройки
build:
  maxIssues: 0
  excludeCorrectable: false

# Правила сложности
complexity:
  active: true
  CognitiveComplexMethod:
    threshold: 15
```

**Команды:**
```bash
# Проверка через Gradle
./gradlew detekt

# HTML отчет
./gradlew detekt --reports html
```

### Android (ktlint)

**Команды:**
```bash
# Проверка
ktlint check

# Автоисправление
ktlint format

# Проверка с отчетом
ktlint check --reporter=plain,output=ktlint-report.txt
```

## 🔧 Интеграция с IDE

### Xcode (iOS)

1. **Автоматическая проверка:**
   - Product → Analyze (⌘+Shift+B)
   - Build Settings → SwiftLint → Run Script Phase

2. **Настройка SwiftLint в Xcode:**
   ```bash
   # Добавить в Build Phases
   if which swiftlint >/dev/null; then
     swiftlint
   else
     echo "warning: SwiftLint not installed"
   fi
   ```

### Android Studio (Android)

1. **Автоматическая проверка:**
   - Analyze → Inspect Code
   - File → Settings → Editor → Inspections

2. **Настройка Detekt в Android Studio:**
   ```kotlin
   // build.gradle.kts
   plugins {
       id("io.gitlab.arturbosch.detekt") version "1.23.0"
   }
   ```

## 📈 CI/CD интеграция

### GitHub Actions

```yaml
name: Code Quality Check

on: [push, pull_request]

jobs:
  ios-quality:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: SwiftLint
        run: |
          brew install swiftlint
          cd mobile/ios
          swiftlint lint --reporter github-actions-logging

  android-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Detekt
        run: |
          cd mobile/android
          ./gradlew detekt
```

### Git Hooks

```bash
# pre-commit hook
#!/bin/bash
cd mobile/ios && swiftlint lint
cd ../android && ./gradlew detekt
```

## 🎯 Правила качества

### iOS (Swift)

**Обязательные правила:**
- ✅ Максимальная длина строки: 120 символов
- ✅ Максимальная длина функции: 50 строк
- ✅ Максимальная сложность: 10
- ✅ Обязательные комментарии для публичных API
- ✅ Запрет force unwrapping без проверки

**Рекомендуемые правила:**
- 🔧 Использование `guard` вместо `if let`
- 🔧 Предпочтение `let` вместо `var`
- 🔧 Использование `private` для внутренних методов

### Android (Kotlin)

**Обязательные правила:**
- ✅ Максимальная длина строки: 120 символов
- ✅ Максимальная длина функции: 60 строк
- ✅ Максимальная сложность: 15
- ✅ Обязательные комментарии для публичных API
- ✅ Запрет `!!` оператора без проверки

**Рекомендуемые правила:**
- 🔧 Использование `val` вместо `var`
- 🔧 Предпочтение data classes
- 🔧 Использование `private` для внутренних методов

## 🚨 Обработка ошибок

### Частые ошибки iOS

```swift
// ❌ Плохо
let name = user.name! // Force unwrapping

// ✅ Хорошо
guard let name = user.name else { return }

// ❌ Плохо
if let name = user.name {
    if let age = user.age {
        // Nested ifs
    }
}

// ✅ Хорошо
guard let name = user.name,
      let age = user.age else { return }
```

### Частые ошибки Android

```kotlin
// ❌ Плохо
val name = user.name!! // Force unwrapping

// ✅ Хорошо
val name = user.name ?: return

// ❌ Плохо
if (user.name != null) {
    if (user.age != null) {
        // Nested ifs
    }
}

// ✅ Хорошо
val name = user.name ?: return
val age = user.age ?: return
```

## 📊 Метрики качества

### Целевые показатели

| Метрика | iOS | Android | Статус |
|---------|-----|---------|--------|
| Покрытие тестами | >80% | >80% | 🎯 |
| Сложность кода | <10 | <15 | 🎯 |
| Дублирование | <3% | <3% | 🎯 |
| Технический долг | <2ч | <2ч | 🎯 |

### Отчеты

```bash
# Генерация отчетов
./mobile/scripts/quality_check_mobile.sh

# Отчеты сохраняются в:
# - mobile/ios/swiftlint-report.html
# - mobile/android/build/reports/detekt/
# - mobile/quality_report_YYYYMMDD_HHMMSS.md
```

## 🔄 Автоматизация

### Pre-commit hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Проверка качества кода..."

# iOS
if [ -d "mobile/ios" ]; then
    cd mobile/ios
    if ! swiftlint lint --quiet; then
        echo "❌ SwiftLint ошибки найдены"
        exit 1
    fi
    cd ../..
fi

# Android
if [ -d "mobile/android" ]; then
    cd mobile/android
    if ! ./gradlew detekt --quiet; then
        echo "❌ Detekt ошибки найдены"
        exit 1
    fi
    cd ../..
fi

echo "✅ Проверка качества пройдена"
```

### IDE настройки

**VS Code:**
```json
{
  "swiftlint.enable": true,
  "kotlin.linting.enabled": true,
  "kotlin.linting.detekt.enabled": true
}
```

## 🎉 Заключение

Использование правильных инструментов проверки кода для мобильных приложений критически важно для:

- ✅ **Качества кода** - соответствие стандартам
- ✅ **Производительности** - оптимизация приложений
- ✅ **Безопасности** - выявление уязвимостей
- ✅ **Поддерживаемости** - читаемость и структура
- ✅ **Командной работы** - единые стандарты

**Помните:** flake8 для Python, SwiftLint для iOS, Detekt для Android! 🚀

