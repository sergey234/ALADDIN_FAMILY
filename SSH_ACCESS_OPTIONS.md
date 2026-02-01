# Анализ вариантов прямого SSH доступа для развертывания

## Цель
Реализовать развертывание ALADDIN API Gateway через прямое SSH подключение, минуя ограничения терминала.

---

## Вариант 1: Python Paramiko (рекомендуется)

### Что нужно:

1. **Библиотека paramiko:**
   ```bash
   pip3 install paramiko
   ```

2. **Доступ к Python:**
   - Python 3.6+
   - Возможность устанавливать пакеты через pip

3. **Сетевой доступ:**
   - Доступ к серверу `149.154.65.180:22` (SSH порт)
   - Нет блокировки исходящих соединений

4. **Права на чтение файлов:**
   - Доступ к `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/api_gateway_complete.py`
   - Доступ к `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/sfm_adapter.py`

### Что я могу сделать:

✅ **Полностью реализуемо:**
- Подключение к серверу через SSH
- Загрузка файлов через SFTP
- Выполнение команд на сервере
- Развертывание (backup → upload → синтаксис → замена → перезапуск → проверка)

### Пример реализации:

```python
#!/usr/bin/env python3
import paramiko
import os
from pathlib import Path

# Параметры
SERVER = "149.154.65.180"
USER = "root"
PASSWORD = "Sergio675"
REMOTE_PATH = "/opt/aladdin-backend"
LOCAL_PATH = Path("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")

# Подключение
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=30)

# SFTP для загрузки файлов
sftp = ssh.open_sftp()
sftp.put(str(LOCAL_PATH / "api_gateway_complete.py"), f"{REMOTE_PATH}/api_gateway_complete.py")
sftp.put(str(LOCAL_PATH / "sfm_adapter.py"), f"{REMOTE_PATH}/sfm_adapter.py")
sftp.close()

# Выполнение команд развертывания
commands = [
    f"cd {REMOTE_PATH}",
    "cp api_gateway.py api_gateway_backup_$(date +%Y%m%d_%H%M%S).py 2>/dev/null || echo 'Первый деплой'",
    "python3 -m py_compile api_gateway_complete.py",
    "cp api_gateway_complete.py api_gateway.py",
    "systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null",
    "sleep 10",
    "curl -s http://127.0.0.1:8002/api/health"
]

for cmd in commands:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode())
    if stderr.read():
        print(f"Ошибка: {stderr.read().decode()}")

ssh.close()
```

### Преимущества:
- ✅ Полный контроль над процессом
- ✅ Не требует терминала
- ✅ Можно обрабатывать ошибки
- ✅ Можно логировать каждый шаг

### Недостатки:
- ❌ Требует установки paramiko
- ❌ Требует сетевого доступа к серверу

---

## Вариант 2: Python Fabric

### Что нужно:

1. **Библиотека fabric:**
   ```bash
   pip3 install fabric
   ```

2. **Те же требования, что и для paramiko**

### Пример реализации:

```python
from fabric import Connection

c = Connection('root@149.154.65.180', connect_kwargs={'password': 'Sergio675'})

# Загрузка файлов
c.put('api_gateway_complete.py', '/opt/aladdin-backend/')
c.put('sfm_adapter.py', '/opt/aladdin-backend/')

# Выполнение команд
c.run('cd /opt/aladdin-backend && cp api_gateway.py api_gateway_backup_$(date +%Y%m%d_%H%M%S).py')
c.run('python3 -m py_compile api_gateway_complete.py')
c.run('cp api_gateway_complete.py api_gateway.py')
c.run('systemctl restart aladdin-api-gateway || systemctl restart aladdin-main-api-gateway')
```

### Преимущества:
- ✅ Более простой API чем paramiko
- ✅ Удобные методы для загрузки файлов

### Недостатки:
- ❌ Требует установки fabric
- ❌ Менее гибкий чем paramiko

---

## Вариант 3: Python Base64 через SSH (без SCP)

### Что нужно:

1. **Только стандартная библиотека Python:**
   - `base64` (встроена)
   - `subprocess` для expect (если нужен)
   - Или `paramiko` для SSH

2. **Те же требования к сетевому доступу**

### Пример реализации:

```python
import paramiko
import base64

ssh = paramiko.SSHClient()
ssh.connect('149.154.65.180', username='root', password='Sergio675')

# Читаем и кодируем файлы
with open('api_gateway_complete.py', 'rb') as f:
    content_b64 = base64.b64encode(f.read()).decode()

# Отправляем через SSH команду
stdin, stdout, stderr = ssh.exec_command(
    f"echo '{content_b64}' | base64 -d > /opt/aladdin-backend/api_gateway_complete.py"
)
print(stdout.read().decode())
```

### Преимущества:
- ✅ Не требует SCP/SFTP
- ✅ Работает через обычный SSH
- ✅ Можно использовать только стандартную библиотеку (если есть paramiko)

### Недостатки:
- ❌ Медленнее для больших файлов
- ❌ Ограничения на размер команды

---

## Вариант 4: Python pexpect

### Что нужно:

1. **Библиотека pexpect:**
   ```bash
   pip3 install pexpect
   ```

2. **Доступ к командам ssh/scp** (но не через терминал инструмента)

### Пример реализации:

```python
import pexpect

# SCP загрузка
child = pexpect.spawn('scp api_gateway_complete.py root@149.154.65.180:/opt/aladdin-backend/')
child.expect('password:')
child.sendline('Sergio675')
child.expect(pexpect.EOF)
```

### Преимущества:
- ✅ Работает как expect, но через Python
- ✅ Хорошо для интерактивных команд

### Недостатки:
- ❌ Требует доступ к командам ssh/scp
- ❌ Менее надежен чем paramiko

---

## Вариант 5: Готовые скрипты на сервере

### Что нужно:

1. **Способ загрузить скрипты на сервер** (один раз):
   - Через веб-интерфейс
   - Через другой механизм
   - Вручную

2. **SSH доступ для выполнения скриптов**

### Пример:

Если скрипты уже на сервере:
```python
import paramiko

ssh = paramiko.SSHClient()
ssh.connect('149.154.65.180', username='root', password='Sergio675')

# Выполняем готовый скрипт
stdin, stdout, stderr = ssh.exec_command('cd /opt/aladdin-backend && bash deploy_script.sh')
print(stdout.read().decode())
```

### Преимущества:
- ✅ Скрипты уже готовы
- ✅ Простое выполнение

### Недостатки:
- ❌ Нужен способ загрузить скрипты первый раз

---

## Что мне нужно для реализации (приоритеты)

### Минимальные требования:

1. ✅ **Python 3.6+** - уже есть
2. ✅ **Доступ к файлам** - есть через `read_file`
3. ❓ **Возможность установить paramiko:**
   ```python
   # Проверка
   try:
       import paramiko
   except ImportError:
       # Нужна возможность установить
       import subprocess
       subprocess.run(['pip3', 'install', 'paramiko'])
   ```

4. ❓ **Сетевой доступ к серверу:**
   - Проверка: `ping 149.154.65.180`
   - Проверка: `telnet 149.154.65.180 22`
   - Или попытка подключения через paramiko

### Проверка возможностей:

```python
# 1. Проверка Python
import sys
print(f"Python: {sys.version}")

# 2. Проверка paramiko
try:
    import paramiko
    print("✅ paramiko доступен")
except ImportError:
    print("❌ paramiko не установлен")
    # Попытка установить
    import subprocess
    result = subprocess.run(['pip3', 'install', 'paramiko'], 
                          capture_output=True, text=True)
    print(result.stdout)

# 3. Проверка сетевого доступа
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex(('149.154.65.180', 22))
    sock.close()
    if result == 0:
        print("✅ Сервер доступен на порту 22")
    else:
        print("❌ Сервер недоступен")
except Exception as e:
    print(f"❌ Ошибка проверки: {e}")

# 4. Проверка доступа к файлам
from pathlib import Path
files = [
    "api_gateway_complete.py",
    "sfm_adapter.py"
]
for f in files:
    path = Path(f"/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/{f}")
    if path.exists():
        print(f"✅ {f} доступен ({path.stat().st_size} bytes)")
    else:
        print(f"❌ {f} не найден")
```

---

## Рекомендуемый план действий

### Шаг 1: Проверка возможностей
- Проверить наличие Python
- Проверить возможность установки paramiko
- Проверить сетевой доступ к серверу
- Проверить доступ к файлам

### Шаг 2: Установка зависимостей
- Установить paramiko (если нужно)
- Проверить подключение к серверу

### Шаг 3: Реализация развертывания
- Использовать Вариант 1 (Paramiko) - самый надежный
- Или Вариант 3 (Base64 через SSH) - если paramiko недоступен

---

## Итоговый ответ: что мне нужно

### Для реализации через paramiko:

1. ✅ **Python 3.6+** - есть
2. ✅ **Доступ к файлам** - есть через `read_file`
3. ❓ **Возможность выполнить:**
   ```python
   import subprocess
   subprocess.run(['pip3', 'install', 'paramiko'])
   ```
   Или paramiko уже установлен

4. ❓ **Сетевой доступ:**
   - Проверка через `socket` или попытка подключения
   - Доступ к `149.154.65.180:22`

5. ✅ **Пароль:** `Sergio675` - известен

### Если paramiko недоступен:

Могу использовать **Вариант 3 (Base64 через SSH)** с subprocess и expect, но это требует:
- Доступ к команде `expect` (обычно есть на macOS/Linux)
- Возможность выполнить subprocess команды

---

## Вывод

**Мне нужно:**
1. Возможность установить/использовать `paramiko` (или он уже установлен)
2. Сетевой доступ к серверу `149.154.65.180:22`
3. Возможность выполнить Python код с сетевыми операциями

**Если эти условия выполнены - могу реализовать развертывание полностью через paramiko.**

**Если paramiko недоступен - могу попробовать Вариант 3 (Base64 через SSH) с expect.**



