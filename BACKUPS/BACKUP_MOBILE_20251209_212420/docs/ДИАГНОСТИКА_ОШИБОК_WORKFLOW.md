# 🔍 ДИАГНОСТИКА: Почему workflow падает с ошибкой

## ✅ ЧТО РАБОТАЕТ

1. ✅ **Workflow запускается** - API возвращает HTTP 204 (успех)
2. ✅ **Workflow виден в GitHub** - файл распознается
3. ✅ **Токен работает** - запросы проходят успешно

## ❌ ПРОБЛЕМА

**Все запуски завершаются с ошибкой (failure)**

Последние запуски:
- ❌ #137 - failure
- ❌ #136 - failure  
- ❌ #135 - failure

## 🔍 КАК ПРОВЕРИТЬ ОШИБКИ

### Способ 1: Через GitHub UI (самый простой)

1. Откройте последний запуск:
   ```
   https://github.com/sergey234/ALADDIN_FAMILY/actions/runs/19818187324
   ```

2. **Что искать:**
   - Красный крестик ❌ рядом с названием job
   - Шаг, на котором упал workflow
   - Детальные логи ошибки

3. **Откройте упавший шаг:**
   - Нажмите на шаг с ошибкой
   - Прокрутите логи вниз
   - Найдите строку с "Error:" или "❌"

### Способ 2: Через скрипты

**Проверить статус:**
```bash
./проверить_статус.sh
```

**Запустить и проверить:**
```bash
./логи_workflow.sh
```

## 🎯 ТИПИЧНЫЕ ОШИБКИ

### 1. Отсутствуют секреты
**Ошибка:** `Secret not found` или `required input is missing`

**Решение:**
- Проверьте GitHub Secrets: `Settings` → `Secrets and variables` → `Actions`
- Нужные секреты:
  - `APPLE_TEAM_ID`
  - `IOS_DISTRIBUTION_CERTIFICATE`
  - `IOS_DISTRIBUTION_CERTIFICATE_PASSWORD`
  - `PROVISIONING_PROFILE_APP`
  - `PROVISIONING_PROFILE_EXTENSION`

### 2. Ошибка сборки Xcode
**Ошибка:** `xcodebuild failed` или `Code signing error`

**Решение:**
- Проверьте сертификаты и профили
- Убедитесь, что профили App Store Distribution (не Development)
- Проверьте Bundle ID

### 3. Ошибка экспорта IPA
**Ошибка:** `Export failed` или `Invalid provisioning profile`

**Решение:**
- Проверьте ExportOptions.plist
- Убедитесь, что профили правильные
- Проверьте UUID профилей

### 4. Ошибка загрузки в App Store Connect
**Ошибка:** `Upload failed` или `API key invalid`

**Решение:**
- Проверьте App Store Connect API ключи
- Или используйте ручную загрузку через Transporter

## 📋 ЧЕКЛИСТ ДИАГНОСТИКИ

- [ ] Открыл последний запуск в GitHub UI
- [ ] Нашел шаг с ошибкой
- [ ] Прочитал детальные логи
- [ ] Проверил GitHub Secrets
- [ ] Проверил сертификаты и профили
- [ ] Проверил Bundle ID

## 🔗 ПРЯМЫЕ ССЫЛКИ

**Последний запуск:**
```
https://github.com/sergey234/ALADDIN_FAMILY/actions/runs/19818187324
```

**Все запуски:**
```
https://github.com/sergey234/ALADDIN_FAMILY/actions/workflows/appstore.yml
```

**Настройки Secrets:**
```
https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
```

## 💡 РЕКОМЕНДАЦИЯ

**Откройте последний запуск в GitHub UI** - там будут детальные логи с указанием точной ошибки:
```
https://github.com/sergey234/ALADDIN_FAMILY/actions/runs/19818187324
```

Это самый быстрый способ понять, в чем проблема!

