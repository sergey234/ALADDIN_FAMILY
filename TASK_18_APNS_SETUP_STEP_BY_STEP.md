# 🔔 ЗАДАЧА 18: APNs SETUP - ПОШАГОВАЯ ИНСТРУКЦИЯ

**Дата:** 2026-02-09  
**Bundle ID:** `family.aladdin.ios`  
**Приоритет:** 🔥 КРИТИЧЕСКИЙ  
**Время выполнения:** 2-3 часа

---

## 📋 ОГЛАВЛЕНИЕ

1. [ПОДГОТОВКА (AI + Пользователь)](#1-подготовка)
2. [СОЗДАНИЕ APP ID И СЕРТИФИКАТОВ (Пользователь)](#2-создание-app-id-и-сертификатов-пользователь)
3. [КОНВЕРТАЦИЯ И ЗАГРУЗКА СЕРТИФИКАТОВ (Пользователь)](#3-конвертация-и-загрузка-сертификатов-пользователь)
4. [НАСТРОЙКА СЕРВЕРНОЙ ЧАСТИ (AI)](#4-настройка-серверной-части-ai)
5. [ТЕСТИРОВАНИЕ (AI + Пользователь)](#5-тестирование)

---

## 1. ПОДГОТОВКА

### ✅ ЧТО ДЕЛАЕТ AI:
- [x] Проверяет Info.plist - `remote-notification` в UIBackgroundModes ✅
- [x] Проверяет AppDelegate - обработка device token ✅
- [x] Проверяет NotificationManager - регистрация токена ✅
- [x] Проверяет APIService - метод `registerDeviceToken` ✅
- [x] Создает инструкцию (этот файл) ✅

### 📝 ЧТО ДЕЛАЕТ ПОЛЬЗОВАТЕЛЬ:
1. **Проверяет Apple Developer Account:**
   - Открывает: https://developer.apple.com/account
   - Входит в аккаунт
   - Убеждается, что аккаунт активен и оплачен

2. **Подготавливает Mac:**
   - Открывает Keychain Access (Приложения → Утилиты)
   - Готовит место для сохранения сертификатов (например, ~/Desktop/apns_certificates)

---

## 2. СОЗДАНИЕ APP ID И СЕРТИФИКАТОВ (Пользователь)

### 📝 ШАГ 2.1: Создание Certificate Signing Request (CSR)

**ВЫПОЛНЯЕТ ПОЛЬЗОВАТЕЛЬ:**

1. На Mac откройте **Keychain Access**
2. В меню: **Keychain Access** → **Certificate Assistant** → **Request a Certificate From a Certificate Authority**
3. Заполните форму:
   - **User Email Address:** Ваш email
   - **Common Name:** Ваше имя или название компании
   - **CA Email Address:** Оставьте пустым
   - **Request is:** Выберите **"Saved to disk"**
4. Нажмите **"Continue"**
5. Сохраните файл `CertificateSigningRequest.certSigningRequest` на рабочий стол

**✅ РЕЗУЛЬТАТ:** Файл CSR создан

---

### 📝 ШАГ 2.2: Создание App ID с Push Notifications

**ВЫПОЛНЯЕТ ПОЛЬЗОВАТЕЛЬ:**

1. Откройте: https://developer.apple.com/account
2. Перейдите в **"Certificates, Identifiers & Profiles"**
3. В левом меню выберите **"Identifiers"**
4. Нажмите кнопку **"+"** (создать новый)
5. Выберите **"App IDs"** → **"Continue"**
6. Выберите **"App"** → **"Continue"**
7. Заполните:
   - **Description:** `ALADDIN Family iOS App`
   - **Bundle ID:** `family.aladdin.ios` (Explicit)
8. В разделе **"Capabilities"**:
   - ✅ Отметьте **"Push Notifications"**
9. Нажмите **"Continue"** → **"Register"**

**✅ РЕЗУЛЬТАТ:** App ID создан с Push Notifications

---

### 📝 ШАГ 2.3: Создание Development Push Certificate

**ВЫПОЛНЯЕТ ПОЛЬЗОВАТЕЛЬ:**

1. В Apple Developer Portal перейдите в **"Certificates"**
2. Нажмите кнопку **"+"** (создать новый)
3. Выберите **"Apple Push Notification service SSL (Sandbox)"** → **"Continue"**
4. Выберите App ID: `family.aladdin.ios` → **"Continue"**
5. Нажмите **"Choose File"** → Выберите `CertificateSigningRequest.certSigningRequest`
6. Нажмите **"Continue"** → **"Download"**
7. Сохраните файл `aps_development.cer` на рабочий стол

**✅ РЕЗУЛЬТАТ:** Development сертификат скачан

---

### 📝 ШАГ 2.4: Создание Production Push Certificate

**ВЫПОЛНЯЕТ ПОЛЬЗОВАТЕЛЬ:**

1. В Apple Developer Portal в разделе **"Certificates"**
2. Нажмите кнопку **"+"** (создать новый)
3. Выберите **"Apple Push Notification service SSL (Production)"** → **"Continue"**
4. Выберите App ID: `family.aladdin.ios` → **"Continue"**
5. Нажмите **"Choose File"** → Выберите тот же `CertificateSigningRequest.certSigningRequest`
6. Нажмите **"Continue"** → **"Download"**
7. Сохраните файл `aps_production.cer` на рабочий стол

**✅ РЕЗУЛЬТАТ:** Production сертификат скачан

---

### 📝 ШАГ 2.5: Экспорт сертификатов в .p12 формат

**ВЫПОЛНЯЕТ ПОЛЬЗОВАТЕЛЬ:**

1. Дважды кликните на `aps_development.cer` → откроется в Keychain Access
2. Найдите сертификат в Keychain Access (обычно в "My Certificates")
3. Раскройте сертификат (стрелка слева) → увидите приватный ключ
4. Выберите **оба** (сертификат + ключ) → ПКМ → **"Export 2 items..."**
5. Сохраните как `apns_development.p12`
6. Введите пароль для .p12 файла (запомните его!)
7. Повторите для `aps_production.cer` → сохраните как `apns_production.p12`

**✅ РЕЗУЛЬТАТ:** Два .p12 файла созданы

---

## 3. КОНВЕРТАЦИЯ И ЗАГРУЗКА СЕРТИФИКАТОВ (Пользователь)

### 📝 ШАГ 3.1: Конвертация .p12 в .pem формат

**ВЫПОЛНЯЕТ ПОЛЬЗОВАТЕЛЬ:**

Откройте Terminal и выполните:

```bash
# Создайте директорию для сертификатов
mkdir -p ~/apns_certificates
cd ~/apns_certificates

# Конвертация Development сертификата
openssl pkcs12 -in ~/Desktop/apns_development.p12 -out apns_development.pem -nodes -clcerts
# Введите пароль от .p12 файла когда попросит

# Конвертация Production сертификата
openssl pkcs12 -in ~/Desktop/apns_production.p12 -out apns_production.pem -nodes -clcerts
# Введите пароль от .p12 файла когда попросит

# Проверка содержимого
cat apns_development.pem
cat apns_production.pem
```

**✅ РЕЗУЛЬТАТ:** Два .pem файла созданы

---

### 📝 ШАГ 3.2: Загрузка сертификатов на сервер

**ВЫПОЛНЯЕТ ПОЛЬЗОВАТЕЛЬ:**

В Terminal выполните:

```bash
# Загрузите Development сертификат
scp ~/apns_certificates/apns_development.pem root@149.154.65.180:/opt/aladdin-backend/certificates/
# Введите пароль: Sergio675

# Загрузите Production сертификат
scp ~/apns_certificates/apns_production.pem root@149.154.65.180:/opt/aladdin-backend/certificates/
# Введите пароль: Sergio675
```

**✅ РЕЗУЛЬТАТ:** Сертификаты загружены на сервер

---

### 📝 ШАГ 3.3: Настройка прав доступа на сервере

**ВЫПОЛНЯЕТ ПОЛЬЗОВАТЕЛЬ:**

Подключитесь к серверу и выполните:

```bash
ssh root@149.154.65.180
# Введите пароль: Sergio675

# Создайте директорию если не существует
mkdir -p /opt/aladdin-backend/certificates

# Установите правильные права
chmod 600 /opt/aladdin-backend/certificates/*.pem
chown root:root /opt/aladdin-backend/certificates/*.pem

# Проверьте что файлы на месте
ls -la /opt/aladdin-backend/certificates/
```

**✅ РЕЗУЛЬТАТ:** Сертификаты установлены с правильными правами

**📝 СООБЩИТЕ AI:** "Сертификаты загружены на сервер, можно переходить к шагу 4"

---

## 4. НАСТРОЙКА СЕРВЕРНОЙ ЧАСТИ (AI)

### ✅ ШАГ 4.1: Установка Python библиотеки для APNs

**ВЫПОЛНЯЕТ AI:**

```bash
# Подключение к серверу и установка библиотеки
ssh root@149.154.65.180
pip install PyAPNs2
# или
pip install python-apns
```

---

### ✅ ШАГ 4.2: Создание push_notification_service.py

**ВЫПОЛНЯЕТ AI:**

Создает файл `/opt/aladdin-backend/push_notification_service.py` с полной реализацией APNs сервиса.

---

### ✅ ШАГ 4.3: Создание endpoint для регистрации device token

**ВЫПОЛНЯЕТ AI:**

Проверяет наличие endpoint `/api/devices/register-ios` на сервере. Если нет - создает.

---

### ✅ ШАГ 4.4: Добавление endpoint для отправки push-уведомлений

**ВЫПОЛНЯЕТ AI:**

Добавляет endpoint `/api/notifications/push/send` в `notifications_router_extended.py`.

---

### ✅ ШАГ 4.5: Интеграция в main.py

**ВЫПОЛНЯЕТ AI:**

Проверяет что все импорты и роутеры подключены в `main.py`.

---

### ✅ ШАГ 4.6: Перезапуск сервера

**ВЫПОЛНЯЕТ AI:**

```bash
systemctl restart aladdin-backend
systemctl status aladdin-backend
```

**✅ РЕЗУЛЬТАТ:** Серверная часть настроена и работает

---

## 5. ТЕСТИРОВАНИЕ

### ✅ ШАГ 5.1: Проверка endpoint'ов (AI)

**ВЫПОЛНЯЕТ AI:**

```bash
# Проверка health endpoint
curl https://aladdin-ai.ru/api/notifications/health

# Проверка endpoint для регистрации device token
curl -X POST https://aladdin-ai.ru/api/devices/register-ios \
  -H "Content-Type: application/json" \
  -d '{"deviceToken": "test_token", "platform": "iOS", "appVersion": "1.0.0"}'
```

---

### 📝 ШАГ 5.2: Тестирование на реальном устройстве (Пользователь)

**ВЫПОЛНЯЕТ ПОЛЬЗОВАТЕЛЬ:**

1. **Откройте Xcode:**
   - Откройте проект ALADDIN_iOS
   - Подключите iPhone/iPad
   - Выберите устройство в схеме сборки

2. **Настройте Provisioning Profile:**
   - Xcode → Target → Signing & Capabilities
   - Убедитесь что выбран правильный Team
   - Xcode автоматически создаст/обновит Provisioning Profile с Push Notifications

3. **Запустите приложение:**
   - Нажмите Run (⌘R)
   - Приложение установится на устройство

4. **Проверьте регистрацию токена:**
   - Откройте приложение
   - Разрешите уведомления (если спросит)
   - Проверьте в Xcode Console - должен появиться device token
   - Проверьте на сервере - токен должен быть сохранен в базе данных

5. **Отправьте тестовое push-уведомление:**
   - Используйте endpoint `/api/notifications/push/send` (AI предоставит команду)
   - Проверьте что уведомление пришло на устройство

**✅ РЕЗУЛЬТАТ:** Push-уведомления работают!

---

## 📋 ЧЕКЛИСТ ВЫПОЛНЕНИЯ

### Пользователь:
- [ ] Шаг 2.1: CSR создан
- [ ] Шаг 2.2: App ID создан с Push Notifications
- [ ] Шаг 2.3: Development сертификат скачан
- [ ] Шаг 2.4: Production сертификат скачан
- [ ] Шаг 2.5: Сертификаты экспортированы в .p12
- [ ] Шаг 3.1: Сертификаты конвертированы в .pem
- [ ] Шаг 3.2: Сертификаты загружены на сервер
- [ ] Шаг 3.3: Права доступа настроены
- [ ] Шаг 5.2: Тестирование на устройстве выполнено

### AI:
- [x] Шаг 1: Подготовка и проверка iOS кода
- [ ] Шаг 4.1: Установка PyAPNs2
- [ ] Шаг 4.2: Создание push_notification_service.py
- [ ] Шаг 4.3: Проверка/создание endpoint для device token
- [ ] Шаг 4.4: Добавление endpoint для отправки push
- [ ] Шаг 4.5: Интеграция в main.py
- [ ] Шаг 4.6: Перезапуск сервера
- [ ] Шаг 5.1: Тестирование endpoint'ов

---

## 🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ

После выполнения всех шагов:
- ✅ APNs сертификаты настроены
- ✅ Серверная часть готова к отправке push-уведомлений
- ✅ iOS приложение регистрирует device token
- ✅ Push-уведомления работают на реальных устройствах

---

## 📞 КОНТАКТЫ И ПОДДЕРЖКА

Если возникли проблемы:
1. Проверьте логи сервера: `journalctl -u aladdin-backend -f`
2. Проверьте логи iOS приложения в Xcode Console
3. Проверьте что сертификаты не истекли в Apple Developer Portal

---

**✅ ГОТОВО К ВЫПОЛНЕНИЮ!**
