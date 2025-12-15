# 🔑 КАК ДОБАВИТЬ СЕКРЕТЫ В GITHUB

**Результат проверки:** ❌ Секреты не настроены

**Решение:** Добавить секреты в GitHub для автоматической загрузки в App Store Connect

---

## 📋 ЧТО НУЖНО ДОБАВИТЬ

### Обязательные секреты:

1. **APP_STORE_CONNECT_API_KEY** — содержимое .p8 файла
2. **APP_STORE_CONNECT_ISSUER_ID** — Issuer ID из App Store Connect
3. **APP_STORE_CONNECT_API_KEY_ID** — Key ID из App Store Connect

### Опциональные секреты:

4. **APPLE_TEAM_ID** — Team ID: `6CJVBBUGSN` (рекомендуется)

---

## 🎯 ШАГ 1: СОЗДАТЬ API КЛЮЧ В APP STORE CONNECT

### 1.1. Открыть App Store Connect

1. **Откройте браузер**
2. **Перейдите:** https://appstoreconnect.apple.com
3. **Войдите** с аккаунтом `sergey21-02-84@list.ru`

### 1.2. Создать API ключ

1. **Перейдите:** Users and Access → Keys
2. **Нажмите:** "+" (создать новый ключ)
3. **Заполните форму:**
   - **Name:** GitHub Actions (или любое другое название)
   - **Access:** App Manager (или Admin)
4. **Нажмите:** "Generate"

### 1.3. Скачать и сохранить данные

1. **Скачайте .p8 файл:**
   - ⚠️ **ВАЖНО:** Скачать можно только один раз!
   - Сохраните файл в безопасном месте

2. **Сохраните Issuer ID:**
   - Находится на той же странице
   - Формат: UUID (например: `12345678-1234-1234-1234-123456789012`)

3. **Сохраните Key ID:**
   - Находится рядом с ключом
   - Формат: строка (например: `ABC123DEF4`)

---

## 🎯 ШАГ 2: ДОБАВИТЬ СЕКРЕТЫ В GITHUB

### 2.1. Открыть страницу секретов

1. **Откройте браузер**
2. **Перейдите:** https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
3. **Войдите** в GitHub (если нужно)

### 2.2. Добавить APP_STORE_CONNECT_API_KEY

1. **Нажмите:** "New repository secret"
2. **Name:** `APP_STORE_CONNECT_API_KEY` (точно так, регистр важен!)
3. **Secret:**
   - Откройте скачанный .p8 файл в текстовом редакторе
   - Скопируйте **ВСЁ содержимое** файла (включая строки `-----BEGIN PRIVATE KEY-----` и `-----END PRIVATE KEY-----`)
   - Вставьте в поле "Secret"
4. **Нажмите:** "Add secret"

**Важно:**
- ✅ Должен начинаться с `-----BEGIN PRIVATE KEY-----`
- ✅ Должен заканчиваться `-----END PRIVATE KEY-----`
- ✅ Должен содержать все строки (не обрезан)

### 2.3. Добавить APP_STORE_CONNECT_ISSUER_ID

1. **Нажмите:** "New repository secret"
2. **Name:** `APP_STORE_CONNECT_ISSUER_ID` (точно так)
3. **Secret:** Вставьте Issuer ID (UUID)
4. **Нажмите:** "Add secret"

**Формат:** UUID (например: `12345678-1234-1234-1234-123456789012`)

### 2.4. Добавить APP_STORE_CONNECT_API_KEY_ID

1. **Нажмите:** "New repository secret"
2. **Name:** `APP_STORE_CONNECT_API_KEY_ID` (точно так)
3. **Secret:** Вставьте Key ID
4. **Нажмите:** "Add secret"

**Формат:** Строка (например: `ABC123DEF4`)

### 2.5. Добавить APPLE_TEAM_ID (опционально, но рекомендуется)

1. **Нажмите:** "New repository secret"
2. **Name:** `APPLE_TEAM_ID` (точно так)
3. **Secret:** `6CJVBBUGSN`
4. **Нажмите:** "Add secret"

---

## ✅ ШАГ 3: ПРОВЕРИТЬ СЕКРЕТЫ

### 3.1. Запустить проверку снова

1. **Откройте:** https://github.com/sergey234/ALADDIN_FAMILY/actions
2. **Найдите:** "Check Secrets" workflow
3. **Нажмите:** "Run workflow"
4. **Выберите ветку:** `master` или `main`
5. **Нажмите:** "Run workflow"

### 3.2. Проверить результат

**Если всё правильно, должно быть:**

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

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

### Названия секретов

Названия должны быть **точно такими** (регистр важен!):

- ✅ `APP_STORE_CONNECT_API_KEY` (правильно)
- ❌ `app_store_connect_api_key` (неправильно — маленькие буквы)
- ❌ `APP_STORE_CONNECT_APIKEY` (неправильно — без подчёркивания)

### Формат APP_STORE_CONNECT_API_KEY

API ключ должен быть в формате .p8 файла:

```
-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg...
... (много строк) ...
-----END PRIVATE KEY-----
```

**Важно:**
- ✅ Должен начинаться с `-----BEGIN PRIVATE KEY-----`
- ✅ Должен заканчиваться `-----END PRIVATE KEY-----`
- ✅ Должен содержать все строки (не обрезан)

### Безопасность

- ⚠️ **НЕ делитесь** .p8 файлом
- ⚠️ **НЕ коммитьте** секреты в git
- ⚠️ **НЕ публикуйте** секреты в открытом доступе
- ✅ Храните .p8 файл в безопасном месте

---

## 🎯 ЧТО ДЕЛАТЬ ДАЛЬШЕ

### После добавления секретов:

1. ✅ **Запустить "Check Secrets" workflow** снова
2. ✅ **Проверить, что все секреты найдены**
3. ✅ **Использовать "Build and Upload to App Store" workflow**
4. ✅ **Дождаться автоматической загрузки** в App Store Connect

---

## 📝 ЧЕКЛИСТ

### Создание API ключа:

- [ ] Открыть App Store Connect
- [ ] Создать новый API ключ
- [ ] Скачать .p8 файл
- [ ] Сохранить Issuer ID
- [ ] Сохранить Key ID

### Добавление секретов:

- [ ] Добавить `APP_STORE_CONNECT_API_KEY`
- [ ] Добавить `APP_STORE_CONNECT_ISSUER_ID`
- [ ] Добавить `APP_STORE_CONNECT_API_KEY_ID`
- [ ] Добавить `APPLE_TEAM_ID` (опционально)

### Проверка:

- [ ] Запустить "Check Secrets" workflow
- [ ] Проверить, что все секреты найдены
- [ ] Убедиться, что статус Success

---

## ✅ ИТОГО

**Проблема:**
- ❌ Секреты не настроены в GitHub

**Решение:**
1. ✅ Создать API ключ в App Store Connect
2. ✅ Добавить секреты в GitHub
3. ✅ Проверить через "Check Secrets" workflow

**После настройки:**
- ✅ Можно использовать "Build and Upload to App Store" workflow
- ✅ Билд автоматически загрузится в App Store Connect

---

**Дата:** 29 ноября 2025  
**Инструкция:** Как добавить секреты в GitHub для App Store Connect

