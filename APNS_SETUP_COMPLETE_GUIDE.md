# 🔔 ПОЛНАЯ ИНСТРУКЦИЯ ПО НАСТРОЙКЕ APNs (Apple Push Notification service)

**Дата создания:** 10 февраля 2026 г.  
**Bundle ID:** `family.aladdin.ios`  
**Приоритет:** 🔥 КРИТИЧЕСКИЙ  
**Время выполнения:** 2-3 часа

---

## 📋 ОГЛАВЛЕНИЕ

1. [Подготовка](#подготовка)
2. [Создание App ID с Push Notifications](#создание-app-id)
3. [Генерация сертификатов](#генерация-сертификатов)
4. [Создание Provisioning Profiles](#создание-provisioning-profiles)
5. [Установка сертификатов на сервер](#установка-на-сервер)
6. [Настройка серверной части](#настройка-серверной-части)
7. [Тестирование](#тестирование)
8. [Проверка и валидация](#проверка)

---

## 🎯 ПОДГОТОВКА

### Что нужно иметь:

1. ✅ **Apple Developer Account** (активный, оплаченный)
   - Ссылка: https://developer.apple.com/account
   - Проверка: Войти и убедиться, что аккаунт активен

2. ✅ **Bundle ID приложения**
   - Текущий: `family.aladdin.ios`
   - Проверка: В Xcode → Target → General → Bundle Identifier

3. ✅ **Доступ к серверу**
   - Сервер: `root@149.154.65.180`
   - Пароль: `Sergio675`
   - Проверка: `ssh root@149.154.65.180`

4. ✅ **macOS с Keychain Access**
   - Для работы с сертификатами

---

## 📱 ШАГ 1: СОЗДАНИЕ APP ID С PUSH NOTIFICATIONS

### 1.1 Вход в Apple Developer Portal

1. Откройте: https://developer.apple.com/account
2. Войдите в свой Apple Developer аккаунт
3. Перейдите в раздел **"Certificates, Identifiers & Profiles"**

### 1.2 Проверка существующего App ID

1. В левом меню выберите **"Identifiers"**
2. Найдите или создайте App ID: `family.aladdin.ios`
3. Если App ID уже существует:
   - Нажмите на него
   - Проверьте, включена ли опция **"Push Notifications"**
   - Если НЕТ → нажмите **"Edit"** → включите **"Push Notifications"** → **"Save"**

### 1.3 Создание нового App ID (если не существует)

1. Нажмите кнопку **"+"** (создать новый)
2. Выберите **"App IDs"** → **"Continue"**
3. Выберите **"App"** → **"Continue"**
4. Заполните:
   - **Description:** `ALADDIN Family iOS App`
   - **Bundle ID:** `family.aladdin.ios` (Explicit)
5. В разделе **"Capabilities"**:
   - ✅ Отметьте **"Push Notifications"**
   - ✅ Отметьте другие необходимые capabilities (если нужно)
6. Нажмите **"Continue"** → **"Register"**

**Результат:** App ID создан с включенной Push Notifications capability

---

## 🔐 ШАГ 2: ГЕНЕРАЦИЯ СЕРТИФИКАТОВ

### 2.1 Создание Certificate Signing Request (CSR)

1. На Mac откройте **"Keychain Access"** (Приложения → Утилиты)
2. В меню выберите **"Keychain Access"** → **"Certificate Assistant"** → **"Request a Certificate From a Certificate Authority"**
3. Заполните форму:
   - **User Email Address:** Ваш email (например, sergio@example.com)
   - **Common Name:** Ваше имя или название компании
   - **CA Email Address:** Оставьте пустым
   - **Request is:** Выберите **"Saved to disk"**
4. Нажмите **"Continue"** → Сохраните файл `CertificateSigningRequest.certSigningRequest` на рабочий стол

**Результат:** Файл CSR создан и сохранен

### 2.2 Создание Development Push Certificate

1. В Apple Developer Portal перейдите в **"Certificates"**
2. Нажмите кнопку **"+"** (создать новый)
3. Выберите **"Apple Push Notification service SSL (Sandbox)"** → **"Continue"**
4. Выберите App ID: `family.aladdin.ios` → **"Continue"**
5. Нажмите **"Choose File"** → Выберите созданный `CertificateSigningRequest.certSigningRequest`
6. Нажмите **"Continue"** → **"Download"**
7. Сохраните файл `aps_development.cer` на рабочий стол

**Результат:** Development Push Certificate скачан

### 2.3 Создание Production Push Certificate

1. В Apple Developer Portal в разделе **"Certificates"**
2. Нажмите кнопку **"+"** (создать новый)
3. Выберите **"Apple Push Notification service SSL (Sandbox & Production)"** → **"Continue"**
4. Выберите App ID: `family.aladdin.ios` → **"Continue"**
5. Нажмите **"Choose File"** → Выберите тот же `CertificateSigningRequest.certSigningRequest`
6. Нажмите **"Continue"** → **"Download"**
7. Сохраните файл `aps_production.cer` на рабочий стол

**Результат:** Production Push Certificate скачан

### 2.4 Установка сертификатов в Keychain

1. Дважды кликните на `aps_development.cer` → Откроется Keychain Access
2. Убедитесь, что сертификат установлен в **"login"** keychain
3. Дважды кликните на `aps_production.cer` → Установите в Keychain
4. В Keychain Access найдите сертификаты:
   - `Apple Development iOS Push Services: family.aladdin.ios` (Development)
   - `Apple Production iOS Push Services: family.aladdin.ios` (Production)

**Результат:** Сертификаты установлены в Keychain

### 2.5 Экспорт сертификатов в .p12 формат

#### Для Development сертификата:

1. В Keychain Access найдите: `Apple Development iOS Push Services: family.aladdin.ios`
2. Раскройте сертификат (стрелка слева)
3. Вы увидите приватный ключ под сертификатом
4. Выберите **оба** (сертификат + ключ) → Правый клик → **"Export 2 items"**
5. Сохраните как: `apns_development.p12`
6. Введите пароль для .p12 файла (запомните его!)
7. Нажмите **"OK"**

#### Для Production сертификата:

1. В Keychain Access найдите: `Apple Production iOS Push Services: family.aladdin.ios`
2. Раскройте сертификат
3. Выберите сертификат + приватный ключ → Правый клик → **"Export 2 items"**
4. Сохраните как: `apns_production.p12`
5. Введите пароль для .p12 файла (запомните его!)
6. Нажмите **"OK"**

**Результат:** Два .p12 файла созданы:
- `apns_development.p12` (для тестирования)
- `apns_production.p12` (для продакшена)

---

## 📋 ШАГ 3: СОЗДАНИЕ PROVISIONING PROFILES

### 3.1 Development Provisioning Profile

1. В Apple Developer Portal перейдите в **"Profiles"**
2. Нажмите кнопку **"+"** (создать новый)
3. Выберите **"iOS App Development"** → **"Continue"**
4. Выберите App ID: `family.aladdin.ios` → **"Continue"**
5. Выберите сертификаты разработчика → **"Continue"**
6. Выберите устройства для тестирования → **"Continue"**
7. Введите имя профиля: `ALADDIN Development` → **"Generate"**
8. Нажмите **"Download"** → Сохраните файл

**Результат:** Development Provisioning Profile скачан

### 3.2 Production Provisioning Profile (App Store)

1. В разделе **"Profiles"** нажмите **"+"**
2. Выберите **"App Store"** → **"Continue"**
3. Выберите App ID: `family.aladdin.ios` → **"Continue"**
4. Выберите сертификат для App Store → **"Continue"**
5. Введите имя профиля: `ALADDIN App Store` → **"Generate"**
6. Нажмите **"Download"** → Сохраните файл

**Результат:** Production Provisioning Profile скачан

### 3.3 Установка Provisioning Profiles в Xcode

1. Дважды кликните на скачанные `.mobileprovision` файлы
2. Они автоматически установятся в Xcode
3. В Xcode: **Preferences** → **Accounts** → Выберите ваш Apple ID → **Download Manual Profiles**
4. В проекте: **Target** → **Signing & Capabilities** → Выберите соответствующий профиль

**Результат:** Provisioning Profiles установлены

---

## 🖥️ ШАГ 4: УСТАНОВКА СЕРТИФИКАТОВ НА СЕРВЕР

### 4.1 Подготовка сертификатов для сервера

На Mac выполните команды для конвертации .p12 в .pem:

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

**Результат:** Два .pem файла созданы

### 4.2 Загрузка сертификатов на сервер

```bash
# Загрузите сертификаты на сервер
scp ~/apns_certificates/apns_development.pem root@149.154.65.180:/opt/aladdin-backend/certificates/
scp ~/apns_certificates/apns_production.pem root@149.154.65.180:/opt/aladdin-backend/certificates/

# Или используйте expect для автоматизации
expect -c "
set timeout 30
set password \"Sergio675\"
spawn scp ~/apns_certificates/apns_development.pem root@149.154.65.180:/opt/aladdin-backend/certificates/
expect \"password:\" { send \"\$password\\r\" }
expect eof
"

expect -c "
set timeout 30
set password \"Sergio675\"
spawn scp ~/apns_certificates/apns_production.pem root@149.154.65.180:/opt/aladdin-backend/certificates/
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 4.3 Настройка прав доступа на сервере

```bash
# Подключитесь к серверу
ssh root@149.154.65.180

# Создайте директорию если не существует
mkdir -p /opt/aladdin-backend/certificates

# Установите правильные права
chmod 600 /opt/aladdin-backend/certificates/*.pem
chown root:root /opt/aladdin-backend/certificates/*.pem

# Проверьте что файлы на месте
ls -la /opt/aladdin-backend/certificates/
```

**Результат:** Сертификаты установлены на сервере с правильными правами

---

## 🔧 ШАГ 5: НАСТРОЙКА СЕРВЕРНОЙ ЧАСТИ

### 5.1 Установка Python библиотек для APNs

На сервере выполните:

```bash
# Подключитесь к серверу
ssh root@149.154.65.180

# Активируйте виртуальное окружение (если используется)
source /opt/aladdin-backend/venv/bin/activate  # или ваш путь к venv

# Установите библиотеку для работы с APNs
pip install PyAPNs2
# или
pip install python-apns

# Проверьте установку
python3 -c "import apns2; print('APNs library installed')"
```

### 5.2 Создание модуля для отправки push-уведомлений

Создайте файл `/opt/aladdin-backend/push_notification_service.py`:

```python
#!/usr/bin/env python3
"""
APNs Push Notification Service для ALADDIN
"""

import os
import json
from apns2.client import APNsClient
from apns2.payload import Payload
from apns2.credentials import TokenCredentials

class APNsService:
    def __init__(self, use_sandbox=True):
        """
        Инициализация APNs сервиса
        
        Args:
            use_sandbox: True для development, False для production
        """
        self.use_sandbox = use_sandbox
        
        # Пути к сертификатам
        if use_sandbox:
            cert_path = "/opt/aladdin-backend/certificates/apns_development.pem"
            self.topic = "family.aladdin.ios"
            self.host = "api.sandbox.push.apple.com"
        else:
            cert_path = "/opt/aladdin-backend/certificates/apns_production.pem"
            self.topic = "family.aladdin.ios"
            self.host = "api.push.apple.com"
        
        # Проверка существования сертификата
        if not os.path.exists(cert_path):
            raise FileNotFoundError(f"APNs certificate not found: {cert_path}")
        
        # Создание клиента
        self.client = APNsClient(
            credentials=TokenCredentials.from_file(cert_path),
            use_sandbox=use_sandbox
        )
    
    def send_notification(self, device_token: str, message: str, badge: int = None, sound: str = "default"):
        """
        Отправка push-уведомления
        
        Args:
            device_token: Device token устройства
            message: Текст уведомления
            badge: Число для badge (опционально)
            sound: Звук уведомления (по умолчанию "default")
        
        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            payload = Payload(
                alert=message,
                badge=badge,
                sound=sound
            )
            
            response = self.client.send_notification(
                device_token=device_token,
                payload=payload,
                topic=self.topic
            )
            
            if response.status == "success":
                print(f"✅ Push notification sent successfully to {device_token}")
                return True
            else:
                print(f"❌ Failed to send push notification: {response.reason}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending push notification: {str(e)}")
            return False
    
    def send_custom_notification(self, device_token: str, data: dict):
        """
        Отправка кастомного push-уведомления с дополнительными данными
        
        Args:
            device_token: Device token устройства
            data: Словарь с данными уведомления
                {
                    "alert": "Текст уведомления",
                    "badge": 1,
                    "sound": "default",
                    "custom_data": {...}
                }
        """
        try:
            payload = Payload(
                alert=data.get("alert", ""),
                badge=data.get("badge"),
                sound=data.get("sound", "default"),
                custom=data.get("custom_data", {})
            )
            
            response = self.client.send_notification(
                device_token=device_token,
                payload=payload,
                topic=self.topic
            )
            
            return response.status == "success"
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

# Singleton instance
_apns_service_dev = None
_apns_service_prod = None

def get_apns_service(use_sandbox=True):
    """Получить экземпляр APNs сервиса"""
    global _apns_service_dev, _apns_service_prod
    
    if use_sandbox:
        if _apns_service_dev is None:
            _apns_service_dev = APNsService(use_sandbox=True)
        return _apns_service_dev
    else:
        if _apns_service_prod is None:
            _apns_service_prod = APNsService(use_sandbox=False)
        return _apns_service_prod
```

### 5.3 Добавление endpoint для отправки push-уведомлений

Добавьте в `api_gateway.py`:

```python
from push_notification_service import get_apns_service

@app.post("/api/notifications/push/send")
async def send_push_notification(data: dict):
    """Отправить push-уведомление"""
    device_token = data.get("device_token")
    message = data.get("message", "")
    badge = data.get("badge")
    use_sandbox = data.get("use_sandbox", True)  # True для development
    
    if not device_token:
        return {"error": "device_token is required", "success": False}
    
    try:
        apns_service = get_apns_service(use_sandbox=use_sandbox)
        success = apns_service.send_notification(
            device_token=device_token,
            message=message,
            badge=badge
        )
        
        return {
            "success": success,
            "device_token": device_token,
            "message": message
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

**Результат:** Серверная часть настроена для отправки push-уведомлений

---

## 🧪 ШАГ 6: ТЕСТИРОВАНИЕ

### 6.1 Получение Device Token в iOS приложении

Убедитесь, что в `AppDelegate.swift` или `NotificationManager.swift` есть код для получения device token:

```swift
func application(_ application: UIApplication, 
                didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
    let tokenParts = deviceToken.map { data in String(format: "%02.2hhx", data) }
    let token = tokenParts.joined()
    print("📱 Device Token: \(token)")
    
    // Отправьте token на сервер
    sendDeviceTokenToServer(token: token)
}
```

### 6.2 Тестирование через curl

```bash
# Тест отправки push-уведомления через API
curl -X POST https://aladdin-ai.ru/api/notifications/push/send \
  -H "Content-Type: application/json" \
  -d '{
    "device_token": "ВАШ_DEVICE_TOKEN",
    "message": "Тестовое уведомление от ALADDIN",
    "badge": 1,
    "use_sandbox": true
  }'
```

### 6.3 Тестирование напрямую через APNs (для отладки)

```bash
# Установите httpie или используйте curl
pip install httpie

# Отправка через APNs напрямую (development)
http --verify=no POST https://api.sandbox.push.apple.com/3/device/ВАШ_DEVICE_TOKEN \
  apns-topic:"family.aladdin.ios" \
  apns-push-type:"alert" \
  apns-priority:10 \
  Content-Type:"application/json" \
  body:='{"aps":{"alert":"Test notification","badge":1}}' \
  --cert=/opt/aladdin-backend/certificates/apns_development.pem
```

**Результат:** Push-уведомление приходит на устройство

---

## ✅ ШАГ 7: ПРОВЕРКА И ВАЛИДАЦИЯ

### 7.1 Чек-лист проверки

- [ ] App ID создан с Push Notifications capability
- [ ] Development сертификат создан и скачан
- [ ] Production сертификат создан и скачан
- [ ] Сертификаты экспортированы в .p12 формат
- [ ] Сертификаты конвертированы в .pem формат
- [ ] Сертификаты загружены на сервер
- [ ] Права доступа к сертификатам настроены (600)
- [ ] Python библиотека для APNs установлена
- [ ] Модуль push_notification_service.py создан
- [ ] Endpoint для отправки push добавлен в API Gateway
- [ ] Device Token получен в iOS приложении
- [ ] Тестовое уведомление успешно отправлено
- [ ] Уведомление приходит на устройство

### 7.2 Команды для проверки на сервере

```bash
# Проверка наличия сертификатов
ls -la /opt/aladdin-backend/certificates/

# Проверка содержимого сертификата
openssl x509 -in /opt/aladdin-backend/certificates/apns_development.pem -text -noout | grep -A 5 "Subject:"

# Проверка установки Python библиотеки
python3 -c "import apns2; print('✅ APNs library OK')"

# Проверка синтаксиса push_notification_service.py
python3 -m py_compile /opt/aladdin-backend/push_notification_service.py
```

---

## 🚨 РЕШЕНИЕ ПРОБЛЕМ

### Проблема: "Certificate not found"

**Решение:**
- Проверьте путь к сертификатам
- Убедитесь, что файлы имеют расширение .pem
- Проверьте права доступа: `chmod 600 *.pem`

### Проблема: "Invalid device token"

**Решение:**
- Убедитесь, что device token получен правильно
- Проверьте, что используется правильный сертификат (dev/prod)
- Убедитесь, что Bundle ID совпадает

### Проблема: "Topic mismatch"

**Решение:**
- Проверьте, что topic = "family.aladdin.ios"
- Убедитесь, что Bundle ID в сертификате совпадает

### Проблема: "Connection refused"

**Решение:**
- Проверьте, что используется правильный host:
  - Development: `api.sandbox.push.apple.com`
  - Production: `api.push.apple.com`
- Проверьте сетевое подключение сервера

---

## 📝 ЗАМЕТКИ

- **Development сертификат** используется для тестирования на реальных устройствах
- **Production сертификат** используется для App Store и TestFlight
- Сертификаты действительны **1 год**, после чего нужно обновить
- Device Token может измениться при переустановке приложения
- Всегда тестируйте сначала на development окружении

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

После успешной настройки APNs:

1. ✅ Интегрировать отправку push в существующие endpoint'ы
2. ✅ Добавить логирование отправки уведомлений
3. ✅ Настроить обработку ошибок
4. ✅ Добавить очередь для массовой отправки
5. ✅ Настроить мониторинг доставки уведомлений

---

**Дата создания:** 10 февраля 2026 г.  
**Версия:** 1.0  
**Статус:** ✅ Готово к выполнению
