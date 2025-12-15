# 🤖 РУКОВОДСТВО ДЛЯ ML СИСТЕМЫ: Подключение и работа с сервером

## 📋 Оглавление
1. [Параметры подключения](#параметры-подключения)
2. [Инструмент expect](#инструмент-expect)
3. [Базовые команды](#базовые-команды)
4. [Примеры скриптов](#примеры-скриптов)
5. [Безопасность](#безопасность)
6. [Частые задачи](#частые-задачи)
7. [Решение проблем](#решение-проблем)

---

## 🔐 Параметры подключения

### Основная информация:
- **Сервер**: `root@149.154.65.180`
- **Пароль**: `Sergio675`
- **Протокол**: SSH
- **Порт**: 22 (по умолчанию)

### Строка подключения:
```bash
ssh root@149.154.65.180
```

---

## 🛠️ Инструмент expect

### Что такое expect?
`expect` — это инструмент для автоматизации интерактивных команд. Он позволяет автоматически отвечать на запросы (например, ввод пароля).

### Почему нужен expect?
Обычные SSH команды требуют ввода пароля вручную:
```bash
ssh root@149.154.65.180 "команда"
# ❌ Требует ввод пароля вручную - ML система не может это сделать
```

С `expect` пароль вводится автоматически:
```bash
expect -c "spawn ssh root@149.154.65.180 'команда'; expect 'password:' { send 'Sergio675\r' }"
# ✅ Автоматически вводит пароль и выполняет команду
```

### Установка expect:
```bash
# macOS
brew install expect

# Linux (Ubuntu/Debian)
apt install expect

# Проверка установки
which expect
```

---

## 📝 Базовые команды

### 1. Простая команда (одна строка)

**Формат:**
```bash
expect -c "
set timeout 30
set password \"Sergio675\"
set server \"root@149.154.65.180\"
spawn ssh \$server \"ВАША_КОМАНДА\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

**Пример:**
```bash
expect -c "
set timeout 30
set password \"Sergio675\"
spawn ssh root@149.154.65.180 \"ls -la /var/www\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 2. Несколько команд подряд

**Формат:**
```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

# Команда 1
spawn ssh \$server \"команда1\"
expect \"password:\" { send \"\$password\\r\" }
expect eof

# Команда 2
spawn ssh \$server \"команда2\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 3. Копирование файлов (scp)

**Формат:**
```bash
expect -c "
set timeout 60
set password \"Sergio675\"
spawn scp /путь/к/локальному/файлу root@149.154.65.180:/путь/на/сервере
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

**Пример:**
```bash
expect -c "
set timeout 60
set password \"Sergio675\"
spawn scp /Users/user/file.txt root@149.154.65.180:/tmp/file.txt
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

---

## 📄 Примеры скриптов

### Пример 1: Простой скрипт для одной задачи

**Файл:** `simple_command.sh`
```bash
#!/usr/bin/expect -f
set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== Выполнение команды ==="
spawn ssh $server "uptime"
expect "password:" { send "$password\r" }
expect eof
```

**Использование:**
```bash
chmod +x simple_command.sh
./simple_command.sh
```

### Пример 2: Скрипт с несколькими шагами

**Файл:** `multi_step.sh`
```bash
#!/usr/bin/expect -f
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== Шаг 1: Проверка статуса ==="
spawn ssh $server "systemctl status nginx"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "=== Шаг 2: Проверка диска ==="
spawn ssh $server "df -h"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "=== Шаг 3: Проверка памяти ==="
spawn ssh $server "free -h"
expect "password:" { send "$password\r" }
expect eof
```

### Пример 3: Копирование файла и выполнение команды

**Файл:** `copy_and_execute.sh`
```bash
#!/usr/bin/expect -f
set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

# Шаг 1: Копирование файла
puts "📤 Копирование файла..."
spawn scp /local/path/file.txt $server:/tmp/file.txt
expect "password:" { send "$password\r" }
expect eof

# Шаг 2: Выполнение команды на сервере
puts ""
puts "🚀 Выполнение команды..."
spawn ssh $server "cat /tmp/file.txt"
expect "password:" { send "$password\r" }
expect eof
```

### Пример 4: Работа с базой данных PostgreSQL

**Файл:** `database_command.sh`
```bash
#!/usr/bin/expect -f
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"
set db_user "aladdin_user"
set db_password "AladdinSecure2024!"
set db_name "aladdin_db"

puts "=== Выполнение SQL команды ==="
spawn ssh $server "PGPASSWORD='$db_password' psql -h localhost -U $db_user -d $db_name -c 'SELECT COUNT(*) FROM users;'"
expect "password:" { send "$password\r" }
expect eof
```

### Пример 5: Выполнение SQL скрипта

**Файл:** `execute_sql.sh`
```bash
#!/usr/bin/expect -f
set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set db_user "aladdin_user"
set db_password "AladdinSecure2024!"
set db_name "aladdin_db"

# Шаг 1: Копирование SQL файла
puts "📤 Копирование SQL файла..."
spawn scp /local/path/script.sql $server:/tmp/script.sql
expect "password:" { send "$password\r" }
expect eof

# Шаг 2: Выполнение SQL скрипта
puts ""
puts "🚀 Выполнение SQL скрипта..."
spawn ssh $server "PGPASSWORD='$db_password' psql -h localhost -U $db_user -d $db_name -f /tmp/script.sql"
expect "password:" { send "$password\r" }
expect eof
```

---

## 🔒 Безопасность

### ⚠️ ВАЖНО: Пароль в скриптах

**Текущая ситуация:**
- Пароль `Sergio675` хранится в скриптах
- Это работает, но не безопасно для продакшена

**Рекомендации для продакшена:**

1. **Использовать SSH-ключи** (лучший вариант):
```bash
# Генерация ключа
ssh-keygen -t rsa -b 4096

# Копирование ключа на сервер
ssh-copy-id root@149.154.65.180

# После этого можно использовать без пароля:
ssh root@149.154.65.180 "команда"
```

2. **Использовать переменные окружения:**
```bash
#!/usr/bin/expect -f
set password $env(SSH_PASSWORD)  # Читает из переменной окружения
set server "root@149.154.65.180"
```

3. **Использовать файл с паролем (с ограниченными правами):**
```bash
chmod 600 ~/.ssh/password_file
# Читать пароль из файла в скрипте
```

### ✅ Текущий подход (для разработки):
- Пароль в скриптах — **ОК для разработки**
- Не коммитить скрипты с паролями в публичный Git
- Для продакшена — перейти на SSH-ключи

---

## 🎯 Частые задачи

### 1. Проверка статуса службы

```bash
expect -c "
set timeout 30
set password \"Sergio675\"
spawn ssh root@149.154.65.180 \"systemctl status nginx\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 2. Перезапуск службы

```bash
expect -c "
set timeout 30
set password \"Sergio675\"
spawn ssh root@149.154.65.180 \"systemctl restart nginx\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 3. Просмотр логов

```bash
expect -c "
set timeout 30
set password \"Sergio675\"
spawn ssh root@149.154.65.180 \"tail -n 50 /var/log/nginx/error.log\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 4. Редактирование файла (через sed)

```bash
expect -c "
set timeout 30
set password \"Sergio675\"
spawn ssh root@149.154.65.180 \"sed -i 's/old/new/g' /etc/nginx/nginx.conf\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 5. Создание директории

```bash
expect -c "
set timeout 30
set password \"Sergio675\"
spawn ssh root@149.154.65.180 \"mkdir -p /var/www/new_directory\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 6. Установка пакета

```bash
expect -c "
set timeout 120
set password \"Sergio675\"
spawn ssh root@149.154.65.180 \"apt update && apt install -y package_name\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 7. Работа с PostgreSQL

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set db_password \"AladdinSecure2024!\"
spawn ssh root@149.154.65.180 \"PGPASSWORD='\$db_password' psql -h localhost -U aladdin_user -d aladdin_db -c 'SELECT * FROM users;'\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

---

## 🐛 Решение проблем

### Проблема 1: "command not found: expect"

**Решение:**
```bash
# macOS
brew install expect

# Linux
apt install expect
```

### Проблема 2: "Connection timed out"

**Причины:**
- Сервер недоступен
- Неправильный IP адрес
- Проблемы с сетью

**Решение:**
```bash
# Проверка доступности
ping 149.154.65.180

# Проверка SSH порта
telnet 149.154.65.180 22
```

### Проблема 3: "Permission denied"

**Причины:**
- Неправильный пароль
- Пользователь не имеет прав

**Решение:**
- Проверить пароль
- Убедиться, что используете `root@`

### Проблема 4: "No space left on device"

**Решение:**
```bash
expect -c "
set timeout 30
set password \"Sergio675\"
spawn ssh root@149.154.65.180 \"df -h\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### Проблема 5: Скрипт зависает

**Решение:**
- Увеличить `timeout`:
```bash
set timeout 300  # 5 минут вместо 30 секунд
```

---

## 📚 Шаблоны для копирования

### Шаблон 1: Базовый скрипт

```bash
#!/usr/bin/expect -f
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== Начало выполнения ==="

# Ваши команды здесь
spawn ssh $server "ВАША_КОМАНДА"
expect "password:" { send "$password\r" }
expect eof

puts "=== Завершено ==="
```

### Шаблон 2: Скрипт с обработкой ошибок

```bash
#!/usr/bin/expect -f
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== Начало выполнения ==="

spawn ssh $server "ВАША_КОМАНДА"
expect {
    "password:" { 
        send "$password\r"
        exp_continue
    }
    "error" {
        puts "❌ Ошибка выполнения!"
        exit 1
    }
    eof
}

puts "=== Завершено ==="
```

### Шаблон 3: Скрипт с несколькими шагами

```bash
#!/usr/bin/expect -f
set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

# Шаг 1
puts "📦 Шаг 1: Описание..."
spawn ssh $server "команда1"
expect "password:" { send "$password\r" }
expect eof

# Шаг 2
puts ""
puts "🚀 Шаг 2: Описание..."
spawn ssh $server "команда2"
expect "password:" { send "$password\r" }
expect eof

# Шаг 3
puts ""
puts "✅ Шаг 3: Описание..."
spawn ssh $server "команда3"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Все шаги выполнены!"
```

---

## ✅ Чеклист перед выполнением команд

1. ✅ Проверить доступность сервера: `ping 149.154.65.180`
2. ✅ Убедиться, что `expect` установлен: `which expect`
3. ✅ Проверить правильность пароля
4. ✅ Установить разумный `timeout`
5. ✅ Проверить права на выполнение скрипта: `chmod +x script.sh`

---

## 🎓 Итоговая памятка

### Для ML системы:

1. **Всегда используйте expect** для автоматизации SSH команд
2. **Пароль**: `Sergio675`
3. **Сервер**: `root@149.154.65.180`
4. **Формат команды**:
   ```bash
   expect -c "spawn ssh root@149.154.65.180 'команда'; expect 'password:' { send 'Sergio675\r' }"
   ```
5. **Для скриптов**: создавайте файлы с `#!/usr/bin/expect -f`
6. **Timeout**: всегда устанавливайте разумный timeout (30-120 секунд)

### Структура команды:
```
expect -c "
  set timeout 60
  set password \"Sergio675\"
  set server \"root@149.154.65.180\"
  spawn ssh \$server \"ВАША_КОМАНДА\"
  expect \"password:\" { send \"\$password\\r\" }
  expect eof
"
```

---

## 📞 Дополнительная информация

### Полезные команды для диагностики:

```bash
# Проверка подключения
ssh -v root@149.154.65.180

# Проверка версии expect
expect -v

# Тестовая команда
expect -c "spawn ssh root@149.154.65.180 'echo Hello'; expect 'password:' { send 'Sergio675\r' }"
```

---

**Дата создания:** 22 ноября 2024  
**Версия:** 1.0  
**Для:** ML системы, работающие с сервером 149.154.65.180


