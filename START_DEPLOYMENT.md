# 🚀 ГОТОВО К РАЗВЕРТЫВАНИЮ ALADDIN API GATEWAY

## ✅ Что подготовлено:

1. **api_gateway_complete.py** - API Gateway со всеми 101 endpoint
2. **sfm_adapter.py** - SFM адаптер для связи с AI-функциями
3. **5 скриптов для развертывания:**
   - `deploy_now.sh` - Bash скрипт с expect
   - `deploy_python.py` - Python скрипт
   - `deploy_api_gateway_final.exp` - Expect скрипт (самый полный)
   - `check_server_before_deploy.exp` - Проверка сервера
   - `create_backup_before_deploy.exp` - Создание backup

## 🎯 БЫСТРОЕ РАЗВЕРТЫВАНИЕ (выберите один способ):

### Способ 1: Expect скрипт (рекомендуется)
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
chmod +x deploy_api_gateway_final.exp
./deploy_api_gateway_final.exp
```

### Способ 2: Bash скрипт
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
chmod +x deploy_now.sh
./deploy_now.sh
```

### Способ 3: Python скрипт
```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 deploy_python.py
```

### Способ 4: Ручное развертывание
Смотрите файл `COMMANDS_TO_RUN.txt` для пошаговых команд

## 📋 Что делает развертывание:

1. ✅ Создает backup текущей версии
2. ✅ Загружает `api_gateway_complete.py` на сервер
3. ✅ Загружает `sfm_adapter.py` на сервер
4. ✅ Проверяет синтаксис Python
5. ✅ Заменяет `api_gateway.py` на новую версию
6. ✅ Перезапускает сервис API Gateway
7. ✅ Тестирует health endpoint

## 🔍 После развертывания проверьте:

```bash
curl http://149.154.65.180/api/health
curl https://aladdin-ai.ru/api/health
```

Ожидаемый ответ:
```json
{
  "status": "ok",
  "sfm_adapter": "available",
  "endpoints": 101,
  "groups": ["components", "security", "monitoring", "protection", "system"]
}
```

## 📝 Детали сервера:

- **IP:** 149.154.65.180
- **Пользователь:** root
- **Пароль:** Sergio675
- **Путь:** /opt/aladdin-backend
- **Порт API:** 8002

## ⚠️ Если что-то пошло не так:

1. Проверьте сервер: `./check_server_before_deploy.exp`
2. Создайте backup: `./create_backup_before_deploy.exp`
3. Проверьте логи: `ssh root@149.154.65.180 "journalctl -u aladdin-api-gateway -n 50"`

---

**Готово к запуску! Выберите один из способов выше и выполните развертывание.**



