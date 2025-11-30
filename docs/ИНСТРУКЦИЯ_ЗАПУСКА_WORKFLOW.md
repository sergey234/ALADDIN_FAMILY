# 📋 ПОЛНАЯ ИНСТРУКЦИЯ: Как запустить workflow appstore.yml

**Дата создания:** 30 ноября 2025  
**Цель:** Подробная инструкция для ML системы о том, как запустить workflow для сборки и загрузки приложения в App Store

---

## 🎯 ЦЕЛЬ

Запустить workflow `appstore.yml`, который:
- ✅ Собирает приложение с подписью
- ✅ Использует provisioning profiles
- ✅ Создает IPA файл
- ✅ Загружает в App Store Connect

---

## 📌 ПРЕДВАРИТЕЛЬНЫЕ УСЛОВИЯ

### 1. Проверка конфигурации workflow

**Файл:** `.github/workflows/appstore.yml`

**Проверьте триггеры:**
```yaml
on:
  workflow_dispatch:  # Запуск вручную через GitHub UI
  push:
    tags:
      - 'v*'  # Автоматически при создании тега v1.0.0, v1.0.1 и т.д.
```

**Важно:** Workflow должен запускаться только при тегах `v*` или вручную.

### 2. Проверка конфликтующих workflows

**Файл:** `.github/workflows/deploy.yml`

**Убедитесь, что deploy.yml НЕ запускается при тегах:**
```yaml
on:
  # ОТКЛЮЧЕНО для тегов - используем appstore.yml вместо этого
  # push:
  #   tags:
  #     - 'v*'
  workflow_dispatch:
```

**Почему это важно:** Если оба workflow настроены на теги `v*`, может запуститься не тот workflow.

---

## 🚀 СПОСОБ 1: Запуск через тег (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Проверка текущих тегов

```bash
# Перейти в директорию проекта
cd /path/to/ALADDIN_iOS

# Проверить текущие теги
git tag --list | tail -5
```

**Ожидаемый результат:**
```
v1.0.5
v1.0.6
v1.0.7
v1.0.8
```

### Шаг 2: Проверка статуса Git

```bash
# Проверить статус
git status

# Убедиться, что все изменения закоммичены
# Если есть незакоммиченные изменения:
git add .
git commit -m "Описание изменений"
git push origin master
```

### Шаг 3: Создание нового тега

```bash
# Создать тег с версией (увеличить на 1 от последней)
git tag -a "v1.0.9" -m "Release 1.0.9 - App Store Build"

# Проверить, что тег создан
git tag --list | grep v1.0.9
```

**Формат тега:** `vX.Y.Z` (например, `v1.0.9`, `v1.1.0`, `v2.0.0`)

### Шаг 4: Отправка тега в GitHub

```bash
# Отправить тег в GitHub
git push origin v1.0.9

# Или отправить все теги сразу
git push origin --tags
```

**Ожидаемый результат:**
```
Enumerating objects: 1, done.
Counting objects: 100% (1/1), done.
Writing objects: 100% (1/1), 175 bytes | 87.00 KiB/s, done.
Total 1 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/sergey234/ALADDIN_FAMILY.git
 * [new tag]           v1.0.9 -> v1.0.9
```

### Шаг 5: Проверка запуска workflow

**Через 1-2 минуты после отправки тега:**

1. Откройте страницу GitHub Actions:
   ```
   https://github.com/sergey234/ALADDIN_FAMILY/actions
   ```

2. Найдите workflow "Build and Upload to App Store"

3. Проверьте, что появился новый запуск с тегом `v1.0.9`

4. Статус должен быть:
   - `Queued` (в очереди)
   - `In progress` (выполняется)
   - `Success` (успешно) - через ~25-35 минут

---

## 🔧 СПОСОБ 2: Запуск вручную через GitHub UI

### Шаг 1: Открыть страницу workflow

```
https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
```

### Шаг 2: Нажать кнопку "Run workflow"

1. На странице workflow найдите кнопку **"Run workflow"** (справа вверху)
2. Нажмите на неё

### Шаг 3: Выбрать параметры

1. **Branch:** Выберите `master` (или нужную ветку)
2. **Use workflow from:** Оставьте `master`
3. Нажмите зеленую кнопку **"Run workflow"**

### Шаг 4: Проверка запуска

1. На странице появится новый запуск
2. Статус будет `Queued` или `In progress`
3. Дождитесь завершения (~25-35 минут)

---

## ⚠️ РЕШЕНИЕ ПРОБЛЕМ

### Проблема 1: Workflow не запускается при теге

**Причина:** Конфликт с другими workflows или неправильная конфигурация.

**Решение:**
1. Проверьте, что в `deploy.yml` отключен триггер на теги:
   ```yaml
   # ОТКЛЮЧЕНО для тегов
   # push:
   #   tags:
   #     - 'v*'
   ```

2. Убедитесь, что `appstore.yml` настроен правильно:
   ```yaml
   on:
     push:
       tags:
         - 'v*'
   ```

3. Закоммитьте изменения:
   ```bash
   git add .github/workflows/deploy.yml
   git commit -m "Fix: Disable deploy.yml auto-trigger on tags"
   git push origin master
   ```

4. Создайте новый тег:
   ```bash
   git tag -a "v1.0.10" -m "Release 1.0.10"
   git push origin v1.0.10
   ```

### Проблема 2: Запускается не тот workflow

**Причина:** Несколько workflows настроены на теги `v*`.

**Решение:**
1. Проверьте все workflows в `.github/workflows/`
2. Убедитесь, что только `appstore.yml` запускается при тегах
3. Отключите триггеры на теги в других workflows

### Проблема 3: Workflow запускается, но падает с ошибкой

**Причина:** Проблемы с сертификатами, профилями или конфигурацией.

**Решение:**
1. Откройте запуск workflow
2. Посмотрите логи ошибки
3. Проверьте GitHub Secrets:
   - `IOS_DISTRIBUTION_CERTIFICATE`
   - `IOS_DISTRIBUTION_CERTIFICATE_PASSWORD`
   - `PROVISIONING_PROFILE_APP`
   - `PROVISIONING_PROFILE_EXTENSION`
   - `APP_STORE_CONNECT_API_KEY`
   - `APP_STORE_CONNECT_ISSUER_ID`
   - `APP_STORE_CONNECT_API_KEY_ID`

---

## 📋 ПОЛНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ ДЕЙСТВИЙ

### Для ML системы (автоматизация):

```bash
#!/bin/bash

# 1. Перейти в директорию проекта
cd /path/to/ALADDIN_iOS

# 2. Проверить статус Git
git status

# 3. Закоммитить изменения (если есть)
git add .
git commit -m "Prepare for release"
git push origin master

# 4. Получить последний тег
LAST_TAG=$(git tag --list | grep -E '^v[0-9]' | sort -V | tail -1)
echo "Последний тег: $LAST_TAG"

# 5. Увеличить версию (пример: v1.0.9 -> v1.0.10)
# Это нужно сделать вручную или через скрипт версионирования
NEW_TAG="v1.0.10"

# 6. Создать тег
git tag -a "$NEW_TAG" -m "Release $NEW_TAG - App Store Build"

# 7. Отправить тег
git push origin "$NEW_TAG"

# 8. Подтверждение
echo "✅ Тег $NEW_TAG отправлен! Workflow должен запуститься через 1-2 минуты."
echo "🔍 Проверьте: https://github.com/sergey234/ALADDIN_FAMILY/actions"
```

---

## 🔍 ПРОВЕРКА УСПЕШНОСТИ

### Что проверить после запуска:

1. **Workflow запустился:**
   - Откройте: `https://github.com/sergey234/ALADDIN_FAMILY/actions`
   - Найдите запуск с нужным тегом
   - Статус должен быть `In progress` или `Success`

2. **Сборка успешна:**
   - В логах workflow должен быть шаг "Build Archive" со статусом ✅
   - Должен быть создан файл `ALADDIN.xcarchive`

3. **IPA создан:**
   - В логах должен быть шаг "Export IPA" со статусом ✅
   - Должен быть создан файл `.ipa`

4. **Загрузка в App Store:**
   - В логах должен быть шаг "Upload to App Store Connect" со статусом ✅
   - Через 30-60 минут билд должен появиться в App Store Connect

---

## 📝 ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Теги должны начинаться с `v`:**
   - ✅ Правильно: `v1.0.9`, `v1.1.0`, `v2.0.0`
   - ❌ Неправильно: `1.0.9`, `release-1.0.9`

2. **Только один workflow должен запускаться при тегах:**
   - ✅ `appstore.yml` - для App Store
   - ❌ `deploy.yml` - должен быть отключен для тегов

3. **Время выполнения:**
   - Сборка: ~15-20 минут
   - Экспорт IPA: ~2-3 минуты
   - Загрузка в App Store: ~5-10 минут
   - **ИТОГО: ~25-35 минут**

4. **Проверка перед запуском:**
   - Все изменения закоммичены
   - GitHub Secrets настроены
   - Provisioning profiles актуальны
   - Сертификаты не истекли

---

## 🎯 ИТОГОВАЯ КОМАНДА (БЫСТРЫЙ ЗАПУСК)

```bash
# Полная последовательность в одной команде:
cd /path/to/ALADDIN_iOS && \
git tag -a "v1.0.9" -m "Release 1.0.9 - App Store Build" && \
git push origin v1.0.9 && \
echo "✅ Workflow запущен! Проверьте: https://github.com/sergey234/ALADDIN_FAMILY/actions"
```

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

- **GitHub Actions документация:** https://docs.github.com/en/actions
- **Workflow файл:** `.github/workflows/appstore.yml`
- **Страница Actions:** `https://github.com/sergey234/ALADDIN_FAMILY/actions`
- **Страница Secrets:** `https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions`

---

**Дата последнего обновления:** 30 ноября 2025  
**Автор:** AI Assistant  
**Версия инструкции:** 1.0

