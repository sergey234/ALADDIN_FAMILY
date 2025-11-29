# ⚡ БЫСТРАЯ ПРОВЕРКА APP ID

**Проблема:** App ID `family.aladdin.ios` не виден в списке

---

## 🔍 ЧТО ДЕЛАТЬ

### Вариант 1: Проверить существующие App ID

1. **Откройте:** https://developer.apple.com/account/resources/identifiers/list

2. **Проверьте список:**
   - Ищите App ID с Bundle ID: `family.aladdin.ios`
   - Ищите App ID с Bundle ID: `family.aladdin.ios.packetTunnel`

3. **Если найдены:**
   - ✅ App ID уже существуют
   - ✅ Можно создавать профили
   - ⚠️ Возможно, они называются по-другому

---

### Вариант 2: Создать App ID (если не найдены)

1. **Откройте:** https://developer.apple.com/account/resources/identifiers/list
2. **Нажмите "+"** (Register a new identifier)
3. **Выберите:** App IDs → Continue
4. **Выберите:** App → Continue
5. **Заполните:**
   - **Description:** `ALADDIN iOS App`
   - **Bundle ID:** `family.aladdin.ios` (Explicit)
   - **Capabilities:** Network Extensions, Personal VPN
6. **Нажмите:** Continue → Register

---

### Вариант 3: Использовать существующий App ID

Если App ID существует, но с другим названием:
- ✅ Можно использовать существующий
- ✅ Просто выберите его при создании профиля

---

## ✅ ПОСЛЕ ПРОВЕРКИ

После создания/проверки App ID:
1. Вернуться к созданию профилей
2. App ID должны быть видны в списке!

---

**Подробная инструкция:** `СОЗДАНИЕ_APP_ID.md`

