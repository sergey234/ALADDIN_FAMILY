# ⚡ БЫСТРЫЙ СТАРТ: ВАРИАНТ B (АВТОМАТИЧЕСКАЯ ПОДПИСЬ)

## 🎯 ЦЕЛЬ

Добавить 3 секрета в GitHub для автоматической подписи билдов.

---

## 📋 БЫСТРАЯ ИНСТРУКЦИЯ (5 МИНУТ)

### 1️⃣ Создать API ключ (2 минуты)

1. Откройте: https://appstoreconnect.apple.com
2. Войдите в аккаунт
3. Нажмите на ваше имя (правый верхний угол) → **"Users and Access"** / **"Пользователи и доступ"**
4. Перейдите на вкладку **"Keys"** / **"Ключи"**
5. Нажмите **"+"** → **"Generate API Key"** / **"Создать API ключ"**
3. Имя: `ALADDIN iOS CI/CD`
4. Access: **"App Manager"**
5. Нажмите **"Generate"**
6. **Скачайте .p8 файл** (кнопка "Download API Key")
7. **Запишите:**
   - **Key ID** (виден на странице)
   - **Issuer ID** (UUID вверху страницы)

### 2️⃣ Подготовить секреты (1 минута)

**Вариант A: Автоматически (РЕКОМЕНДУЕТСЯ)**

Запустите скрипт:
```bash
~/Desktop/ALADDIN_Profiles/prepare_api_secrets.sh
```

Скрипт:
- Найдет .p8 файл
- Подготовит содержимое для секретов
- Скопирует все в буфер обмена
- Запросит Issuer ID и Key ID

**Вариант B: Вручную**

1. Откройте .p8 файл в текстовом редакторе
2. Скопируйте ВСЁ содержимое (включая `-----BEGIN PRIVATE KEY-----` и `-----END PRIVATE KEY-----`)
3. Запишите Issuer ID и Key ID

### 3️⃣ Добавить в GitHub (2 минуты)

1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
2. Добавьте 3 секрета:

   **Секрет 1: APP_STORE_CONNECT_API_KEY**
   - Name: `APP_STORE_CONNECT_API_KEY`
   - Secret: содержимое .p8 файла (из буфера обмена)

   **Секрет 2: APP_STORE_CONNECT_ISSUER_ID**
   - Name: `APP_STORE_CONNECT_ISSUER_ID`
   - Secret: Issuer ID (UUID)

   **Секрет 3: APP_STORE_CONNECT_API_KEY_ID**
   - Name: `APP_STORE_CONNECT_API_KEY_ID`
   - Secret: Key ID

### 4️⃣ Запустить workflow

1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions
2. Выберите: **"Build and Upload to App Store"**
3. Нажмите: **"Run workflow"**

---

## ✅ ПРОВЕРКА

Убедитесь, что добавлены все секреты:

- ✅ `APP_STORE_CONNECT_API_KEY`
- ✅ `APP_STORE_CONNECT_ISSUER_ID`
- ✅ `APP_STORE_CONNECT_API_KEY_ID`
- ✅ `APPLE_TEAM_ID` (6CJVBBUGSN)
- ✅ `PROVISIONING_PROFILE_APP`
- ✅ `PROVISIONING_PROFILE_EXTENSION`

---

## 📖 ПОДРОБНАЯ ИНСТРУКЦИЯ

Если что-то непонятно, смотрите:
- `docs/ПОШАГОВАЯ_ИНСТРУКЦИЯ_ВАРИАНТ_B.md` - детальная инструкция
- `docs/КАК_ДОБАВИТЬ_СЕКРЕТЫ_В_GITHUB.md` - общая инструкция

---

## 🚀 ГОТОВО!

После добавления секретов workflow будет использовать автоматическую подпись!

