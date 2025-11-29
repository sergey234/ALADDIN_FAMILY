# 🔑 НАСТРОЙКА КЛЮЧЕЙ ДЛЯ GITHUB ACTIONS

**Дата:** 29 ноября 2025  
**Цель:** Настроить секреты GitHub для автоматической сборки и загрузки в App Store

---

## 📋 НУЖНЫЕ СЕКРЕТЫ

### 1. APPLE_TEAM_ID (обязательно для сборки)

**Значение:** `6CJVBBUGSN`  
**Где взять:** Уже известно из проекта  
**Для чего:** Автоматическая подпись при сборке

### 2. APP_STORE_CONNECT_API_KEY (для загрузки в App Store)

**Формат:** Содержимое `.p8` файла  
**Где получить:** App Store Connect → Users and Access → Keys  
**Для чего:** Загрузка билда в App Store Connect

### 3. APP_STORE_CONNECT_ISSUER_ID (для загрузки в App Store)

**Формат:** UUID (например: `12345678-1234-1234-1234-123456789012`)  
**Где взять:** App Store Connect → Users and Access → Keys  
**Для чего:** Аутентификация в App Store Connect API

### 4. APP_STORE_CONNECT_API_KEY_ID (для загрузки в App Store)

**Формат:** Строка (например: `ABC123DEF4`)  
**Где взять:** App Store Connect → Users and Access → Keys  
**Для чего:** Идентификация API ключа

---

## 🎯 ПОШАГОВАЯ ИНСТРУКЦИЯ

### Шаг 1: Открыть страницу секретов GitHub

**Ссылка:**
```
https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
```

**Или:**
1. Откройте: https://github.com/sergey234/ALADDIN_FAMILY
2. Нажмите: Settings (в верхней панели)
3. В левом меню: Secrets and variables → Actions

---

### Шаг 2: Добавить APPLE_TEAM_ID

1. **Нажмите:** "New repository secret"
2. **Name:** `APPLE_TEAM_ID`
3. **Secret:** `6CJVBBUGSN`
4. **Нажмите:** "Add secret"

---

### Шаг 3: Создать API ключ в App Store Connect

1. **Откройте:** https://appstoreconnect.apple.com
2. **Перейдите:** Users and Access → Keys
3. **Нажмите:** "+" (создать новый ключ)
4. **Заполните:**
   - **Name:** `ALADDIN GitHub Actions` (или любое имя)
   - **Access:** App Manager (или Admin)
5. **Нажмите:** "Generate"
6. **Скопируйте:**
   - **Key ID** (например: `ABC123DEF4`) → это `APP_STORE_CONNECT_API_KEY_ID`
   - **Issuer ID** (UUID) → это `APP_STORE_CONNECT_ISSUER_ID`
7. **Скачайте:** `.p8` файл → откройте и скопируйте содержимое → это `APP_STORE_CONNECT_API_KEY`

**⚠️ ВАЖНО:** `.p8` файл можно скачать только один раз! Сохраните его в безопасном месте.

---

### Шаг 4: Добавить секреты в GitHub

#### 4.1. APP_STORE_CONNECT_API_KEY

1. **Нажмите:** "New repository secret"
2. **Name:** `APP_STORE_CONNECT_API_KEY`
3. **Secret:** Вставьте содержимое `.p8` файла (весь текст от `-----BEGIN PRIVATE KEY-----` до `-----END PRIVATE KEY-----`)
4. **Нажмите:** "Add secret"

#### 4.2. APP_STORE_CONNECT_ISSUER_ID

1. **Нажмите:** "New repository secret"
2. **Name:** `APP_STORE_CONNECT_ISSUER_ID`
3. **Secret:** Вставьте Issuer ID (UUID)
4. **Нажмите:** "Add secret"

#### 4.3. APP_STORE_CONNECT_API_KEY_ID

1. **Нажмите:** "New repository secret"
2. **Name:** `APP_STORE_CONNECT_API_KEY_ID`
3. **Secret:** Вставьте Key ID (строка)
4. **Нажмите:** "Add secret"

---

## ✅ ПРОВЕРКА СЕКРЕТОВ

### После добавления всех секретов:

1. **Откройте:** https://github.com/sergey234/ALADDIN_FAMILY/actions
2. **Найдите:** "Check Secrets" workflow
3. **Нажмите:** "Run workflow"
4. **Проверьте результат:**
   - ✅ Все секреты найдены
   - ✅ Формат правильный

---

## 📋 ЧЕКЛИСТ

### Обязательные секреты:

- [ ] `APPLE_TEAM_ID` = `6CJVBBUGSN` (для сборки)
- [ ] `APP_STORE_CONNECT_API_KEY` = содержимое `.p8` файла (для загрузки)
- [ ] `APP_STORE_CONNECT_ISSUER_ID` = UUID (для загрузки)
- [ ] `APP_STORE_CONNECT_API_KEY_ID` = Key ID (для загрузки)

### Опциональные (для полной автоматизации):

- [ ] Все секреты добавлены
- [ ] Проверка секретов прошла успешно

---

## 🎯 ИТОГО

**Для сборки (Build Only):**
- ✅ Нужен только `APPLE_TEAM_ID`

**Для загрузки в App Store:**
- ✅ Нужны все 4 секрета

**Начнём с `APPLE_TEAM_ID`, потом добавим остальные!** 🚀

---

**Дата:** 29 ноября 2025  
**Инструкция:** Настройка секретов GitHub для автоматической сборки

