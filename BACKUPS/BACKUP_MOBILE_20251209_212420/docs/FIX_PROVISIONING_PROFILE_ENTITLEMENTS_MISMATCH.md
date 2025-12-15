# 🔧 Исправление несоответствия entitlements в provisioning profile

## 🚨 ПРОБЛЕМА

Ошибка:
```
Provisioning profile "ALADDINPacketTunnel Dev." doesn't match the entitlements file's value for the com.apple.developer.networking.networkextension entitlement.
```

**Причина:** В provisioning profile используется старое значение `packet-tunnel-provider`, а в entitlements файле мы изменили на `packet-tunnel`.

---

## ✅ РЕШЕНИЕ: Пересоздать профиль в Portal

Профиль был создан **ДО** того, как мы изменили entitlements. Нужно создать **новый** профиль в Portal.

### **ШАГ 1: Убедись, что в Portal всё правильно**

1. Зайди на: https://developer.apple.com/account/resources/identifiers/list
2. Найди Bundle ID: `family.aladdin.ios.packetTunnel`
3. Кликни на Bundle ID
4. Проверь Capabilities:
   - ✅ **Personal VPN** - включена
   - ✅ **Network Extensions** - включена
   - ✅ Внутри Network Extensions выбран **"Packet Tunnel Provider"**
5. **Сохрани (Save)** - даже если ничего не менял

### **ШАГ 2: Удали старый профиль в Portal**

1. Зайди на: https://developer.apple.com/account/resources/profiles/list
2. Найди профиль **"ALADDINPacketTunnel Dev."**
3. **Удали его** (кнопка Delete)

### **ШАГ 3: Создай новый профиль**

1. На странице Profiles нажми **"+"** (плюс)
2. Выбери **"iOS App Development"** → **Continue**
3. Выбери App ID: **`family.aladdin.ios.packetTunnel`**
4. Выбери Certificate: **твой iOS Development сертификат**
5. Название: **`ALADDINPacketTunnel Dev New`** (или любое другое)
6. Нажми **"Generate"**
7. **Скачай** `.mobileprovision` файл

### **ШАГ 4: Установи новый профиль**

1. **Дважды кликни** на скачанный `.mobileprovision` файл
2. Он установится в Xcode автоматически

### **ШАГ 5: Обнови настройки в Xcode**

1. **Удали старый профиль** из системы:
   ```bash
   rm ~/Library/MobileDevice/Provisioning\ Profiles/84158b68-a95d-4817-8735-b99dcd174870.mobileprovision
   ```

2. **В Xcode:**
   - Target **ALADDINPacketTunnel**
   - **Signing & Capabilities**
   - В поле **Provisioning Profile** выбери новый профиль **"ALADDINPacketTunnel Dev New"**

3. **Перезапусти Xcode** (⌘Q → открой заново)

4. **Собери проект** (⌘B)

---

## 🔍 АЛЬТЕРНАТИВНОЕ РЕШЕНИЕ: Вернуть старое значение

Если не хочешь пересоздавать профиль, можно временно вернуть старое значение в entitlements:

### **В `ALADDINPacketTunnel.entitlements`:**
```xml
<key>com.apple.developer.networking.networkextension</key>
<array>
    <string>packet-tunnel-provider</string>
</array>
```

### **В `ALADDINPacketTunnelDebug.entitlements`:**
```xml
<key>com.apple.developer.networking.networkextension</key>
<array>
    <string>packet-tunnel-provider</string>
</array>
```

**НО:** Это не рекомендуется, так как Apple рекомендует использовать `packet-tunnel` вместо `packet-tunnel-provider`.

---

## ✅ РЕКОМЕНДУЕМОЕ РЕШЕНИЕ

**Лучше пересоздать профиль** в Portal после того, как убедишься, что в Portal всё правильно настроено. Новый профиль будет содержать правильные entitlements.

---

## 📋 ЧЕКЛИСТ

- ✅ В Portal Bundle ID имеет правильные capabilities
- ✅ Старый профиль удалён из Portal
- ✅ Новый профиль создан и скачан
- ✅ Новый профиль установлен (двойной клик)
- ✅ Старый профиль удалён из системы
- ✅ В Xcode выбран новый профиль
- ✅ Xcode перезапущен
- ✅ Проект собран успешно

