# 📋 КАК ПОЛУЧИТЬ ЛОГИ WORKFLOW ДЛЯ ДИАГНОСТИКИ

## ✅ Да, вы присылаете логи!

То, что вы присылаете - это **логи из GitHub Actions workflow**, но это **не полные логи** - это только вывод определенных шагов (в основном "Build Archive").

## 🔍 ГДЕ НАЙТИ ПОЛНЫЕ ЛОГИ

### Способ 1: Через GitHub Web Interface (РЕКОМЕНДУЕТСЯ)

1. **Откройте страницу Actions в вашем репозитории:**
   ```
   https://github.com/sergey234/ALADDIN_FAMILY/actions
   ```

2. **Найдите последний запуск workflow:**
   - Найдите workflow "Check Secrets" (или другой, который вы запускаете)
   - Нажмите на него

3. **Откройте конкретный запуск:**
   - Нажмите на последний запуск (например, "#60" или "#61")
   - Вы увидите список всех шагов (jobs)

4. **Откройте нужный шаг:**
   - Найдите шаг "Extract App Profile UUID"
   - Нажмите на него, чтобы развернуть
   - Скопируйте весь вывод

5. **Повторите для других шагов:**
   - "Extract Extension Profile UUID"
   - "Force Extract UUID and Rename Profiles"
   - "Verify Profiles"
   - "Build Archive"

### Способ 2: Через GitHub CLI (если установлен)

```bash
# Установить GitHub CLI (если не установлен)
brew install gh

# Авторизоваться
gh auth login

# Получить логи последнего запуска
gh run view --log

# Получить логи конкретного запуска
gh run view <RUN_ID> --log

# Сохранить логи в файл
gh run view <RUN_ID> --log > workflow_logs.txt
```

### Способ 3: Через API GitHub

```bash
# Получить список запусков
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/sergey234/ALADDIN_FAMILY/actions/runs

# Получить логи конкретного запуска
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/sergey234/ALADDIN_FAMILY/actions/runs/<RUN_ID>/logs
```

---

## 📋 КАКИЕ ЛОГИ МНЕ НУЖНЫ

Для диагностики проблемы с UUID мне нужны логи следующих шагов:

### 1. **Extract App Profile UUID**
   - Нужно увидеть:
     - `✅ App profile XML decoded successfully` или ошибку
     - `✅ UUID extracted via plutil/grep/strings: ...` или сообщение об ошибке
     - `✅ App provisioning profile installed with UUID: ...` или сообщение об ошибке

### 2. **Extract Extension Profile UUID**
   - Аналогично для extension профиля

### 3. **Force Extract UUID and Rename Profiles**
   - Нужно увидеть:
     - `✅ App profile renamed to: UUID.mobileprovision` или сообщение об ошибке
     - `✅ Extension profile renamed to: UUID.mobileprovision` или сообщение об ошибке
     - Список файлов до и после переименования

### 4. **Verify Profiles**
   - Нужно увидеть:
     - Список всех файлов в директории профилей
     - `✅ App profile found: UUID.mobileprovision` или `❌ App profile NOT found`
     - `✅ Extension profile found: UUID.mobileprovision` или `❌ Extension profile NOT found`

### 5. **Build Archive**
   - Нужно увидеть:
     - `✅ Using UUID for ALADDIN_PROVISIONING_PROFILE: UUID` или `⚠️  Using full path`
     - Значения переменных: `APP_PROFILE_UUID`, `EXT_PROFILE_UUID`

---

## 🎯 КАК ПРИСЛАТЬ ЛОГИ

### Вариант 1: Скопировать весь вывод шага
1. Откройте шаг в GitHub Actions
2. Нажмите на кнопку "Copy" (если есть) или выделите весь текст
3. Вставьте в сообщение

### Вариант 2: Скопировать только важные части
Если лог очень длинный, скопируйте только:
- Начало шага (первые 10-20 строк)
- Сообщения об ошибках (строки с `❌`, `⚠️`)
- Сообщения об успехе (строки с `✅`)
- Конец шага (последние 10-20 строк)

### Вариант 3: Сделать скриншот
Если текст слишком длинный, сделайте скриншот важных частей

---

## 💡 ПРИМЕР: ЧТО МНЕ НУЖНО УВИДЕТЬ

Вот пример того, что я хочу увидеть в логах шага "Extract App Profile UUID":

```
🔍 Extracting UUID from app profile...
✅ App profile XML decoded successfully
   XML length: 12345 characters
✅ UUID extracted via plutil: 12345678-1234-1234-1234-123456789ABC
✅ App provisioning profile installed with UUID: 12345678-1234-1234-1234-123456789ABC
```

Или, если есть ошибка:

```
🔍 Extracting UUID from app profile...
❌ Failed to decode app profile XML (exit code: 1)
   Error output: security: SecKeychainItemCopyAccess: User interaction is not allowed.
```

Или:

```
🔍 Extracting UUID from app profile...
✅ App profile XML decoded successfully
   XML length: 12345 characters
⚠️  plutil failed to extract UUID, trying other methods...
🔍 Trying grep methods to extract UUID...
⚠️  grep methods failed to extract UUID
   Searching for UUID pattern in XML...
   No UUID found in XML
❌ CRITICAL: Could not extract UUID from app profile!
```

---

## 🚀 БЫСТРЫЙ СПОСОБ

1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions
2. Найдите последний запуск workflow
3. Откройте шаг "Extract App Profile UUID"
4. Скопируйте весь вывод и пришлите мне

Это поможет понять, почему UUID не извлекаются!

