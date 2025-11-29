# 🔐 ЧТО ТАКОЕ KEY И CSR

**Дата:** 29 ноября 2025

---

## 📋 ФАЙЛЫ НА DESKTOP

### 1️⃣ `CertificateSigningRequest.certSigningRequest` (CSR)
- ✅ **Это нужно загрузить в Developer Portal**
- ✅ Это запрос на создание сертификата
- ✅ Безопасно отправлять в Apple

### 2️⃣ `ALADDIN_Distribution.key` (Приватный ключ)
- ⚠️ **НЕ загружайте этот файл никуда!**
- ⚠️ Это ваш приватный ключ - храните в секрете!
- ⚠️ Нужен для установки сертификата позже

---

## 🎯 ЧТО ДЕЛАТЬ

### Шаг 1: Загрузить CSR в Developer Portal

1. Откройте: https://developer.apple.com/account/resources/certificates/list
2. Нажмите "+"
3. Выберите "Apple Distribution"
4. Нажмите "Choose File"
5. **Выберите:** `CertificateSigningRequest.certSigningRequest` ✅
6. **НЕ выбирайте:** `ALADDIN_Distribution.key` ❌

---

### Шаг 2: Сохранить приватный ключ

1. **Приватный ключ (`ALADDIN_Distribution.key`) нужен для установки сертификата**
2. Когда скачаете сертификат от Apple (`distribution.cer`), он будет работать с этим ключом
3. **Не удаляйте** файл `ALADDIN_Distribution.key` - он нужен!

---

## ✅ ИТОГО

- **CSR** → загрузить в Developer Portal
- **KEY** → сохранить, не удалять, не загружать никуда

---

**Дата:** 29 ноября 2025  
**Важно:** Загружайте только CSR, не KEY!

