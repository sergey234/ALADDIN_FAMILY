# 🔄 АЛЬТЕРНАТИВНЫЕ РЕШЕНИЯ ДЛЯ PROVISIONING PROFILE

**Дата:** 2 декабря 2024  
**Проблема:** Xcode игнорирует Manual signing параметры из-за `CODE_SIGN_STYLE = Automatic` в `project.pbxproj`

---

## ✅ РЕШЕНИЕ 1: Изменить project.pbxproj (РЕКОМЕНДУЕТСЯ)

### Описание:
Изменить `CODE_SIGN_STYLE = Manual` в `project.pbxproj` для Release конфигурации.

### Плюсы:
- ✅ Гарантированно работает
- ✅ Минимальное изменение (только Release)
- ✅ Не влияет на Debug конфигурацию
- ✅ Постоянное решение

### Минусы:
- ❌ Требует изменения `project.pbxproj`
- ❌ Нужно коммитить изменения в репозиторий

### Как сделать:
```bash
# Найти и заменить для Release конфигурации
sed -i '' 's/CODE_SIGN_STYLE = Automatic;/CODE_SIGN_STYLE = Manual;/g' ALADDIN.xcodeproj/project.pbxproj
# Но нужно быть осторожным - заменит ВСЕ вхождения
```

**Более безопасный способ:**
Изменить только для Release конфигурации ALADDIN target (строки ~1267, ~1347).

---

## 🔄 РЕШЕНИЕ 2: Временное изменение project.pbxproj в CI

### Описание:
Использовать `sed` или `awk` для временного изменения `project.pbxproj` только в CI перед сборкой, затем вернуть обратно.

### Плюсы:
- ✅ Не требует коммита изменений в репозиторий
- ✅ Локальная разработка не затронута
- ✅ Работает в CI

### Минусы:
- ❌ Сложнее в реализации
- ❌ Нужно точно знать структуру project.pbxproj
- ❌ Риск сломать проект, если sed команда неверна

### Как сделать:
```bash
# В workflow перед сборкой:
# 1. Создать backup
cp ALADDIN.xcodeproj/project.pbxproj ALADDIN.xcodeproj/project.pbxproj.backup

# 2. Изменить только для Release конфигурации ALADDIN target
# Нужно найти точные строки для Release конфигурации
sed -i '' '/name = Release;/,/};/ s/CODE_SIGN_STYLE = Automatic;/CODE_SIGN_STYLE = Manual;/g' ALADDIN.xcodeproj/project.pbxproj

# 3. После сборки (в finally блоке):
# cp ALADDIN.xcodeproj/project.pbxproj.backup ALADDIN.xcodeproj/project.pbxproj
```

**Проблема:** `project.pbxproj` имеет сложную структуру, и `sed` может заменить не те строки.

---

## 🔄 РЕШЕНИЕ 3: Использовать App Store Connect API с Automatic Signing

### Описание:
Вместо Manual signing использовать Automatic signing с App Store Connect API ключами.

### Плюсы:
- ✅ Не требует изменения `project.pbxproj`
- ✅ Apple рекомендует этот подход
- ✅ Автоматическое управление профилями

### Минусы:
- ❌ Требует App Store Connect API ключи
- ❌ Может не работать в CI из-за "No Accounts" ошибки
- ❌ Менее предсказуемо, чем Manual signing

### Как сделать:
1. Создать App Store Connect API ключ
2. Добавить в GitHub Secrets:
   - `APP_STORE_CONNECT_API_KEY` (base64 .p8 файла)
   - `APP_STORE_CONNECT_ISSUER_ID`
   - `APP_STORE_CONNECT_API_KEY_ID`
3. Использовать `-allowProvisioningUpdates` в xcodebuild

**Проблема:** Мы уже пробовали это - не работает в CI из-за отсутствия Apple ID аккаунта.

---

## 🔄 РЕШЕНИЕ 4: Создать Release-CI конфигурацию

### Описание:
Создать новую конфигурацию `Release-CI` в Xcode с Manual signing, использовать её только в CI.

### Плюсы:
- ✅ Разделение CI и локальной разработки
- ✅ Release остается Automatic для локальной разработки

### Минусы:
- ❌ Требует изменения `project.pbxproj` (добавление новой конфигурации)
- ❌ Более сложная структура проекта
- ❌ Нужно настроить все targets для новой конфигурации

### Как сделать:
1. В Xcode: Project → Info → Configurations → + → Duplicate "Release" Configuration
2. Назвать "Release-CI"
3. Для Release-CI установить Manual signing
4. В workflow использовать `-configuration Release-CI`

**Проблема:** Все равно требует изменения `project.pbxproj`.

---

## 🔄 РЕШЕНИЕ 5: Использовать Python/Ruby скрипт для изменения project.pbxproj

### Описание:
Написать скрипт, который парсит `project.pbxproj` и изменяет только нужные строки для Release конфигурации.

### Плюсы:
- ✅ Более точное изменение (только нужные строки)
- ✅ Можно использовать в CI без коммита

### Минусы:
- ❌ Сложнее в реализации
- ❌ Нужно понимать структуру project.pbxproj
- ❌ Риск сломать проект

### Пример (Python):
```python
import re

with open('ALADDIN.xcodeproj/project.pbxproj', 'r') as f:
    content = f.read()

# Найти Release конфигурацию для ALADDIN target
# Изменить CODE_SIGN_STYLE = Automatic на Manual
pattern = r'(A100000F.*?name = Release;.*?CODE_SIGN_STYLE = )Automatic(;.*?name = Release;)'
replacement = r'\1Manual\2'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('ALADDIN.xcodeproj/project.pbxproj', 'w') as f:
    f.write(content)
```

---

## 🔄 РЕШЕНИЕ 6: Использовать Xcode Cloud или другой CI

### Описание:
Использовать Xcode Cloud, который лучше интегрирован с Apple Developer Portal.

### Плюсы:
- ✅ Нативная интеграция с Apple
- ✅ Автоматическое управление сертификатами и профилями
- ✅ Не требует изменения проекта

### Минусы:
- ❌ Требует миграции с GitHub Actions
- ❌ Другая система CI/CD
- ❌ Может быть дороже

---

## 📊 СРАВНЕНИЕ РЕШЕНИЙ

| Решение | Сложность | Надежность | Влияние на проект | Рекомендация |
|---------|-----------|------------|-------------------|--------------|
| 1. Изменить project.pbxproj | ⭐ Низкая | ⭐⭐⭐⭐⭐ Высокая | ⭐ Минимальное | ✅ **ЛУЧШЕЕ** |
| 2. Временное изменение в CI | ⭐⭐⭐ Средняя | ⭐⭐⭐ Средняя | ⭐ Нет | ⚠️ Рискованно |
| 3. App Store Connect API | ⭐⭐ Низкая | ⭐⭐ Низкая | ⭐ Нет | ❌ Не работает |
| 4. Release-CI конфигурация | ⭐⭐⭐ Средняя | ⭐⭐⭐⭐ Высокая | ⭐⭐ Среднее | ✅ Хорошо |
| 5. Python скрипт | ⭐⭐⭐⭐ Высокая | ⭐⭐⭐ Средняя | ⭐ Нет | ⚠️ Сложно |
| 6. Xcode Cloud | ⭐⭐ Низкая | ⭐⭐⭐⭐ Высокая | ⭐ Нет | ⚠️ Миграция |

---

## 🎯 РЕКОМЕНДАЦИЯ

### Для быстрого решения:
**РЕШЕНИЕ 1: Изменить project.pbxproj для Release конфигурации**

Это самое простое и надежное решение. Минимальное изменение, которое решит проблему навсегда.

### Если нельзя изменять project.pbxproj:
**РЕШЕНИЕ 2: Временное изменение в CI**

Но нужно быть очень осторожным с `sed` командами, чтобы не сломать проект.

### Для долгосрочного решения:
**РЕШЕНИЕ 4: Release-CI конфигурация**

Разделение CI и локальной разработки, но все равно требует изменения `project.pbxproj`.

---

## 💡 ВЫВОД

**Все решения, кроме миграции на Xcode Cloud, так или иначе требуют изменения `project.pbxproj`.**

**Самое простое и надежное решение - изменить `CODE_SIGN_STYLE = Manual` для Release конфигурации напрямую в `project.pbxproj`.**

---

**Дата:** 2 декабря 2024

