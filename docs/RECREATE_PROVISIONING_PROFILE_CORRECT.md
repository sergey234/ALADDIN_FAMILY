# 🔧 Пересоздание Provisioning Profile с правильными настройками

## 🚨 ПРОБЛЕМА

Профиль "ALADDINPacketTunnel Dev." содержит **множество** типов Network Extensions:
- app-proxy-provider
- content-filter-provider
- packet-tunnel-provider
- dns-proxy
- dns-settings
- relay
- url-filter-provider
- hotspot-provider

А в entitlements только `packet-tunnel-provider`. Xcode требует точного совпадения.

---

## ✅ РЕШЕНИЕ: Пересоздать профиль с правильными настройками

### **ШАГ 1: Проверь Bundle ID в Portal**

1. Зайди на: https://developer.apple.com/account/resources/identifiers/list
2. Найди Bundle ID: `family.aladdin.ios.packetTunnel`
3. Кликни на Bundle ID
4. Проверь раздел **"Capabilities"**:
   - ✅ **Personal VPN** - включена
   - ✅ **Network Extensions** - включена
   - ⚠️ **ВАЖНО:** Внутри Network Extensions должна быть выбрана **ТОЛЬКО** "Packet Tunnel Provider"
   - ❌ **НЕ должно быть:** app-proxy, content-filter, dns-proxy и т.д.

5. Если выбрано несколько типов:
   - Сними галочки со всех, кроме **"Packet Tunnel Provider"**
   - Сохрани (Save)

### **ШАГ 2: Удали старый профиль**

1. Зайди на: https://developer.apple.com/account/resources/profiles/list
2. Найди профиль **"ALADDINPacketTunnel Dev."**
3. **Удали его** (кнопка Delete)

### **ШАГ 3: Создай новый профиль**

1. На странице Profiles нажми **"+"** (плюс)
2. Выбери **"iOS App Development"** → **Continue**
3. Выбери App ID: **`family.aladdin.ios.packetTunnel`**
   - Убедись, что у этого App ID выбрана **ТОЛЬКО** "Packet Tunnel Provider"
4. Выбери Certificate: **твой iOS Development сертификат**
5. Название: **`ALADDINPacketTunnel Dev New`**
6. Нажми **"Generate"**
7. **Скачай** `.mobileprovision` файл

### **ШАГ 4: Установи новый профиль**

1. **Удали старый профиль** из системы:
   ```bash
   rm ~/Library/MobileDevice/Provisioning\ Profiles/84158b68-a95d-4817-8735-b99dcd174870.mobileprovision
   ```

2. **Дважды кликни** на новый `.mobileprovision` файл
3. Он установится в Xcode автоматически

### **ШАГ 5: Обнови настройки в Xcode**

1. **В Xcode:**
   - Target **ALADDINPacketTunnel**
   - **Signing & Capabilities**
   - В поле **Provisioning Profile** выбери новый профиль **"ALADDINPacketTunnel Dev New"**

2. **Перезапусти Xcode** (⌘Q → открой заново)

3. **Собери проект** (⌘B)

---

## 🔍 ПРОВЕРКА: Что должно быть в новом профиле

После установки нового профиля проверь:

```bash
security cms -D -i ~/Library/MobileDevice/Provisioning\ Profiles/[UUID].mobileprovision | grep -A 5 "com.apple.developer.networking.networkextension"
```

**Должно быть:**
```xml
<key>com.apple.developer.networking.networkextension</key>
<array>
    <string>packet-tunnel-provider</string>
</array>
```

**НЕ должно быть других типов!**

---

## ✅ ИТОГ

Главное - в Portal для Bundle ID должна быть выбрана **ТОЛЬКО** "Packet Tunnel Provider" (без других типов Network Extensions). Тогда новый профиль будет содержать только нужное значение, и всё совпадёт с entitlements.

