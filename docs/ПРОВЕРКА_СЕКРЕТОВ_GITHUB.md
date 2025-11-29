# ✅ ПРОВЕРКА СЕКРЕТОВ В GITHUB

**Цель:** Проверить, что все необходимые секреты настроены для загрузки в App Store Connect

---

## 🔑 НЕОБХОДИМЫЕ СЕКРЕТЫ

### Обязательные секреты для загрузки в App Store Connect:

1. **APP_STORE_CONNECT_API_KEY**
   - Содержимое .p8 файла (API ключ из App Store Connect)
   - Формат: многострочный текст (-----BEGIN PRIVATE KEY----- ... -----END PRIVATE KEY-----)

2. **APP_STORE_CONNECT_ISSUER_ID**
   - Issuer ID из App Store Connect
   - Формат: UUID (например: `12345678-1234-1234-1234-123456789012`)

3. **APP_STORE_CONNECT_API_KEY_ID**
   - Key ID из App Store Connect
   - Формат: строка (например: `ABC123DEF4`)

### Опциональные секреты (рекомендуется):

4. **APPLE_TEAM_ID**
   - Team ID: `6CJVBBUGSN`
   - Используется для автоматической подписи

---

## 📋 КАК ПРОВЕРИТЬ СЕКРЕТЫ

### Шаг 1: Открыть страницу секретов

1. **Откройте GitHub:**
   - https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions

2. **Проверьте наличие секретов:**
   - Должны быть видны все секреты (но не их значения)
   - Проверьте названия:
     - ✅ `APP_STORE_CONNECT_API_KEY`
     - ✅ `APP_STORE_CONNECT_ISSUER_ID`
     - ✅ `APP_STORE_CONNECT_API_KEY_ID`
     - ✅ `APPLE_TEAM_ID` (опционально)

### Шаг 2: Проверить через workflow

1. **Запустить тестовый workflow:**
   - Откройте: https://github.com/sergey234/ALADDIN_FAMILY/actions
   - Выберите: "Build and Upload to App Store"
   - Нажмите: "Run workflow"
   - Выберите ветку: `main` или `master`
   - Нажмите: "Run workflow"

2. **Проверить логи:**
   - Если секреты настроены правильно — сборка начнётся
   - Если секретов нет — будет ошибка: "APP_STORE_CONNECT_API_KEY secret is not set!"

---

## 🔍 ЧТО ПРОВЕРИТЬ

### Проверка 1: Названия секретов

Убедитесь, что названия секретов **точно совпадают** (регистр важен!):

- ✅ `APP_STORE_CONNECT_API_KEY` (правильно)
- ❌ `app_store_connect_api_key` (неправильно — маленькие буквы)
- ❌ `APP_STORE_CONNECT_APIKEY` (неправильно — без подчёркивания)

### Проверка 2: Формат APP_STORE_CONNECT_API_KEY

API ключ должен быть в формате .p8 файла:

```
-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg...
... (много строк) ...
-----END PRIVATE KEY-----
```

**Важно:**
- ✅ Должен начинаться с `-----BEGIN PRIVATE KEY-----`
- ✅ Должен заканчиваться `-----END PRIVATE KEY-----`
- ✅ Должен содержать все строки (не обрезан)

### Проверка 3: Формат APP_STORE_CONNECT_ISSUER_ID

Issuer ID должен быть UUID:

- ✅ `12345678-1234-1234-1234-123456789012` (правильно)
- ❌ `12345678-1234-1234-1234` (неправильно — неполный)
- ❌ `12345678123412341234123456789012` (неправильно — без дефисов)

### Проверка 4: Формат APP_STORE_CONNECT_API_KEY_ID

Key ID должен быть строкой:

- ✅ `ABC123DEF4` (правильно)
- ✅ `1234567890` (правильно)
- ❌ Пустая строка (неправильно)

---

## 🧪 ТЕСТОВЫЙ WORKFLOW ДЛЯ ПРОВЕРКИ

Создайте простой workflow для проверки секретов:

```yaml
name: Check Secrets

on:
  workflow_dispatch:

jobs:
  check-secrets:
    runs-on: ubuntu-latest
    steps:
      - name: Check APP_STORE_CONNECT_API_KEY
        run: |
          if [ -z "${{ secrets.APP_STORE_CONNECT_API_KEY }}" ]; then
            echo "❌ APP_STORE_CONNECT_API_KEY is not set"
            exit 1
          else
            echo "✅ APP_STORE_CONNECT_API_KEY is set"
            echo "Length: $(echo '${{ secrets.APP_STORE_CONNECT_API_KEY }}' | wc -c) characters"
          fi
      
      - name: Check APP_STORE_CONNECT_ISSUER_ID
        run: |
          if [ -z "${{ secrets.APP_STORE_CONNECT_ISSUER_ID }}" ]; then
            echo "❌ APP_STORE_CONNECT_ISSUER_ID is not set"
            exit 1
          else
            echo "✅ APP_STORE_CONNECT_ISSUER_ID is set"
            echo "Value: ${{ secrets.APP_STORE_CONNECT_ISSUER_ID }}"
          fi
      
      - name: Check APP_STORE_CONNECT_API_KEY_ID
        run: |
          if [ -z "${{ secrets.APP_STORE_CONNECT_API_KEY_ID }}" ]; then
            echo "❌ APP_STORE_CONNECT_API_KEY_ID is not set"
            exit 1
          else
            echo "✅ APP_STORE_CONNECT_API_KEY_ID is set"
            echo "Value: ${{ secrets.APP_STORE_CONNECT_API_KEY_ID }}"
          fi
      
      - name: Check APPLE_TEAM_ID
        run: |
          if [ -z "${{ secrets.APPLE_TEAM_ID }}" ]; then
            echo "⚠️ APPLE_TEAM_ID is not set (optional)"
          else
            echo "✅ APPLE_TEAM_ID is set"
            echo "Value: ${{ secrets.APPLE_TEAM_ID }}"
          fi
```

---

## ✅ ЧЕКЛИСТ ПРОВЕРКИ

### Обязательные секреты:

- [ ] `APP_STORE_CONNECT_API_KEY` — содержимое .p8 файла
- [ ] `APP_STORE_CONNECT_ISSUER_ID` — UUID из App Store Connect
- [ ] `APP_STORE_CONNECT_API_KEY_ID` — Key ID из App Store Connect

### Опциональные секреты:

- [ ] `APPLE_TEAM_ID` — Team ID: `6CJVBBUGSN`

### Проверка формата:

- [ ] `APP_STORE_CONNECT_API_KEY` начинается с `-----BEGIN PRIVATE KEY-----`
- [ ] `APP_STORE_CONNECT_API_KEY` заканчивается `-----END PRIVATE KEY-----`
- [ ] `APP_STORE_CONNECT_ISSUER_ID` в формате UUID
- [ ] `APP_STORE_CONNECT_API_KEY_ID` не пустой

---

## 🎯 ЧТО ДЕЛАТЬ ДАЛЬШЕ

### Если все секреты настроены:

1. ✅ **Запустить "Build and Upload to App Store" workflow**
2. ✅ **Дождаться завершения** (20-40 минут)
3. ✅ **Проверить результат** в App Store Connect

### Если секретов нет или они неправильные:

1. ✅ **Создать API ключ** в App Store Connect
2. ✅ **Добавить секреты** в GitHub
3. ✅ **Повторить проверку**

---

## 📝 ГДЕ НАЙТИ ЗНАЧЕНИЯ СЕКРЕТОВ

### APP_STORE_CONNECT_API_KEY:

1. App Store Connect → Users and Access → Keys
2. Найдите ваш ключ (или создайте новый)
3. Скачайте .p8 файл
4. Откройте файл в текстовом редакторе
5. Скопируйте всё содержимое (включая BEGIN и END строки)

### APP_STORE_CONNECT_ISSUER_ID:

1. App Store Connect → Users and Access → Keys
2. На той же странице найдите "Issuer ID"
3. Скопируйте UUID

### APP_STORE_CONNECT_API_KEY_ID:

1. App Store Connect → Users and Access → Keys
2. Найдите ваш ключ
3. Скопируйте "Key ID"

### APPLE_TEAM_ID:

- Значение: `6CJVBBUGSN`
- Или найдите в App Store Connect → Users and Access → Team

---

## ✅ ИТОГО

**Проверка секретов:**

1. ✅ Открыть: https://github.com/sergey234/ALADDIN_FAMILY/settings/secrets/actions
2. ✅ Проверить наличие всех секретов
3. ✅ Запустить workflow для проверки
4. ✅ Если всё правильно — использовать "Build and Upload to App Store" workflow

**Если секреты настроены правильно:**
- ✅ Можно использовать автоматическую загрузку
- ✅ Workflow "Build and Upload to App Store" будет работать
- ✅ Билд автоматически загрузится в App Store Connect

---

**Дата:** 28 ноября 2025  
**Инструкция:** Как проверить секреты в GitHub

