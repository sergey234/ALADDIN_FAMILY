# 📋 ИНСТРУКЦИЯ: Как получить информацию из Apple Developer Portal

**Цель:** Собрать полную информацию о Certificates, Identifiers и Profiles для анализа

---

## 🔐 ШАГ 1: CERTIFICATES (Сертификаты)

### Где найти:
1. Откройте: https://developer.apple.com/account/resources/certificates/list
2. Или: https://developer.apple.com/account → **Certificates, Identifiers & Profiles** → **Certificates**

### Что нужно скопировать:
**Скопируйте всю таблицу сертификатов:**

```
Name | Type | Platform | Created By | Expiration
-----|------|----------|-----------|------------
SERGEY KHLYSTOV | Development | All | SERGEY KHLYSTOV | 2026/11/27
SERGEY KHLYSTOV | Distribution Managed | All | SERGEY KHLYSTOV | 2026/11/29
...
```

**Или сделайте скриншот всей таблицы сертификатов**

---

## 🆔 ШАГ 2: IDENTIFIERS (App ID)

### Где найти:
1. Откройте: https://developer.apple.com/account/resources/identifiers/list
2. Или: https://developer.apple.com/account → **Certificates, Identifiers & Profiles** → **Identifiers**

### Что нужно сделать:

#### 2.1. Найти App ID для основного приложения
1. В поиске введите: `family.aladdin.ios`
2. Нажмите на найденный App ID
3. **Скопируйте или сфотографируйте:**
   - **Description** (название)
   - **Bundle ID** (должно быть `family.aladdin.ios`)
   - **Capabilities** (все включенные capabilities)
   - **Status** (Active/Expired)

#### 2.2. Найти App ID для расширения
1. В поиске введите: `family.aladdin.ios.packetTunnel`
2. Нажмите на найденный App ID
3. **Скопируйте или сфотографируйте:**
   - **Description** (название)
   - **Bundle ID** (должно быть `family.aladdin.ios.packetTunnel`)
   - **Capabilities** (все включенные capabilities)
   - **ВАЖНО:** Проверьте что включены:
     - ✅ **Network Extensions**
     - ✅ **Personal VPN**
   - **Status** (Active/Expired)

#### 2.3. Скопировать весь список App ID
**Скопируйте всю таблицу App ID:**

```
Type | Identifier | Description | Status
-----|------------|-------------|--------
App IDs | family.aladdin.ios | ... | Active
App IDs | family.aladdin.ios.packetTunnel | ... | Active
...
```

**Или сделайте скриншот всей таблицы App ID**

---

## 📄 ШАГ 3: PROFILES (Provisioning Profiles)

### Где найти:
1. Откройте: https://developer.apple.com/account/resources/profiles/list
2. Или: https://developer.apple.com/account → **Certificates, Identifiers & Profiles** → **Profiles**

### Что нужно сделать:

#### 3.1. Скопировать весь список профилей
**Скопируйте всю таблицу Profiles:**

```
Name | Type | App ID | Status | Expiration
-----|------|-------|--------|------------
ALADDIN App Store Distribution | App Store | family.aladdin.ios | Active | 2026/11/29
ALADDINPacketTunnel Dev New | Development | family.aladdin.ios.packetTunnel | Active | 2026/11/27
...
```

**Или сделайте скриншот всей таблицы Profiles**

#### 3.2. Детальная информация по каждому профилю

**Для каждого профиля (особенно для ALADDIN):**

1. **Нажмите на название профиля** (например, "ALADDIN App Store Distribution")
2. **Скопируйте или сфотографируйте:**
   - **Name** (название профиля)
   - **Type** (App Store / Development / Ad Hoc)
   - **App ID** (для какого Bundle ID)
   - **Certificates** (какие сертификаты связаны)
   - **Status** (Active / Expired / Invalid)
   - **Expiration Date** (дата истечения)
   - **UUID** (если видно)

**Особенно важно для:**
- ✅ Профили с названием содержащим "ALADDIN"
- ✅ Профили для `family.aladdin.ios`
- ✅ Профили для `family.aladdin.ios.packetTunnel`

---

## 📸 ШАГ 4: СКРИНШОТЫ (Альтернатива)

Если проще сделать скриншоты:

### Что сфотографировать:

1. **Страница Certificates:**
   - Вся таблица сертификатов
   - URL: https://developer.apple.com/account/resources/certificates/list

2. **Страница Identifiers:**
   - Вся таблица App ID
   - Детальная страница для `family.aladdin.ios`
   - Детальная страница для `family.aladdin.ios.packetTunnel`
   - URL: https://developer.apple.com/account/resources/identifiers/list

3. **Страница Profiles:**
   - Вся таблица Profiles
   - Детальная страница каждого профиля с названием "ALADDIN"
   - URL: https://developer.apple.com/account/resources/profiles/list

---

## 📋 ЧЕКЛИСТ: Что нужно собрать

### ✅ Certificates:
- [ ] Список всех сертификатов (таблица)
- [ ] Особенно: Distribution сертификаты

### ✅ Identifiers:
- [ ] Список всех App ID (таблица)
- [ ] Детали для `family.aladdin.ios`:
  - [ ] Description
  - [ ] Bundle ID
  - [ ] Capabilities (все включенные)
  - [ ] Status
- [ ] Детали для `family.aladdin.ios.packetTunnel`:
  - [ ] Description
  - [ ] Bundle ID
  - [ ] Capabilities (особенно Network Extensions и Personal VPN)
  - [ ] Status

### ✅ Profiles:
- [ ] Список всех Profiles (таблица)
- [ ] Детали для каждого профиля с "ALADDIN" в названии:
  - [ ] Name
  - [ ] Type (App Store / Development / Ad Hoc)
  - [ ] App ID
  - [ ] Certificates (какие связаны)
  - [ ] Status
  - [ ] Expiration Date
  - [ ] UUID (если видно)

---

## 🎯 БЫСТРЫЙ СПОСОБ (если нужно быстро)

### Вариант 1: Скопировать текст
1. Откройте каждую страницу
2. Выделите всю таблицу (Cmd+A)
3. Скопируйте (Cmd+C)
4. Вставьте в сообщение

### Вариант 2: Скриншоты
1. Откройте каждую страницу
2. Сделайте скриншот (Cmd+Shift+4)
3. Пришлите скриншоты

### Вариант 3: Экспорт (если доступно)
1. Некоторые страницы позволяют экспортировать данные
2. Проверьте кнопку "Export" или "Download"

---

## 📝 ПРИМЕР: Как должна выглядеть информация

### Certificates:
```
Name: SERGEY KHLYSTOV
Type: Distribution
Platform: All
Created By: SERGEY KHLYSTOV
Expiration: 2026/11/29
```

### Identifiers:
```
App ID: family.aladdin.ios
Description: ALADDIN iOS App
Capabilities:
  - App Groups
  - Push Notifications
Status: Active
```

### Profiles:
```
Name: ALADDIN App Store Distribution
Type: App Store
App ID: family.aladdin.ios
Certificates: SERGEY KHLYSTOV (Distribution)
Status: Active
Expiration: 2026/11/29
UUID: 3eeb2cf2-7b0a-4115-a769-b8d7509bdae4
```

---

## 🔗 ПРЯМЫЕ ССЫЛКИ

1. **Certificates:**
   https://developer.apple.com/account/resources/certificates/list

2. **Identifiers:**
   https://developer.apple.com/account/resources/identifiers/list

3. **Profiles:**
   https://developer.apple.com/account/resources/profiles/list

4. **Главная страница:**
   https://developer.apple.com/account/resources

---

## ⚠️ ВАЖНО

- **Не нужно** скачивать файлы (.mobileprovision)
- **Нужно** только скопировать/сфотографировать информацию со страниц
- **Особенно важно** информация о Profiles с названием "ALADDIN"
- **Проверьте** что у `family.aladdin.ios.packetTunnel` включены Network Extensions и Personal VPN

---

**После сбора информации пришлите её, и я проведу полный анализ!**

