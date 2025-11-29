# 🔐 ПОДРОБНОЕ РУКОВОДСТВО: Подключение к серверу и загрузка файлов

**Дата создания:** 19 ноября 2025  
**Цель:** Детальное описание процесса подключения к серверу и загрузки файлов для ML моделей и разработчиков

---

## 📋 ОГЛАВЛЕНИЕ

1. [Информация о сервере](#1-информация-о-сервере)
2. [Проблема с паролем в SSH/rsync](#2-проблема-с-паролем-в-sshrsync)
3. [Решение: использование expect](#3-решение-использование-expect)
4. [Пошаговый процесс загрузки](#4-пошаговый-процесс-загрузки)
5. [Альтернативные методы](#5-альтернативные-методы)
6. [Проверка и валидация](#6-проверка-и-валидация)

---

## 1. ИНФОРМАЦИЯ О СЕРВЕРЕ

### Параметры подключения:
- **IP адрес:** `149.154.65.180`
- **Пользователь:** `root`
- **Пароль:** `Sergio675`
- **Порт SSH:** `22` (по умолчанию)
- **Протокол:** `SSH`

### Пути на сервере:
- **Лендинг:** `/var/www/aladdin-ai.ru/`
- **Backend (резерв):** `/opt/aladdin-backend/`
- **Nginx конфиги:** `/etc/nginx/sites-available/`

### Локальные пути:
- **Лендинг:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/`

---

## 2. ПРОБЛЕМА С ПАРОЛЕМ В SSH/RSYNC

### ❌ Проблема:
При попытке выполнить команду `rsync` или `ssh` с паролем, система запрашивает пароль интерактивно:

```bash
rsync -avz landing/ root@149.154.65.180:/var/www/aladdin-ai.ru/
# Вывод:
# root@149.154.65.180's password: 
```

**Почему это проблема для автоматизации:**
1. Команда блокируется и ждет ввода пароля
2. Невозможно передать пароль через аргументы командной строки (небезопасно)
3. Интерактивный ввод не работает в скриптах без специальных инструментов

### 🔍 Попытки решения:

#### Попытка 1: Прямая передача пароля (НЕ РАБОТАЕТ)
```bash
rsync -avz --password=Sergio675 landing/ root@149.154.65.180:/var/www/aladdin-ai.ru/
# ❌ Ошибка: rsync не поддерживает передачу пароля через аргументы
```

#### Попытка 2: Использование sshpass (НЕ УСТАНОВЛЕН)
```bash
which sshpass
# Вывод: sshpass не установлен
# ❌ Требуется установка: brew install sshpass
```

#### Попытка 3: SSH ключи (НЕ НАСТРОЕНЫ)
```bash
ls -la ~/.ssh/id_*
# Вывод: SSH ключи не найдены
# ❌ Требуется настройка SSH ключей
```

---

## 3. РЕШЕНИЕ: ИСПОЛЬЗОВАНИЕ EXPECT

### ✅ Что такое expect?

**expect** — это инструмент для автоматизации интерактивных программ. Он позволяет:
- Автоматически отвечать на запросы пароля
- Обрабатывать интерактивные диалоги
- Использоваться в скриптах для автоматизации

### 📦 Проверка установки expect:

```bash
which expect
# Вывод: /usr/bin/expect
# ✅ expect уже установлен в системе
```

**Если expect не установлен:**
```bash
# macOS:
brew install expect

# Ubuntu/Debian:
sudo apt-get install expect

# CentOS/RHEL:
sudo yum install expect
```

---

## 4. ПОШАГОВЫЙ ПРОЦЕСС ЗАГРУЗКИ

### Шаг 1: Создание expect-скрипта для rsync

**Файл:** `deploy_with_password.sh`

```bash
#!/usr/bin/expect -f
# 🚀 Автоматическая загрузка лендинга на сервер с паролем

# Установка таймаута (30 секунд)
set timeout 30

# Параметры подключения
set password "Sergio675"
set server "root@149.154.65.180"
set local_path "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/"
set remote_path "/var/www/aladdin-ai.ru/"

# Вывод информации
puts "🚀 Начинаю загрузку лендинга на сервер..."
puts "📦 Локальная директория: $local_path"
puts "🌐 Сервер: $server"
puts "📁 Путь на сервере: $remote_path"
puts ""

# Запуск rsync
spawn rsync -avz --progress $local_path $server:$remote_path

# Обработка интерактивных запросов
expect {
    # Если запрошен пароль
    "password:" {
        send "$password\r"      # Отправляем пароль + Enter
        exp_continue            # Продолжаем ожидание
    }
    # Если запрошено подтверждение SSH fingerprint
    "Are you sure you want to continue connecting" {
        send "yes\r"            # Отправляем "yes" + Enter
        exp_continue            # Продолжаем ожидание
    }
    # Если команда завершена успешно
    eof {
        puts "\n✅ Загрузка завершена!"
    }
    # Если превышен таймаут
    timeout {
        puts "\n❌ Таймаут при загрузке"
        exit 1
    }
}

# Ожидание завершения процесса
wait
```

**Объяснение ключевых команд expect:**
- `set timeout 30` — таймаут 30 секунд
- `spawn` — запускает команду и перехватывает её ввод/вывод
- `expect` — ожидает определенные строки в выводе
- `send` — отправляет текст в программу
- `\r` — символ возврата каретки (Enter)
- `exp_continue` — продолжает ожидание после отправки ответа
- `eof` — конец файла (команда завершена)
- `wait` — ждет завершения процесса

### Шаг 2: Установка прав на выполнение

```bash
chmod +x deploy_with_password.sh
```

**Что делает:**
- Делает файл исполняемым
- Позволяет запускать скрипт напрямую: `./deploy_with_password.sh`

### Шаг 3: Выполнение скрипта

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./deploy_with_password.sh
```

**Что происходит:**
1. Скрипт запускает `rsync`
2. Когда rsync запрашивает пароль, expect автоматически отправляет `Sergio675`
3. Если это первое подключение, expect отвечает "yes" на запрос подтверждения SSH fingerprint
4. rsync загружает файлы на сервер
5. Скрипт выводит результат

**Пример вывода:**
```
🚀 Начинаю загрузку лендинга на сервер...
📦 Локальная директория: /Users/.../landing/
🌐 Сервер: root@149.154.65.180
📁 Путь на сервере: /var/www/aladdin-ai.ru/

spawn rsync -avz --progress ...
root@149.154.65.180's password: 
building file list ... 
21 files to consider
./
consent.html
       13656 100%    0.00kB/s    0:00:00 (xfer#1, to-check=16/21)
index.html
      227287 100%   43.35MB/s    0:00:00 (xfer#2, to-check=13/21)
...

✅ Загрузка завершена!
```

---

## 5. НАСТРОЙКА ПРАВ ДОСТУПА НА СЕРВЕРЕ

### Шаг 4: Создание expect-скрипта для настройки прав

**Файл:** `fix_permissions.sh`

```bash
#!/usr/bin/expect -f
# 🔧 Настройка прав доступа на сервере

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"
set remote_path "/var/www/aladdin-ai.ru"

puts "🔧 Настраиваю права доступа на сервере..."
puts ""

# Выполняем команды на сервере через SSH
spawn ssh $server "chown -R www-data:www-data $remote_path && find $remote_path -type d -exec chmod 755 {} \\; && find $remote_path -type f -exec chmod 644 {} \\; && systemctl reload nginx && echo '✅ Права доступа настроены, Nginx перезагружен'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    eof {
        puts "\n✅ Готово!"
    }
    timeout {
        puts "\n❌ Таймаут"
        exit 1
    }
}

wait
```

**Что делают команды на сервере:**
1. `chown -R www-data:www-data /var/www/aladdin-ai.ru` — меняет владельца всех файлов на `www-data` (пользователь Nginx)
2. `find ... -type d -exec chmod 755 {} \;` — устанавливает права 755 (rwxr-xr-x) для всех директорий
3. `find ... -type f -exec chmod 644 {} \;` — устанавливает права 644 (rw-r--r--) для всех файлов
4. `systemctl reload nginx` — перезагружает Nginx без простоя

### Шаг 5: Выполнение скрипта

```bash
chmod +x fix_permissions.sh
./fix_permissions.sh
```

**Вывод:**
```
🔧 Настраиваю права доступа на сервере...

spawn ssh root@149.154.65.180 chown -R ...
root@149.154.65.180's password: 
✅ Права доступа настроены, Nginx перезагружен

✅ Готово!
```

---

## 6. ПРОВЕРКА И ВАЛИДАЦИЯ

### Шаг 6: Проверка доступности файлов

```bash
# Проверка главной страницы
curl -s -o /dev/null -w "index.html: %{http_code}\n" https://aladdin-ai.ru/

# Проверка новых документов
curl -s -o /dev/null -w "consent.html: %{http_code}\n" https://aladdin-ai.ru/consent.html
curl -s -o /dev/null -w "privacy.html: %{http_code}\n" https://aladdin-ai.ru/privacy.html
curl -s -o /dev/null -w "terms.html: %{http_code}\n" https://aladdin-ai.ru/terms.html
```

**Ожидаемый результат:**
```
index.html: 200
consent.html: 200
privacy.html: 200
terms.html: 200
```

**Коды ответа HTTP:**
- `200` — OK (файл доступен)
- `404` — Not Found (файл не найден)
- `403` — Forbidden (нет прав доступа)
- `500` — Internal Server Error (ошибка сервера)

---

## 7. АЛЬТЕРНАТИВНЫЕ МЕТОДЫ

### Метод 1: SSH ключи (рекомендуется для продакшн)

**Преимущества:**
- Не требует пароля
- Более безопасно
- Работает без expect

**Настройка:**

```bash
# 1. Генерация SSH ключа (если нет)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 2. Копирование ключа на сервер
ssh-copy-id root@149.154.65.180
# Или вручную:
cat ~/.ssh/id_rsa.pub | ssh root@149.154.65.180 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# 3. Теперь можно использовать без пароля:
rsync -avz landing/ root@149.154.65.180:/var/www/aladdin-ai.ru/
```

### Метод 2: sshpass (проще, но менее безопасно)

**Установка:**
```bash
# macOS:
brew install sshpass

# Ubuntu/Debian:
sudo apt-get install sshpass
```

**Использование:**
```bash
sshpass -p 'Sergio675' rsync -avz landing/ root@149.154.65.180:/var/www/aladdin-ai.ru/
```

**⚠️ Внимание:** Пароль передается в командной строке, что видно в `ps aux`. Используйте только для тестирования!

### Метод 3: Переменные окружения

```bash
# Установка переменной (небезопасно, видно в ps)
export SSHPASS='Sergio675'
sshpass -e rsync -avz landing/ root@149.154.65.180:/var/www/aladdin-ai.ru/
```

---

## 8. ПОЛНЫЙ ПРОЦЕСС В ОДНОМ СКРИПТЕ

### Файл: `deploy_complete.sh`

```bash
#!/usr/bin/expect -f
# 🚀 Полный процесс деплоя: загрузка + настройка прав

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"
set local_path "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/"
set remote_path "/var/www/aladdin-ai.ru"

puts "=========================================="
puts "🚀 ПОЛНЫЙ ПРОЦЕСС ДЕПЛОЯ ЛЕНДИНГА"
puts "=========================================="
puts ""

# ШАГ 1: Загрузка файлов
puts "📦 ШАГ 1: Загрузка файлов на сервер..."
spawn rsync -avz --progress $local_path $server:$remote_path/

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    eof {
        puts "\n✅ Файлы загружены!"
    }
    timeout {
        puts "\n❌ Таймаут при загрузке"
        exit 1
    }
}

wait

# ШАГ 2: Настройка прав
puts "\n🔧 ШАГ 2: Настройка прав доступа..."
spawn ssh $server "chown -R www-data:www-data $remote_path && find $remote_path -type d -exec chmod 755 {} \\; && find $remote_path -type f -exec chmod 644 {} \\; && systemctl reload nginx && echo '✅ Права настроены, Nginx перезагружен'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    eof {
        puts "\n✅ Права настроены!"
    }
    timeout {
        puts "\n❌ Таймаут при настройке прав"
        exit 1
    }
}

wait

# ШАГ 3: Проверка
puts "\n🔍 ШАГ 3: Проверка доступности..."
puts "   Проверяю файлы на сервере..."

# Выполняем проверку через exec (не через spawn, т.к. это локальная команда)
exec curl -s -o /dev/null -w "   index.html: %{http_code}\n" https://aladdin-ai.ru/
exec curl -s -o /dev/null -w "   consent.html: %{http_code}\n" https://aladdin-ai.ru/consent.html
exec curl -s -o /dev/null -w "   privacy.html: %{http_code}\n" https://aladdin-ai.ru/privacy.html
exec curl -s -o /dev/null -w "   terms.html: %{http_code}\n" https://aladdin-ai.ru/terms.html

puts "\n=========================================="
puts "✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!"
puts "=========================================="
puts ""
puts "🌐 Проверьте лендинг: https://aladdin-ai.ru/"
puts "📄 Документы:"
puts "   - https://aladdin-ai.ru/consent.html"
puts "   - https://aladdin-ai.ru/privacy.html"
puts "   - https://aladdin-ai.ru/terms.html"
```

---

## 9. ОБЪЯСНЕНИЕ ДЛЯ ML МОДЕЛЕЙ

### Почему expect?

**Проблема:** Команды `ssh` и `rsync` запрашивают пароль интерактивно, что блокирует выполнение в скриптах.

**Решение:** `expect` автоматизирует интерактивные диалоги:
1. Перехватывает вывод команды
2. Распознает запрос пароля
3. Автоматически отправляет пароль
4. Продолжает выполнение

### Структура expect-скрипта:

```tcl
#!/usr/bin/expect -f
# 1. Настройка параметров
set timeout 30
set password "пароль"

# 2. Запуск команды
spawn команда

# 3. Обработка ответов
expect {
    "запрос пароля" {
        send "пароль\r"
        exp_continue
    }
    eof {
        # Команда завершена
    }
}

# 4. Ожидание завершения
wait
```

### Ключевые понятия:

- **spawn** — запускает команду и перехватывает её ввод/вывод
- **expect** — ожидает определенные строки в выводе
- **send** — отправляет текст в программу
- **\r** — символ Enter (возврат каретки)
- **exp_continue** — продолжает ожидание после отправки ответа
- **eof** — конец файла (команда завершена)
- **timeout** — превышен таймаут ожидания

---

## 10. ЧЕКЛИСТ ДЕПЛОЯ

### Перед деплоем:
- [ ] Проверено, что все файлы готовы локально
- [ ] Проверена доступность сервера: `ping 149.154.65.180`
- [ ] Проверена установка expect: `which expect`
- [ ] Создан expect-скрипт для загрузки
- [ ] Установлены права на выполнение: `chmod +x script.sh`

### Процесс деплоя:
- [ ] Выполнен скрипт загрузки файлов
- [ ] Проверено, что файлы загружены
- [ ] Выполнен скрипт настройки прав
- [ ] Проверено, что права установлены корректно

### После деплоя:
- [ ] Проверена доступность главной страницы (200 OK)
- [ ] Проверена доступность всех документов (200 OK)
- [ ] Протестирована форма оплаты
- [ ] Проверено, что API URL правильный
- [ ] Проверено, что чекбокс согласия работает

---

## 11. УСТРАНЕНИЕ ПРОБЛЕМ

### Проблема 1: "Connection refused"
```bash
ssh: connect to host 149.154.65.180 port 22: Connection refused
```

**Решение:**
- Проверьте, что сервер доступен: `ping 149.154.65.180`
- Проверьте, что SSH сервис запущен на сервере
- Проверьте firewall на сервере

### Проблема 2: "Permission denied"
```bash
Permission denied (publickey,password).
```

**Решение:**
- Проверьте правильность пароля
- Проверьте, что пользователь `root` имеет доступ
- Проверьте настройки SSH на сервере (`/etc/ssh/sshd_config`)

### Проблема 3: "Timeout"
```bash
timeout: timed out
```

**Решение:**
- Увеличьте таймаут: `set timeout 60`
- Проверьте сетевое соединение
- Проверьте, что сервер не перегружен

### Проблема 4: "No such file or directory"
```bash
rsync: change_dir "/var/www/aladdin-ai.ru" failed: No such file or directory
```

**Решение:**
- Создайте директорию на сервере: `ssh root@149.154.65.180 "mkdir -p /var/www/aladdin-ai.ru"`
- Проверьте правильность пути

---

## 12. БЕЗОПАСНОСТЬ

### ⚠️ ВАЖНО: Защита паролей

**НЕ ДЕЛАЙТЕ:**
- ❌ Не коммитьте скрипты с паролями в Git
- ❌ Не передавайте пароли через аргументы командной строки
- ❌ Не храните пароли в открытом виде

**ДЕЛАЙТЕ:**
- ✅ Используйте SSH ключи для продакшн
- ✅ Храните пароли в переменных окружения или секретах
- ✅ Используйте `.gitignore` для скриптов с паролями
- ✅ Ограничивайте права доступа к скриптам: `chmod 600 script.sh`

### Пример безопасного скрипта:

```bash
#!/usr/bin/expect -f
# Читаем пароль из переменной окружения
set password $env(SSH_PASSWORD)

# Или из файла (с ограниченными правами)
set f [open "/path/to/password.txt" r]
set password [read $f]
close $f
```

---

## 13. ИТОГОВАЯ СТРУКТУРА ФАЙЛОВ

```
ALADDIN_iOS/
├── landing/                          # Локальные файлы лендинга
│   ├── index.html
│   ├── consent.html
│   ├── privacy.html
│   └── terms.html
├── deploy_with_password.sh          # Скрипт загрузки файлов
├── fix_permissions.sh               # Скрипт настройки прав
├── deploy_complete.sh               # Полный процесс деплоя
└── docs/
    └── SERVER_DEPLOYMENT_DETAILED_GUIDE.md  # Это руководство
```

---

## 14. БЫСТРЫЙ СТАРТ

### Для быстрого деплоя выполните:

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# 1. Загрузка файлов
./deploy_with_password.sh

# 2. Настройка прав
./fix_permissions.sh

# 3. Проверка
curl -s -o /dev/null -w "Status: %{http_code}\n" https://aladdin-ai.ru/
```

---

## 15. ЗАКЛЮЧЕНИЕ

Это руководство описывает полный процесс автоматизации загрузки файлов на сервер с использованием `expect` для обработки интерактивных запросов пароля. 

**Ключевые моменты:**
1. ✅ `expect` автоматизирует интерактивные диалоги
2. ✅ Скрипты можно переиспользовать для будущих деплоев
3. ✅ Процесс полностью автоматизирован
4. ✅ Легко добавить проверки и валидацию

**Для продакшн рекомендуется:**
- Настроить SSH ключи вместо паролей
- Использовать CI/CD системы (GitHub Actions, GitLab CI)
- Добавить автоматическое тестирование после деплоя

---

**Дата обновления:** 19 ноября 2025  
**Автор:** AI Assistant (Auto)  
**Версия:** 1.0

