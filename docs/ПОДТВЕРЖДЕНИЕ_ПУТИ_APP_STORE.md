# ✅ ПОДТВЕРЖДЕНИЕ: Правильный путь для App Store

**Дата:** 29 ноября 2025  
**Вопрос:** Правильно ли мы идем?

---

## ✅ ДА, ПУТЬ ПРАВИЛЬНЫЙ!

### 🎯 ЧТО ВЫБРАТЬ:

**Distribution → App Store Connect**

Это именно то, что нужно для публикации в App Store!

---

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ

### Шаг 1: Выбрать тип профиля

1. **На странице создания профиля:**
   - Вы увидите список типов
   - **НЕ выбирайте:** Development (для разработки)
   - **Выберите:** **Distribution → App Store Connect** ✅

2. **Почему именно "App Store Connect":**
   - ✅ Для публикации в App Store
   - ✅ Работает с Manual signing на CI/CD
   - ✅ Не требует регистрацию устройств
   - ✅ Это то, что нужно для GitHub Actions

---

### Шаг 2: Создать профиль для основного приложения

1. **После выбора "App Store Connect":**
   - Нажмите "Continue"

2. **Выбрать App ID:**
   - Выберите `family.aladdin.ios` (основное приложение)
   - Нажмите "Continue"

3. **Выбрать сертификат:**
   - Выберите **"Apple Distribution"** сертификат
   - Нажмите "Continue"

4. **Ввести название:**
   - **Profile Name:** `ALADDIN App Store Distribution`
   - Нажмите "Generate"

5. **Скачать профиль:**
   - Нажмите "Download"
   - Сохраните файл

---

### Шаг 3: Создать профиль для Network Extension

1. **Повторить процесс:**
   - Нажмите "+" (Create a new provisioning profile)
   - Выберите **Distribution → App Store Connect**
   - Нажмите "Continue"

2. **Выбрать App ID:**
   - Выберите `family.aladdin.ios.packetTunnel` (Network Extension)
   - Нажмите "Continue"

3. **Выбрать сертификат:**
   - Выберите **"Apple Distribution"** сертификат
   - Нажмите "Continue"

4. **Ввести название:**
   - **Profile Name:** `ALADDIN PacketTunnel App Store Distribution`
   - Нажмите "Generate"

5. **Скачать профиль:**
   - Нажмите "Download"
   - Сохраните файл

---

## ✅ ПРОВЕРКА

### Что должно быть:

1. **В Developer Portal:**
   - ✅ Два профиля типа **"App Store Connect"** (не Development!)
   - ✅ Оба используют сертификат "Apple Distribution"
   - ✅ Оба профиля скачаны

2. **Названия профилей:**
   - ✅ `ALADDIN App Store Distribution` (для `family.aladdin.ios`)
   - ✅ `ALADDIN PacketTunnel App Store Distribution` (для `family.aladdin.ios.packetTunnel`)

---

## 🎯 ПОЧЕМУ ЭТО ПРАВИЛЬНО

### Development профили:
- ❌ Для разработки и тестирования
- ❌ Требуют регистрацию устройств
- ❌ Не работают для App Store
- ❌ Обычно "Xcode managed"

### App Store Connect профили:
- ✅ Для публикации в App Store
- ✅ Не требуют регистрацию устройств
- ✅ Работают с Manual signing
- ✅ Обычно "manually managed"

---

## 📝 СЛЕДУЮЩИЕ ШАГИ

После создания профилей:

1. Закодировать в base64
2. Обновить GitHub Secrets
3. Запустить workflow

**Инструкция:** `docs/БЫСТРАЯ_ИНСТРУКЦИЯ_APP_STORE_PROFILES.md`

---

**Дата:** 29 ноября 2025  
**Подтверждение:** Да, путь правильный! Выбирайте "App Store Connect"

