# 📊 АНАЛИЗ: Где находится база данных и backend

## ✅ Текущая ситуация

### iOS приложение подключается к:
- **DEBUG**: `https://api-dev.aladdin.family/api`
- **PRODUCTION**: `https://api.aladdin.family/api`

### Архитектура (87% сервер / 13% iOS):
- **Сервер (87%)**: SFM, AI-агенты, менеджеры, боты, PostgreSQL БД
- **iOS (13%)**: UI, Keychain, VPN-клиент, кэш, API транспорт

### Сервер 149.154.65.180 (aladdin-ai.ru):
- ✅ Статический сайт (landing page)
- ✅ Nginx настроен
- ❓ Backend API - **не найден** (или еще не развернут)
- ❓ PostgreSQL - **не найден** (или еще не установлен)

---

## ❓ Вопросы

### 1. Где СЕЙЧАС находится backend и PostgreSQL?

**Вариант A**: Backend на `api-dev.aladdin.family` (другой сервер)
- PostgreSQL БД находится там же
- Нужен SSH доступ к тому серверу для выполнения SQL скрипта

**Вариант B**: Backend уже частично на 149.154.65.180
- Нужно найти где он находится
- Проверить есть ли PostgreSQL

**Вариант C**: Backend еще не развернут на 149.154.65.180
- Нужно создать структуру backend
- Установить PostgreSQL
- Выполнить SQL скрипт

---

## 🔍 Что нужно для выполнения SQL скрипта

Для выполнения `REFERRAL_DB_SETUP.sql` нужны:

1. **IP адрес сервера** с PostgreSQL
   - Вариант A: IP сервера `api-dev.aladdin.family`
   - Вариант B: `149.154.65.180` (если PostgreSQL уже установлен)

2. **Параметры подключения**:
   - Пользователь БД (обычно `postgres`, `aladdin`, или другой)
   - Пароль БД
   - Имя базы данных (обычно `aladdin`, `aladdin_db`, или другое)
   - Порт (обычно `5432`)

3. **SSH доступ** к серверу для выполнения команд

---

## 🚀 План действий

### Шаг 1: Определить где находится backend

**Вариант 1**: Если backend на `api-dev.aladdin.family`:
```bash
# Нужен SSH доступ к тому серверу
ssh user@api-dev.aladdin.family
# Или через IP, если известен
```

**Вариант 2**: Если backend на 149.154.65.180:
```bash
# Проверить есть ли PostgreSQL
ssh root@149.154.65.180 "which psql"
ssh root@149.154.65.180 "systemctl status postgresql"
```

### Шаг 2: Найти параметры подключения к БД

**Способ 1**: Через конфигурацию Python проекта:
```bash
# На сервере с backend
find /opt /var/www /home -name "*.py" -o -name ".env" | \
  xargs grep -l "postgres\|DATABASE\|DB_" | head -10
```

**Способ 2**: Через переменные окружения:
```bash
# На сервере с backend
env | grep -i postgres
cat /etc/environment | grep -i postgres
```

**Способ 3**: Через Docker (если используется):
```bash
docker ps | grep postgres
docker inspect <container_id> | grep -i postgres
```

### Шаг 3: Выполнить SQL скрипт

**Если PostgreSQL на том же сервере**:
```bash
psql -U <user> -d <database> -f REFERRAL_DB_SETUP.sql
```

**Если PostgreSQL на другом сервере**:
```bash
psql -h <host> -U <user> -d <database> -f REFERRAL_DB_SETUP.sql
```

---

## 💡 Рекомендации

### Для будущего переезда на 149.154.65.180:

1. **Установить PostgreSQL** (если еще не установлен):
```bash
apt update
apt install postgresql postgresql-contrib
systemctl start postgresql
systemctl enable postgresql
```

2. **Создать базу данных**:
```bash
sudo -u postgres psql
CREATE DATABASE aladdin_db;
CREATE USER aladdin_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE aladdin_db TO aladdin_user;
\q
```

3. **Выполнить SQL скрипт**:
```bash
psql -U aladdin_user -d aladdin_db -f REFERRAL_DB_SETUP.sql
```

4. **Настроить backend** для подключения к PostgreSQL

---

## ❓ Что нужно от вас

1. **Где СЕЙЧАС находится backend?**
   - На `api-dev.aladdin.family`?
   - Или уже на 149.154.65.180?

2. **Есть ли SSH доступ к серверу с backend?**
   - Если да, предоставьте:
     - IP адрес или домен
     - Пользователь SSH
     - Пароль или ключ

3. **Параметры PostgreSQL** (если известны):
   - Хост
   - Порт
   - Пользователь
   - Пароль
   - Имя базы данных

4. **Когда планируется переезд на 149.154.65.180?**
   - Если скоро, можно подготовить все заранее
   - Если позже, выполнить SQL на текущем сервере

---

## 📝 Следующие шаги

После получения информации:
1. ✅ Подключиться к серверу с PostgreSQL
2. ✅ Выполнить `REFERRAL_DB_SETUP.sql`
3. ✅ Проверить создание таблиц
4. ✅ Интегрировать API endpoints
5. ✅ Протестировать реферальную программу


