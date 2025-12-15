# 🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: CODE_SIGN_IDENTITY

**Дата:** 2 декабря 2024  
**Проблема:** Xcode все еще не находит provisioning profiles, несмотря на `CODE_SIGN_STYLE = Manual`

---

## 🔍 ОБНАРУЖЕННАЯ ПРОБЛЕМА

После изменения `CODE_SIGN_STYLE = Manual` в `project.pbxproj`, ошибка все еще сохранялась.

### Анализ показал:

1. **ALADDIN Release:**
   - `CODE_SIGN_IDENTITY = "Apple Development"` ❌ (неправильно для App Store Distribution)
   - Должно быть: `CODE_SIGN_IDENTITY = "Apple Distribution"` ✅

2. **ALADDINPacketTunnel Release:**
   - `CODE_SIGN_IDENTITY = "iPhone Developer"` ❌ (неправильно для App Store Distribution)
   - Должно быть: `CODE_SIGN_IDENTITY = "Apple Distribution"` ✅
   - `PROVISIONING_PROFILE_SPECIFIER` отсутствовал ❌
   - Должен быть: `PROVISIONING_PROFILE_SPECIFIER = "";` ✅

---

## ✅ ИСПРАВЛЕНИЯ

### 1. ALADDIN Release (A100000F)
```diff
- CODE_SIGN_IDENTITY = "Apple Development";
+ CODE_SIGN_IDENTITY = "Apple Distribution";
  CODE_SIGN_STYLE = Manual;
```

### 2. ALADDINPacketTunnel Release (C0F3001C)
```diff
- CODE_SIGN_IDENTITY = "iPhone Developer";
+ CODE_SIGN_IDENTITY = "Apple Distribution";
  CODE_SIGN_STYLE = Manual;
+ PROVISIONING_PROFILE_SPECIFIER = "";
```

---

## 📊 РАЗНИЦА МЕЖДУ СЕРТИФИКАТАМИ

| Сертификат | Использование | Для чего |
|------------|---------------|----------|
| **Apple Development** | Локальная разработка, Debug | Тестирование на устройствах разработчика |
| **Apple Distribution** | App Store, Release | Публикация в App Store, TestFlight |
| **iPhone Developer** | Устаревший | Старый формат, не рекомендуется |

---

## 🎯 ПОЧЕМУ ЭТО ВАЖНО

**Xcode использует `CODE_SIGN_IDENTITY` для:**
1. Поиска правильного сертификата в keychain
2. Сопоставления сертификата с provisioning profile
3. Определения типа подписи (Development vs Distribution)

**Если `CODE_SIGN_IDENTITY` не совпадает с сертификатом:**
- Xcode не может найти правильный сертификат
- Provisioning profile не может быть сопоставлен
- Результат: ошибка "requires a provisioning profile"

---

## ✅ ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После этих изменений:
1. ✅ Xcode найдет правильный сертификат (`Apple Distribution`)
2. ✅ Provisioning profiles будут сопоставлены с сертификатом
3. ✅ Manual signing должен работать корректно

---

**Дата:** 2 декабря 2024  
**Статус:** ✅ Исправления применены

