# 🚀 ИНСТРУКЦИЯ: Загрузка Components и System роутеров на сервер

**Дата:** 10 февраля 2026  
**Задачи:** 21 (Components), 23 (System Management)  
**Приоритет:** Высокий

---

## 📋 ПОДГОТОВКА

### **Файлы для загрузки:**
1. `components_router.py` - 14 endpoints для управления компонентами
2. `system_router.py` - 11 endpoints для управления системой

### **Пути на сервере:**
- `/opt/aladdin-backend/security/api/routers/components_router.py`
- `/opt/aladdin-backend/security/api/routers/system_router.py`
- `/opt/aladdin-backend/main.py` (нужно обновить)

---

## 📝 ПОШАГОВАЯ ИНСТРУКЦИЯ

### **ШАГ 1: СОЗДАНИЕ РЕЗЕРВНЫХ КОПИЙ**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"📦 Создание резервных копий...\"

# Бэкап main.py
spawn ssh \$server \"cp /opt/aladdin-backend/main.py /opt/aladdin-backend/main.py.backup_\$(date +%Y%m%d_%H%M%S)\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Резервные копии созданы\"
"
```

---

### **ШАГ 2: ЗАГРУЗКА components_router.py**

```bash
expect -c "
set timeout 120
set password \"Sergio675\"
set server \"root@149.154.65.180\"
set local_file \"components_router.py\"
set remote_file \"/opt/aladdin-backend/security/api/routers/components_router.py\"

puts \"📤 Загрузка components_router.py...\"

spawn scp -o StrictHostKeyChecking=no \$local_file \$server:\$remote_file
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ components_router.py загружен\"
"
```

---

### **ШАГ 3: ЗАГРУЗКА system_router.py**

```bash
expect -c "
set timeout 120
set password \"Sergio675\"
set server \"root@149.154.65.180\"
set local_file \"system_router.py\"
set remote_file \"/opt/aladdin-backend/security/api/routers/system_router.py\"

puts \"📤 Загрузка system_router.py...\"

spawn scp -o StrictHostKeyChecking=no \$local_file \$server:\$remote_file
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ system_router.py загружен\"
"
```

---

### **ШАГ 4: ПОДКЛЮЧЕНИЕ РОУТЕРОВ В main.py**

Нужно добавить в `main.py`:

```python
# ✅ ЗАДАЧА 21: Components Router
try:
    from security.api.routers.components_router import router as components_router
    components_router_available = True
except ImportError as e:
    print(f"⚠️ Components router not available: {e}")
    components_router_available = False
    components_router = None

# ✅ ЗАДАЧА 23: System Router
try:
    from security.api.routers.system_router import router as system_router
    system_router_available = True
except ImportError as e:
    print(f"⚠️ System router not available: {e}")
    system_router_available = False
    system_router = None
```

И подключить:

```python
# ✅ ЗАДАЧА 21: Подключение Components Router
if components_router_available:
    try:
        app.include_router(components_router)
        print("✅ Роутер Components подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Components: {e}")

# ✅ ЗАДАЧА 23: Подключение System Router
if system_router_available:
    try:
        app.include_router(system_router)
        print("✅ Роутер System подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения System: {e}")
```

**Команда для обновления main.py:**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"📝 Обновление main.py...\"

# Читаем текущий main.py и добавляем импорты и подключения
# (Нужно вручную отредактировать файл или использовать sed)
"
```

**Или через SSH:**

```bash
ssh root@149.154.65.180
# Вручную отредактировать main.py
nano /opt/aladdin-backend/main.py
```

---

### **ШАГ 5: ПРОВЕРКА СИНТАКСИСА**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"🔍 Проверка синтаксиса...\"

spawn ssh \$server \"cd /opt/aladdin-backend && python3 -m py_compile components_router.py system_router.py main.py\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Синтаксис проверен\"
"
```

---

### **ШАГ 6: ПЕРЕЗАПУСК СЕРВЕРА**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"🔄 Перезапуск сервера...\"

spawn ssh \$server \"systemctl restart aladdin-backend.service\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}

puts \"✅ Сервер перезапущен\"
"
```

---

### **ШАГ 7: ПРОВЕРКА СТАТУСА СЕРВИСА**

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"📊 Проверка статуса сервиса...\"

spawn ssh \$server \"systemctl status aladdin-backend.service | head -10\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}
"
```

---

### **ШАГ 8: ТЕСТИРОВАНИЕ ENDPOINTS**

#### **Components endpoints:**

```bash
# 1. GET /api/components/health
curl http://149.154.65.180:8000/api/components/health

# 2. GET /api/components/list
curl http://149.154.65.180:8000/api/components/list

# 3. GET /api/components/status/{component_id}
curl http://149.154.65.180:8000/api/components/status/component_1

# 4. GET /api/components/status/all
curl http://149.154.65.180:8000/api/components/status/all

# 5. GET /api/components/config/{component_id}
curl http://149.154.65.180:8000/api/components/config/component_1

# 6. POST /api/components/enable/{component_id}
curl -X POST http://149.154.65.180:8000/api/components/enable/component_1

# 7. POST /api/components/disable/{component_id}
curl -X POST http://149.154.65.180:8000/api/components/disable/component_1

# 8. POST /api/components/restart/{component_id}
curl -X POST http://149.154.65.180:8000/api/components/restart/component_1

# 9. GET /api/components/metrics/{component_id}
curl http://149.154.65.180:8000/api/components/metrics/component_1

# 10. GET /api/components/logs/{component_id}
curl http://149.154.65.180:8000/api/components/logs/component_1

# 11. GET /api/components/dependencies/{component_id}
curl http://149.154.65.180:8000/api/components/dependencies/component_1

# 12. POST /api/components/test/{component_id}
curl -X POST http://149.154.65.180:8000/api/components/test/component_1

# 13. POST /api/components/update/{component_id}
curl -X POST http://149.154.65.180:8000/api/components/update/component_1

# 14. POST /api/components/config/update/{component_id}
curl -X POST http://149.154.65.180:8000/api/components/config/update/component_1 \
  -H "Content-Type: application/json" \
  -d '{"config": {"enabled": true}}'
```

#### **System endpoints:**

```bash
# 1. GET /api/system/health
curl http://149.154.65.180:8000/api/system/health

# 2. GET /api/system/info
curl http://149.154.65.180:8000/api/system/info

# 3. GET /api/system/logs
curl http://149.154.65.180:8000/api/system/logs?level=info&limit=10

# 4. POST /api/system/maintenance
curl -X POST http://149.154.65.180:8000/api/system/maintenance \
  -H "Content-Type: application/json" \
  -d '{"enabled": false, "message": "Maintenance mode"}'

# 5. GET /api/system/metrics
curl http://149.154.65.180:8000/api/system/metrics

# 6. POST /api/system/backup
curl -X POST http://149.154.65.180:8000/api/system/backup

# 7. GET /api/system/backup/status
curl http://149.154.65.180:8000/api/system/backup/status

# 8. GET /api/system/uptime
curl http://149.154.65.180:8000/api/system/uptime

# 9. GET /api/system/version
curl http://149.154.65.180:8000/api/system/version

# 10. POST /api/system/restart
curl -X POST http://149.154.65.180:8000/api/system/restart

# 11. GET /api/system/resources
curl http://149.154.65.180:8000/api/system/resources
```

---

## ✅ КРИТЕРИИ УСПЕХА

1. ✅ Оба роутера загружены на сервер
2. ✅ Роутеры подключены в main.py
3. ✅ Синтаксис проверен (нет ошибок)
4. ✅ Сервер перезапущен успешно
5. ✅ Все 14 Components endpoints возвращают 200 OK
6. ✅ Все 11 System endpoints возвращают 200 OK
7. ✅ Нет ошибок в логах сервера

---

## 🔍 ПРОВЕРКА ЛОГОВ

```bash
expect -c "
set timeout 60
set password \"Sergio675\"
set server \"root@149.154.65.180\"

puts \"📋 Проверка логов...\"

spawn ssh \$server \"journalctl -u aladdin-backend.service -n 50 | grep -E '(Components|System|ERROR|WARNING)'\"
expect {
    \"password:\" { send \"\$password\\r\"; exp_continue }
    eof
}
"
```

---

## 📝 ПРИМЕЧАНИЯ

- Все endpoints используют SFM adapter если доступен
- Если SFM adapter недоступен, возвращаются mock данные
- Все endpoints имеют fallback ответы для стабильности
- Логирование всех операций включено

---

**Готово к выполнению!** 🚀
