# ⚡ БЫСТРАЯ КОНВЕРТАЦИЯ PROVISIONING PROFILES

## 📋 Команды для копирования

### 1. Конвертировать основной профиль в base64:
```bash
base64 -i ~/Downloads/ALADDIN_App_Store.mobileprovision -o - | pbcopy
```
Результат скопирован в буфер обмена → вставьте в GitHub Secret `PROVISIONING_PROFILE_APP`

### 2. Конвертировать профиль расширения в base64:
```bash
base64 -i ~/Downloads/ALADDINPacketTunnel_App_Store.mobileprovision -o - | pbcopy
```
Результат скопирован в буфер обмена → вставьте в GitHub Secret `PROVISIONING_PROFILE_EXTENSION`

### 3. Если файлы в другом месте, укажите полный путь:
```bash
# Пример для основного профиля
base64 -i /путь/к/файлу/ALADDIN_App_Store.mobileprovision -o - | pbcopy

# Пример для профиля расширения
base64 -i /путь/к/файлу/ALADDINPacketTunnel_App_Store.mobileprovision -o - | pbcopy
```

### 4. Проверить что base64 правильный (опционально):
```bash
# Для основного профиля
base64 -i ~/Downloads/ALADDIN_App_Store.mobileprovision -o - | base64 -d > /tmp/test.mobileprovision
security cms -D -i /tmp/test.mobileprovision | grep -A 5 "TeamName"

# Для профиля расширения
base64 -i ~/Downloads/ALADDINPacketTunnel_App_Store.mobileprovision -o - | base64 -d > /tmp/test_ext.mobileprovision
security cms -D -i /tmp/test_ext.mobileprovision | grep -A 5 "TeamName"
```

---

## 📝 Что делать дальше:

1. ✅ Выполните команду 1 → скопируйте результат в GitHub Secret `PROVISIONING_PROFILE_APP`
2. ✅ Выполните команду 2 → скопируйте результат в GitHub Secret `PROVISIONING_PROFILE_EXTENSION`
3. ✅ Проверьте что `APPLE_TEAM_ID` = `6CJVBBUGSN`
4. ✅ Запустите workflow

---

**Полная инструкция:** `docs/ПОШАГОВАЯ_ИНСТРУКЦИЯ_СОЗДАНИЯ_PROFILES.md`

