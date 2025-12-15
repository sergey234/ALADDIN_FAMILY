# 📋 ИНСТРУКЦИЯ: Запуск Workflow для отправки в App Store

**Дата создания:** 30 ноября 2025  
**Проект:** ALADDIN iOS  
**Статус:** ✅ Готово к использованию

---

## ⚠️ ВАЖНО: Какой Workflow использовать

### ✅ ПРАВИЛЬНЫЙ: `appstore.yml` - "Build and Upload to App Store"

**Используйте ТОЛЬКО этот workflow для загрузки в App Store!**

**Что делает:**
- ✅ Устанавливает сертификат подписи (из `IOS_DISTRIBUTION_CERTIFICATE`)
- ✅ Устанавливает provisioning profiles (App и Extension)
- ✅ Собирает архив с правильной подписью
- ✅ Создает IPA файл
- ✅ Отправляет в App Store Connect автоматически

**Файл:** `.github/workflows/appstore.yml`

---

### ❌ НЕПРАВИЛЬНЫЙ: `build-only.yml` - "Build Only (No Upload)"

**НЕ используйте этот workflow для App Store!**

**Что делает:**
- ❌ Собирает архив БЕЗ подписи (`CODE_SIGN_IDENTITY=""`)
- ❌ БЕЗ provisioning profiles
- ❌ НЕ создает IPA файл
- ❌ НЕ отправляет в App Store
- ⚠️ Только для CI тестирования компиляции

**Проблема:** Раньше запускался автоматически при `git push origin master` и тратил время впустую.

**Файл:** `.github/workflows/build-only.yml` (автозапуск отключен)

---

## 🚀 СПОСОБ 1: Запуск через создание тега (АВТОМАТИЧЕСКИЙ)

### Шаг 1: Создать тег

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Создать тег (например, v1.0.0)
git tag -a "v1.0.0" -m "Release version 1.0.0"

# Или с датой для тестирования
git tag -a "v1.0.0-$(date +%Y%m%d-%H%M%S)" -m "Test build $(date +%Y%m%d-%H%M%S)"
```

### Шаг 2: Отправить тег на GitHub

```bash
# Отправить тег
git push origin --tags

# Или отправить конкретный тег
git push origin v1.0.0
```

### Шаг 3: Workflow запустится автоматически

- ✅ Workflow `appstore.yml` запустится автоматически
- ✅ Начнется сборка с подписью
- ✅ IPA будет создан и отправлен в App Store Connect

### Шаг 4: Проверить статус

1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions
2. Найдите запуск "Build and Upload to App Store"
3. Дождитесь завершения (обычно 15-30 минут)

---

## 🎯 СПОСОБ 2: Запуск вручную через GitHub UI (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Открыть GitHub Actions

1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions
2. В левом меню найдите: **"Build and Upload to App Store"**
3. Нажмите на название workflow

### Шаг 2: Запустить workflow

1. Нажмите кнопку **"Run workflow"** (справа вверху)
2. Выберите ветку: **`master`** (или нужную ветку)
3. Нажмите зеленую кнопку **"Run workflow"**

### Шаг 3: Дождаться завершения

- ⏳ Сборка займет 15-30 минут
- ✅ Можно следить за прогрессом в реальном времени
- ✅ Логи доступны сразу

### Шаг 4: Проверить результат

1. Откройте запуск workflow
2. Проверьте все шаги (зеленые галочки):
   - ✅ Setup Signing Certificate
   - ✅ Setup Provisioning Profiles
   - ✅ Build Archive (with signing)
   - ✅ Export IPA
   - ✅ Upload to App Store Connect

---

## 📋 ПРОВЕРКА УСПЕШНОСТИ

### ✅ Успешный запуск

**Признаки успеха:**
- ✅ Все шаги завершены с зелеными галочками
- ✅ В логах: "✅ Signing certificate installed and verified"
- ✅ В логах: "✅ App provisioning profile installed with UUID: ..."
- ✅ В логах: "✅ Extension provisioning profile installed with UUID: ..."
- ✅ В логах: "Archive created successfully"
- ✅ В логах: "IPA file found: ..."
- ✅ В логах: "Uploading to App Store Connect..." или "Uploaded successfully"

**Результат:**
- ✅ IPA файл создан
- ✅ Билд загружен в App Store Connect
- ✅ Статус в App Store Connect: "Processing" → "Ready to Submit"

### ❌ Неуспешный запуск

**Признаки ошибки:**
- ❌ Красный крестик на каком-то шаге
- ❌ В логах: "❌ Failed to decode certificate"
- ❌ В логах: "❌ Provisioning profile not found"
- ❌ В логах: "❌ Archive not found"
- ❌ В логах: "❌ IPA file not found"

**Что делать:**
1. Проверьте логи ошибки
2. См. раздел "Решение проблем" ниже
3. Проверьте GitHub Secrets (см. документ `ПОЛНАЯ_СВОДКА_СЕРТИФИКАТОВ_И_КЛЮЧЕЙ.md`)

---

## 🔧 РЕШЕНИЕ ВОЗМОЖНЫХ ПРОБЛЕМ

### Проблема 1: "Failed to decode certificate"

**Причина:** Неправильный base64 в `IOS_DISTRIBUTION_CERTIFICATE`

**Решение:**
1. Проверьте файл: `~/Desktop/ALADDIN_Profiles/Certificates/distribution_certificate_base64.txt`
2. Убедитесь, что файл не пустой и содержит валидный base64
3. Обновите GitHub Secret: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
4. Скопируйте ВСЁ содержимое файла (одна длинная строка)

### Проблема 2: "Provisioning profile not found"

**Причина:** Неправильный base64 в `PROVISIONING_PROFILE_APP` или `PROVISIONING_PROFILE_EXTENSION`

**Решение:**
1. Проверьте файлы:
   - `~/Desktop/ALADDIN_Profiles/app_profile_appstore_base64.txt` (должен быть ~16 KB)
   - `~/Desktop/ALADDIN_Profiles/extension_profile_appstore_base64.txt` (должен быть ~17 KB)
2. Убедитесь, что используете правильный файл (не `app_profile_appstore_base64_NEW.txt` - он неполный!)
3. Обновите GitHub Secrets с правильными файлами

### Проблема 3: "Archive not found" или "Build failed"

**Причина:** Ошибка компиляции или неправильная конфигурация проекта

**Решение:**
1. Проверьте логи сборки в workflow
2. Убедитесь, что проект компилируется локально
3. Проверьте, что все зависимости установлены
4. Проверьте версию Xcode (должна быть 16.2.0)

### Проблема 4: "IPA file not found"

**Причина:** Ошибка экспорта архива в IPA

**Решение:**
1. Проверьте логи шага "Export IPA"
2. Убедитесь, что архив создан успешно
3. Проверьте, что provisioning profiles правильно установлены
4. Проверьте, что сертификат найден в keychain

### Проблема 5: "Upload to App Store Connect failed"

**Причина:** Неправильные API ключи или проблемы с сетью

**Решение:**
1. Проверьте GitHub Secrets:
   - `APP_STORE_CONNECT_API_KEY`
   - `APP_STORE_CONNECT_ISSUER_ID`
   - `APP_STORE_CONNECT_API_KEY_ID`
2. Если API ключи не установлены, IPA будет доступен как artifact для ручной загрузки
3. Используйте Transporter для ручной загрузки (см. `ЗАГРУЗКА_ЧЕРЕЗ_TRANSPORTER.md`)

---

## 🤖 ГОТОВЫЙ СКРИПТ ДЛЯ ML СИСТЕМЫ

### Скрипт для автоматического запуска workflow

```bash
#!/bin/bash
# Скрипт для запуска workflow appstore.yml

set -e

echo "🚀 Запуск workflow для отправки в App Store..."

# Перейти в директорию проекта
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Проверить, что мы в правильной директории
if [ ! -f "ALADDIN.xcodeproj/project.pbxproj" ]; then
    echo "❌ Ошибка: не найден проект ALADDIN.xcodeproj"
    exit 1
fi

# Проверить, что есть изменения для коммита (опционально)
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Есть незакоммиченные изменения"
    read -p "Закоммитить изменения? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Prepare for App Store build $(date +%Y%m%d-%H%M%S)"
    fi
fi

# Создать тег
TAG_NAME="v1.0.0-$(date +%Y%m%d-%H%M%S)"
echo "📌 Создание тега: $TAG_NAME"
git tag -a "$TAG_NAME" -m "App Store build $(date +%Y%m%d-%H%M%S)"

# Отправить изменения и тег
echo "📤 Отправка на GitHub..."
git push origin master
git push origin --tags

echo "✅ Тег отправлен! Workflow запустится автоматически."
echo "🔗 Проверьте статус: https://github.com/sergey234/ALADDIN_FAMILY/actions"
```

**Использование:**
```bash
chmod +x запустить_workflow.sh
./запустить_workflow.sh
```

---

## 📊 ЧЕКЛИСТ ПЕРЕД ЗАПУСКОМ

### Перед запуском workflow убедитесь:

- [ ] Все изменения закоммичены и отправлены на GitHub
- [ ] GitHub Secrets установлены (см. `ПОЛНАЯ_СВОДКА_СЕРТИФИКАТОВ_И_КЛЮЧЕЙ.md`):
  - [ ] `IOS_DISTRIBUTION_CERTIFICATE`
  - [ ] `IOS_DISTRIBUTION_CERTIFICATE_PASSWORD`
  - [ ] `PROVISIONING_PROFILE_APP`
  - [ ] `PROVISIONING_PROFILE_EXTENSION`
  - [ ] `APP_STORE_CONNECT_API_KEY`
  - [ ] `APP_STORE_CONNECT_ISSUER_ID`
  - [ ] `APP_STORE_CONNECT_API_KEY_ID`
  - [ ] `APPLE_TEAM_ID`
- [ ] Проект компилируется локально без ошибок
- [ ] Выбран правильный workflow: **"Build and Upload to App Store"** (appstore.yml)
- [ ] НЕ выбран workflow: "Build Only (No Upload)" (build-only.yml)

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ И ПРЕДУПРЕЖДЕНИЯ

### ⚠️ Проблема #1: build-only.yml запускался автоматически

**Что происходило:**
- При каждом `git push origin master` автоматически запускался `build-only.yml`
- Он собирал архив без подписи
- Не загружал в App Store Connect
- Тратилось время впустую

**Решение:**
- ✅ Автоматический запуск `build-only.yml` отключен
- ✅ Используйте только `appstore.yml` для App Store

### ⚠️ Проблема #2: Архив был не готов для App Store

**build-only.yml создавал:**
- ❌ Архив без подписи (`CODE_SIGN_IDENTITY=""`)
- ❌ Без provisioning profiles
- ❌ Без IPA файла
- ❌ Только для CI тестирования

**appstore.yml создает:**
- ✅ Архив с подписью
- ✅ С provisioning profiles
- ✅ Создает IPA
- ✅ Отправляет в App Store

### ✅ Подтверждение: appstore.yml — правильный workflow

**Да, подтверждаю: `appstore.yml` — это правильный workflow:**

- ✅ С подписью
- ✅ С профилями
- ✅ Создает IPA
- ✅ Отправляет в App Store

**Это тот workflow, который нужно использовать для загрузки в App Store. Используем в работе только его!**

---

## 🔗 ПОЛЕЗНЫЕ ССЫЛКИ

- **GitHub Actions:** https://github.com/sergey234/ALADDIN_FAMILY/actions
- **GitHub Secrets:** https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
- **App Store Connect:** https://appstoreconnect.apple.com
- **Developer Portal:** https://developer.apple.com/account/resources/profiles/list

---

## 📝 ИСТОРИЯ ИЗМЕНЕНИЙ

### Версия 1.0 (30 ноября 2025)
- ✅ Создана полная инструкция по запуску workflow
- ✅ Описаны два способа запуска (тег и вручную)
- ✅ Добавлены решения проблем
- ✅ Добавлен готовый скрипт для ML системы
- ✅ Добавлен чеклист перед запуском
- ✅ Подтверждено, что appstore.yml — правильный workflow

---

**Последнее обновление:** 30 ноября 2025  
**Версия документа:** 1.0  
**Статус:** ✅ Готово к использованию
