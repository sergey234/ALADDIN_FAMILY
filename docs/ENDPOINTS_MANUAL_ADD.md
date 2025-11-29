# 📝 РУКОВОДСТВО: ДОБАВЛЕНИЕ ENDPOINTS ВРУЧНУЮ

**Дата:** 2025-11-26  
**Проблема:** Команды `sed` и `expect` создают ошибки при добавлении многострочного кода

---

## ✅ РЕШЕНИЕ: ДОБАВИТЬ ВРУЧНУЮ

### Файл для редактирования:
`/opt/aladdin-backend/security/microservices/api_gateway.py`

---

## 📋 ЧТО НУЖНО ДОБАВИТЬ

### 1. Импорты (после строки 56):
```python
from security.managers.monitor_manager import MonitorManager, MonitorConfig
from security.managers.alert_manager import AlertManager
```

### 2. Глобальные переменные (после `sleep_manager = None`):
```python
monitor_manager = None
alert_manager = None
```

### 3. Инициализация и endpoints (перед `if __name__ == "__main__":`):
См. файл `docs/ENDPOINTS_CODE_TO_ADD.md`

---

## 🔧 КАК ДОБАВИТЬ

### Вариант 1: Через SSH и nano/vi
```bash
ssh root@149.154.65.180
cd /opt/aladdin-backend/security/microservices
nano api_gateway.py
# Добавить код в нужных местах
```

### Вариант 2: Через Python скрипт (без expect)
Создать скрипт локально, загрузить через scp, выполнить на сервере

---

**Готово к добавлению!** 📝

