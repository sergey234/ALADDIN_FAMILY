# 🔔 ЗАДАЧА 18: APNs SETUP - ПОЛНЫЙ АЛГОРИТМ

**Дата:** 2026-02-09  
**Bundle ID:** `family.aladdin.ios`  
**Статус:** ✅ Готово к выполнению

---

## 📋 СОДЕРЖАНИЕ

1. [ПОДГОТОВКА](#1-подготовка)
2. [СОЗДАНИЕ CSR](#2-создание-csr)
3. [СОЗДАНИЕ APP ID](#3-создание-app-id)
4. [СОЗДАНИЕ СЕРТИФИКАТОВ](#4-создание-сертификатов)
5. [ЭКСПОРТ В P12](#5-экспорт-в-p12)
6. [КОНВЕРТАЦИЯ В PEM](#6-конвертация-в-pem)
7. [ЗАГРУЗКА НА СЕРВЕР](#7-загрузка-на-сервер)
8. [НАСТРОЙКА СЕРВЕРА](#8-настройка-сервера)
9. [ТЕСТИРОВАНИЕ](#9-тестирование)

---

## 1. ПОДГОТОВКА

### ✅ AI УЖЕ СДЕЛАЛ:
- [x] Проверил Info.plist - `remote-notification` в UIBackgroundModes ✅
- [x] Проверил AppDelegate - обработка device token ✅
- [x] Проверил NotificationManager - регистрация токена ✅
- [x] Проверил APIService - метод `registerDeviceToken` ✅
- [x] Создал `push_notification_service.py` ✅
- [x] Добавил endpoint `/api/notifications/push/send` ✅

### 📝 ВАМ НУЖНО:
1. Открыть https://developer.apple.com/account
2. Войти в Apple Developer Account
3. Убедиться что аккаунт активен и оплачен

---

## 2. СОЗДАНИЕ CSR

### Шаг 2.1: Открыть Keychain Access
1. Finder → Приложения → Утилиты → Keychain Access
2. Или ⌘+Space → ввести "Keychain Access"

### Шаг 2.2: Создать Certificate Signing Request
1. В меню: **Keychain Access** → **Certificate Assistant** → **Request a Certificate From a Certificate Authority...**
2. Заполнить форму:
   - **User Email Address:** ваш email
   - **Common Name:** ваше имя или название компании
   - **CA Email Address:** оставить пустым
   - **Request is:** выбрать **"Saved to disk"**
3. Нажать **"Continue"**
4. Выбрать место сохранения: **Desktop** (Рабочий стол)
5. Нажать **"Save"**
6. Файл сохранится как: `CertificateSigningRequest.certSigningRequest`

**✅ РЕЗУЛЬТАТ:** CSR файл создан на рабочем столе

---

## 3. СОЗДАНИЕ APP ID

### Шаг 3.1: Перейти в Apple Developer Portal
1. Открыть: https://developer.apple.com/account
2. Перейти: **Certificates, IDs & Profiles** → **Identifiers**

### Шаг 3.2: Создать новый App ID
1. Нажать кнопку **"+"** (создать новый)
2. Выбрать **"App IDs"** → **"Continue"**
3. Выбрать **"App"** → **"Continue"**
4. Заполнить:
   - **Description:** `ALADDIN Family iOS App`
   - **Bundle ID:** `family.aladdin.ios` (Explicit)
5. В разделе **"Capabilities"**:
   - ✅ Отметить **"Push Notifications"**
6. Нажать **"Continue"** → **"Register"**

**✅ РЕЗУЛЬТАТ:** App ID создан с Push Notifications capability

---

## 4. СОЗДАНИЕ СЕРТИФИКАТОВ

### Шаг 4.1: Перейти в раздел Certificates
1. В Apple Developer Portal: **Certificates, IDs & Profiles** → **Certificates**
2. Нажать кнопку **"+"** (создать новый)

### Шаг 4.2: Создать Development сертификат
1. Выбрать: **Services** → **Apple Push Notification service SSL (Sandbox)**
2. Нажать **"Continue"**
3. Выбрать App ID: `family.aladdin.ios` → **"Continue"**
4. Нажать **"Choose File"**
5. Выбрать файл: `CertificateSigningRequest.certSigningRequest` (с рабочего стола)
6. Нажать **"Continue"** → **"Download"**
7. Сохранить файл: `aps_development.cer` на рабочий стол

**✅ РЕЗУЛЬТАТ:** Development сертификат скачан

### Шаг 4.3: Создать Production сертификат
1. В разделе **Certificates** снова нажать **"+"**
2. Выбрать: **Services** → **Apple Push Notification service SSL (Sandbox & Production)**
3. Нажать **"Continue"**
4. Выбрать App ID: `family.aladdin.ios` → **"Continue"**
5. Нажать **"Choose File"**
6. Выбрать тот же файл: `CertificateSigningRequest.certSigningRequest`
7. Нажать **"Continue"** → **"Download"**
8. Сохранить файл: `aps_production.cer` на рабочий стол

**✅ РЕЗУЛЬТАТ:** Production сертификат скачан

---

## 5. ЭКСПОРТ В P12

### Шаг 5.1: Установить Development сертификат
1. Дважды кликнуть на `aps_development.cer` → откроется в Keychain Access
2. Сертификат появится в разделе **"My Certificates"**

### Шаг 5.2: Экспортировать Development сертификат
1. В Keychain Access найти сертификат (обычно называется "Apple Push Services: family.aladdin.ios")
2. Раскрыть сертификат (стрелка слева) → увидеть приватный ключ
3. Выбрать **оба** (сертификат + ключ) → ПКМ → **"Export 2 items..."**
4. Сохранить как: `apns_development.p12`
5. Ввести пароль для .p12 файла (запомнить его!)
6. Нажать **"Save"**

**✅ РЕЗУЛЬТАТ:** Development сертификат экспортирован в .p12

### Шаг 5.3: Установить и экспортировать Production сертификат
1. Дважды кликнуть на `aps_production.cer` → откроется в Keychain Access
2. Повторить шаги 5.2 для Production сертификата
3. Сохранить как: `apns_production.p12`
4. Ввести пароль (можно тот же или другой)

**✅ РЕЗУЛЬТАТ:** Production сертификат экспортирован в .p12

---

## 6. КОНВЕРТАЦИЯ В PEM

### Шаг 6.1: Создать директорию для сертификатов
Откройте Terminal и выполните:

```bash
mkdir -p ~/apns_certificates
cd ~/apns_certificates
```

### Шаг 6.2: Конвертировать Development сертификат
```bash
openssl pkcs12 -in ~/Desktop/apns_development.p12 -out apns_development.pem -nodes -clcerts
```

**Важно:** Когда попросит, введите пароль от .p12 файла

### Шаг 6.3: Конвертировать Production сертификат
```bash
openssl pkcs12 -in ~/Desktop/apns_production.p12 -out apns_production.pem -nodes -clcerts
```

**Важно:** Когда попросит, введите пароль от .p12 файла

### Шаг 6.4: Проверить содержимое
```bash
cat apns_development.pem
cat apns_production.pem
```

Должны увидеть содержимое сертификатов (BEGIN CERTIFICATE... END CERTIFICATE)

**✅ РЕЗУЛЬТАТ:** Два .pem файла созданы в `~/apns_certificates/`

---

## 7. ЗАГРУЗКА НА СЕРВЕР

### Шаг 7.1: Загрузить Development сертификат
```bash
scp ~/apns_certificates/apns_development.pem root@149.154.65.180:/opt/aladdin-backend/certificates/
```

**Пароль:** `Sergio675`

### Шаг 7.2: Загрузить Production сертификат
```bash
scp ~/apns_certificates/apns_production.pem root@149.154.65.180:/opt/aladdin-backend/certificates/
```

**Пароль:** `Sergio675`

### Шаг 7.3: Настроить права доступа
```bash
ssh root@149.154.65.180
# Пароль: Sergio675

# Создать директорию если не существует
mkdir -p /opt/aladdin-backend/certificates

# Установить правильные права
chmod 600 /opt/aladdin-backend/certificates/*.pem
chown root:root /opt/aladdin-backend/certificates/*.pem

# Проверить что файлы на месте
ls -la /opt/aladdin-backend/certificates/
```

Должны увидеть:
- `apns_development.pem`
- `apns_production.pem`

**✅ РЕЗУЛЬТАТ:** Сертификаты загружены на сервер с правильными правами

**📝 СООБЩИТЕ AI:** "Сертификаты загружены на сервер, можно переходить к шагу 8"

---

## 8. НАСТРОЙКА СЕРВЕРА

### ✅ Шаг 8.1: Установка PyAPNs2 (AI выполняет)
```bash
ssh root@149.154.65.180
pip install PyAPNs2
# или
pip install python-apns
```

### ✅ Шаг 8.2: Загрузка push_notification_service.py (AI выполняет)
```bash
# AI загрузит файл push_notification_service.py на сервер
scp push_notification_service.py root@149.154.65.180:/opt/aladdin-backend/
```

### ✅ Шаг 8.3: Проверка endpoint для device token (AI выполняет)
```bash
# Проверить что endpoint /api/devices/register-ios существует
curl https://aladdin-ai.ru/api/devices/register-ios
```

### ✅ Шаг 8.4: Интеграция push endpoint (AI выполняет)
Endpoint `/api/notifications/push/send` уже добавлен в `notifications_router_extended.py`

### ✅ Шаг 8.5: Обновление main.py (AI выполняет)
Проверить что `notifications_router` подключен в `main.py`

### ✅ Шаг 8.6: Перезапуск сервера (AI выполняет)
```bash
systemctl restart aladdin-backend
systemctl status aladdin-backend
```

**✅ РЕЗУЛЬТАТ:** Серверная часть настроена и работает

---

## 9. ТЕСТИРОВАНИЕ

### ✅ Шаг 9.1: Проверка endpoint'ов (AI выполняет)

#### Проверка health endpoint:
```bash
curl https://aladdin-ai.ru/api/notifications/health
```

#### Проверка endpoint для регистрации device token:
```bash
curl -X POST https://aladdin-ai.ru/api/devices/register-ios \
  -H "Content-Type: application/json" \
  -d '{
    "deviceToken": "test_token_12345",
    "platform": "iOS",
    "appVersion": "1.0.0"
  }'
```

#### Проверка endpoint для отправки push:
```bash
curl -X POST "https://aladdin-ai.ru/api/notifications/push/send?device_token=TEST_TOKEN&message=Test%20notification&use_sandbox=true"
```

### 📝 Шаг 9.2: Тестирование на реальном устройстве (ВЫ выполняете)

#### 9.2.1: Открыть Xcode
1. Открыть проект ALADDIN_iOS в Xcode
2. Подключить iPhone/iPad через USB

#### 9.2.2: Настроить Provisioning Profile
1. Xcode → Target → **Signing & Capabilities**
2. Убедиться что выбран правильный **Team**
3. Xcode автоматически создаст/обновит Provisioning Profile с Push Notifications
4. Проверить что Bundle Identifier: `family.aladdin.ios`

#### 9.2.3: Запустить приложение
1. Выбрать подключенное устройство в схеме сборки
2. Нажать **Run** (⌘R)
3. Приложение установится на устройство

#### 9.2.4: Проверить регистрацию токена
1. Открыть приложение на устройстве
2. Разрешить уведомления (если спросит)
3. Открыть Xcode Console (⌘⇧Y)
4. Найти строку с device token (обычно начинается с "📱 Register device token" или "Device token:")
5. Скопировать device token

#### 9.2.5: Отправить тестовое push-уведомление
AI отправит тестовое push используя скопированный device token:

```bash
curl -X POST "https://aladdin-ai.ru/api/notifications/push/send?device_token=ВАШ_DEVICE_TOKEN&message=Тестовое%20уведомление&title=ALADDIN%20Test&use_sandbox=true"
```

**✅ РЕЗУЛЬТАТ:** Push-уведомление должно прийти на устройство!

---

## ✅ ФИНАЛЬНЫЙ ЧЕКЛИСТ

### ВЫ ВЫПОЛНИЛИ:
- [ ] Шаг 2: CSR создан
- [ ] Шаг 3: App ID создан с Push Notifications
- [ ] Шаг 4.2: Development сертификат скачан
- [ ] Шаг 4.3: Production сертификат скачан
- [ ] Шаг 5: Сертификаты экспортированы в .p12
- [ ] Шаг 6: Сертификаты конвертированы в .pem
- [ ] Шаг 7: Сертификаты загружены на сервер
- [ ] Шаг 9.2: Тестирование на устройстве выполнено

### AI ВЫПОЛНИЛ:
- [x] Шаг 1: Подготовка iOS кода
- [x] Создание push_notification_service.py
- [x] Добавление endpoint для push
- [ ] Шаг 8: Установка PyAPNs2
- [ ] Шаг 8: Загрузка файлов на сервер
- [ ] Шаг 8: Перезапуск сервера
- [ ] Шаг 9.1: Тестирование endpoint'ов

---

## 🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ

После выполнения всех шагов:
- ✅ APNs сертификаты настроены
- ✅ Серверная часть готова к отправке push-уведомлений
- ✅ iOS приложение регистрирует device token
- ✅ Push-уведомления работают на реальных устройствах

---

## 📞 ПОДДЕРЖКА

Если возникли проблемы:
1. Проверьте логи сервера: `journalctl -u aladdin-backend -f`
2. Проверьте логи iOS приложения в Xcode Console
3. Проверьте что сертификаты не истекли в Apple Developer Portal
4. Проверьте что Bundle ID совпадает: `family.aladdin.ios`

---

**✅ АЛГОРИТМ ГОТОВ К ВЫПОЛНЕНИЮ!**
