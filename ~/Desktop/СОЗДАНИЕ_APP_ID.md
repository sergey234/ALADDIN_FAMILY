# 📱 СОЗДАНИЕ APP ID

**Дата:** 29 ноября 2025  
**Проблема:** App ID `family.aladdin.ios` не виден в списке

---

## 🎯 РЕШЕНИЕ: СОЗДАТЬ APP ID

Если App ID не виден, его нужно создать в Developer Portal.

---

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ

### Шаг 1: Открыть страницу Identifiers

1. **Открыть:** https://developer.apple.com/account/resources/identifiers/list
2. **Нажать "+"** (Register a new identifier)

---

### Шаг 2: Выбрать тип App ID

1. **Выбрать:** **"App IDs"** (первый вариант)
2. **Нажать "Continue"**

---

### Шаг 3: Выбрать тип App ID

1. **Выбрать:** **"App"** (для основного приложения)
2. **Нажать "Continue"**

---

### Шаг 4: Заполнить информацию

1. **Description (Описание):**
   - Ввести: `ALADDIN iOS App`

2. **Bundle ID:**
   - Выбрать **"Explicit"**
   - Ввести: `family.aladdin.ios`

3. **Capabilities (Возможности):**
   - ✅ **Network Extensions** (обязательно для VPN!)
   - ✅ **Personal VPN** (обязательно для VPN!)
   - ✅ **Push Notifications** (если используете)
   - ✅ **App Groups** (если используете)
   - ✅ Другие возможности по необходимости

4. **Нажать "Continue"**

5. **Проверить информацию и нажать "Register"**

---

### Шаг 5: Создать App ID для Network Extension

1. **Нажать "+"** (Register a new identifier)

2. **Выбрать:** **"App IDs"** → **"Continue"**

3. **Выбрать:** **"App"** → **"Continue"**

4. **Заполнить:**
   - **Description:** `ALADDIN PacketTunnel Extension`
   - **Bundle ID:** Выбрать **"Explicit"** → Ввести: `family.aladdin.ios.packetTunnel`
   - **Capabilities:**
     - ✅ **Network Extensions** (обязательно!)
     - ✅ **Personal VPN** (обязательно!)

5. **Нажать "Continue"** → **"Register"**

---

## ✅ ПРОВЕРКА

### Что должно быть:

1. **В списке Identifiers:**
   - ✅ `family.aladdin.ios` (App)
   - ✅ `family.aladdin.ios.packetTunnel` (App)

2. **Оба App ID должны иметь:**
   - ✅ Network Extensions capability
   - ✅ Personal VPN capability

---

## 🎯 СЛЕДУЮЩИЙ ШАГ

После создания App ID:
1. Вернуться к созданию профилей
2. Теперь App ID должны быть видны в списке!

---

**Дата:** 29 ноября 2025  
**Инструкция:** Создание App ID для приложения

