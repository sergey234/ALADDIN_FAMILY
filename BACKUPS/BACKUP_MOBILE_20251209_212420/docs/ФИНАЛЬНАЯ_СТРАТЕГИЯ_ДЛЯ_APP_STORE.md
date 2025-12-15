# 🎯 ФИНАЛЬНАЯ СТРАТЕГИЯ ДЛЯ APP STORE

**Дата:** 29 ноября 2025  
**Проблема:** Локально Xcode 13.2.1 (iOS 15.2 SDK) - не подходит для App Store  
**Решение:** ✅ Всё делаем на GitHub Actions (Xcode 16.2.0, iOS 18 SDK)

---

## ✅ ПРАВИЛЬНОЕ РАЗДЕЛЕНИЕ

### Локально (Xcode 13.2.1):
- ✅ **Разработка кода**
- ✅ **Тестирование в симуляторе**
- ✅ **Отладка**
- ❌ **НЕ собираем финальный билд для App Store**

### GitHub Actions (Xcode 16.2.0):
- ✅ **Сборка для App Store** (iOS 18 SDK)
- ✅ **Подпись** (с готовыми provisioning profiles)
- ✅ **Загрузка в App Store Connect**

---

## 📋 РАБОЧИЙ ПРОЦЕСС

### 1. Разработка (локально):

```
Локально (Xcode 13.2.1):
→ Пишем код
→ Тестируем в симуляторе
→ Исправляем ошибки
→ Коммитим и пушим
```

### 2. Проверка компиляции (GitHub Actions):

```
GitHub Actions (автоматически):
→ Проверяет компиляцию (без подписи)
→ Сообщает об ошибках
→ Создаёт артефакты
```

### 3. Финальная сборка (GitHub Actions):

```
GitHub Actions (Xcode 16.2.0):
→ Собирает Archive с подписью
→ Использует готовые provisioning profiles
→ Загружает в App Store Connect
```

---

## 🎯 ТЕКУЩИЙ СТАТУС

### ✅ Что уже работает:

1. **GitHub Actions компиляция:**
   - ✅ Workflow "Build Only (No Upload)" работает
   - ✅ Последний запуск: **Success** ✅
   - ✅ Компиляция проходит успешно
   - ✅ Archive создаётся (без подписи, для проверки)

### ⏳ Что нужно сделать:

1. **Настроить подпись на GitHub Actions:**
   - ⏳ Получить provisioning profiles (локально или через API)
   - ⏳ Добавить в GitHub Secrets
   - ⏳ Обновить workflow для использования profiles
   - ⏳ Собрать с подписью
   - ⏳ Загрузить в App Store Connect

---

## 📋 ПЛАН ДЕЙСТВИЙ

### Шаг 1: Получить Provisioning Profiles

**Вариант A: Локально в Xcode (проще)**

1. **Открыть проект в Xcode:**
   - Открыть `ALADDIN.xcodeproj` или `ALADDIN.xcworkspace`
   - Выбрать target "ALADDIN"
   - Signing & Capabilities → выбрать Team `6CJVBBUGSN`
   - Поставить галочку "Automatically manage signing"
   - Xcode создаст provisioning profiles автоматически

2. **Проверить Network Extension:**
   - Выбрать target "ALADDINPacketTunnel"
   - Signing & Capabilities → выбрать Team `6CJVBBUGSN`
   - "Automatically manage signing"
   - Xcode создаст profiles для Network Extension

3. **Экспортировать profiles:**
   ```bash
   # Найти profiles
   ls ~/Library/MobileDevice/Provisioning\ Profiles/
   
   # Скопировать нужные:
   # - family.aladdin.ios (основное приложение)
   # - family.aladdin.ios.packetTunnel (Network Extension)
   ```

**Вариант B: Через API ключи (сложнее, но автоматически)**

1. **Создать API ключ в App Store Connect:**
   - App Store Connect → Users and Access → Keys
   - Создать новый ключ
   - Скачать .p8 файл

2. **Использовать в workflow:**
   - GitHub Actions может создавать profiles автоматически
   - Через API ключи App Store Connect

---

### Шаг 2: Добавить в GitHub

**Вариант A: Через Secrets (проще)**

1. **Экспортировать profiles:**
   - Скопировать .mobileprovision файлы
   - Закодировать в base64:
     ```bash
     base64 -i profile.mobileprovision
     ```

2. **Добавить в GitHub Secrets:**
   - Repository → Settings → Secrets → Actions
   - Добавить:
     - `PROVISIONING_PROFILE_APP` (основное приложение)
     - `PROVISIONING_PROFILE_EXTENSION` (Network Extension)

**Вариант B: Через fastlane match (рекомендуется для долгосрочного использования)**

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
   - Загрузить profiles
   - Использовать в workflow

---

### Шаг 3: Обновить Workflow

**Использовать готовые profiles:**

```yaml
- name: Setup Provisioning Profiles
  run: |
    mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles/
    # Декодировать и сохранить profiles из secrets
    echo "${{ secrets.PROVISIONING_PROFILE_APP }}" | base64 -d > ~/Library/MobileDevice/Provisioning\ Profiles/app.mobileprovision
    echo "${{ secrets.PROVISIONING_PROFILE_EXTENSION }}" | base64 -d > ~/Library/MobileDevice/Provisioning\ Profiles/extension.mobileprovision

- name: Build Archive (with signing)
  env:
    APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
  run: |
    xcodebuild archive \
      -project ALADDIN.xcodeproj \
      -scheme ALADDIN \
      -configuration Release \
      -archivePath ./build/ALADDIN.xcarchive \
      -destination 'generic/platform=iOS' \
      CODE_SIGN_STYLE=Manual \
      DEVELOPMENT_TEAM="$APPLE_TEAM_ID" \
      PROVISIONING_PROFILE_SPECIFIER="family.aladdin.ios"
```

---

## ✅ ИТОГО

**Правильная стратегия:**

1. **Локально (Xcode 13.2.1):**
   - ✅ Разработка
   - ✅ Тестирование
   - ✅ Настройка Signing (создание profiles)
   - ❌ НЕ собираем финальный билд

2. **GitHub Actions (Xcode 16.2.0):**
   - ✅ Проверка компиляции (уже работает!)
   - ⏳ Сборка с подписью (следующий шаг)
   - ⏳ Загрузка в App Store Connect

**Следующий шаг:** Настроить подпись на GitHub Actions! 🎯

---

**Дата:** 29 ноября 2025  
**Инструкция:** Финальная стратегия для App Store

