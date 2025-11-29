# 📝 S3-12: ЦЕНТРАЛИЗОВАННОЕ ЛОГИРОВАНИЕ

**Статус:** В процессе  
**Дата:** 2025-11-27

---

## ✅ ЧТО УЖЕ СДЕЛАНО

1. **Директории созданы** ✅
   - `/var/log/aladdin/api_gateway/`
   - `/var/log/aladdin/managers/`
   - `/var/log/aladdin/agents/`
   - `/var/log/aladdin/bots/`
   - `/var/log/aladdin/microservices/`

2. **python-json-logger установлен** ✅

3. **Скрипт настройки создан** ✅
   - `/tmp/setup_centralized_logging.py`

---

## 🔧 ЧТО НУЖНО СДЕЛАТЬ

### 1. Выполнить скрипт настройки
```bash
cd /opt/aladdin-backend
source venvs/main_env/bin/activate
python3 /tmp/setup_centralized_logging.py
```

### 2. Обновить код для использования централизованного логирования

**Файлы для обновления:**
- `/opt/aladdin-backend/security/microservices/api_gateway.py`
- `/opt/aladdin-backend/security/managers/*.py`
- `/opt/aladdin-backend/security/ai_agents/*.py`
- `/opt/aladdin-backend/security/bots/*.py`

**Изменения:**
```python
# Было:
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Станет:
from security.utils.logging_utils import setup_logging, get_logger
setup_logging()
logger = get_logger(__name__)
```

### 3. Настроить logrotate

Создать `/etc/logrotate.d/aladdin`:
```
/var/log/aladdin/*/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
    sharedscripts
    postrotate
        systemctl reload aladdin-api-gateway > /dev/null 2>&1 || true
    endscript
}
```

### 4. Перезапустить сервисы

```bash
systemctl restart aladdin-api-gateway
systemctl restart aladdin-backend
```

---

## 📋 ПРОВЕРКА

1. Проверить создание логов:
```bash
ls -lh /var/log/aladdin/*/*.log
```

2. Проверить формат (JSON):
```bash
tail -n 1 /var/log/aladdin/api_gateway/api_gateway.log | python3 -m json.tool
```

3. Проверить ротацию:
```bash
logrotate -d /etc/logrotate.d/aladdin
```

---

**Готово к выполнению!** 🚀

