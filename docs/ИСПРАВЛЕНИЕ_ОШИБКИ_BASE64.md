# 🔧 ИСПРАВЛЕНИЕ ОШИБКИ BASE64

**Дата:** 29 ноября 2025  
**Проблема:** `base64: stdin: (null): error decoding base64 input stream`

---

## ❌ ПРОБЛЕМА

**Ошибка в логах:**
```
✅ App provisioning profile installed
base64: stdin: (null): error decoding base64 input stream
Error: Process completed with exit code 1
```

**Причина:**
- Секрет `PROVISIONING_PROFILE_EXTENSION` содержит невалидный base64
- Возможно, есть переносы строк или пробелы

---

## ✅ РЕШЕНИЕ

### Шаг 1: Файл исправлен локально

✅ Файл `~/Desktop/ALADDIN_Profiles/extension_profile_base64.txt` пересоздан без переносов строк

### Шаг 2: Обновить секрет в GitHub

1. **Откройте настройки секретов:**
   https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

2. **Найдите секрет:**
   - `PROVISIONING_PROFILE_EXTENSION`

3. **Нажмите "Update"** (или создайте новый, если его нет)

4. **Скопируйте содержимое исправленного файла:**
   ```bash
   cat ~/Desktop/ALADDIN_Profiles/extension_profile_base64.txt | pbcopy
   ```
   (Уже скопировано в буфер обмена!)

5. **Вставьте в поле "Secret":**
   - Cmd+V (Mac) или Ctrl+V (Windows)
   - **ВАЖНО:** Вставьте ВСЁ содержимое, без пропусков

6. **Нажмите "Update secret"**

---

## 🚀 ПОСЛЕ ОБНОВЛЕНИЯ СЕКРЕТА

### Запустить сборку снова:

1. **Создать новый тег:**
   ```bash
   cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
   git tag -a v1.0.0-build-$(date +%Y%m%d-%H%M%S) -m "Build with fixed extension profile"
   git push origin --tags
   ```

2. **Или запустить через браузер:**
   - Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
   - Нажмите "Run workflow"

---

## ✅ ПРОВЕРКА

После обновления секрета и запуска сборки, в логах должно быть:

```
✅ App provisioning profile installed
✅ Extension provisioning profile installed
📋 Installed provisioning profiles:
-rw-r--r--  1 runner  staff  XXK app.mobileprovision
-rw-r--r--  1 runner  staff  XXK extension.mobileprovision
```

**Если всё так** → ✅ Проблема решена!

---

## 📋 ЧТО БЫЛО ИСПРАВЛЕНО

1. ✅ Убраны переносы строк из base64
2. ✅ Убраны пробелы
3. ✅ Файл пересоздан в одну строку
4. ✅ Base64 валидирован

---

**Дата:** 29 ноября 2025  
**Статус:** ✅ Файл исправлен, нужно обновить секрет в GitHub

