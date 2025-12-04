# 📦 ВАЖНЫЕ ФАЙЛЫ ДЛЯ ОТПРАВКИ IPA В APP STORE CONNECT

**Дата:** 03.12.2025  
**Проект:** ALADDIN iOS  
**Метод отправки:** GitHub Actions (автоматическая загрузка)

---

## 🎯 КРИТИЧЕСКИ ВАЖНЫЕ ФАЙЛЫ

### 1. GitHub Actions Workflow

#### Основной workflow для сборки и загрузки:

**Файл:** `.github/workflows/check-secrets.yml`

**Назначение:**
- Сборка проекта (xcodebuild archive)
- Экспорт IPA (xcodebuild -exportArchive)
- Загрузка в App Store Connect (apple-actions/upload-testflight-build@v1)
- Сохранение IPA как артефакт

**Ключевые секции:**
- Проверка GitHub Secrets (API ключи)
- Настройка Xcode
- Настройка сертификатов и профилей
- Сборка архива
- Экспорт IPA
- Загрузка в App Store Connect

**Статус:** ✅ Работает, используется для автоматической загрузки

---

#### Альтернативный workflow для загрузки IPA:

**Файл:** `.github/workflows/upload-ipa-only.yml`

**Назначение:**
- Загрузка уже собранного IPA из артефактов
- Полезен, если нужно загрузить IPA без пересборки

**Статус:** ✅ Готов к использованию

---

### 2. Конфигурация экспорта IPA

**Файл:** `ExportOptions.plist`

**Назначение:**
- Настройки экспорта IPA для App Store
- Метод экспорта: `app-store`
- Team ID: `6CJVBBUGSN`
- Стиль подписи: `automatic` или `manual`
- Настройки биткода и символов

**Ключевые параметры:**
```xml
<key>method</key>
<string>app-store</string>
<key>teamID</key>
<string>6CJVBBUGSN</string>
<key>signingStyle</key>
<string>automatic</string>
<key>uploadSymbols</key>
<true/>
<key>uploadBitcode</key>
<false/>
```

**Статус:** ✅ Используется в workflow

---

### 3. Настройки проекта Xcode

**Файл:** `ALADDIN.xcodeproj/project.pbxproj`

**Назначение:**
- Все настройки проекта Xcode
- Версия приложения (MARKETING_VERSION)
- Build number (CURRENT_PROJECT_VERSION)
- Bundle ID
- Team ID
- Provisioning profiles
- Code signing settings

**Ключевые значения:**
- **MARKETING_VERSION:** 1.0.0
- **CURRENT_PROJECT_VERSION:** 3 (текущий build number)
- **Bundle ID:** family.aladdin.ios
- **Team ID:** 6CJVBBUGSN

**Важно:** При каждой новой загрузке нужно увеличивать CURRENT_PROJECT_VERSION!

**Статус:** ✅ Актуальный, build number = 3

---

### 4. Настройки приложения

**Файл:** `ALADDIN/Info.plist`

**Назначение:**
- Основные настройки приложения
- Bundle identifier
- Minimum iOS version
- UIBackgroundModes (исправлено: удалены недопустимые значения)
- ITSAppUsesNonExemptEncryption (NO - стандартное шифрование iOS)

**Ключевые настройки:**
- **Minimum iOS:** 15.0
- **UIBackgroundModes:** только допустимые значения
- **ITSAppUsesNonExemptEncryption:** NO

**Статус:** ✅ Исправлен, готов к публикации

---

## 🔐 ФАЙЛЫ ПОДПИСИ И БЕЗОПАСНОСТИ

### 5. GitHub Secrets (не в репозитории!)

**Важно:** Эти файлы НЕ хранятся в репозитории, только в GitHub Secrets!

**Необходимые Secrets:**
- `APP_STORE_CONNECT_API_KEY` - приватный ключ API (.p8 файл)
- `APP_STORE_CONNECT_ISSUER_ID` - ID издателя
- `APP_STORE_CONNECT_API_KEY_ID` - ID API ключа
- `PROVISIONING_PROFILE_APP` - профиль для основного приложения (base64)
- `PROVISIONING_PROFILE_EXTENSION` - профиль для расширения (base64)
- `APPLE_DISTRIBUTION_CERTIFICATE` - сертификат распределения (base64)
- `APPLE_DISTRIBUTION_CERTIFICATE_PASSWORD` - пароль сертификата

**Где настроить:**
- GitHub → Settings → Secrets and variables → Actions
- Добавить каждый secret отдельно

---

### 6. Provisioning Profiles (в GitHub Secrets)

**Профили хранятся в GitHub Secrets как base64:**

- `PROVISIONING_PROFILE_APP` - для family.aladdin.ios
- `PROVISIONING_PROFILE_EXTENSION` - для family.aladdin.ios.packetTunnel

**UUID профилей (из workflow):**
- APP_PROFILE_UUID: `4dc2e0ff-f7bd-4ac0-aca8-98143ea99e7f`
- EXT_PROFILE_UUID: `d1e59dc9-2171-4eca-a316-1bf714c895ec`

---

## 📋 ДОКУМЕНТАЦИЯ

### 7. Инструкции по загрузке IPA

**Файлы:**
- `docs/AppStore/ИНСТРУКЦИЯ_ЗАГРУЗКИ_IPA_ДЛЯ_ML_СИСТЕМЫ.md` - полная инструкция
- `docs/AppStore/ПОШАГОВАЯ_ИНСТРУКЦИЯ_ОТПРАВКИ_НА_РЕВЬЮ.md` - отправка на ревью
- `docs/AppStore/БИЛД_ГОТОВ_К_ОТПРАВКЕ.md` - информация о готовом билде

---

## 🔄 ПРОЦЕСС ЗАГРУЗКИ IPA

### Шаг 1: Триггер workflow

**Способ 1: Автоматический (push в master)**
```bash
git push origin master
```

**Способ 2: Ручной запуск**
- GitHub → Actions → Check Secrets and Build → Run workflow

**Способ 3: Пустой коммит**
```bash
git commit --allow-empty -m "chore: trigger IPA upload"
git push origin master
```

### Шаг 2: Сборка проекта

Workflow выполняет:
1. Checkout кода
2. Setup Xcode (16.2.0)
3. Setup сертификатов и профилей
4. Сборка архива: `xcodebuild archive`
5. Экспорт IPA: `xcodebuild -exportArchive`

### Шаг 3: Загрузка в App Store Connect

Workflow использует:
- `apple-actions/upload-testflight-build@v1`
- API ключи из GitHub Secrets
- IPA файл: `./build/export/ALADDIN.ipa`

### Шаг 4: Сохранение артефакта

IPA сохраняется как артефакт GitHub Actions:
- Название: `ALADDIN-IPA`
- Retention: 30 дней
- Artifact ID: 4749592382 (последний)

---

## 📊 ТЕКУЩИЕ НАСТРОЙКИ

### Версии и номера сборок:

- **MARKETING_VERSION:** 1.0.0
- **CURRENT_PROJECT_VERSION:** 3
- **Минимальная версия iOS:** 15.0
- **Bundle ID:** family.aladdin.ios

### Team и сертификаты:

- **Team ID:** 6CJVBBUGSN
- **Team Name:** SERGEY KHLYSTOV
- **Certificate:** Apple Distribution

### Последние загрузки:

- **Build 1:** 1.0.0 (1) - Ready to Submit
- **Build 2:** 1.0.0 (2) - Processing / Ready to Submit
- **Build 3:** 1.0.0 (3) - Подтвержден ✅ (03.12.2025, 14:54)

---

## 🔧 КАК УВЕЛИЧИТЬ BUILD NUMBER

### Перед следующей загрузкой:

1. **Открыть файл:**
   ```
   ALADDIN.xcodeproj/project.pbxproj
   ```

2. **Найти все CURRENT_PROJECT_VERSION:**
   ```bash
   grep "CURRENT_PROJECT_VERSION" ALADDIN.xcodeproj/project.pbxproj
   ```

3. **Заменить все значения:**
   - Текущий: `CURRENT_PROJECT_VERSION = 3;`
   - Новый: `CURRENT_PROJECT_VERSION = 4;`

4. **Закоммитить и запушить:**
   ```bash
   git add ALADDIN.xcodeproj/project.pbxproj
   git commit -m "fix: увеличить build number до 4"
   git push origin master
   ```

---

## 📁 СТРУКТУРА ВАЖНЫХ ФАЙЛОВ

```
ALADDIN_iOS/
├── .github/
│   └── workflows/
│       ├── check-secrets.yml          ← ОСНОВНОЙ WORKFLOW
│       └── upload-ipa-only.yml        ← АЛЬТЕРНАТИВНЫЙ WORKFLOW
│
├── ALADDIN.xcodeproj/
│   └── project.pbxproj                 ← НАСТРОЙКИ ПРОЕКТА (build number!)
│
├── ALADDIN/
│   └── Info.plist                      ← НАСТРОЙКИ ПРИЛОЖЕНИЯ
│
├── ExportOptions.plist                 ← НАСТРОЙКИ ЭКСПОРТА IPA
│
└── docs/
    └── AppStore/
        ├── ИНСТРУКЦИЯ_ЗАГРУЗКИ_IPA_ДЛЯ_ML_СИСТЕМЫ.md
        ├── ПОШАГОВАЯ_ИНСТРУКЦИЯ_ОТПРАВКИ_НА_РЕВЬЮ.md
        └── БИЛД_ГОТОВ_К_ОТПРАВКЕ.md
```

---

## 🔐 GITHUB SECRETS (НЕ В РЕПОЗИТОРИИ!)

### Обязательные Secrets:

1. **APP_STORE_CONNECT_API_KEY**
   - Приватный ключ API (.p8 файл)
   - Формат: содержимое файла AuthKey_XXXXX.p8

2. **APP_STORE_CONNECT_ISSUER_ID**
   - ID издателя из App Store Connect
   - Формат: UUID

3. **APP_STORE_CONNECT_API_KEY_ID**
   - ID API ключа
   - Формат: 10 символов

4. **PROVISIONING_PROFILE_APP**
   - Профиль для основного приложения
   - Формат: base64 encoded .mobileprovision

5. **PROVISIONING_PROFILE_EXTENSION**
   - Профиль для расширения (PacketTunnel)
   - Формат: base64 encoded .mobileprovision

6. **APPLE_DISTRIBUTION_CERTIFICATE**
   - Сертификат распределения
   - Формат: base64 encoded .p12

7. **APPLE_DISTRIBUTION_CERTIFICATE_PASSWORD**
   - Пароль сертификата
   - Формат: строка

---

## 🚀 КОМАНДЫ ДЛЯ ЗАПУСКА

### Запуск workflow через git:

```bash
# Перейти в директорию проекта
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Создать пустой коммит для триггера
git commit --allow-empty -m "chore: trigger IPA upload to App Store Connect"

# Отправить в GitHub
git push origin master
```

### Проверка статуса workflow:

1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions
2. Найдите workflow "Build and Upload to App Store"
3. Проверьте статус выполнения

### Проверка загрузки IPA:

1. Откройте: https://appstoreconnect.apple.com/apps/6755897079/testflight/ios/builds
2. Найдите новый билд
3. Проверьте статус: Processing → Ready to Submit

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

### Build Number:

- **ВСЕГДА увеличивайте** перед новой загрузкой
- Текущий: 3
- Следующий: 4
- Apple не принимает дубликаты build number!

### API Ключи:

- Хранятся только в GitHub Secrets
- НЕ коммитятся в репозиторий
- Должны быть действительными и не истекшими

### Provisioning Profiles:

- Должны быть действительными
- Должны соответствовать Bundle ID
- Должны быть для App Store Distribution

### Сертификаты:

- Должны быть действительными
- Должны быть для App Store Distribution
- Не должны быть истекшими

---

## 📋 ЧЕКЛИСТ ПЕРЕД ЗАГРУЗКОЙ

### Технические проверки:

- [ ] Build number увеличен (если новая загрузка)
- [ ] GitHub Secrets настроены
- [ ] Provisioning profiles действительны
- [ ] Сертификаты действительны
- [ ] ExportOptions.plist настроен правильно
- [ ] Info.plist исправлен (UIBackgroundModes)
- [ ] Проект компилируется без ошибок

### Проверка workflow:

- [ ] Workflow файл существует: `.github/workflows/check-secrets.yml`
- [ ] Синтаксис YAML правильный
- [ ] Триггеры настроены (push в master)
- [ ] Все шаги workflow корректны

---

## 🔄 ИСТОРИЯ ЗАГРУЗОК

### Успешные загрузки:

1. **Build 1.0.0 (1)**
   - Delivery UUID: 93884757-a0ee-4e51-9e6d-41f9e0ec07c5
   - Статус: Ready to Submit
   - Дата: 03.12.2025

2. **Build 1.0.0 (3)**
   - Delivery UUID: 5c9173ec-5564-4871-9003-67ad1a2ee9d7
   - Статус: Подтвержден ✅
   - Дата: 03.12.2025, 14:54
   - Размер: 8.47 МБ

### Ошибки и исправления:

- **Build 1.0.0 (2):** Ошибка дубликата build number - исправлено увеличением до 3
- **Info.plist:** Удалены недопустимые значения UIBackgroundModes

---

## 📞 ПОДДЕРЖКА

### Если workflow не работает:

1. Проверьте логи в GitHub Actions
2. Проверьте GitHub Secrets
3. Проверьте синтаксис YAML
4. Проверьте, что проект компилируется локально

### Если IPA не загружается:

1. Проверьте API ключи (действительны, не истекли)
2. Проверьте build number (уникальный, больше предыдущего)
3. Проверьте логи загрузки в workflow
4. Проверьте статус в App Store Connect

---

## ✅ ИТОГ

### Критически важные файлы:

1. ✅ `.github/workflows/check-secrets.yml` - основной workflow
2. ✅ `ExportOptions.plist` - настройки экспорта
3. ✅ `ALADDIN.xcodeproj/project.pbxproj` - настройки проекта (build number!)
4. ✅ `ALADDIN/Info.plist` - настройки приложения
5. ✅ GitHub Secrets - API ключи и профили (не в репозитории!)

### Документация:

- ✅ `docs/AppStore/ИНСТРУКЦИЯ_ЗАГРУЗКИ_IPA_ДЛЯ_ML_СИСТЕМЫ.md`
- ✅ `docs/AppStore/ПОШАГОВАЯ_ИНСТРУКЦИЯ_ОТПРАВКИ_НА_РЕВЬЮ.md`
- ✅ `docs/AppStore/БИЛД_ГОТОВ_К_ОТПРАВКЕ.md`

---

**Все важные файлы задокументированы! 🎉**

