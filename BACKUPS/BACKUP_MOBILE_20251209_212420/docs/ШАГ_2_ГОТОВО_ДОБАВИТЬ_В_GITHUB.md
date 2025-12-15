# ✅ ШАГ 2: ФАЙЛЫ ГОТОВЫ - ДОБАВИТЬ В GITHUB SECRETS

**Дата:** 29 ноября 2025  
**Статус:** Файлы готовы, нужно добавить в GitHub Secrets

---

## ✅ ЧТО УЖЕ ГОТОВО

- ✅ Файлы base64 созданы и находятся на Desktop
- ✅ Файлы открыты в TextEdit для копирования
- ✅ Готовы к добавлению в GitHub Secrets

---

## 🎯 ЧТО ДЕЛАТЬ СЕЙЧАС

### Шаг 2.1: Скопировать содержимое первого файла

1. **В открытом окне TextEdit с `app_profile_base64.txt`:**
   - Нажать Cmd+A (выделить всё)
   - Нажать Cmd+C (скопировать)
   - Содержимое скопировано в буфер обмена

---

### Шаг 2.2: Добавить первый секрет в GitHub

1. **Открыть GitHub в браузере:**
   - Перейти: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
   - Войти в аккаунт (если не вошли)

2. **Добавить секрет:**
   - Нажать зелёную кнопку "New repository secret" (справа вверху)
   - **Name:** ввести `PROVISIONING_PROFILE_APP`
   - **Secret:** вставить содержимое (Cmd+V)
   - Нажать "Add secret"

3. **Проверить:**
   - Должен появиться секрет `PROVISIONING_PROFILE_APP` в списке

---

### Шаг 2.3: Скопировать содержимое второго файла

1. **В открытом окне TextEdit с `extension_profile_base64.txt`:**
   - Нажать Cmd+A (выделить всё)
   - Нажать Cmd+C (скопировать)
   - Содержимое скопировано в буфер обмена

---

### Шаг 2.4: Добавить второй секрет в GitHub

1. **В том же окне GitHub:**
   - Нажать "New repository secret" снова
   - **Name:** ввести `PROVISIONING_PROFILE_EXTENSION`
   - **Secret:** вставить содержимое (Cmd+V)
   - Нажать "Add secret"

2. **Проверить:**
   - Должен появиться секрет `PROVISIONING_PROFILE_EXTENSION` в списке

---

### Шаг 2.5: Проверить секрет APPLE_TEAM_ID

1. **Проверить список секретов:**
   - Должен быть секрет `APPLE_TEAM_ID` со значением `6CJVBBUGSN`

2. **Если нет:**
   - Нажать "New repository secret"
   - **Name:** `APPLE_TEAM_ID`
   - **Secret:** `6CJVBBUGSN`
   - Нажать "Add secret"

---

## ✅ ПРОВЕРКА РЕЗУЛЬТАТА

### Что должно быть в GitHub Secrets:

1. ✅ `PROVISIONING_PROFILE_APP` - добавлен
2. ✅ `PROVISIONING_PROFILE_EXTENSION` - добавлен
3. ✅ `APPLE_TEAM_ID` - должен быть `6CJVBBUGSN`

---

## 🎯 СЛЕДУЮЩИЙ ШАГ

После добавления всех секретов:
- **ЭТАП 3:** Обновить workflow для использования profiles
- Я подготовлю обновлённый workflow файл

**Сообщите, когда добавите секреты, и я обновлю workflow!** 🚀

---

**Дата:** 29 ноября 2025  
**Инструкция:** Добавление profiles в GitHub Secrets

