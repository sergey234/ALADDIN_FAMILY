# 📦 ИНСТРУКЦИЯ: КАК ЗАГРУЗИТЬ IPA В APP STORE CONNECT

**Для:** Другая ML система  
**Дата:** 03.12.2025  
**Проект:** ALADDIN iOS

---

## 🎯 КРАТКОЕ ОПИСАНИЕ ПРОЦЕССА

IPA файл загружается в App Store Connect автоматически через GitHub Actions workflow `check-secrets.yml` с использованием `apple-actions/upload-testflight-build@v1`.

---

## 📋 ЧТО НУЖНО ДЛЯ ЗАГРУЗКИ

### 1. GitHub Secrets (обязательно):

- `APP_STORE_CONNECT_API_KEY` - приватный ключ API (файл .p8)
- `APP_STORE_CONNECT_ISSUER_ID` - ID издателя
- `APP_STORE_CONNECT_API_KEY_ID` - ID API ключа

### 2. Workflow файл:

- `.github/workflows/check-secrets.yml` - основной workflow для сборки и загрузки

### 3. IPA файл:

- Создается автоматически в workflow
- Путь: `build/export/ALADDIN.ipa`

---

## 🔧 КАК РАБОТАЕТ ЗАГРУЗКА

### Шаг 1: Сборка IPA

```yaml
- name: Export IPA
  run: |
    xcodebuild -exportArchive \
      -archivePath ALADDIN.xcarchive \
      -exportPath build/export \
      -exportOptionsPlist ExportOptions.plist
```

### Шаг 2: Настройка API ключей

```yaml
- name: Setup App Store Connect API keys
  run: |
    if [ -n "${{ secrets.APP_STORE_CONNECT_API_KEY }}" ] && \
       [ -n "${{ secrets.APP_STORE_CONNECT_ISSUER_ID }}" ] && \
       [ -n "${{ secrets.APP_STORE_CONNECT_API_KEY_ID }}" ]; then
      echo "✅ App Store Connect API keys are set"
      echo "APP_STORE_CONNECT_API_KEY_SET=true" >> $GITHUB_ENV
    else
      echo "⚠️ App Store Connect API keys not set"
      echo "APP_STORE_CONNECT_API_KEY_SET=false" >> $GITHUB_ENV
    fi
```

### Шаг 3: Загрузка в App Store Connect

```yaml
- name: Upload to App Store Connect using apple-actions
  if: env.APP_STORE_CONNECT_API_KEY_SET == 'true'
  uses: apple-actions/upload-testflight-build@v1
  with:
    app-path: ${{ env.IPA_FILE_PATH }}
    api-private-key: ${{ secrets.APP_STORE_CONNECT_API_KEY }}
    issuer-id: ${{ secrets.APP_STORE_CONNECT_ISSUER_ID }}
    api-key-id: ${{ secrets.APP_STORE_CONNECT_API_KEY_ID }}
```

### Шаг 4: Сохранение как артефакт

```yaml
- name: Upload IPA as artifact
  uses: actions/upload-artifact@v4
  if: always() && env.IPA_FILE_PATH != ''
  with:
    name: ALADDIN-IPA
    path: ${{ env.IPA_FILE_PATH }}
    retention-days: 30
```

---

## 🚀 КАК ЗАПУСТИТЬ ЗАГРУЗКУ

### Вариант 1: Автоматический запуск (через push)

Workflow запускается автоматически при push в ветку `master`:

```bash
git push origin master
```

### Вариант 2: Ручной запуск (через GitHub Actions)

1. Откройте GitHub → Actions
2. Выберите workflow "Check Secrets and Build"
3. Нажмите "Run workflow"
4. Выберите ветку (обычно `master`)
5. Нажмите "Run workflow"

### Вариант 3: Через терминал (локально)

```bash
# Перейти в директорию проекта
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Сделать коммит и push (если есть изменения)
git add .
git commit -m "chore: trigger workflow for IPA upload"
git push origin master
```

---

## 📝 ПОЛНАЯ ИНСТРУКЦИЯ ДЛЯ ML СИСТЕМЫ

### Шаг 1: Проверить наличие workflow

**Файл:** `.github/workflows/check-secrets.yml`

**Проверка:**
```bash
ls -la .github/workflows/check-secrets.yml
```

**Если файла нет:**
- Создать workflow файл (см. ниже)

### Шаг 2: Проверить GitHub Secrets

**Необходимые secrets:**
- `APP_STORE_CONNECT_API_KEY` - приватный ключ (.p8 файл)
- `APP_STORE_CONNECT_ISSUER_ID` - ID издателя
- `APP_STORE_CONNECT_API_KEY_ID` - ID API ключа

**Проверка через GitHub:**
1. GitHub → Settings → Secrets and variables → Actions
2. Проверить наличие всех трех secrets

### Шаг 3: Запустить workflow

**Через GitHub Actions UI:**
1. GitHub → Actions
2. Выберите "Check Secrets and Build"
3. Нажмите "Run workflow"
4. Выберите ветку `master`
5. Нажмите "Run workflow"

**Через git push:**
```bash
# Создать пустой коммит для триггера
git commit --allow-empty -m "chore: trigger IPA upload"
git push origin master
```

### Шаг 4: Проверить результат

**В GitHub Actions:**
1. Откройте запущенный workflow
2. Проверьте шаг "Upload to App Store Connect using apple-actions"
3. Должно быть: ✅ "UPLOAD SUCCEEDED"

**В App Store Connect:**
1. App Store Connect → TestFlight → Builds
2. Найдите новый билд
3. Статус должен быть "Processing" → "Ready to Submit"

---

## 🔍 СТРУКТУРА WORKFLOW

### Основные секции:

1. **on:** - триггеры запуска
   ```yaml
   on:
     push:
       branches: [ master ]
     workflow_dispatch:
   ```

2. **jobs:** - задачи workflow
   - `check-secrets` - проверка secrets и сборка
   - `upload-ipa` - загрузка IPA (если есть API ключи)

3. **steps:** - шаги выполнения
   - Checkout code
   - Setup Xcode
   - Build archive
   - Export IPA
   - Setup API keys
   - Upload to App Store Connect
   - Upload as artifact

---

## ⚙️ КОНФИГУРАЦИЯ WORKFLOW

### Ключевые параметры:

**Xcode версия:**
```yaml
- uses: maxim-lobanov/setup-xcode@v1
  with:
    xcode-version: '16.2.0'
```

**Схема проекта:**
```yaml
-scheme ALADDIN
```

**Экспорт IPA:**
```yaml
-exportOptionsPlist ExportOptions.plist
```

**Загрузка через apple-actions:**
```yaml
uses: apple-actions/upload-testflight-build@v1
with:
  app-path: ${{ env.IPA_FILE_PATH }}
  api-private-key: ${{ secrets.APP_STORE_CONNECT_API_KEY }}
  issuer-id: ${{ secrets.APP_STORE_CONNECT_ISSUER_ID }}
  api-key-id: ${{ secrets.APP_STORE_CONNECT_API_KEY_ID }}
```

---

## 📊 ЛОГИ И ОТЛАДКА

### Успешная загрузка:

```
✅ App Store Connect API keys are set
IPA file found: build/export/ALADDIN.ipa
Ready to upload to App Store Connect
UPLOAD SUCCEEDED
No errors uploading 'build/export/ALADDIN.ipa'
```

### Ошибки:

**Ошибка 1: API ключи не настроены**
```
⚠️ App Store Connect API keys not set
IPA file will be available as artifact for manual upload
```
**Решение:** Настроить GitHub Secrets

**Ошибка 2: IPA файл не найден**
```
Error: IPA file not found!
```
**Решение:** Проверить путь к IPA файлу

**Ошибка 3: Ошибка аутентификации**
```
Failed to generate JWT token
```
**Решение:** Проверить формат API ключа (.p8)

---

## 🔄 ПОВТОРНАЯ ЗАГРУЗКА IPA

### Если нужно загрузить IPA еще раз:

**Вариант 1: Через GitHub Actions**
1. GitHub → Actions
2. Выберите последний успешный workflow
3. Нажмите "Re-run jobs" → "Re-run all jobs"

**Вариант 2: Через git push**
```bash
# Создать пустой коммит
git commit --allow-empty -m "chore: re-upload IPA"
git push origin master
```

**Вариант 3: Через workflow_dispatch**
1. GitHub → Actions
2. Выберите "Check Secrets and Build"
3. Нажмите "Run workflow"
4. Выберите ветку `master`
5. Нажмите "Run workflow"

---

## 📋 ЧЕКЛИСТ ДЛЯ ML СИСТЕМЫ

### Перед загрузкой:

- [ ] Workflow файл существует: `.github/workflows/check-secrets.yml`
- [ ] GitHub Secrets настроены (3 secrets)
- [ ] Проект компилируется без ошибок
- [ ] ExportOptions.plist настроен правильно
- [ ] Provisioning profiles настроены

### После загрузки:

- [ ] Workflow выполнен успешно
- [ ] IPA загружен в App Store Connect
- [ ] Билд появился в TestFlight → Builds
- [ ] Статус билда: "Processing" → "Ready to Submit"

---

## 🎯 БЫСТРАЯ КОМАНДА ДЛЯ ЗАПУСКА

```bash
# Перейти в директорию проекта
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Создать пустой коммит для триггера workflow
git commit --allow-empty -m "chore: trigger IPA upload to App Store Connect"

# Отправить в GitHub
git push origin master
```

---

## 📞 ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ

### Проблема 1: Workflow не запускается

**Решение:**
- Проверить, что файл `.github/workflows/check-secrets.yml` существует
- Проверить синтаксис YAML
- Проверить триггеры (`on:`)

### Проблема 2: API ключи не работают

**Решение:**
- Проверить формат ключа (.p8)
- Проверить, что ключ не истек
- Проверить права доступа ключа в App Store Connect

### Проблема 3: IPA не создается

**Решение:**
- Проверить, что проект компилируется
- Проверить ExportOptions.plist
- Проверить provisioning profiles

### Проблема 4: Ошибка "The bundle version must be higher than the previously uploaded version"

**Ошибка:**
```
Error: The bundle version must be higher than the previously uploaded version: '1'
```

**Решение:**
1. Проверить текущий build number в проекте:
   ```bash
   grep "CURRENT_PROJECT_VERSION" ALADDIN.xcodeproj/project.pbxproj
   ```

2. Увеличить build number (например, с 2 до 3):
   ```bash
   # Заменить все CURRENT_PROJECT_VERSION = 2 на CURRENT_PROJECT_VERSION = 3
   sed -i '' 's/CURRENT_PROJECT_VERSION = 2;/CURRENT_PROJECT_VERSION = 3;/g' ALADDIN.xcodeproj/project.pbxproj
   ```

3. Закоммитить и запустить workflow:
   ```bash
   git add ALADDIN.xcodeproj/project.pbxproj
   git commit -m "fix: увеличить build number для избежания дубликата"
   git push origin master
   ```

**Важно:** Build number должен быть уникальным и больше предыдущего!

---

## ✅ ИТОГ

### Процесс загрузки IPA:

1. **Workflow запускается** (через push или вручную)
2. **Проект собирается** (xcodebuild archive)
3. **IPA экспортируется** (xcodebuild -exportArchive)
4. **API ключи проверяются** (GitHub Secrets)
5. **IPA загружается** (apple-actions/upload-testflight-build@v1)
6. **IPA сохраняется как артефакт** (для ручной загрузки, если нужно)

### Результат:

- ✅ IPA загружен в App Store Connect
- ✅ Билд появился в TestFlight → Builds
- ✅ Статус: "Processing" → "Ready to Submit" (30-60 минут)

---

**Удачи с загрузкой! 🚀**

