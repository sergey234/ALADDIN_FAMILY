# 📋 ПЛАН С ГОТОВЫМИ PROVISIONING PROFILES

**Дата:** 29 ноября 2025  
**Цель:** Использовать готовые provisioning profiles на GitHub Actions

---

## 🎯 ПРОБЛЕМА

### Локально:
- ❌ Xcode 13.2.1 (iOS 15.2 SDK)
- ❌ Нельзя собрать билд для App Store (нужен iOS 18 SDK)

### GitHub Actions:
- ✅ Xcode 16.2.0 (iOS 18 SDK)
- ❌ Нет доступа к Apple Developer Portal для создания profiles

---

## ✅ РЕШЕНИЕ

### Использовать готовые Provisioning Profiles

**Идея:**
1. Локально в Xcode настроить Signing (создать profiles)
2. Экспортировать profiles
3. Добавить в GitHub Secrets или использовать fastlane match
4. Использовать на GitHub Actions для подписи

---

## 📋 ПОШАГОВЫЙ ПЛАН

### Шаг 1: Локально - Настроить Signing

**В Xcode (ваш Mac):**

1. **Открыть проект:**
   ```
   Открыть ALADDIN.xcodeproj или ALADDIN.xcworkspace
   ```

2. **Настроить Signing:**
   - Выбрать проект в навигаторе
   - Выбрать target "ALADDIN"
   - Вкладка "Signing & Capabilities"
   - Выбрать Team: `6CJVBBUGSN`
   - Поставить галочку "Automatically manage signing"
   - Xcode автоматически создаст provisioning profiles

3. **Проверить Network Extension:**
   - Выбрать target "ALADDINPacketTunnel"
   - Signing & Capabilities
   - Выбрать Team: `6CJVBBUGSN`
   - "Automatically manage signing"
   - Xcode создаст profiles для Network Extension

4. **Проверить, что profiles созданы:**
   ```
   Открыть: ~/Library/MobileDevice/Provisioning Profiles/
   Должны быть файлы .mobileprovision
   ```

---

### Шаг 2: Экспортировать Profiles (опционально)

**Если нужно экспортировать вручную:**

1. **Найти profiles:**
   ```bash
   ls ~/Library/MobileDevice/Provisioning\ Profiles/
   ```

2. **Скопировать нужные:**
   - `family.aladdin.ios` (основное приложение)
   - `family.aladdin.ios.packetTunnel` (Network Extension)

3. **Сохранить для использования на GitHub**

---

### Шаг 3: Добавить в GitHub

**Вариант A: Через fastlane match (рекомендуется)**

1. **Установить fastlane:**
   ```bash
   sudo gem install fastlane
   ```

2. **Инициализировать match:**
   ```bash
   fastlane match init
   ```

3. **Настроить match:**
   - Создать приватный Git репозиторий для profiles
   - Настроить доступ
   - Загрузить profiles

4. **Использовать в workflow:**
   - fastlane match автоматически загрузит profiles
   - Использует для подписи

**Вариант B: Вручную через Secrets**

1. **Экспортировать profiles:**
   - Скопировать .mobileprovision файлы
   - Закодировать в base64

2. **Добавить в GitHub Secrets:**
   - `PROVISIONING_PROFILE_APP` (основное приложение)
   - `PROVISIONING_PROFILE_EXTENSION` (Network Extension)

3. **Использовать в workflow:**
   - Декодировать из base64
   - Сохранить в нужное место
   - Использовать для подписи

---

### Шаг 4: Обновить Workflow

**Использовать готовые profiles:**

```yaml
- name: Setup Provisioning Profiles
  run: |
    mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles/
    # Декодировать и сохранить profiles из secrets
    echo "${{ secrets.PROVISIONING_PROFILE_APP }}" | base64 -d > ~/Library/MobileDevice/Provisioning\ Profiles/app.mobileprovision
    echo "${{ secrets.PROVISIONING_PROFILE_EXTENSION }}" | base64 -d > ~/Library/MobileDevice/Provisioning\ Profiles/extension.mobileprovision

- name: Build Archive (with signing)
  run: |
    xcodebuild archive \
      -project ALADDIN.xcodeproj \
      -scheme ALADDIN \
      -configuration Release \
      -archivePath ./build/ALADDIN.xcarchive \
      -destination 'generic/platform=iOS' \
      CODE_SIGN_STYLE=Manual \
      DEVELOPMENT_TEAM="6CJVBBUGSN" \
      PROVISIONING_PROFILE_SPECIFIER="family.aladdin.ios"
```

---

## 🎯 УПРОЩЁННЫЙ ПЛАН

### Если fastlane match сложно:

**Вариант 1: Использовать Automatic Signing с Team ID**

**На GitHub Actions:**
- Использовать `CODE_SIGN_STYLE=Automatic`
- Указать `DEVELOPMENT_TEAM`
- Но нужен доступ к Apple Developer Portal (через API ключи)

**Проблема:**
- Нет интерактивного доступа
- Нужны API ключи для создания profiles

**Вариант 2: Собрать без подписи, подписать потом**

**Но:**
- Локально старая версия Xcode
- Нельзя подписать правильно

---

## ✅ РЕКОМЕНДАЦИЯ

### Использовать fastlane match:

1. **Управление profiles через Git**
2. **Автоматическая синхронизация**
3. **Безопасное хранение**
4. **Простое использование на CI**

**Или:**

### Использовать готовые profiles через Secrets:

1. **Экспортировать profiles локально**
2. **Добавить в GitHub Secrets**
3. **Использовать в workflow**

---

## 📋 ЧТО ДЕЛАТЬ СЕЙЧАС

### Вариант 1: Проверить компиляцию (уже делаем)

**GitHub Actions:**
- ✅ Собирает без подписи
- ✅ Проверяет компиляцию
- ✅ Создаёт Archive для проверки структуры

### Вариант 2: Настроить подпись (следующий шаг)

**После проверки компиляции:**
1. ✅ Настроить Signing локально в Xcode
2. ✅ Экспортировать profiles
3. ✅ Добавить в GitHub (через match или Secrets)
4. ✅ Обновить workflow для использования profiles
5. ✅ Собрать с подписью на GitHub Actions
6. ✅ Загрузить в App Store Connect

---

## ✅ ИТОГО

**Правильная стратегия:**

1. **Локально (Xcode 13.2.1):**
   - ✅ Разработка
   - ✅ Настройка Signing (создание profiles)
   - ❌ НЕ собираем финальный билд

2. **GitHub Actions (Xcode 16.2.0):**
   - ✅ Сборка с правильной версией Xcode
   - ✅ Использование готовых provisioning profiles
   - ✅ Подпись и загрузка в App Store Connect

**Сначала проверим компиляцию, потом настроим подпись!** 🎯

---

**Дата:** 29 ноября 2025  
**Инструкция:** План с готовыми provisioning profiles

