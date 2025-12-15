# 🚀 КАК ЗАПУСТИТЬ WORKFLOW

## ✅ АВТОМАТИЧЕСКИЙ ЗАПУСК

Workflow настроен на автоматический запуск при **push в master**. 

**Последний push:** коммит `bf053ab5` - workflow должен запуститься автоматически.

**Проверьте статус:**
```
https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
```

---

## 🖱️ РУЧНОЙ ЗАПУСК ЧЕРЕЗ GITHUB UI

### Шаг 1: Откройте workflow
```
https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
```

### Шаг 2: Нажмите "Run workflow"
1. Справа найдите кнопку **"Run workflow"**
2. Нажмите на неё
3. Выберите ветку `master`
4. Нажмите зеленую кнопку **"Run workflow"**

---

## 💻 ЗАПУСК ЧЕРЕЗ КОМАНДНУЮ СТРОКУ

### Вариант 1: GitHub CLI (рекомендуется)

**Установка:**
```bash
brew install gh
gh auth login
```

**Запуск:**
```bash
gh workflow run appstore.yml --ref master
```

**Проверка статуса:**
```bash
gh run list --workflow=appstore.yml
```

### Вариант 2: Скрипт (если установлен GitHub CLI)

```bash
./запустить_workflow.sh
```

### Вариант 3: Через API (нужен токен)

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml/dispatches \
  -d '{"ref":"master"}'
```

---

## 📊 ПРОВЕРКА СТАТУСА

### В браузере:
```
https://github.com/sergey234/ALADDIN_FAMILY/actions
```

**Статусы:**
- 🟡 **Желтый кружок** - выполняется
- ✅ **Зеленая галочка** - успешно завершен
- 🔴 **Красный крестик** - упал (откройте для логов)
- ⚪ **Серый кружок** - в очереди

### Через GitHub CLI:
```bash
gh run list --workflow=appstore.yml --limit 5
gh run watch
```

---

## 🎯 БЫСТРЫЙ ЗАПУСК

**Самый простой способ:**
1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
2. Нажмите **"Run workflow"** → выберите `master` → **"Run workflow"**

---

## ✅ ТЕКУЩИЙ СТАТУС

- ✅ Push выполнен (коммит `bf053ab5`)
- ✅ Workflow должен запуститься автоматически
- ⏳ Проверьте статус через 1-2 минуты

**Прямая ссылка для проверки:**
```
https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
```

