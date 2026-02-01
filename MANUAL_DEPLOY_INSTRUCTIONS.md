# 🚀 РУЧНОЕ РАЗВЕРТЫВАНИЕ API GATEWAY НА СЕРВЕР

**Дата:** 30 января 2026
**Сервер:** 149.154.65.180
**Пользователь:** root
**Пароль:** Sergio675

---

## 📋 ПРОВЕРКА СЕРВЕРА (ВЫПОЛНИТЬ ВРУЧНУЮ)

### ШАГ 1: Подключиться к серверу
```bash
ssh root@149.154.65.180
# Пароль: Sergio675
```

### ШАГ 2: Проверить файлы
```bash
cd /opt/aladdin-backend
ls -la
# Должны быть: api_gateway.py, sfm_adapter.py, safe_function_manager.py
```

### ШАГ 3: Проверить статус сервиса
```bash
systemctl status aladdin-api-gateway --no-pager
# или
systemctl status aladdin-main-api-gateway --no-pager
```

---

## 🛡️ РЕЗЕРВНОЕ КОПИРОВАНИЕ (ВЫПОЛНИТЬ ВРУЧНУЮ)

### ШАГ 1: Создать backup директорию
```bash
cd /opt/aladdin-backend
mkdir -p backup_before_deployment_$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=backup_before_deployment_$(date +%Y%m%d_%H%M%S)
```

### ШАГ 2: Сохранить текущие файлы
```bash
# Сохранить API Gateway
cp api_gateway.py $BACKUP_DIR/ 2>/dev/null || echo "api_gateway.py не найден"

# Сохранить SFM адаптер
cp sfm_adapter.py $BACKUP_DIR/ 2>/dev/null || echo "sfm_adapter.py не найден"

# Сохранить systemd сервис
cp /etc/systemd/system/aladdin-api-gateway.service $BACKUP_DIR/ 2>/dev/null || \
cp /etc/systemd/system/aladdin-main-api-gateway.service $BACKUP_DIR/ 2>/dev/null || \
echo "systemd сервис не найден"

# Сохранить nginx конфигурацию
cp /etc/nginx/sites-available/aladdin-ai.ru $BACKUP_DIR/ 2>/dev/null || \
echo "nginx конфигурация не найдена"
```

### ШАГ 3: Создать архив backup
```bash
tar -czf ${BACKUP_DIR}.tar.gz $BACKUP_DIR
echo "✅ Backup создан: ${BACKUP_DIR}.tar.gz"
```

---

## 📤 ЗАГРУЗКА ФАЙЛОВ НА СЕРВЕР (ВЫПОЛНИТЬ ИЗ ЛОКАЛЬНОЙ МАШИНЫ)

### ШАГ 1: Из локальной директории проекта
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
```

### ШАГ 2: Загрузить api_gateway_complete.py
```bash
scp api_gateway_complete.py root@149.154.65.180:/opt/aladdin-backend/
# Пароль: Sergio675
```

### ШАГ 3: Загрузить sfm_adapter.py
```bash
scp sfm_adapter.py root@149.154.65.180:/opt/aladdin-backend/
# Пароль: Sergio675
```

---

## 🔄 ЗАМЕНА И ПЕРЕЗАПУСК (ВЫПОЛНИТЬ НА СЕРВЕРЕ)

### ШАГ 1: Подключиться к серверу
```bash
ssh root@149.154.65.180
cd /opt/aladdin-backend
```

### ШАГ 2: Заменить API Gateway
```bash
# Создать backup текущего файла
cp api_gateway.py api_gateway_backup_manual_$(date +%Y%m%d_%H%M%S).py 2>/dev/null || echo "Первый деплой"

# Заменить на новую версию
cp api_gateway_complete.py api_gateway.py
echo "✅ API Gateway заменен"
```

### ШАГ 3: Проверить синтаксис
```bash
python3 -m py_compile api_gateway.py && echo "✅ Синтаксис OK"
python3 -c "from sfm_adapter import sfm_adapter; print('✅ SFM Adapter OK')"
```

### ШАГ 4: Перезапустить сервис
```bash
# Попробовать разные варианты
systemctl restart aladdin-api-gateway 2>/dev/null || \
systemctl restart aladdin-main-api-gateway 2>/dev/null || \
echo "⚠️ Сервис не найден, возможно нужно создать systemd unit"
```

### ШАГ 5: Проверить статус
```bash
systemctl status aladdin-api-gateway --no-pager 2>/dev/null || \
systemctl status aladdin-main-api-gateway --no-pager 2>/dev/null || \
echo "⚠️ Сервис статус неизвестен"
```

---

## 🧪 ТЕСТИРОВАНИЕ (ВЫПОЛНИТЬ НА СЕРВЕРЕ)

### ШАГ 1: Тест локального API
```bash
# Health endpoint
curl -s http://localhost:8002/api/health | python3 -m json.tool

# Тест компонентов
curl -s http://localhost:8002/api/components/status/test | python3 -m json.tool

# Тест AI категорий
curl -s http://localhost:8002/api/ai/categories/stats | python3 -m json.tool

# Тест darkweb
curl -s http://localhost:8002/api/darkweb/stats | python3 -m json.tool

# Тест уведомлений
curl -s http://localhost:8002/api/notifications/unread_count | python3 -m json.tool
```

### ШАГ 2: Тест внешнего API (с другого терминала)
```bash
# Через домен
curl -s https://aladdin-ai.ru/api/health | python3 -m json.tool

# Через IP
curl -s http://149.154.65.180/api/health | python3 -m json.tool
```

---

## 🔄 ОТКАТ В СЛУЧАЕ ПРОБЛЕМ (ВЫПОЛНИТЬ НА СЕРВЕРЕ)

### ШАГ 1: Восстановить из backup
```bash
cd /opt/aladdin-backend

# Найти последний backup
ls -la *backup* | tail -5

# Восстановить API Gateway
cp api_gateway_backup_manual_*.py api_gateway.py 2>/dev/null || \
cp backup_before_deployment_*/api_gateway.py . 2>/dev/null || \
echo "❌ Backup не найден"

# Перезапустить
systemctl restart aladdin-api-gateway 2>/dev/null || \
systemctl restart aladdin-main-api-gateway 2>/dev/null
```

---

## 📊 ПРОВЕРКА РАЗВЕРТЫВАНИЯ

### Ожидаемые результаты:
```json
{
  "status": "ok",
  "sfm_adapter": "available",
  "endpoints": 101,
  "groups": ["components", "security", "monitoring", "protection", "system"]
}
```

### Все endpoints должны возвращать:
- `"source": "sfm"` - при успешной SFM интеграции
- `"source": "mock"` - при fallback

---

## 🎯 ЧЕКЛИСТ РАЗВЕРТЫВАНИЯ

- [ ] Подключен к серверу (ssh root@149.154.65.180)
- [ ] Создан backup (backup_before_deployment_*.tar.gz)
- [ ] Загружен api_gateway_complete.py
- [ ] Загружен sfm_adapter.py
- [ ] API Gateway заменен (api_gateway.py)
- [ ] Синтаксис проверен (python3 -m py_compile)
- [ ] Сервис перезапущен (systemctl restart)
- [ ] Health endpoint работает (/api/health)
- [ ] Тестирование пройдено (5+ endpoints)
- [ ] Внешний доступ работает (через домен/IP)

---

## 🚨 ЕСЛИ ЧТО-ТО ПОШЛО НЕ ТАК

1. **Откат из backup:**
   ```bash
   cd /opt/aladdin-backend
   tar -xzf backup_before_deployment_*.tar.gz
   cp backup_before_deployment_*/api_gateway.py .
   systemctl restart aladdin-api-gateway
   ```

2. **Проверить логи:**
   ```bash
   journalctl -u aladdin-api-gateway -n 50 --no-pager
   journalctl -u aladdin-main-api-gateway -n 50 --no-pager
   ```

3. **Проверить порт:**
   ```bash
   netstat -tlnp | grep 8002
   ss -tlnp | grep 8002
   ```

4. **Проверить nginx:**
   ```bash
   nginx -t
   systemctl status nginx
   ```

---

**ВЫПОЛНИТЬ ВСЕ ШАГИ ПО ПОРЯДКУ! ЕСЛИ ЧТО-ТО НЕ ЯСНО - СПРОСИТЬ!**


