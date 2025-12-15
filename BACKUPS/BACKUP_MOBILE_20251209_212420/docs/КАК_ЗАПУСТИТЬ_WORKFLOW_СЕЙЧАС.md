# 🚀 КАК ЗАПУСТИТЬ WORKFLOW СЕЙЧАС

**Дата:** 1 декабря 2025  
**Проблема:** Workflow не запускается автоматически, но GitHub Actions включен

---

## ✅ ПРОВЕРЕНО:

- ✅ GitHub Actions включен в настройках
- ✅ Структура `on:` правильная
- ✅ YAML синтаксис валидный
- ✅ Коммиты отправлены на GitHub

---

## 🚀 СПОСОБ 1: Запуск через GitHub UI (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Откройте страницу workflow

**Ссылка:** https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml

### Шаг 2: Нажмите "Run workflow"

1. Найдите кнопку **"Run workflow"** (справа вверху, зеленая кнопка)
2. Если кнопки нет - см. раздел "Если кнопки нет" ниже

### Шаг 3: Выберите параметры

1. Выберите ветку: **`master`**
2. Нажмите зеленую кнопку **"Run workflow"**

### Шаг 4: Проверьте запуск

1. Workflow должен появиться в списке запусков
2. Статус: **"Queued"** → **"In progress"** → **"Completed"**
3. Время выполнения: 15-30 минут

---

## 🏷️ СПОСОБ 2: Запуск через тег (АВТОМАТИЧЕСКИЙ)

### Шаг 1: Создайте тег

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Создать тег
git tag -a "v1.0.3-$(date +%Y%m%d-%H%M%S)" -m "Test: запуск appstore.yml"

# Отправить тег
git push origin --tags
```

### Шаг 2: Проверьте запуск

1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions
2. Найдите запуск с вашим тегом
3. Workflow должен запуститься автоматически

---

## 🔧 ЕСЛИ КНОПКИ "RUN WORKFLOW" НЕТ

### Причина 1: Workflow отключен

**Решение:**
1. Проверьте настройки: https://github.com/sergey234/ALADDIN_FAMILY/settings/actions
2. Убедитесь, что **"Allow all actions and reusable workflows"** включено
3. Проверьте, что workflow не заблокирован

### Причина 2: Нет прав доступа

**Решение:**
1. Проверьте права: https://github.com/sergey234/ALADDIN_FAMILY/settings/access
2. Убедитесь, что у вас есть **Write** доступ к репозиторию

### Причина 3: Workflow не поддерживает workflow_dispatch

**Проверка:**
1. Откройте файл: `.github/workflows/appstore.yml`
2. Проверьте, что есть строка: `workflow_dispatch:`
3. Если нет - добавьте (см. ниже)

---

## 🔧 ЕСЛИ WORKFLOW НЕ ЗАПУСКАЕТСЯ ПОСЛЕ НАЖАТИЯ

### Причина 1: Проблема с секретами

**Проверка:**
1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
2. Убедитесь, что все секреты установлены:
   - `IOS_DISTRIBUTION_CERTIFICATE`
   - `IOS_DISTRIBUTION_CERTIFICATE_PASSWORD`
   - `PROVISIONING_PROFILE_APP`
   - `PROVISIONING_PROFILE_EXTENSION`
   - `APP_STORE_CONNECT_API_KEY`
   - `APP_STORE_CONNECT_ISSUER_ID`
   - `APP_STORE_CONNECT_API_KEY_ID`
   - `APPLE_TEAM_ID`

### Причина 2: Ошибка в workflow файле

**Проверка:**
1. Откройте запуск workflow
2. Проверьте логи ошибок
3. Найдите, на каком шаге упал workflow
4. Исправьте ошибку

### Причина 3: Размер файла слишком большой

**Решение:**
- Создать упрощенную версию (см. РЕШЕНИЕ 1 ниже)

---

## 🔧 АЛЬТЕРНАТИВНЫЕ РЕШЕНИЯ

### РЕШЕНИЕ 1: Создать упрощенную версию

**Цель:** Проверить, запускается ли workflow вообще

**Шаги:**
1. Создать новый файл: `.github/workflows/appstore-simple.yml`
2. Включить только основные шаги (50-100 строк):
   - Checkout
   - Setup Xcode
   - Build Archive
   - Export IPA
3. Проверить, запускается ли
4. Если да - постепенно добавлять код

**Вероятность успеха:** 80%

---

### РЕШЕНИЕ 2: Переименовать файл

**Цель:** Обойти возможный кэш GitHub

**Шаги:**
1. Создать новый файл: `.github/workflows/build-appstore.yml`
2. Скопировать весь код из `appstore.yml`
3. Удалить старый `appstore.yml`
4. Закоммитить и отправить на GitHub
5. Попробовать запустить новый workflow

**Вероятность успеха:** 50%

---

### РЕШЕНИЕ 3: Разбить на части

**Цель:** Упростить структуру

**Шаги:**
1. Создать `setup.yml` - настройка (сертификат, профили)
2. Создать `build.yml` - сборка архива
3. Создать `export.yml` - экспорт IPA
4. Использовать `needs:` для связи между jobs

**Вероятность успеха:** 70%

---

### РЕШЕНИЕ 4: Проверить кэш GitHub

**Цель:** Обойти возможный кэш

**Шаги:**
1. Подождать 5-10 минут
2. Очистить кэш браузера (Cmd+Shift+R или Ctrl+Shift+R)
3. Обновить страницу Actions
4. Попробовать запустить снова

**Вероятность успеха:** 40%

---

## 📋 ЧЕКЛИСТ ПЕРЕД ЗАПУСКОМ

- [ ] GitHub Actions включен в настройках
- [ ] Workflow permissions: "Read and write permissions"
- [ ] Все секреты установлены в GitHub Secrets
- [ ] Проект компилируется локально без ошибок
- [ ] Выбран правильный workflow: "Build and Upload to App Store"
- [ ] Попробован ручной запуск через UI
- [ ] Проверены логи (если workflow запустился)

---

## 🔗 ПОЛЕЗНЫЕ ССЫЛКИ

- **GitHub Actions:** https://github.com/sergey234/ALADDIN_FAMILY/actions
- **Workflow:** https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
- **GitHub Secrets:** https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
- **Настройки Actions:** https://github.com/sergey234/ALADDIN_FAMILY/settings/actions

---

## 🎯 РЕКОМЕНДАЦИЯ

**Начните с СПОСОБА 1 (через GitHub UI):**

1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
2. Нажмите **"Run workflow"**
3. Выберите ветку: **`master`**
4. Нажмите **"Run workflow"**

**Если не работает:**
- Попробуйте РЕШЕНИЕ 1 (упрощенная версия)
- Или РЕШЕНИЕ 2 (переименовать файл)

---

**Дата:** 1 декабря 2025  
**Статус:** Инструкция готова к использованию

