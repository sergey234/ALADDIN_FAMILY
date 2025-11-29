# 🔍 Где найти настройки VPN в Apple Developer Portal

## 📋 Страница: Certificates, Identifiers & Profiles

**Ссылка:** https://developer.apple.com/account/resources/identifiers/list

На этой странице вы увидите список всех **Bundle IDs** вашего аккаунта.

---

## 🎯 Что нужно найти

### **Bundle ID для VPN Extension:**

Найдите Bundle ID: **`family.aladdin.ios.packetTunnel`**

Это Bundle ID для Network Extension (VPN расширения).

---

## 📍 Пошаговая инструкция

### **ШАГ 1: Откройте страницу Identifiers**

1. Зайдите на: https://developer.apple.com/account/resources/identifiers/list
2. Войдите в свой Apple Developer аккаунт
3. Вы увидите список всех Bundle IDs

### **ШАГ 2: Найдите Bundle ID**

1. **В поиске** (если есть) введите: `packetTunnel`
2. **Или прокрутите список** и найдите: `family.aladdin.ios.packetTunnel`
3. **Нажмите на Bundle ID** (кликните на строку)

### **ШАГ 3: Проверьте Capabilities**

После клика на Bundle ID откроется страница с деталями.

**Проверьте раздел "Capabilities":**

Должны быть включены (галочки):
- ✅ **Personal VPN** - должна быть включена
- ✅ **Network Extensions** - должна быть включена
  - Внутри Network Extensions должен быть выбран **"Packet Tunnel Provider"**

### **ШАГ 4: Если не включены**

1. **Включите галочки:**
   - Поставьте галочку на **Personal VPN**
   - Поставьте галочку на **Network Extensions**
   - Внутри Network Extensions выберите **"Packet Tunnel Provider"**

2. **Нажмите "Save"** (Сохранить) в правом верхнем углу

3. **Подождите 1-2 минуты** (Apple обновит настройки)

---

## 🔍 Если Bundle ID не найден

### **Создайте новый Bundle ID:**

1. **На странице Identifiers** нажмите кнопку **"+"** (плюс) в левом верхнем углу
2. **Выберите "App IDs"** → **"Continue"**
3. **Выберите "App"** → **"Continue"**
4. **Заполните:**
   - **Description:** `ALADDIN Packet Tunnel Extension`
   - **Bundle ID:** `family.aladdin.ios.packetTunnel` (Explicit)
5. **Включите Capabilities:**
   - ✅ **Personal VPN**
   - ✅ **Network Extensions** → выберите **"Packet Tunnel Provider"**
6. **Нажмите "Continue"** → **"Register"**

---

## 📋 Структура страницы

### **Что вы увидите на странице Identifiers:**

```
Certificates, Identifiers & Profiles
├── Identifiers
│   ├── App IDs
│   │   ├── family.aladdin.ios (основное приложение)
│   │   └── family.aladdin.ios.packetTunnel (VPN Extension) ← НАЙТИ ЭТО
│   ├── Services IDs
│   └── ...
├── Certificates
└── Profiles
```

### **На странице Bundle ID вы увидите:**

```
family.aladdin.ios.packetTunnel
├── Description: ALADDIN Packet Tunnel Extension
├── Bundle ID: family.aladdin.ios.packetTunnel
├── Capabilities: ← ПРОВЕРИТЬ ЗДЕСЬ
│   ├── ☑ Personal VPN
│   ├── ☑ Network Extensions
│   │   └── ☑ Packet Tunnel Provider
│   └── ...
└── [Save] [Cancel]
```

---

## ✅ Чеклист проверки

### **На странице Bundle ID должно быть:**

1. ✅ **Bundle ID:** `family.aladdin.ios.packetTunnel`
2. ✅ **Personal VPN:** включена (галочка стоит)
3. ✅ **Network Extensions:** включена (галочка стоит)
4. ✅ **Packet Tunnel Provider:** выбран внутри Network Extensions

### **Если всё включено:**

- ✅ Всё правильно!
- Вернитесь в Xcode
- Обновите provisioning profiles
- Personal VPN должна стать активной

---

## 🔧 Если не можете найти Bundle ID

### **Вариант 1: Проверьте фильтры**

На странице Identifiers могут быть фильтры:
- **Type:** выберите "App IDs"
- **Platform:** выберите "iOS"
- **Status:** выберите "All"

### **Вариант 2: Используйте поиск**

1. В верхней части страницы найдите поле поиска
2. Введите: `packetTunnel` или `family.aladdin.ios.packetTunnel`
3. Нажмите Enter

### **Вариант 3: Проверьте другой аккаунт**

Если Bundle ID не найден:
- Возможно, он создан в другом Apple Developer аккаунте
- Проверьте, что вы вошли в правильный аккаунт
- Team ID должен быть `6CJVBBUGSN`

---

## 🎯 Итоговая инструкция

1. **Откройте:** https://developer.apple.com/account/resources/identifiers/list
2. **Найдите:** `family.aladdin.ios.packetTunnel`
3. **Кликните** на Bundle ID
4. **Проверьте Capabilities:**
   - Personal VPN ✅
   - Network Extensions ✅ → Packet Tunnel Provider ✅
5. **Если не включены** - включите и сохраните
6. **Подождите 1-2 минуты**
7. **Вернитесь в Xcode** и обновите профили

---

## 📝 Примечание

Если вы видите только футер страницы (Copyright © 2025 Apple Inc.), это может означать:
- Вы не вошли в аккаунт
- Нужно авторизоваться
- Или страница не загрузилась полностью

**Попробуйте:**
1. Обновить страницу (F5 или ⌘R)
2. Войти в аккаунт заново
3. Проверить, что у вас есть доступ к Apple Developer Program

