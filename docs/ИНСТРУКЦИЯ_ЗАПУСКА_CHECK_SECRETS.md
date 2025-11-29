# 🚀 ИНСТРУКЦИЯ: ЗАПУСК WORKFLOW "CHECK SECRETS"

**Статус:** Workflow файл создан и готов к использованию

---

## ✅ ЧТО УЖЕ СДЕЛАНО

1. ✅ Создан файл `.github/workflows/check-secrets.yml`
2. ✅ Workflow настроен для проверки всех секретов
3. ✅ Файл добавлен в git (если нужно — сделать commit и push)

---

## 📋 ШАГИ ДЛЯ ЗАПУСКА WORKFLOW

### Шаг 1: Убедиться, что файл в GitHub

**Если файл ещё не в GitHub:**

1. **Сделать commit и push:**
   ```bash
   cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
   git add .github/workflows/check-secrets.yml
   git commit -m "Add Check Secrets workflow"
   git push origin main
   ```

**Если файл уже в GitHub:**
- Переходите к шагу 2

---

### Шаг 2: Открыть GitHub Actions

1. **Откройте браузер**
2. **Перейдите по ссылке:**
   - https://github.com/sergey234/ALADDIN_FAMILY/actions

---

### Шаг 3: Найти workflow "Check Secrets"

1. **В левой панели** найдите раздел "All workflows"
2. **Найдите** "Check Secrets" в списке
3. **Если его нет:**
   - Подождите 1-2 минуты (GitHub может обновляться)
   - Обновите страницу (F5 или Cmd+R)
   - Проверьте, что файл был закоммичен и запушен

---

### Шаг 4: Запустить workflow

1. **Нажмите на** "Check Secrets" в списке workflows
2. **Справа вверху** нажмите кнопку **"Run workflow"**
3. **Выберите ветку:**
   - Выберите `main` или `master` из выпадающего списка
4. **Нажмите зелёную кнопку** **"Run workflow"**

---

### Шаг 5: Проверить результат

1. **Дождитесь запуска** (5-10 секунд)
2. **Нажмите на запущенный workflow** в списке
3. **Нажмите на job** "check-secrets"
4. **Проверьте логи:**
   - Откройте каждый step
   - Проверьте вывод

---

## ✅ ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

### Если все секреты настроены:

```
✅ APP_STORE_CONNECT_API_KEY is set
✅ Format looks correct (contains BEGIN PRIVATE KEY)
✅ APP_STORE_CONNECT_ISSUER_ID is set
✅ Format looks correct (UUID)
✅ APP_STORE_CONNECT_API_KEY_ID is set
✅ APPLE_TEAM_ID is set

📋 SUMMARY:
===========
✅ All required secrets are set!
✅ You can use 'Build and Upload to App Store' workflow
```

**Статус:** ✅ Зелёная галочка (Success)

---

### Если секретов нет:

```
❌ APP_STORE_CONNECT_API_KEY is not set
❌ APP_STORE_CONNECT_ISSUER_ID is not set
❌ APP_STORE_CONNECT_API_KEY_ID is not set

📋 SUMMARY:
===========
❌ Some required secrets are missing
❌ Please add missing secrets to GitHub
```

**Статус:** ❌ Красный крестик (Failure)

---

## 🎯 ЧТО ДЕЛАТЬ ДАЛЬШЕ

### Если все секреты есть (✅ Success):

1. ✅ **Можно использовать** "Build and Upload to App Store" workflow
2. ✅ **Запустить** автоматическую сборку и загрузку
3. ✅ **Дождаться** завершения (20-40 минут)

### Если секретов нет (❌ Failure):

1. ✅ **Создать API ключ** в App Store Connect
2. ✅ **Добавить секреты** в GitHub
3. ✅ **Повторить проверку**

---

## 🔗 ПРЯМЫЕ ССЫЛКИ

- **GitHub Actions:** https://github.com/sergey234/ALADDIN_FAMILY/actions
- **Secrets:** https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
- **App Store Connect:** https://appstoreconnect.apple.com

---

## ✅ ИТОГО

**Шаги для запуска:**

1. ✅ Убедиться, что файл в GitHub (commit + push)
2. ✅ Открыть: https://github.com/sergey234/ALADDIN_FAMILY/actions
3. ✅ Найти "Check Secrets" workflow
4. ✅ Нажать "Run workflow"
5. ✅ Выбрать ветку `main` или `master`
6. ✅ Нажать "Run workflow"
7. ✅ Проверить результат в логах

**После проверки:**
- Если секреты есть → использовать "Build and Upload to App Store"
- Если секретов нет → добавить секреты в GitHub

---

**Дата:** 29 ноября 2025  
**Инструкция:** Пошаговая инструкция запуска workflow "Check Secrets"

