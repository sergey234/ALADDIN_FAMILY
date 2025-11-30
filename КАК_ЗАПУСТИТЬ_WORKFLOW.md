# 🚀 КАК ЗАПУСТИТЬ WORKFLOW APPSTORE.YML

**Дата:** 30 ноября 2025  
**Workflow:** Build and Upload to App Store (appstore.yml)

---

## ✅ СПОСОБ 1: Запуск через GitHub UI (САМЫЙ ПРОСТОЙ)

### Шаг 1: Откройте Actions
Перейдите по ссылке:
**https://github.com/sergey234/ALADDIN_FAMILY/actions**

### Шаг 2: Найдите workflow
В левом меню найдите и нажмите:
**"Build and Upload to App Store"**

### Шаг 3: Запустите вручную
1. Нажмите кнопку **"Run workflow"** (справа вверху)
2. Выберите ветку: **`master`**
3. Нажмите зеленую кнопку **"Run workflow"**

### Шаг 4: Дождитесь завершения
- ⏳ Сборка займет 15-30 минут
- ✅ Следите за прогрессом в реальном времени

---

## ✅ СПОСОБ 2: Запуск через тег (АВТОМАТИЧЕСКИЙ)

### Создать тег:
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
git tag -a "v1.0.13" -m "Запуск appstore.yml"
git push origin v1.0.13
```

Workflow запустится автоматически при отправке тега.

---

## ✅ СПОСОБ 3: Запуск через API (ДЛЯ АВТОМАТИЗАЦИИ)

### Используйте скрипт:
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
export GITHUB_TOKEN=ваш_токен
./запустить_workflow.sh
```

### Или через curl напрямую:
```bash
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml/dispatches \
  -d '{"ref":"master"}'
```

---

## 🔗 ПРЯМАЯ ССЫЛКА ДЛЯ ЗАПУСКА

**Откройте эту ссылку и нажмите "Run workflow":**
https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml

---

## ⚠️ ЕСЛИ WORKFLOW НЕ ЗАПУСКАЕТСЯ

### Проверьте:
1. ✅ Workflow файл существует: `.github/workflows/appstore.yml`
2. ✅ Workflow включен в репозитории (Settings → Actions → General)
3. ✅ У вас есть права на запуск workflow
4. ✅ Ветка `master` существует и актуальна

### Решение:
- Используйте **СПОСОБ 1** (через GitHub UI) - это самый надежный способ
- Или создайте новый тег: `git tag -a "v1.0.14" -m "Test" && git push origin v1.0.14`

---

**Рекомендуется использовать СПОСОБ 1 (через GitHub UI) - это самый простой и надежный способ!**

