# 🔐 КАК СОЗДАТЬ СЕРТИФИКАТ APPLE DISTRIBUTION

**Дата:** 29 ноября 2025  
**Проблема:** Нужен сертификат "Apple Distribution" для создания App Store профилей

---

## 🎯 ЦЕЛЬ

Создать сертификат "Apple Distribution" через Keychain Access и загрузить его в Developer Portal.

---

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ

### Шаг 1: Открыть Keychain Access

1. **Открыть Spotlight:**
   - Нажать Cmd+Space
   - Ввести "Keychain Access"
   - Нажать Enter

2. **Или через Finder:**
   - Applications → Utilities → Keychain Access

---

### Шаг 2: Создать Certificate Signing Request (CSR)

1. **В Keychain Access:**
   - Меню: Keychain Access → Certificate Assistant → Request a Certificate From a Certificate Authority...

2. **Заполнить форму:**
   - **User Email Address:** `sergey21-02-84@list.ru`
   - **Common Name:** `Sergey Khlystov` (или ваше имя)
   - **CA Email Address:** оставить пустым
   - **Request is:** выбрать **"Saved to disk"** ✅
   - Нажать "Continue"

3. **Сохранить файл:**
   - Выбрать место сохранения (например, Desktop)
   - Имя файла: `CertificateSigningRequest.certSigningRequest`
   - Нажать "Save"

**Результат:**
- ✅ Файл CSR создан и сохранен на Desktop

---

### Шаг 3: Загрузить CSR в Developer Portal

1. **Открыть страницу создания сертификата:**
   - https://developer.apple.com/account/resources/certificates/list
   - Нажать "+" (Create a new certificate)

2. **Выбрать тип сертификата:**
   - Выбрать **"Apple Distribution"**
   - Нажать "Continue"

3. **Загрузить CSR:**
   - На странице "Upload a Certificate Signing Request"
   - Нажать "Choose File"
   - Выбрать файл `CertificateSigningRequest.certSigningRequest` (с Desktop)
   - Нажать "Continue"

4. **Скачать сертификат:**
   - После обработки появится кнопка "Download"
   - Нажать "Download"
   - Сохранить файл (например, `distribution.cer`)

**Результат:**
- ✅ Сертификат скачан

---

### Шаг 4: Установить сертификат в Keychain

1. **Двойной клик на файл сертификата:**
   - Найти файл `distribution.cer` в Finder
   - Двойной клик для открытия

2. **Сертификат установится автоматически:**
   - Откроется Keychain Access
   - Сертификат появится в разделе "My Certificates"

3. **Проверить установку:**
   - Открыть Keychain Access
   - В левом меню выбрать "My Certificates"
   - Найти "Apple Distribution: ..." (ваше имя)
   - Должен быть виден сертификат

**Результат:**
- ✅ Сертификат установлен в Keychain

---

### Шаг 5: Проверить в Developer Portal

1. **Открыть страницу сертификатов:**
   - https://developer.apple.com/account/resources/certificates/list

2. **Проверить список:**
   - Должен появиться сертификат "Apple Distribution"
   - Статус: "Active" (зеленый)

**Результат:**
- ✅ Сертификат создан и активен

---

## ✅ ПРОВЕРКА

### Что должно быть:

1. **В Keychain Access:**
   - ✅ Сертификат "Apple Distribution" в разделе "My Certificates"
   - ✅ Сертификат не истек

2. **В Developer Portal:**
   - ✅ Сертификат "Apple Distribution" в списке
   - ✅ Статус: "Active"

---

## 🎯 СЛЕДУЮЩИЙ ШАГ

После создания сертификата:
1. Вернуться к созданию App Store профилей
2. Теперь можно выбрать сертификат "Apple Distribution"

**Инструкция:** `docs/БЫСТРАЯ_ИНСТРУКЦИЯ_APP_STORE_PROFILES.md`

---

## ⚠️ ВАЖНО

- **CSR файл** нужен только для создания сертификата
- После создания сертификата CSR можно удалить
- **Сертификат** должен быть установлен в Keychain для работы

---

**Дата:** 29 ноября 2025  
**Инструкция:** Создание сертификата Apple Distribution

