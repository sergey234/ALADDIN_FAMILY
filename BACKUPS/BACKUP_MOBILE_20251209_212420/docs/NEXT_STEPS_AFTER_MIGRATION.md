# 🎯 СЛЕДУЮЩИЕ ШАГИ ПОСЛЕ ПЕРЕНОСА

**Дата:** 2025-11-26  
**Статус:** ✅ Все файлы перенесены (363 файла)  
**Следующий этап:** Серверное конфигурирование

---

## ✅ ЧТО УЖЕ СДЕЛАНО

- ✅ **plan2-plan10:** Все файлы перенесены на сервер
  - SFM + валидатор
  - AI Agents (76 файлов)
  - Bots (30 файлов)
  - Managers (24 файла)
  - Microservices (17 файлов)
  - Active & Family (25 файлов)
  - VPN+Antivirus+Compliance+Core (116 файлов)
  - Критичные security модули (72 файла)
  - function_registry.json (993KB)

**Всего:** 363 файла Python + 1 JSON файл

---

## 📋 ЧТО ДАЛЬШЕ

### **plan11: Серверное конфигурирование** ⏳

Нужно настроить:

1. **Firewall (ufw/iptables)**
   - Открыть порты для API (443, 80)
   - Закрыть ненужные порты
   - Настроить правила для безопасности

2. **SSL сертификаты**
   - Установить certbot
   - Получить SSL сертификаты
   - Настроить автоматическое обновление

3. **PostgreSQL**
   - Установить PostgreSQL
   - Создать базу данных
   - Создать пользователя
   - Настроить права доступа

4. **Nginx**
   - Установить Nginx
   - Создать конфигурацию
   - Настроить reverse proxy для API
   - Настроить SSL

5. **Systemd сервисы**
   - Создать systemd unit для API Gateway
   - Создать systemd unit для мониторинга
   - Настроить автозапуск

6. **Monitoring & Logging**
   - Настроить логирование
   - Настроить мониторинг
   - Настроить rate limiting

7. **Резервное копирование**
   - Настроить автоматические бэкапы
   - Настроить ротацию логов

---

### **plan12: Тестирование + App Store** ⏳

После конфигурирования:

1. **Тестирование**
   - API endpoints (curl, Postman)
   - 138 функций защиты
   - Нагрузочное тестирование
   - Тесты безопасности
   - Проверка валидатора

2. **App Store**
   - Code signing
   - Создание архива
   - Загрузка в App Store Connect
   - Метаданные, скриншоты
   - Privacy Policy, Terms
   - Ревью и релиз

---

## 🚀 НАЧИНАЕМ С plan11

### Шаг 1: Проверка текущего состояния сервера

```bash
# Проверить, что установлено
ssh root@149.154.65.180
which nginx
which postgresql
which certbot
ufw status
```

### Шаг 2: Установка необходимых компонентов

```bash
# Обновление системы
apt update && apt upgrade -y

# Установка Nginx
apt install -y nginx

# Установка PostgreSQL
apt install -y postgresql postgresql-contrib

# Установка Certbot
apt install -y certbot python3-certbot-nginx

# Установка Firewall
apt install -y ufw
```

### Шаг 3: Настройка Firewall

```bash
# Базовые правила
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Шаг 4: Настройка PostgreSQL

```bash
# Создание базы данных
sudo -u postgres psql
CREATE DATABASE aladdin_db;
CREATE USER aladdin_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE aladdin_db TO aladdin_user;
\q
```

### Шаг 5: Настройка Nginx

```bash
# Создание конфигурации
nano /etc/nginx/sites-available/aladdin-backend

# Конфигурация reverse proxy для API
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Активировать конфигурацию
ln -s /etc/nginx/sites-available/aladdin-backend /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Шаг 6: Получение SSL сертификата

```bash
# Получить сертификат
certbot --nginx -d your-domain.com

# Автоматическое обновление
systemctl enable certbot.timer
```

### Шаг 7: Создание Systemd сервисов

```bash
# Создать unit для API Gateway
nano /etc/systemd/system/aladdin-api.service

[Unit]
Description=ALADDIN API Gateway
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/aladdin-backend
Environment="PATH=/opt/aladdin-backend/venvs/main_env/bin"
ExecStart=/opt/aladdin-backend/venvs/main_env/bin/python /opt/aladdin-backend/security/microservices/api_gateway.py
Restart=always

[Install]
WantedBy=multi-user.target

# Активировать сервис
systemctl daemon-reload
systemctl enable aladdin-api
systemctl start aladdin-api
```

---

## 📝 ЧЕКЛИСТ plan11

- [ ] Проверка текущего состояния сервера
- [ ] Установка Nginx
- [ ] Установка PostgreSQL
- [ ] Установка Certbot
- [ ] Установка UFW
- [ ] Настройка Firewall (порты 80, 443, SSH)
- [ ] Создание базы данных PostgreSQL
- [ ] Создание пользователя PostgreSQL
- [ ] Настройка Nginx (reverse proxy)
- [ ] Получение SSL сертификата
- [ ] Настройка автоматического обновления SSL
- [ ] Создание systemd unit для API Gateway
- [ ] Создание systemd unit для мониторинга
- [ ] Настройка логирования
- [ ] Настройка rate limiting
- [ ] Настройка резервного копирования

---

## 🎯 ГОТОВЫ НАЧАТЬ?

**Следующий шаг:** Начать с plan11 - Серверное конфигурирование

**Начнем с проверки текущего состояния сервера?**

