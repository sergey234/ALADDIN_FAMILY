# 🔍 КАК ПРОВЕРИТЬ UUID ПРОФИЛЕЙ В DEVELOPER PORTAL

## 📋 ПРОФИЛИ В DEVELOPER PORTAL

Вы видите:
1. **ALADDIN App Store Distribution** - iOS, App Store, 2026/11/29
2. **ALADDIN PacketTunnel App Store Distribution** - iOS, App Store, 2026/11/29
3. **ALADDINPacketTunnel Dev New** - iOS, Development, 2026/11/28

---

## ❓ ВАЖНЫЙ ВОПРОС: Какие UUID у этих профилей?

### Если UUID СТАРЫЕ (нужно удалить):
- `de134a6b-7135-4f75-bc3b-4a68fd753f7c` → **УДАЛИТЬ!**
- `c0a22622-4b23-4be3-b18d-b744dbf8e6ce` → **УДАЛИТЬ!**

### Если UUID НОВЫЕ (можно проверить):
- Любые другие UUID → проверить содержимое

---

## 🔍 КАК ПРОВЕРИТЬ UUID В DEVELOPER PORTAL

### Способ 1: Через Developer Portal (визуально)

1. Откройте: https://developer.apple.com/account/resources/profiles/list
2. Нажмите на профиль **"ALADDIN App Store Distribution"**
3. В детальной информации найдите **UUID** (обычно внизу страницы)
4. Сравните с:
   - ❌ Старый: `de134a6b-7135-4f75-bc3b-4a68fd753f7c`
   - ✅ Новый: любой другой UUID

5. Повторите для **"ALADDIN PacketTunnel App Store Distribution"**
6. Сравните с:
   - ❌ Старый: `c0a22622-4b23-4be3-b18d-b744dbf8e6ce`
   - ✅ Новый: любой другой UUID

### Способ 2: Скачать и проверить локально

1. **Скачайте профили:**
   - Нажмите на профиль → "Download"
   - Сохраните в Downloads

2. **Проверьте UUID:**
   ```bash
   # Проверка App профиля
   strings ~/Downloads/ALADDIN_App_Store_Distribution.mobileprovision | grep -oE '[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}' | head -1
   
   # Проверка Extension профиля
   strings ~/Downloads/ALADDIN_PacketTunnel_App_Store_Distribution.mobileprovision | grep -oE '[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}' | head -1
   ```

3. **Проверьте тип профиля:**
   ```bash
   # Проверка App профиля
   security cms -D -i ~/Downloads/ALADDIN_App_Store_Distribution.mobileprovision 2>/dev/null | plutil -extract ProvisionedDevices raw -o - - 2>/dev/null || echo "✅ App Store Distribution (нет ProvisionedDevices)"
   
   # Проверка Extension профиля
   security cms -D -i ~/Downloads/ALADDIN_PacketTunnel_App_Store_Distribution.mobileprovision 2>/dev/null | plutil -extract ProvisionedDevices raw -o - - 2>/dev/null || echo "✅ App Store Distribution (нет ProvisionedDevices)"
   ```

---

## ✅ ЧТО ДЕЛАТЬ В ЗАВИСИМОСТИ ОТ UUID

### Если UUID СТАРЫЕ (de134a6b... и c0a22622...):

1. **Удалить эти профили** в Developer Portal
2. **Удалить секреты** в GitHub
3. **Создать НОВЫЕ профили** типа "App Store"

### Если UUID НОВЫЕ (другие):

1. **Проверить тип профиля:**
   - Должен быть App Store Distribution (нет ProvisionedDevices)
   - Если есть ProvisionedDevices → удалить и создать новые

2. **Если профили правильные:**
   - Закодировать в base64
   - Обновить GitHub Secrets

---

## 📋 БЫСТРАЯ ПРОВЕРКА

Запустите скрипт проверки:

```bash
~/Desktop/ALADDIN_Profiles/СКРИПТ_ПРОВЕРКИ_ПРОФИЛЕЙ.sh
```

Скрипт покажет:
- ✅ Тип профиля (App Store Distribution или Development/Ad Hoc)
- ✅ UUID (новый или старый)
- ✅ Capabilities для Extension

---

## ⚠️ ВАЖНО

**Даже если в Developer Portal профили показываются как "App Store", они могут быть неправильными!**

Признаки правильного профиля:
- ✅ Тип в Developer Portal: "App Store"
- ✅ НЕТ ProvisionedDevices (проверка через `plutil`)
- ✅ UUID НЕ совпадает со старым UUID

Признаки неправильного профиля:
- ❌ ЕСТЬ ProvisionedDevices
- ❌ UUID совпадает со старым UUID (`de134a6b...` или `c0a22622...`)

---

## 🎯 РЕКОМЕНДАЦИЯ

**Лучше всего:**
1. Удалить все старые профили (с известными UUID)
2. Создать новые профили типа "App Store"
3. Проверить каждый профиль перед использованием

Это гарантирует, что профили правильные!

