# ⚠️ ВАЖНО: ИСПОЛЬЗОВАТЬ ТОЛЬКО appstore.yml ДЛЯ APP STORE!

**Дата:** 30 ноября 2025  
**Статус:** ✅ КРИТИЧЕСКИ ВАЖНО!

---

## 🎯 ГЛАВНОЕ ПРАВИЛО

### ✅ ИСПОЛЬЗУЕМ В РАБОТЕ ТОЛЬКО: `appstore.yml`

**Это правильный workflow для загрузки в App Store!**

---

## ✅ ПОДТВЕРЖДЕНИЕ: appstore.yml

**appstore.yml** - это **ПРАВИЛЬНЫЙ** workflow:

- ✅ **С подписью** - использует сертификат из GitHub Secrets
- ✅ **С профилями** - использует provisioning profiles
- ✅ **Создает IPA** - экспортирует правильный IPA файл
- ✅ **Отправляет в App Store** - автоматически загружает через API

**Это тот workflow, который нужно использовать для загрузки в App Store!**

---

## ❌ НЕ ИСПОЛЬЗОВАТЬ ДЛЯ APP STORE

### build-only.yml
- ❌ БЕЗ подписи
- ❌ БЕЗ профилей
- ❌ НЕ создает IPA
- ❌ НЕ загружает в App Store
- ⚠️ Только для CI тестирования

### deploy.yml
- ⚠️ Для staging/production деплоя
- ❌ НЕ для App Store

### Другие workflows
- ❌ НЕ для App Store

---

## 📋 КАК ЗАПУСТИТЬ appstore.yml

### Вариант 1: Через тег (автоматически) ✅

```bash
git tag -a "v1.0.0" -m "Release ALADDIN X AI"
git push origin --tags
```

**Workflow автоматически запустится!**

### Вариант 2: Вручную через GitHub UI ✅

1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions
2. Выберите: **"Build and Upload to App Store"**
3. Нажмите: **"Run workflow"**
4. Выберите ветку: `master`
5. Нажмите: **"Run workflow"**

---

## ✅ ЧТО ДЕЛАЕТ appstore.yml

1. **Setup Signing Certificate** ✅
   - Импортирует сертификат из GitHub Secrets
   - Создает keychain
   - Проверяет сертификат

2. **Setup Provisioning Profiles** ✅
   - Устанавливает профили для app и extension
   - Извлекает UUID

3. **Build Archive (with signing)** ✅
   - Собирает архив **С ПОДПИСЬЮ**
   - Использует правильные профили

4. **Export IPA** ✅
   - Создает IPA файл
   - С правильной подписью

5. **Upload to App Store Connect** ✅
   - **ЗАГРУЖАЕТ в App Store Connect**
   - Автоматически через API

---

## 🎯 ЗАПОМНИТЬ

### ✅ ИСПОЛЬЗУЕМ ТОЛЬКО: `appstore.yml`

**Для загрузки в App Store:**
- ✅ Только `appstore.yml`
- ✅ Никаких других workflows
- ✅ Это правило!

---

## 📊 СРАВНЕНИЕ

| Workflow | Для App Store? | Подпись | IPA | Загрузка |
|----------|----------------|---------|-----|----------|
| **appstore.yml** | ✅ ДА | ✅ ДА | ✅ ДА | ✅ ДА |
| build-only.yml | ❌ НЕТ | ❌ НЕТ | ❌ НЕТ | ❌ НЕТ |
| deploy.yml | ❌ НЕТ | ⚠️ Иногда | ⚠️ Иногда | ❌ НЕТ |

---

## ⚠️ ВАЖНО

**Если нужно загрузить в App Store:**
- ✅ Используйте **ТОЛЬКО** `appstore.yml`
- ❌ НЕ используйте `build-only.yml`
- ❌ НЕ используйте `deploy.yml`
- ❌ НЕ используйте другие workflows

**Это правило! Запомнить!**

---

## 🔗 ССЫЛКИ

- **GitHub Actions:** https://github.com/sergey234/ALADDIN_FAMILY/actions
- **Workflow файл:** `.github/workflows/appstore.yml`
- **App Store Connect:** https://appstoreconnect.apple.com

---

**Дата:** 30 ноября 2025  
**Статус:** ✅ ЗАПОМНЕНО - используем только appstore.yml!

