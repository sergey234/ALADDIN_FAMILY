# 🔧 Удаление и пересоздание Provisioning Profile - Пошаговая инструкция

## 📋 ШАГ 1: Удалить старый профиль в Portal

1. **Открой:** https://developer.apple.com/account/resources/profiles/list
2. **Найди профиль:** "ALADDINPacketTunnel Dev."
3. **Кликни на профиль** (откроется страница с деталями)
4. **Нажми кнопку "Delete"** (вверху справа)
5. **Подтверди удаление**

---

## 📋 ШАГ 2: Проверить Bundle ID в Portal (ВАЖНО!)

**ПЕРЕД созданием нового профиля проверь:**

1. **Открой:** https://developer.apple.com/account/resources/identifiers/list
2. **Найди Bundle ID:** `family.aladdin.ios.packetTunnel`
3. **Кликни на Bundle ID**
4. **Проверь раздел "Capabilities":**
   - ✅ **Personal VPN** - включена
   - ✅ **Network Extensions** - включена
   - ⚠️ **КРИТИЧНО:** Внутри Network Extensions должна быть выбрана **ТОЛЬКО** "Packet Tunnel Provider"
   - ❌ **НЕ должно быть:** app-proxy, content-filter, dns-proxy, dns-settings, relay, url-filter-provider, hotspot-provider

5. **Если выбрано несколько типов:**
   - Сними галочки со всех, кроме **"Packet Tunnel Provider"**
   - Нажми **"Save"** (Сохранить)

6. **Подожди 1-2 минуты** (Apple обновит настройки)

---

## 📋 ШАГ 3: Создать новый профиль

1. **Вернись на:** https://developer.apple.com/account/resources/profiles/list
2. **Нажми кнопку "+"** (плюс в левом верхнем углу)
3. **Выбери "iOS App Development"** → **Continue**
4. **Выбери App ID:**
   - Выбери **`family.aladdin.ios.packetTunnel`** из списка
   - Убедись, что у этого App ID выбрана **ТОЛЬКО** "Packet Tunnel Provider"
5. **Выбери Certificate:**
   - Выбери свой **iOS Development** сертификат
6. **Название профиля:**
   - Введи: **`ALADDINPacketTunnel Dev New`** (или любое другое название)
7. **Нажми "Generate"** (Создать)
8. **Скачай** `.mobileprovision` файл (кнопка Download)

---

## 📋 ШАГ 4: Удалить старый профиль из системы

**В терминале выполни:**
```bash
rm ~/Library/MobileDevice/Provisioning\ Profiles/84158b68-a95d-4817-8735-b99dcd174870.mobileprovision
```

Или найди все профили для packetTunnel и удали их:
```bash
rm ~/Library/MobileDevice/Provisioning\ Profiles/*packetTunnel*.mobileprovision
```

---

## 📋 ШАГ 5: Установить новый профиль

1. **Найди скачанный файл** `.mobileprovision` (обычно в папке Downloads)
2. **Дважды кликни** на файл
3. **Xcode откроется** и установит профиль автоматически
4. **Или перетащи файл** в окно Xcode

---

## 📋 ШАГ 6: Обновить настройки в Xcode

1. **Открой Xcode** с проектом `ALADDIN.xcodeproj`
2. **Выбери таргет ALADDINPacketTunnel**
3. **Вкладка "Signing & Capabilities"**
4. **Сними галочку** "Automatically manage signing" (если включена)
5. **В поле "Provisioning Profile"** выбери новый профиль **"ALADDINPacketTunnel Dev New"**
6. **Убедись, что Team выбран** (правильный Team ID)

---

## 📋 ШАГ 7: Перезапустить Xcode и собрать

1. **Закрой Xcode** полностью (⌘Q)
2. **Открой проект заново**
3. **Собери проект** (⌘B)

---

## ✅ ПРОВЕРКА: Что должно быть в новом профиле

После установки проверь содержимое нового профиля:

```bash
# Найди UUID нового профиля
ls -lt ~/Library/MobileDevice/Provisioning\ Profiles/*.mobileprovision | head -1

# Проверь содержимое (замени UUID на реальный)
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

## 🎯 ГЛАВНОЕ

**САМОЕ ВАЖНОЕ:** В Portal для Bundle ID должна быть выбрана **ТОЛЬКО** "Packet Tunnel Provider" (без других типов Network Extensions). Иначе новый профиль будет содержать все типы, и ошибка повторится.

**Проверь это ПЕРЕД созданием нового профиля!**

