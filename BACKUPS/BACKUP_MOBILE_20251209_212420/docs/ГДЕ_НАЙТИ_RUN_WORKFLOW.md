# 🔍 ГДЕ НАЙТИ КНОПКУ "Run workflow" В GITHUB ACTIONS

**Дата:** 1 декабря 2025  
**Проблема:** Не видно кнопку "Run workflow" в GitHub UI

---

## 📍 МЕСТОПОЛОЖЕНИЕ КНОПКИ "Run workflow"

### Способ 1: Через страницу Actions (основной способ)

1. **Откройте страницу Actions:**
   ```
   https://github.com/sergey234/ALADDIN_FAMILY/actions
   ```

2. **Найдите workflow "Build and Upload to App Store":**
   - В левой панели найдите список workflows
   - Или прокрутите вниз до списка всех workflows
   - Найдите: **"Build and Upload to App Store"**

3. **Кликните на название workflow:**
   - Это откроет страницу конкретного workflow
   - URL будет: `https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml`

4. **Кнопка "Run workflow" находится:**
   - **Справа вверху** страницы workflow
   - Рядом с кнопками фильтров
   - Выглядит как синяя кнопка с текстом "Run workflow"

---

### Способ 2: Прямая ссылка на workflow

**Откройте напрямую:**
```
https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
```

**Кнопка "Run workflow" должна быть справа вверху.**

---

## ⚠️ ЕСЛИ КНОПКИ НЕТ

### Причина 1: Workflow не имеет `workflow_dispatch`

**Проверьте файл `.github/workflows/appstore.yml`:**

Должно быть:
```yaml
on:
  workflow_dispatch: {}  # ← Должно быть!
  push:
    branches:
      - master
  tags:
    - 'v*'
```

**Если нет `workflow_dispatch`** - кнопки не будет!

---

### Причина 2: Actions отключены в настройках

**Проверьте:**
1. Откройте: `https://github.com/sergey234/ALADDIN_FAMILY/settings/actions`
2. В разделе **"Actions permissions"** должно быть:
   - ✅ "Allow all actions and reusable workflows"
   - ❌ НЕ должно быть: "Disable actions"

**Если Actions отключены** - кнопки не будет!

---

### Причина 3: Нет прав доступа

**Проверьте:**
- Вы должны быть владельцем репозитория или иметь права администратора
- Если вы только участник (collaborator) - кнопки может не быть

---

### Причина 4: Workflow еще не был запущен ни разу

**Решение:**
- Попробуйте сделать push в master (должен запуститься автоматически)
- После первого запуска кнопка должна появиться

---

## 🔍 АЛЬТЕРНАТИВНЫЕ СПОСОБЫ ЗАПУСКА

### Способ 1: Через GitHub API

Если кнопки нет, можно запустить через API:

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml/dispatches \
  -d '{"ref":"master"}'
```

---

### Способ 2: Создать тег

Workflow запустится автоматически при создании тега:

```bash
git tag -a "v1.0.1" -m "Test workflow"
git push origin --tags
```

---

### Способ 3: Push в master

Workflow запустится автоматически при push в master:

```bash
git commit --allow-empty -m "Trigger workflow"
git push origin master
```

---

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ

### Шаг 1: Откройте страницу Actions

```
https://github.com/sergey234/ALADDIN_FAMILY/actions
```

---

### Шаг 2: Найдите workflow

В левой панели найдите:
- **"Build and Upload to App Store"**
- Или прокрутите вниз до списка workflows

---

### Шаг 3: Кликните на название workflow

Это откроет страницу:
```
https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
```

---

### Шаг 4: Найдите кнопку "Run workflow"

- **Местоположение:** Справа вверху страницы
- **Внешний вид:** Синяя кнопка с текстом "Run workflow"
- **Рядом с:** Кнопками фильтров и поиска

---

### Шаг 5: Нажмите "Run workflow"

1. Нажмите кнопку "Run workflow"
2. Выберите ветку: `master`
3. Нажмите зеленую кнопку "Run workflow"

---

## 🖼️ ВИЗУАЛЬНОЕ ОПИСАНИЕ

```
┌─────────────────────────────────────────────────────────┐
│ GitHub > sergey234 > ALADDIN_FAMILY > Actions           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [Filters ▼]  [Run workflow] ← КНОПКА ЗДЕСЬ!            │
│                                                          │
│  Build and Upload to App Store                          │
│  ────────────────────────────────────────────────────    │
│                                                          │
│  Workflow runs                                           │
│  [All] [Success] [Failure] [Cancelled]                  │
│                                                          │
│  (список запусков)                                       │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ ПРОВЕРКА

### Чеклист:

- [ ] Открыта страница: `https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml`
- [ ] В файле `.github/workflows/appstore.yml` есть `workflow_dispatch: {}`
- [ ] Actions включены в настройках
- [ ] Есть права администратора репозитория
- [ ] Кнопка "Run workflow" видна справа вверху

---

## 🚨 ЕСЛИ ВСЕ ЕЩЕ НЕТ КНОПКИ

1. **Проверьте файл workflow:**
   ```bash
   grep -A 2 "workflow_dispatch" .github/workflows/appstore.yml
   ```

2. **Проверьте настройки Actions:**
   - `https://github.com/sergey234/ALADDIN_FAMILY/settings/actions`

3. **Попробуйте альтернативные способы:**
   - Создайте тег: `git tag -a "v1.0.1" && git push origin --tags`
   - Или сделайте push: `git commit --allow-empty -m "trigger" && git push`

---

**Дата:** 1 декабря 2025  
**Статус:** Инструкция по поиску кнопки "Run workflow"

