# 🔧 **ПОДКЛЮЧЕНИЕ И РАБОТА С СЕРВЕРОМ ALADDIN**

## 📋 **ОБЩАЯ ИНФОРМАЦИЯ**

### **Серверные данные:**
- **IP адрес**: `149.154.65.180`
- **Пользователь**: `root`
- **Пароль**: `Sergio675`
- **OS**: Ubuntu 24.04 LTS (Noble)
- **Python**: 3.12
- **Пути**:
  - `/opt/aladdin-backend/` - основная директория проекта
  - `/opt/aladdin-backend/venv/` - виртуальное окружение (старое)
  - `/opt/aladdin-backend/venvs/main_env/` - основное виртуальное окружение

---

## 🛠️ **НЕОБХОДИМЫЕ ИНСТРУМЕНТЫ**

### **На локальной машине (macOS):**
```bash
# Установить Homebrew (если нет):
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установить необходимые инструменты:
brew install openssh
brew install sshpass
brew install rsync
```

### **Проверка подключения:**
```bash
# Тест SSH подключения:
ssh -o StrictHostKeyChecking=no root@149.154.65.180 "echo 'SSH работает'"

# Или через sshpass:
sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180 "echo 'SSH работает'"
```

---

## 🔌 **ПОДКЛЮЧЕНИЕ К СЕРВЕРУ**

### **Способ 1: Прямой SSH (рекомендуемый)**
```bash
# Подключение:
ssh root@149.154.65.180

# Ввод пароля: Sergio675
```

### **Способ 2: SSH через sshpass (для скриптов)**
```bash
# Подключение с паролем:
sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180

# Выполнение команды:
sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180 "ls -la /opt/aladdin-backend/"
```

### **Способ 3: SCP для копирования файлов**
```bash
# Копирование файла на сервер:
scp -o StrictHostKeyChecking=no /path/to/local/file root@149.154.65.180:/path/to/remote/file

# С паролем через sshpass:
sshpass -p 'Sergio675' scp -o StrictHostKeyChecking=no local_file root@149.154.65.180:/remote/path/
```

---

## 📁 **СТРУКТУРА ПРОЕКТА НА СЕРВЕРЕ**

### **Основные директории:**
```
/opt/aladdin-backend/
├── api_gateway.py                 # Основной API файл
├── api_gateway_complete.py        # Полная версия API
├── sfm_adapter.py                 # Адаптер SFM
├── safe_function_manager.py       # SFM (старый)
├── requirements.txt               # Зависимости
├── venv/                          # Виртуальное окружение (старое)
├── venvs/main_env/                # Основное виртуальное окружение
├── security/                      # SFM компоненты
│   ├── safe_function_manager.py   # SFM основной файл
│   ├── sfm_singleton.py           # Singleton SFM
│   ├── core/                      # Базовые компоненты
│   ├── bots/                      # Боты и компоненты
│   └── ai_agents/                 # AI агенты
├── logs/                          # Логи
└── __pycache__/                   # Кэш Python
```

### **Сервисы:**
```bash
# API Gateway (порт 8001):
systemctl status aladdin-api-gateway

# Main API Gateway (порт 8002):
systemctl restart aladdin-main-api-gateway

# Nginx (прокси на 443):
systemctl status nginx
```

---

## 🚀 **РАБОТА С ВИРТУАЛЬНЫМ ОКРУЖЕНИЕМ**

### **Активация основного venv:**
```bash
# Переход в директорию проекта:
cd /opt/aladdin-backend

# Активация виртуального окружения:
source venvs/main_env/bin/activate

# Теперь Python команды будут использовать venv:
python3 --version
pip list

# Деактивация:
deactivate
```

### **Установка пакетов:**
```bash
# Активация venv:
source venvs/main_env/bin/activate

# Установка пакетов:
pip install package_name

# Или обновление:
pip install -r requirements.txt

# Деактивация:
deactivate
```

---

## 📊 **ПРОВЕРКА СТАТУСА СИСТЕМЫ**

### **Проверка API:**
```bash
# Health check основного API (порт 8002):
curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool

# Пример ответа:
{
    "status": "ok",
    "sfm_adapter": "fallback",
    "endpoints": 101,
    "groups": ["components", "security", "monitoring", "protection", "system"]
}
```

### **Проверка SFM:**
```bash
# Активация venv:
cd /opt/aladdin-backend && source venvs/main_env/bin/activate

# Тест SFM:
PYTHONPATH=/opt/aladdin-backend:$PYTHONPATH python3 -c "
from security.sfm_singleton import get_sfm
sfm = get_sfm()
print(f'SFM functions: {len(sfm.functions)}')
print(f'Status: {sfm.status}')
"

# Деактивация:
deactivate
```

### **Проверка логов:**
```bash
# Логи API:
journalctl -u aladdin-main-api-gateway -n 20

# Логи nginx:
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# Системные логи:
journalctl -n 50
```

---

## 🔄 **РАЗВЕРТЫВАНИЕ ИЗМЕНЕНИЙ**

### **Шаг 1: Подготовка**
```bash
# Создание backup:
cp /opt/aladdin-backend/api_gateway.py /opt/aladdin-backend/api_gateway.backup.$(date +%Y%m%d_%H%M%S)
cp /opt/aladdin-backend/sfm_adapter.py /opt/aladdin-backend/sfm_adapter.backup.$(date +%Y%m%d_%H%M%S)
```

### **Шаг 2: Копирование файлов**
```bash
# С локальной машины на сервер:
scp -o StrictHostKeyChecking=no api_gateway.py root@149.154.65.180:/opt/aladdin-backend/
scp -o StrictHostKeyChecking=no sfm_adapter.py root@149.154.65.180:/opt/aladdin-backend/
```

### **Шаг 3: Перезапуск сервиса**
```bash
# Перезапуск API:
systemctl restart aladdin-main-api-gateway

# Проверка статуса:
systemctl status aladdin-main-api-gateway

# Ожидание запуска (5-10 секунд):
sleep 10
```

### **Шаг 4: Тестирование**
```bash
# Проверка health:
curl -s http://127.0.0.1:8002/api/health

# Тест endpoint:
curl -s 'http://127.0.0.1:8002/api/phishing/sensitivity'

# Проверка логов на ошибки:
journalctl -u aladdin-main-api-gateway -n 10 | grep -i error
```

---

## 🧪 **ТЕСТИРОВАНИЕ API**

### **Основные endpoints для тестирования:**
```bash
# Health check:
curl -s http://127.0.0.1:8002/api/health

# Components:
curl -s 'http://127.0.0.1:8002/api/components/status/crash_detection_agent'

# Security:
curl -s 'http://127.0.0.1:8002/api/phishing/sensitivity'
curl -s 'http://127.0.0.1:8002/api/malware/scan_scheduled'

# Analytics:
curl -s 'http://127.0.0.1:8002/api/analytics/overview'

# Protection:
curl -s 'http://127.0.0.1:8002/api/darkweb/leaks'
```

### **Load testing:**
```bash
# Простой load test:
for i in {1..50}; do
  curl -s http://127.0.0.1:8002/api/health > /dev/null &
done
wait
echo "Load test completed"
```

---

## 🔧 **ОТЛАДКА ПРОБЛЕМ**

### **Если API не запускается:**
```bash
# Проверить логи:
journalctl -u aladdin-main-api-gateway -n 20

# Проверить синтаксис:
cd /opt/aladdin-backend && source venvs/main_env/bin/activate
python3 -m py_compile api_gateway.py
python3 -c "import sfm_adapter"
deactivate
```

### **Если SFM не работает:**
```bash
# Тест SFM изолированно:
cd /opt/aladdin-backend && source venvs/main_env/bin/activate
PYTHONPATH=/opt/aladdin-backend:$PYTHONPATH python3 -c "
try:
    from security.sfm_singleton import get_sfm
    sfm = get_sfm()
    print('SFM OK')
except Exception as e:
    print(f'SFM Error: {e}')
"
deactivate
```

### **Если соединение потеряно:**
```bash
# Переподключение:
sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@149.154.65.180

# Или через screen/tmux для стабильности:
ssh root@149.154.65.180
apt install screen
screen -S aladdin
# Теперь сессия не прервется при разрыве
```

---

## 📈 **МОНИТОРИНГ ПРОИЗВОДИТЕЛЬНОСТИ**

### **Проверка ресурсов:**
```bash
# CPU и память:
top -n 1 | head -10

# Диск:
df -h

# Процессы API:
ps aux | grep uvicorn

# Сеть:
netstat -tulnp | grep :800
```

### **Мониторинг API:**
```bash
# Активные соединения:
ss -tulnp | grep :8002

# Ошибки в логах:
journalctl -u aladdin-main-api-gateway --since "1 hour ago" | grep -i error | wc -l
```

---

## 🔄 **BACKUP И RESTORE**

### **Полный backup:**
```bash
# Создание полного архива:
cd /opt
tar -czf aladdin_backup_$(date +%Y%m%d_%H%M%S).tar.gz aladdin-backend/

# Копирование на локальную машину:
scp root@149.154.65.180:/opt/aladdin_backup_*.tar.gz ~/Desktop/
```

### **Restore:**
```bash
# Остановка сервисов:
systemctl stop aladdin-main-api-gateway
systemctl stop nginx

# Распаковка:
cd /opt
tar -xzf aladdin_backup_20260202_120000.tar.gz

# Запуск:
systemctl start nginx
systemctl start aladdin-main-api-gateway
```

---

## ⚠️ **ВАЖНЫЕ ЗАМЕЧАНИЯ**

### **Безопасность:**
- Всегда используйте `StrictHostKeyChecking=no` только для известных серверов
- Не храните пароли в скриптах в открытом виде
- Регулярно меняйте пароли

### **Производительность:**
- API использует 4 workers по умолчанию
- SFM может загружаться 30-60 секунд
- Nginx проксирует с таймаутом 30 секунд

### **Отладка:**
- Используйте `journalctl` для просмотра логов
- `python3 -c` для быстрого тестирования
- `screen` или `tmux` для долгих сессий

### **Резервные планы:**
- Всегда имейте backup рабочих файлов
- Тестируйте изменения на копии перед продакшеном
- Имейте план отката в случае проблем

---

## 🎯 **КОМПЛЕКТ КОМАНД ДЛЯ БЫСТРОГО СТАРТА**

```bash
# 1. Подключение:
sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180

# 2. Переход в проект:
cd /opt/aladdin-backend && source venvs/main_env/bin/activate

# 3. Проверка статуса:
curl -s http://127.0.0.1:8002/api/health

# 4. Тест SFM:
PYTHONPATH=/opt/aladdin-backend:$PYTHONPATH python3 -c "from security.sfm_singleton import get_sfm; sfm = get_sfm(); print(f'Functions: {len(sfm.functions)}')"

# 5. Перезапуск API:
deactivate && systemctl restart aladdin-main-api-gateway

# 6. Проверка после перезапуска:
sleep 5 && curl -s http://127.0.0.1:8002/api/health
```

**Теперь любая ML система может подключиться и работать с сервером ALADDIN!** 🚀