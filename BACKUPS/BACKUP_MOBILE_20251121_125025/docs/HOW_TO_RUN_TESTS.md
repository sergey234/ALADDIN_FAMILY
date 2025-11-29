# 🧪 КАК ЗАПУСТИТЬ ТЕСТЫ В XCODE

**Проблема:** Нажимаете Cmd + U, но ничего не происходит

---

## 🔧 РЕШЕНИЕ 1: Добавить файл тестов в проект Xcode

### Шаг 1: Открыть проект в Xcode
```bash
open ALADDIN.xcodeproj
```

### Шаг 2: Добавить файл тестов в проект

1. **В Xcode:**
   - Правой кнопкой на папку `Tests/UnitTests`
   - Выбрать "Add Files to ALADDIN..."
   - Выбрать файл `MockAPIServiceTests.swift`
   - ✅ Убедиться, что стоит галочка "Copy items if needed"
   - ✅ Убедиться, что выбран правильный Target (ALADDINTests или ALADDIN Tests)
   - Нажать "Add"

2. **Или через Finder:**
   - Перетащить файл `MockAPIServiceTests.swift` в Xcode
   - В папку `Tests/UnitTests`
   - ✅ Убедиться, что выбран правильный Target

---

## 🔧 РЕШЕНИЕ 2: Проверить настройки схемы

### Шаг 1: Открыть схему

1. В Xcode: Product → Scheme → Edit Scheme...
2. Или: Нажать на схему вверху (рядом с кнопкой Play)

### Шаг 2: Проверить Test

1. Выбрать "Test" в левом меню
2. Убедиться, что стоит галочка на "ALADDINTests" (или "ALADDIN Tests")
3. Нажать "Close"

---

## 🔧 РЕШЕНИЕ 3: Выбрать правильную схему

### В Xcode:

1. Нажать на схему вверху (рядом с кнопкой Play)
2. Выбрать схему "ALADDIN"
3. Убедиться, что выбран симулятор (например, iPhone 15)

---

## 🔧 РЕШЕНИЕ 4: Запустить тесты через меню

### В Xcode:

1. Product → Test (или Cmd + U)
2. Или: Product → Test Plan → Run All Tests
3. Или: Нажать на иконку теста рядом с кнопкой Play

---

## 🔧 РЕШЕНИЕ 5: Запустить конкретный тест

### В Xcode:

1. Открыть файл `MockAPIServiceTests.swift`
2. Найти функцию теста (например, `testLogin`)
3. Нажать на иконку ▶️ рядом с функцией
4. Или: Правой кнопкой → Run "testLogin"

---

## 🔧 РЕШЕНИЕ 6: Проверить, что тесты компилируются

### В Xcode:

1. Product → Build (или Cmd + B)
2. Проверить, что нет ошибок компиляции
3. Если есть ошибки - исправить их

---

## 🔧 РЕШЕНИЕ 7: Запустить через терминал

### Команда:

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Список доступных симуляторов
xcrun simctl list devices available | grep iPhone

# Запустить тесты (замените DEVICE_ID на ID симулятора)
xcodebuild test \
  -project ALADDIN.xcodeproj \
  -scheme ALADDIN \
  -destination 'platform=iOS Simulator,id=DEVICE_ID' \
  -only-testing:ALADDINTests/MockAPIServiceTests
```

---

## ✅ БЫСТРАЯ ПРОВЕРКА

### 1. Файл существует?
```bash
ls -la Tests/UnitTests/MockAPIServiceTests.swift
```

### 2. Файл в проекте?
- Открыть Xcode
- Проверить, что файл виден в навигаторе проекта
- Если нет - добавить (см. Решение 1)

### 3. Правильный Target?
- Выбрать файл `MockAPIServiceTests.swift` в Xcode
- Открыть File Inspector (правая панель)
- Проверить, что стоит галочка на Test Target

---

## 🐛 ЧАСТЫЕ ПРОБЛЕМЫ

### Проблема 1: "No tests found"

**Решение:**
- Убедиться, что файл добавлен в Test Target
- Проверить, что класс наследуется от `XCTestCase`
- Проверить, что функции начинаются с `test`

### Проблема 2: "Build failed"

**Решение:**
- Проверить ошибки компиляции
- Убедиться, что все импорты правильные
- Проверить, что `@testable import ALADDIN` правильный

### Проблема 3: "Scheme not found"

**Решение:**
- Выбрать схему "ALADDIN" в Xcode
- Или создать новую схему: Product → Scheme → Manage Schemes

---

## 📋 ЧЕКЛИСТ

- [ ] Файл `MockAPIServiceTests.swift` существует
- [ ] Файл добавлен в проект Xcode
- [ ] Файл добавлен в Test Target
- [ ] Схема "ALADDIN" выбрана
- [ ] Симулятор выбран
- [ ] Проект компилируется без ошибок
- [ ] Тесты видны в Test Navigator (Cmd + 6)

---

## 🎯 АЛЬТЕРНАТИВНЫЙ СПОСОБ: Ручное тестирование

Если тесты не запускаются, можно протестировать вручную:

1. **Запустить приложение в Xcode**
2. **Mock API включен по умолчанию** (в DEBUG режиме)
3. **Протестировать критические сценарии:**
   - Открыть экран Profile → проверить загрузку данных
   - Открыть экран Family → проверить список семьи
   - Открыть экран Tariffs → проверить тарифы
   - И т.д.

---

**Дата создания:** 15 ноября 2025  
**Статус:** ✅ **ИНСТРУКЦИЯ ГОТОВА**



