# 📋 ПОЛНОЕ РУКОВОДСТВО: Деплой лендинга на продакшн-сервер

**Дата создания:** 19 ноября 2025  
**Домен:** `https://aladdin-ai.ru/`  
**Сервер:** VDS-KVM-NVMe-Разгон-10.0 (149.154.65.180)  
**Статус:** ✅ Работает, HTTPS настроен, редирект www → основной домен

---

## 📊 ОБЗОР ПРОЕКТА

### Инфраструктура
- **Провайдер:** Host-0 (аккаунт `u3333175`)
- **Домен:** `aladdin-ai.ru` (зарегистрирован в Host-0)
- **VDS:** VDS-KVM-NVMe-Разгон-10.0 (#16146420)
  - **CPU:** 2 ядра
  - **RAM:** 4 GB
  - **Диск:** 60 GB NVMe
  - **ОС:** Ubuntu 24.04.3 LTS
  - **Панель:** ISPmanager 6 Lite
  - **IP:** 149.154.65.180
  - **Хостнейм:** sergey21-02-84.fvds.ru

### Структура проекта
- **Лендинг:** `/var/www/aladdin-ai.ru/`
- **Backend (резерв):** `/opt/aladdin-backend/`
- **Nginx конфиги:** `/etc/nginx/sites-available/`
- **SSL сертификаты:** `/etc/letsencrypt/live/aladdin-ai.ru/`

---

## 🔧 ШАГ 1: ПОДКЛЮЧЕНИЕ К СЕРВЕРУ

### Команда подключения
```bash
ssh root@149.154.65.180
```

**Параметры:**
- **Пользователь:** `root`
- **IP:** `149.154.65.180`
- **Порт:** 22 (по умолчанию)

**Примечание:** При первом подключении система попросит подтвердить fingerprint:
```
The authenticity of host '149.154.65.180' can't be established.
ECDSA key fingerprint is SHA256:U3/Xv1lrTaWarYfrv9ZRnq6SHxL6oeZbO1H1Pa9WGu8.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
```

---

## 🔧 ШАГ 2: ОБНОВЛЕНИЕ СИСТЕМЫ

### Команда
```bash
apt update && apt upgrade -y
```

**Что делает:**
- Обновляет список доступных пакетов (`apt update`)
- Устанавливает все доступные обновления безопасности (`apt upgrade -y`)

**Ожидаемый результат:**
```
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
All packages are up to date.
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
```

---

## 🔧 ШАГ 3: УСТАНОВКА БАЗОВЫХ ПАКЕТОВ

### Команда
```bash
apt install -y ufw fail2ban nginx python3-certbot-nginx git unzip
```

**Что устанавливает:**
- **ufw** — Uncomplicated Firewall (файрволл)
- **fail2ban** — защита от брутфорса
- **nginx** — веб-сервер
- **python3-certbot-nginx** — автоматический выпуск SSL сертификатов
- **git** — система контроля версий
- **unzip** — утилита для распаковки архивов

**Ожидаемый результат:**
```
Setting up nginx (1:1.26.3-108-ubuntu24) ...
Setting up certbot (2.9.0-1) ...
Created symlink /etc/systemd/system/timers.target.wants/certbot.timer → /usr/lib/systemd/system/certbot.timer.
```

---

## 🔧 ШАГ 4: НАСТРОЙКА FIREWALL (UFW)

### Команды
```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

**Что делает:**
- `ufw allow OpenSSH` — разрешает SSH (порт 22)
- `ufw allow 'Nginx Full'` — разрешает HTTP (80) и HTTPS (443)
- `ufw enable` — включает файрволл (подтвердить `y`)

**Проверка статуса:**
```bash
ufw status
```

**Ожидаемый результат:**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443                        ALLOW       Anywhere
OpenSSH                    ALLOW       Anywhere
Nginx Full                 ALLOW       Anywhere
```

**Примечание:** ISPmanager автоматически добавляет свои правила (FTP, почта, DNS), это нормально.

---

## 🔧 ШАГ 5: ВКЛЮЧЕНИЕ FAIL2BAN

### Команды
```bash
systemctl enable --now fail2ban
systemctl status fail2ban
```

**Что делает:**
- `systemctl enable` — включает автозапуск при перезагрузке
- `--now` — запускает сервис сразу
- `systemctl status` — проверяет статус (нажать `q` для выхода из просмотра)

**Ожидаемый результат:**
```
● fail2ban.service - Fail2Ban Service
     Loaded: loaded (/usr/lib/systemd/system/fail2ban.service; enabled; preset: enabled)
     Active: active (running)
```

---

## 🔧 ШАГ 6: СОЗДАНИЕ СТРУКТУРЫ ПРОЕКТА

### Команды
```bash
mkdir -p /var/www/aladdin-ai.ru
mkdir -p /opt/aladdin-backend
```

**Что делает:**
- Создаёт директорию для статического лендинга (`/var/www/aladdin-ai.ru`)
- Создаёт резервную директорию для backend (на будущее)

**Проверка:**
```bash
ls -la /var/www/
```

---

## 🔧 ШАГ 7: НАСТРОЙКА NGINX ДЛЯ ОСНОВНОГО ДОМЕНА

### Команда создания конфига
```bash
cat <<'EOF' >/etc/nginx/sites-available/aladdin-ai.ru
server {
    listen 80;
    listen [::]:80;
    server_name aladdin-ai.ru www.aladdin-ai.ru;

    root /var/www/aladdin-ai.ru;
    index index.html;

    access_log /var/log/nginx/aladdin_ai_access.log;
    error_log  /var/log/nginx/aladdin_ai_error.log;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF
```

**Что делает:**
- Создаёт конфигурацию Nginx для домена `aladdin-ai.ru` и `www.aladdin-ai.ru`
- Настраивает прослушивание порта 80 (HTTP) для IPv4 и IPv6
- Указывает корневую директорию сайта (`root`)
- Настраивает логирование доступа и ошибок
- Правило `try_files` позволяет SPA работать корректно (fallback на `index.html`)

### Включение конфига
```bash
ln -s /etc/nginx/sites-available/aladdin-ai.ru /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default  # если файл существует
```

**Что делает:**
- Создаёт символическую ссылку (включает сайт)
- Удаляет дефолтный конфиг (если есть)

### Проверка и перезагрузка
```bash
nginx -t && systemctl reload nginx
```

**Что делает:**
- `nginx -t` — проверяет синтаксис конфига
- `systemctl reload nginx` — перезагружает конфигурацию без простоя

**Ожидаемый результат:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

## 🔧 ШАГ 8: КОПИРОВАНИЕ ЛЕНДИНГА НА СЕРВЕР

### Команда (выполняется на локальном Mac)
```bash
rsync -avz \
  /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/ \
  root@149.154.65.180:/var/www/aladdin-ai.ru/
```

**Параметры rsync:**
- `-a` — архивный режим (сохраняет права, даты)
- `-v` — подробный вывод
- `-z` — сжатие при передаче

**Что копируется:**
- `index.html` — главная страница
- `styles.css` — стили
- `success.html` — страница успешной оплаты
- `privacy.html` — политика конфиденциальности
- `terms.html` — условия использования
- `help-faq.html` — FAQ
- `help-form.html` — форма помощи
- `cms/` — папка с JSON данными (tariffs.json, banks.json, testimonials.json и т.д.)

**Ожидаемый результат:**
```
building file list ... done
./
index.html
styles.css
success.html
...
sent 159630 bytes  received 428 bytes  8208.10 bytes/sec
total size is 782340  speedup is 4.89
```

### Исправление прав доступа (на сервере)
```bash
chown -R www-data:www-data /var/www/aladdin-ai.ru
find /var/www/aladdin-ai.ru -type d -exec chmod 755 {} \;
find /var/www/aladdin-ai.ru -type f -exec chmod 644 {} \;
systemctl reload nginx
```

**Что делает:**
- `chown -R www-data:www-data` — меняет владельца на пользователя Nginx
- `find ... -type d -exec chmod 755` — права 755 для директорий (rwxr-xr-x)
- `find ... -type f -exec chmod 644` — права 644 для файлов (rw-r--r--)
- `systemctl reload nginx` — перезагружает Nginx

**Проверка:**
```bash
ls -l /var/www/aladdin-ai.ru
```

**Ожидаемый результат:**
```
drwxr-xr-x 2 www-data www-data  4096 Nov 17 18:40 cms
-rw-r--r-- 1 www-data www-data 227353 Nov 19 01:19 index.html
-rw-r--r-- 1 www-data www-data  18787 Nov 18 14:00 styles.css
...
```

---

## 🔧 ШАГ 9: НАСТРОЙКА DNS

### Требуемые DNS-записи (в панели Host-0)

**A-записи (IPv4):**
- `A @ → 149.154.65.180` (основной домен)
- `A www → 149.154.65.180` (поддомен www)

**AAAA-записи (IPv6):**
- ❌ **УДАЛИТЬ** все AAAA-записи (если были `2a00:f940:4::9` или другие)
- Причина: Let's Encrypt проверяет домен, и если IPv6 указывает на другой сервер, валидация не пройдёт

**Как проверить DNS:**
```bash
# На локальной машине
dig aladdin-ai.ru +short
dig www.aladdin-ai.ru +short
```

**Ожидаемый результат:**
```
149.154.65.180
149.154.65.180
```

**Примечание:** Изменения DNS распространяются 5-30 минут (TTL).

---

## 🔧 ШАГ 10: ВЫПУСК SSL СЕРТИФИКАТА (Let's Encrypt)

### Команда
```bash
certbot --nginx -d aladdin-ai.ru -d www.aladdin-ai.ru
```

**Что делает:**
- Автоматически выпускает SSL сертификат для обоих доменов
- Настраивает Nginx для работы с HTTPS
- Настраивает автоматическое обновление сертификата

**Интерактивные вопросы:**
1. **Email адрес:** `sergey21-02-84@list.ru` (для уведомлений о продлении)
2. **Согласие с Terms of Service:** `Y`
3. **Поделиться email с EFF:** `Y` (опционально)
4. **Редирект HTTP → HTTPS:** выбрать опцию `2` (Redirect)

**Ожидаемый результат:**
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/aladdin-ai.ru/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/aladdin-ai.ru/privkey.pem
This certificate expires on 2026-02-17.

Successfully deployed certificate for aladdin-ai.ru to /etc/nginx/sites-enabled/aladdin-ai.ru
Successfully deployed certificate for www.aladdin-ai.ru to /etc/nginx/sites-enabled/aladdin-ai.ru

Congratulations! You have successfully enabled HTTPS on https://aladdin-ai.ru and https://www.aladdin-ai.ru
```

**Автоматическое обновление:**
Certbot создаёт systemd timer, который автоматически обновляет сертификат за 30 дней до истечения:
```bash
systemctl status certbot.timer
```

---

## 🔧 ШАГ 11: НАСТРОЙКА РЕДИРЕКТА www → ОСНОВНОЙ ДОМЕН

### Команда создания конфига редиректа
```bash
cat <<'EOF' >/etc/nginx/sites-available/www.aladdin-ai.ru
server {
    listen 80;
    listen [::]:80;
    server_name www.aladdin-ai.ru;

    return 301 https://aladdin-ai.ru$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name www.aladdin-ai.ru;

    ssl_certificate /etc/letsencrypt/live/aladdin-ai.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aladdin-ai.ru/privkey.pem;

    return 301 https://aladdin-ai.ru$request_uri;
}
EOF
```

**Что делает:**
- Создаёт отдельный конфиг для `www.aladdin-ai.ru`
- Настраивает редирект 301 (постоянный) с HTTP и HTTPS на основной домен
- Использует тот же SSL сертификат

### Включение конфига
```bash
ln -sf /etc/nginx/sites-available/www.aladdin-ai.ru /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

**Примечание:** Может появиться предупреждение:
```
[warn] conflicting server name "www.aladdin-ai.ru" on [::]:443, ignored
```
Это нормально — Nginx использует первый найденный конфиг, редирект работает.

**Проверка:**
```bash
curl -I https://www.aladdin-ai.ru
```

**Ожидаемый результат:**
```
HTTP/2 301
Location: https://aladdin-ai.ru/
```

---

## 🔧 ШАГ 12: ОБНОВЛЕНИЕ URL В МОБИЛЬНОМ ПРИЛОЖЕНИИ

### Файл: `Core/Config/AppConfig.swift`

**Было:**
```swift
static let subscriptionWebsiteURL: String = "https://aladdin.family/subscribe"
```

**Стало:**
```swift
static let subscriptionWebsiteURL: String = "https://aladdin-ai.ru/"
```

**Что делает:**
- Обновляет ссылку на прод-лендинг в iOS приложении
- При нажатии "Оформить подписку" в приложении открывается реальный сайт

---

## 📁 СТРУКТУРА ФАЙЛОВ НА СЕРВЕРЕ

### Лендинг (`/var/www/aladdin-ai.ru/`)
```
/var/www/aladdin-ai.ru/
├── index.html                    # Главная страница (227 KB)
├── styles.css                    # Стили (18 KB)
├── success.html                  # Страница успешной оплаты (30 KB)
├── privacy.html                  # Политика конфиденциальности (7 KB)
├── terms.html                    # Условия использования (7 KB)
├── help-faq.html                 # FAQ (10 KB)
├── help-form.html                # Форма помощи (5 KB)
├── cms/                          # CMS данные (JSON)
│   ├── hero.json                 # Данные для главного экрана
│   ├── tariffs.json              # Тарифы
│   ├── testimonials.json         # Отзывы
│   ├── faq.json                  # FAQ данные
│   ├── banks.json                # Список банков
│   └── methods.json              # Методы оплаты
└── [backup files]                # Резервные копии index.html
```

### Nginx конфиги
```
/etc/nginx/
├── sites-available/
│   ├── aladdin-ai.ru             # Основной конфиг (HTTP + HTTPS)
│   └── www.aladdin-ai.ru         # Редирект www → основной
└── sites-enabled/
    ├── aladdin-ai.ru -> ../sites-available/aladdin-ai.ru
    └── www.aladdin-ai.ru -> ../sites-available/www.aladdin-ai.ru
```

### SSL сертификаты
```
/etc/letsencrypt/
└── live/
    └── aladdin-ai.ru/
        ├── fullchain.pem         # Полная цепочка сертификатов
        ├── privkey.pem           # Приватный ключ
        ├── cert.pem              # Сертификат
        └── chain.pem             # Промежуточные сертификаты
```

### Логи
```
/var/log/nginx/
├── aladdin_ai_access.log        # Лог доступа
└── aladdin_ai_error.log         # Лог ошибок

/var/log/letsencrypt/
└── letsencrypt.log               # Лог Certbot
```

---

## 🔄 ПРОЦЕСС ОБНОВЛЕНИЯ ЛЕНДИНГА

### Метод 1: rsync (рекомендуется)

**На локальной машине (Mac):**
```bash
rsync -avz \
  /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/ \
  root@149.154.65.180:/var/www/aladdin-ai.ru/
```

**Преимущества:**
- Копирует только изменённые файлы (быстро)
- Сохраняет структуру директорий
- Можно запускать многократно (идемпотентно)

**После копирования (на сервере):**
```bash
# Проверка прав (если нужно)
chown -R www-data:www-data /var/www/aladdin-ai.ru
find /var/www/aladdin-ai.ru -type d -exec chmod 755 {} \;
find /var/www/aladdin-ai.ru -type f -exec chmod 644 {} \;
```

**Проверка:**
```bash
# На сервере
ls -l /var/www/aladdin-ai.ru

# В браузере
https://aladdin-ai.ru/
```

### Метод 2: Git (для будущего)

**На сервере:**
```bash
cd /var/www/aladdin-ai.ru
git init
git remote add origin <URL_вашего_репозитория>
git pull origin main
```

**Обновление:**
```bash
cd /var/www/aladdin-ai.ru
git pull origin main
```

### Метод 3: ISPmanager (через панель)

1. Зайти в ISPmanager → Файловый менеджер
2. Перейти в `/var/www/aladdin-ai.ru`
3. Загрузить файлы через веб-интерфейс
4. Проверить права доступа

---

## 🔍 ПРОВЕРКА РАБОТОСПОСОБНОСТИ

### 1. Проверка доступности сайта
```bash
curl -I https://aladdin-ai.ru
```

**Ожидаемый результат:**
```
HTTP/2 200
server: nginx
date: ...
content-type: text/html
```

### 2. Проверка редиректа www
```bash
curl -I https://www.aladdin-ai.ru
```

**Ожидаемый результат:**
```
HTTP/2 301
location: https://aladdin-ai.ru/
```

### 3. Проверка SSL сертификата
```bash
openssl s_client -connect aladdin-ai.ru:443 -servername aladdin-ai.ru < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

**Ожидаемый результат:**
```
notBefore=Nov 19 12:34:11 2025 GMT
notAfter=Feb 17 12:34:11 2026 GMT
```

### 4. Проверка автоматического обновления сертификата
```bash
systemctl status certbot.timer
certbot renew --dry-run
```

**Ожидаемый результат:**
```
The dry run was successful.
```

---

## 🛠️ УСТРАНЕНИЕ ПРОБЛЕМ

### Проблема: 403 Forbidden

**Причина:** Неправильные права доступа к файлам

**Решение:**
```bash
chown -R www-data:www-data /var/www/aladdin-ai.ru
find /var/www/aladdin-ai.ru -type d -exec chmod 755 {} \;
find /var/www/aladdin-ai.ru -type f -exec chmod 644 {} \;
systemctl reload nginx
```

### Проблема: Certbot не может выпустить сертификат (403 на challenge)

**Причина:** DNS указывает на другой сервер (особенно IPv6)

**Решение:**
1. Проверить DNS записи:
   ```bash
   dig aladdin-ai.ru +short
   dig AAAA aladdin-ai.ru +short
   ```
2. Удалить AAAA записи в панели DNS
3. Подождать 5-10 минут
4. Повторить `certbot --nginx -d aladdin-ai.ru -d www.aladdin-ai.ru`

### Проблема: Nginx не перезагружается

**Причина:** Ошибка в конфиге

**Решение:**
```bash
nginx -t  # Проверить синтаксис
# Исправить ошибки в конфиге
systemctl reload nginx
```

### Проблема: Сайт не открывается после обновления

**Решение:**
```bash
# Проверить логи
tail -f /var/log/nginx/aladdin_ai_error.log

# Проверить права
ls -l /var/www/aladdin-ai.ru

# Проверить конфиг
nginx -t
```

---

## 📝 ВАЖНЫЕ ЗАМЕТКИ

### Безопасность
- ✅ Firewall (UFW) включён
- ✅ Fail2ban защищает от брутфорса
- ✅ SSL сертификат автоматически обновляется
- ✅ Права доступа настроены правильно (www-data)

### Производительность
- Nginx кэширует статические файлы
- Можно добавить gzip сжатие (уже включено в дефолтном конфиге Nginx)

### Мониторинг
- Логи доступа: `/var/log/nginx/aladdin_ai_access.log`
- Логи ошибок: `/var/log/nginx/aladdin_ai_error.log`
- Логи Certbot: `/var/log/letsencrypt/letsencrypt.log`

### Резервное копирование
Рекомендуется настроить автоматические бэкапы:
```bash
# Пример скрипта бэкапа
tar -czf /root/backups/aladdin-ai-ru-$(date +%Y%m%d).tar.gz /var/www/aladdin-ai.ru
```

---

## 🔗 ССЫЛКИ И РЕСУРСЫ

- **Домен:** https://aladdin-ai.ru/
- **Провайдер:** Host-0 (аккаунт u3333175)
- **Сервер:** 149.154.65.180 (sergey21-02-84.fvds.ru)
- **SSL:** Let's Encrypt (автообновление через Certbot)
- **Документация Nginx:** https://nginx.org/en/docs/
- **Документация Certbot:** https://eff-certbot.readthedocs.io/

---

## ✅ ЧЕКЛИСТ ГОТОВНОСТИ

- [x] Сервер настроен (Ubuntu 24.04, пакеты установлены)
- [x] Firewall и Fail2ban включены
- [x] Nginx настроен для основного домена
- [x] Лендинг скопирован на сервер
- [x] Права доступа настроены
- [x] DNS записи настроены (A → 149.154.65.180, AAAA удалены)
- [x] SSL сертификат выпущен и установлен
- [x] Редирект www → основной домен настроен
- [x] URL в приложении обновлён
- [x] Сайт доступен по HTTPS
- [x] Автоматическое обновление SSL настроено

---

## 📋 СЛЕДУЮЩИЕ ШАГИ

1. **Добавить согласие на обработку ПДн** (отдельный документ + чек-бокс)
2. **Настроить backend** (если нужно) в `/opt/aladdin-backend/`
3. **Настроить мониторинг** (опционально)
4. **Настроить автоматические бэкапы** (рекомендуется)

---

**Документ создан:** 19 ноября 2025  
**Последнее обновление:** 19 ноября 2025  
**Автор:** AI Assistant (Auto)

