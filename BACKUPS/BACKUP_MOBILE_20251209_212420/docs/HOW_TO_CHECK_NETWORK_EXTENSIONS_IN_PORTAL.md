# 🔍 Как проверить Network Extensions в Apple Developer Portal

## 📋 Где проверить настройки Network Extensions

### **ШАГ 1: Открой страницу Bundle ID**

1. **Зайди на:** https://developer.apple.com/account/resources/identifiers/list
2. **Найди Bundle ID:** `family.aladdin.ios.packetTunnel`
   - Используй поиск или прокрути список
3. **Кликни на Bundle ID** (откроется страница с деталями)

### **ШАГ 2: Найди раздел "Capabilities"**

На странице Bundle ID прокрути вниз до раздела **"Capabilities"**.

Там ты увидишь список всех capabilities:
- Personal VPN
- Network Extensions
- Push Notifications
- и т.д.

### **ШАГ 3: Проверь Network Extensions**

1. **Найди строку "Network Extensions"** в списке Capabilities
2. **Кликни на "Network Extensions"** (на саму строку или на стрелку справа)
3. **Должно открыться подменю** с типами Network Extensions:
   - App Proxy Provider
   - Content Filter Provider
   - **Packet Tunnel Provider** ← ДОЛЖНА БЫТЬ ВЫБРАНА ТОЛЬКО ЭТА
   - DNS Proxy
   - DNS Settings
   - Relay
   - URL Filter Provider
   - Hotspot Provider

### **ШАГ 4: Проверь, что выбрана только "Packet Tunnel Provider"**

**Должно быть:**
- ✅ **Packet Tunnel Provider** - включена (галочка стоит)
- ❌ **Все остальные** - выключены (галочек нет)

**Если выбрано несколько типов:**
- Сними галочки со всех, кроме **"Packet Tunnel Provider"**
- Нажми **"Save"** (Сохранить) в правом верхнем углу

---

## 🔍 ЕСЛИ ПОДМЕНЮ НЕ ОТКРЫВАЕТСЯ

Если при клике на "Network Extensions" подменю не появляется:

1. **Проверь, что Network Extensions включена:**
   - Должна быть галочка на "Network Extensions"
   - Если нет - включи её

2. **Попробуй обновить страницу** (F5 или ⌘R)

3. **Или используй другой браузер** (Safari, Chrome, Firefox)

---

## 📋 АЛЬТЕРНАТИВНЫЙ СПОСОБ: Проверить через созданный профиль

Если уже создал профиль, можно проверить его содержимое:

```bash
# Найди новый профиль
ls -lt ~/Library/MobileDevice/Provisioning\ Profiles/*.mobileprovision | head -1

# Проверь содержимое (замени на реальный путь)
security cms -D -i ~/Library/MobileDevice/Provisioning\ Profiles/[UUID].mobileprovision | grep -A 10 "com.apple.developer.networking.networkextension"
```

**Если в профиле только `packet-tunnel-provider`** - значит всё правильно!
**Если там много типов** - значит в Portal выбрано несколько типов, нужно исправить.

---

## ✅ ЧЕКЛИСТ

- ✅ Bundle ID `family.aladdin.ios.packetTunnel` открыт в Portal
- ✅ Раздел "Capabilities" виден
- ✅ "Network Extensions" включена (галочка)
- ✅ При клике на "Network Extensions" открывается подменю
- ✅ В подменю выбрана ТОЛЬКО "Packet Tunnel Provider"
- ✅ Все остальные типы выключены
- ✅ Сохранено (Save)

---

## 🎯 ГДЕ ИСКАТЬ

**Путь в Portal:**
```
Certificates, Identifiers & Profiles
  → Identifiers
    → App IDs
      → family.aladdin.ios.packetTunnel (клик)
        → Capabilities (прокрути вниз)
          → Network Extensions (клик)
            → Packet Tunnel Provider (должна быть выбрана ТОЛЬКО эта)
```

**Попробуй найти раздел "Capabilities" на странице Bundle ID - там должна быть информация о Network Extensions!**

