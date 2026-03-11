# 📋 BUILD 105: ОБЪЯСНЕНИЕ WARNINGS В GITHUB ACTIONS

**Дата:** 2026-03-11  
**Build:** 105  
**Статус:** ✅ **Сборка успешна!** Warnings не критичны

---

## 🎯 ЧТО ЭТО ЗНАЧИТ

### ✅ **Главное:**
- **Сборка прошла успешно!** ✅
- Это **предупреждения** (warnings), а не ошибки
- Проект работает нормально
- Можно игнорировать до июня 2026 года

---

## 📋 ДЕТАЛЬНОЕ ОБЪЯСНЕНИЕ

### 1. **Предупреждение о Node.js 20**

**Текст:**
```
Node.js 20 actions are deprecated. The following actions are running on Node.js 20 and may not work as expected: actions/cache@v4, actions/checkout@v4, actions/upload-artifact@v4, apple-actions/upload-testflight-build@v1, maxim-lobanov/setup-xcode@v1. Actions will be forced to run with Node.js 24 by default starting June 2nd, 2026.
```

**Что это значит:**
- GitHub Actions использует Node.js 20 для некоторых действий
- Node.js 20 устаревает и будет заменен на Node.js 24
- **С 2 июня 2026 года** все действия будут автоматически использовать Node.js 24
- Сейчас это **не влияет** на работу проекта

**Что нужно сделать:**
- **Сейчас:** Ничего не нужно делать, все работает
- **До июня 2026:** Обновить версии действий в `.github/workflows/*.yml` файлах
- **Или:** Добавить переменную окружения `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` для раннего перехода на Node.js 24

**Затронутые действия:**
- `actions/cache@v4`
- `actions/checkout@v4`
- `actions/upload-artifact@v4`
- `apple-actions/upload-testflight-build@v1`
- `maxim-lobanov/setup-xcode@v1`

---

### 2. **Предупреждение о `set-output`**

**Текст:**
```
The `set-output` command is deprecated and will be disabled soon. Please upgrade to using Environment Files.
```

**Что это значит:**
- Команда `set-output` устаревает в GitHub Actions
- Вместо нее нужно использовать **Environment Files** (`$GITHUB_ENV`)
- **Сейчас это не влияет** на работу проекта

**Что нужно сделать:**
- **Сейчас:** Ничего не нужно делать, все работает
- **В будущем:** Заменить все `::set-output` на `echo "VAR=value" >> $GITHUB_ENV`

**Пример замены:**

**БЫЛО (устаревший способ):**
```yaml
- name: Set output
  run: echo "::set-output name=value::123"
```

**СТАЛО (новый способ):**
```yaml
- name: Set output
  run: echo "VALUE=123" >> $GITHUB_ENV
```

---

## 🔍 ПРОВЕРКА ТЕКУЩЕГО КОДА

### Проверка использования `set-output`:

В файле `.github/workflows/appstore.yml` используется **правильный способ** (`$GITHUB_ENV`):

```yaml
echo "APP_PROFILE_UUID=$APP_PROFILE_UUID" >> $GITHUB_ENV
echo "EXT_PROFILE_UUID=$EXT_PROFILE_UUID" >> $GITHUB_ENV
```

✅ **Это правильно!** Предупреждение может быть из других действий или старых версий.

---

## 📋 РЕКОМЕНДАЦИИ

### ✅ **Сейчас (не критично):**
1. **Игнорировать предупреждения** - все работает нормально
2. **Сборка успешна** - проект компилируется и загружается в App Store Connect
3. **Ничего не нужно менять** до июня 2026 года

### 🔄 **В будущем (до июня 2026):**
1. **Обновить версии действий** в `.github/workflows/*.yml`:
   - Проверить наличие новых версий `actions/cache`, `actions/checkout`, `actions/upload-artifact`
   - Обновить `apple-actions/upload-testflight-build` до последней версии
   - Обновить `maxim-lobanov/setup-xcode` до последней версии

2. **Или добавить переменную окружения** для раннего перехода:
   ```yaml
   env:
     FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
   ```

3. **Проверить использование `set-output`**:
   - Найти все использования `::set-output` в workflow файлах
   - Заменить на `$GITHUB_ENV`

---

## 🎯 ИТОГОВЫЙ ВЫВОД

### ✅ **Статус:**
- **Сборка успешна!** ✅
- **Warnings не критичны** - это предупреждения о будущих изменениях
- **Проект работает нормально**
- **Можно игнорировать** до июня 2026 года

### 📋 **Что делать:**
- **Сейчас:** Ничего не нужно делать
- **До июня 2026:** Обновить версии действий в workflow файлах (опционально)

---

**Статус:** ✅ **НЕ КРИТИЧНО** - можно игнорировать  
**Рекомендация:** Обновить версии действий до июня 2026 года (опционально)
