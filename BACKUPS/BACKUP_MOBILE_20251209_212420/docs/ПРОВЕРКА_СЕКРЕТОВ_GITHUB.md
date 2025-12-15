# ✅ ПРОВЕРКА СЕКРЕТОВ В GITHUB

**Дата:** 29 ноября 2025  
**Цель:** Проверить, что все секреты добавлены

---

## 🔍 КАК ПРОВЕРИТЬ

### Способ 1: Через браузер (РЕКОМЕНДУЕТСЯ)

1. **Открыть GitHub Secrets:**
   https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

2. **Проверить список секретов:**
   Должны быть видны:
   - ✅ `PROVISIONING_PROFILE_APP`
   - ✅ `PROVISIONING_PROFILE_EXTENSION`
   - ✅ `APPLE_TEAM_ID`

3. **Проверить, что они добавлены:**
   - Нажать на каждый секрет
   - Должно показать: "Last updated: [дата]"
   - Значение скрыто (это нормально)

---

## ✅ ЧТО ДОЛЖНО БЫТЬ

### Обязательные секреты:

1. **PROVISIONING_PROFILE_APP**
   - ✅ Должен быть в списке
   - ✅ Последнее обновление: сегодня

2. **PROVISIONING_PROFILE_EXTENSION**
   - ✅ Должен быть в списке
   - ✅ Последнее обновление: сегодня

3. **APPLE_TEAM_ID**
   - ✅ Должен быть в списке
   - ✅ Значение: `6CJVBBUGSN`

---

## 🔧 ЕСЛИ ЧТО-ТО ОТСУТСТВУЕТ

### Если нет PROVISIONING_PROFILE_APP:

1. **Скопировать через терминал:**
   ```bash
   cat ~/Desktop/ALADDIN_Profiles/app_profile_base64.txt | pbcopy
   ```

2. **Добавить в GitHub:**
   - Нажать "New repository secret"
   - Name: `PROVISIONING_PROFILE_APP`
   - Secret: вставить (Cmd+V)
   - Нажать "Add secret"

---

### Если нет PROVISIONING_PROFILE_EXTENSION:

1. **Скопировать через терминал:**
   ```bash
   cat ~/Desktop/ALADDIN_Profiles/extension_profile_base64.txt | pbcopy
   ```

2. **Добавить в GitHub:**
   - Нажать "New repository secret"
   - Name: `PROVISIONING_PROFILE_EXTENSION`
   - Secret: вставить (Cmd+V)
   - Нажать "Add secret"

---

### Если нет APPLE_TEAM_ID:

1. **Добавить в GitHub:**
   - Нажать "New repository secret"
   - Name: `APPLE_TEAM_ID`
   - Secret: `6CJVBBUGSN`
   - Нажать "Add secret"

---

## ✅ ПРОВЕРКА ГОТОВНОСТИ

После проверки должно быть:

- ✅ `PROVISIONING_PROFILE_APP` - добавлен
- ✅ `PROVISIONING_PROFILE_EXTENSION` - добавлен
- ✅ `APPLE_TEAM_ID` = `6CJVBBUGSN` - добавлен

**Если все три секрета есть → готово к следующему шагу!** 🎯

---

**Дата:** 29 ноября 2025  
**Инструкция:** Проверка секретов в GitHub
