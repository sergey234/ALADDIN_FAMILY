# ✅ ИСПРАВЛЕНИЕ PROVISIONING PROFILE UUID

**Дата:** 29 ноября 2025

---

## ❌ ПРОБЛЕМА

**Ошибка:**
```
No profile for team ' ***' matching 'family.aladdin.ios' found
```

**Причина:**
- Xcode не может найти provisioning profiles по `PROVISIONING_PROFILE_SPECIFIER="family.aladdin.ios"`
- Xcode ищет профили по UUID, а не по bundle ID
- Профили установлены, но не переименованы в формат `UUID.mobileprovision`

---

## ✅ РЕШЕНИЕ

1. **Извлечение UUID из профилей:**
   - После декодирования профилей извлекаем их UUID
   - Используем `security cms -D` для декодирования и `plutil` для извлечения UUID
   - Альтернативный способ: `strings` + `grep` для поиска UUID в бинарном файле

2. **Переименование файлов:**
   - Переименовываем профили в формат `UUID.mobileprovision`
   - Xcode автоматически находит профили по UUID в имени файла

3. **Использование UUID в xcodebuild:**
   - Используем `PROVISIONING_PROFILE_SPECIFIER` с UUID вместо bundle ID
   - Для каждого таргета отдельно: `ALADDIN_PROVISIONING_PROFILE_SPECIFIER` и `ALADDINPacketTunnel_PROVISIONING_PROFILE_SPECIFIER`

---

## 📋 ИЗМЕНЕНИЯ В WORKFLOW

### Шаг "Setup Provisioning Profiles":
- Декодирование профилей из base64
- Извлечение UUID из каждого профиля
- Переименование файлов в `UUID.mobileprovision`
- Сохранение UUID в переменные окружения

### Шаг "Build Archive":
- Использование UUID в `PROVISIONING_PROFILE_SPECIFIER`
- Отдельные UUID для каждого таргета
- Fallback на автоматический поиск, если UUID не извлечен

### Шаг "Export IPA":
- Использование UUID в `ExportOptions.plist`
- Правильное указание профилей для каждого bundle ID

---

## 🚀 СЛЕДУЮЩИЕ ШАГИ

1. ✅ Изменения закоммичены и отправлены в GitHub
2. ✅ Запустить workflow снова (создать тег `v1.0.4-build`)
3. ✅ Проверить логи на успешное извлечение UUID
4. ✅ Проверить успешную сборку с подписью

---

**Дата:** 29 ноября 2025  
**Статус:** ✅ Workflow исправлен, готов к повторному запуску

