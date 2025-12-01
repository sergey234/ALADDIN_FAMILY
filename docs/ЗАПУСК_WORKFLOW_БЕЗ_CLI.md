# 🚀 ЗАПУСК WORKFLOW БЕЗ GITHUB CLI

## ⚠️ ПРОБЛЕМА

GitHub CLI (`gh`) требует macOS Monterey (12.0) или новее, а у вас macOS 11 (Big Sur).

## ✅ РЕШЕНИЯ

### 1. **Ручной запуск через GitHub UI (самый простой)**

1. Откройте в браузере:
   ```
   https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
   ```

2. Нажмите кнопку **"Run workflow"** справа

3. Выберите ветку `master`

4. Нажмите зеленую кнопку **"Run workflow"**

✅ **Это самый надежный способ!**

---

### 2. **Автоматический запуск при push**

Workflow настроен на автоматический запуск при push в `master`.

**Просто сделайте push:**
```bash
git add .
git commit -m "trigger: запуск workflow"
git push origin master
```

Workflow запустится автоматически через несколько секунд.

---

### 3. **Запуск через GitHub API (curl)**

Если у вас есть Personal Access Token:

```bash
# Создайте токен: https://github.com/settings/tokens
# Нужны права: workflow

curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml/dispatches \
  -d '{"ref":"master"}'
```

**Создание токена:**
1. Зайдите: https://github.com/settings/tokens
2. Нажмите "Generate new token (classic)"
3. Выберите права: `workflow`
4. Скопируйте токен и используйте в команде выше

---

### 4. **Скрипт для запуска через API**

Создайте файл `запустить_workflow_api.sh`:

```bash
#!/bin/bash

# Получите токен: https://github.com/settings/tokens
GITHUB_TOKEN="YOUR_TOKEN_HERE"
REPO="sergey234/ALADDIN_FAMILY"
WORKFLOW="appstore.yml"
BRANCH="master"

curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/actions/workflows/$WORKFLOW/dispatches" \
  -d "{\"ref\":\"$BRANCH\"}"

if [ $? -eq 0 ]; then
    echo "✅ Workflow запущен!"
    echo "Проверьте: https://github.com/$REPO/actions/workflows/$WORKFLOW"
else
    echo "❌ Ошибка при запуске workflow"
fi
```

**Использование:**
```bash
chmod +x запустить_workflow_api.sh
# Отредактируйте файл и вставьте ваш токен
./запустить_workflow_api.sh
```

---

## 🎯 РЕКОМЕНДУЕМЫЙ СПОСОБ

**Используйте ручной запуск через GitHub UI** - это самый простой и надежный способ:

1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
2. Нажмите **"Run workflow"**
3. Выберите `master`
4. Нажмите **"Run workflow"**

✅ **Работает всегда, не требует установки ничего!**

---

## 📊 ПРОВЕРКА СТАТУСА

После запуска проверьте статус:
```
https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
```

**Статусы:**
- 🟡 Желтый кружок - выполняется
- ✅ Зеленая галочка - успешно
- 🔴 Красный крестик - ошибка (откройте для логов)

---

## 💡 СОВЕТ

Для частых запусков workflow лучше использовать **ручной запуск через UI** или **автоматический запуск при push**. Это не требует установки дополнительных инструментов.

