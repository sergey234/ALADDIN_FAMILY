# ✅ ПРОВЕРКА И ОБНОВЛЕНИЕ GITHUB ACTIONS ДЛЯ APP STORE

**Дата:** 28 ноября 2025  
**Статус:** Обновлено для использования Xcode 16+ и iOS 18 SDK

---

## 📋 ЧТО БЫЛО ПРОВЕРЕНО

### 1. Структура проекта
- ✅ Проект: `ALADDIN.xcodeproj` (не workspace)
- ✅ Bundle ID: `family.aladdin.ios`
- ✅ Team ID: `6CJVBBUGSN`
- ✅ ExportOptions.plist: настроен правильно

### 2. Workflow файл
- ✅ Файл: `.github/workflows/appstore.yml`
- ✅ Обновлён для использования Xcode 16.0
- ✅ Использует macOS 14 (поддерживает Xcode 16)
- ✅ Правильный путь к проекту: `-project ALADDIN.xcodeproj`
- ✅ Использует новый метод загрузки через API ключ

---

## 🔧 ЧТО БЫЛО ОБНОВЛЕНО

### 1. Версия Xcode
- ❌ Было: `latest-stable` (может быть старая версия)
- ✅ Стало: `'16.0'` (требуется для iOS 18 SDK)

### 2. Версия macOS
- ❌ Было: `macos-latest` (может быть старая версия)
- ✅ Стало: `macos-14` (поддерживает Xcode 16)

### 3. Метод загрузки
- ❌ Было: `xcrun altool` (устаревший метод)
- ✅ Стало: `apple-actions/upload-testflight-build@v1` (новый метод через API ключ)

### 4. Путь к проекту
- ✅ Используется: `-project ALADDIN.xcodeproj` (правильно)

### 5. Пути к файлам
- ✅ Archive: `./build/ALADDIN.xcarchive`
- ✅ Export: `./build/export/`
- ✅ IPA: автоматически находится и загружается

---

## 🔑 НЕОБХОДИМЫЕ СЕКРЕТЫ В GITHUB

### Обязательные секреты:

1. **APP_STORE_CONNECT_API_KEY**
   - Содержимое .p8 файла (API ключ из App Store Connect)
   - Как получить:
     - App Store Connect → Users and Access → Keys
     - Создать новый ключ
     - Скачать .p8 файл
     - Скопировать содержимое файла

2. **APP_STORE_CONNECT_ISSUER_ID**
   - Issuer ID из App Store Connect
   - Находится на той же странице, где создаётся ключ

3. **APP_STORE_CONNECT_API_KEY_ID**
   - Key ID из App Store Connect
   - Находится на той же странице, где создаётся ключ

4. **APPLE_TEAM_ID** (опционально, но рекомендуется)
   - Team ID: `6CJVBBUGSN`
   - Используется для автоматической подписи

---

## 📋 КАК ПРОВЕРИТЬ НАСТРОЙКУ

### Шаг 1: Проверить секреты

1. Откройте GitHub репозиторий: https://github.com/sergey234/ALADDIN_FAMILY
2. Перейдите: Settings → Secrets and variables → Actions
3. Проверьте наличие секретов:
   - ✅ `APP_STORE_CONNECT_API_KEY`
   - ✅ `APP_STORE_CONNECT_ISSUER_ID`
   - ✅ `APP_STORE_CONNECT_API_KEY_ID`
   - ✅ `APPLE_TEAM_ID` (опционально)

### Шаг 2: Проверить workflow файл

1. Откройте: `.github/workflows/appstore.yml`
2. Проверьте:
   - ✅ `runs-on: macos-14`
   - ✅ `xcode-version: '16.0'`
   - ✅ `-project ALADDIN.xcodeproj`
   - ✅ Использует `apple-actions/upload-testflight-build@v1`

### Шаг 3: Запустить workflow

1. Откройте: Actions → Build and Upload to App Store
2. Нажмите: "Run workflow"
3. Выберите ветку: `main` или `master`
4. Нажмите: "Run workflow"
5. Дождитесь завершения (10-20 минут)

---

## ✅ ЧТО ДОЛЖНО ПРОИЗОЙТИ

### Успешная сборка:

1. ✅ Checkout code — код загружен
2. ✅ Setup Xcode — Xcode 16.0 установлен
3. ✅ Build Archive — архив создан с iOS 18 SDK
4. ✅ Export IPA — IPA файл экспортирован
5. ✅ Upload to App Store Connect — билд загружен
6. ✅ Upload IPA as artifact — IPA сохранён как артефакт

### Результат:

- ✅ Билд загружен в App Store Connect
- ✅ Статус: "Processing" → "Ready to Submit"
- ✅ Можно заполнять метаданные и отправлять на ревью

---

## ⚠️ ВОЗМОЖНЫЕ ПРОБЛЕМЫ

### Проблема 1: Секреты не настроены

**Ошибка:** "APP_STORE_CONNECT_API_KEY secret is not set"

**Решение:**
1. Создать API ключ в App Store Connect
2. Добавить секреты в GitHub

### Проблема 2: Неправильный путь к проекту

**Ошибка:** "No such file or directory: ALADDIN.xcodeproj"

**Решение:**
1. Проверить структуру репозитория
2. Убедиться, что проект находится в корне
3. Или обновить путь в workflow

### Проблема 3: Ошибка подписи

**Ошибка:** "Code signing error"

**Решение:**
1. Проверить Team ID в секретах
2. Убедиться, что используется Automatic signing
3. Проверить Bundle ID: `family.aladdin.ios`

---

## 🎯 ИТОГО

**Что проверено:**
- ✅ Структура проекта
- ✅ Workflow файл
- ✅ Версия Xcode (16.0)
- ✅ Версия macOS (14)
- ✅ Метод загрузки (API ключ)
- ✅ Пути к файлам

**Что обновлено:**
- ✅ Xcode версия: `'16.0'`
- ✅ macOS версия: `macos-14`
- ✅ Метод загрузки: `apple-actions/upload-testflight-build@v1`
- ✅ Пути к файлам: `./build/`

**Что нужно сделать:**
1. ✅ Проверить секреты в GitHub
2. ✅ Запустить workflow
3. ✅ Дождаться загрузки билда
4. ✅ Заполнить метаданные в App Store Connect

**Проект готов к отправке в App Store через GitHub Actions!** 🚀

---

**Дата:** 28 ноября 2025  
**Статус:** Workflow обновлён и готов к использованию

