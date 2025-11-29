# 🚀 ВАРИАНТ B: АВТОМАТИЧЕСКАЯ ПОДПИСЬ - ПОШАГОВАЯ ИНСТРУКЦИЯ

## ✅ ЧТО НУЖНО СДЕЛАТЬ

Добавить 3 секрета в GitHub для автоматической подписи:
1. `APP_STORE_CONNECT_API_KEY` (содержимое .p8 файла)
2. `APP_STORE_CONNECT_ISSUER_ID` (UUID)
3. `APP_STORE_CONNECT_API_KEY_ID` (ID ключа)

---

## 📋 ШАГ 1: СОЗДАТЬ API КЛЮЧ В APP STORE CONNECT

### 1.1. Откройте App Store Connect

1. Откройте: https://appstoreconnect.apple.com
2. Войдите в аккаунт
3. Нажмите на ваше имя (правый верхний угол)
4. Выберите **"Users and Access"** / **"Пользователи и доступ"**
5. Перейдите на вкладку **"Keys"** / **"Ключи"**

### 1.2. Создайте новый ключ

1. Нажмите кнопку **"+"** (Generate API Key / Создать API ключ)
2. Введите **Name** / **Имя**: `ALADDIN iOS CI/CD` (или любое другое имя)
3. Выберите **Access** / **Доступ**: **"App Manager"** / **"Менеджер приложений"** (достаточно для загрузки билдов)
4. Нажмите **"Generate"** / **"Создать"**

### 1.3. Скачайте и сохраните данные

**ВАЖНО: Скачайте .p8 файл СРАЗУ - его нельзя будет скачать позже!**

1. Нажмите **"Download API Key"** - скачается файл `AuthKey_XXXXXXXX.p8`
2. **Сохраните файл** в безопасное место (например, `~/Desktop/ALADDIN_Profiles/`)
3. **Запишите:**
   - **Key ID**: виден на странице (например, `ABC123DEF4`)
   - **Issuer ID**: виден вверху страницы (UUID, например, `12345678-1234-1234-1234-123456789012`)

---

## 📋 ШАГ 2: ПОДГОТОВИТЬ СЕКРЕТЫ

### 2.1. Подготовить API Key (.p8 файл)

Откройте Terminal и выполните:

```bash
cd ~/Desktop/ALADDIN_Profiles
cat AuthKey_XXXXXXXX.p8
```

**Скопируйте ВСЁ содержимое** (включая строки `-----BEGIN PRIVATE KEY-----` и `-----END PRIVATE KEY-----`)

### 2.2. Проверить Issuer ID и Key ID

- **Issuer ID**: UUID вверху страницы Keys (например: `12345678-1234-1234-1234-123456789012`)
- **Key ID**: ID ключа на странице ключа (например: `ABC123DEF4`)

---

## 📋 ШАГ 3: ДОБАВИТЬ СЕКРЕТЫ В GITHUB

### 3.1. Откройте страницу секретов

Перейдите: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

### 3.2. Добавить APP_STORE_CONNECT_API_KEY

1. Нажмите **"New repository secret"**
2. **Name**: `APP_STORE_CONNECT_API_KEY`
3. **Secret**: вставьте ВСЁ содержимое .p8 файла:
   ```
   -----BEGIN PRIVATE KEY-----
   MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg...
   ... (весь текст файла) ...
   -----END PRIVATE KEY-----
   ```
4. Нажмите **"Add secret"**

### 3.3. Добавить APP_STORE_CONNECT_ISSUER_ID

1. Нажмите **"New repository secret"**
2. **Name**: `APP_STORE_CONNECT_ISSUER_ID`
3. **Secret**: вставьте Issuer ID (UUID, например: `12345678-1234-1234-1234-123456789012`)
4. Нажмите **"Add secret"**

### 3.4. Добавить APP_STORE_CONNECT_API_KEY_ID

1. Нажмите **"New repository secret"**
2. **Name**: `APP_STORE_CONNECT_API_KEY_ID`
3. **Secret**: вставьте Key ID (например: `ABC123DEF4`)
4. Нажмите **"Add secret"**

---

## ✅ ШАГ 4: ПРОВЕРИТЬ

### 4.1. Проверить секреты

Убедитесь, что добавлены все 3 секрета:
- ✅ `APP_STORE_CONNECT_API_KEY`
- ✅ `APP_STORE_CONNECT_ISSUER_ID`
- ✅ `APP_STORE_CONNECT_API_KEY_ID`

### 4.2. Проверить обязательные секреты

Также должны быть:
- ✅ `APPLE_TEAM_ID` (6CJVBBUGSN)
- ✅ `PROVISIONING_PROFILE_APP` (base64)
- ✅ `PROVISIONING_PROFILE_EXTENSION` (base64)

---

## 🚀 ШАГ 5: ЗАПУСТИТЬ WORKFLOW

1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions
2. Выберите: **"Build and Upload to App Store"**
3. Нажмите: **"Run workflow"**
4. Дождитесь завершения

---

## ⚠️ ВАЖНО

- **Не делитесь** .p8 файлом и секретами
- **Не коммитьте** .p8 файл в Git
- **Сохраните** .p8 файл в безопасном месте (может понадобиться позже)

---

## 🔍 ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ

1. **Проверьте формат** .p8 файла - должен начинаться с `-----BEGIN PRIVATE KEY-----`
2. **Проверьте Issuer ID** - должен быть UUID формата
3. **Проверьте Key ID** - должен быть строкой без пробелов
4. **Проверьте права** ключа - должно быть "App Manager" или выше

---

## 📖 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ

- [Apple: Creating API Keys for App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api)
- [GitHub Actions: Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

