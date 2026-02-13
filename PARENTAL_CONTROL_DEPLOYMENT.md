# 📤 Инструкция по загрузке Parental Control Sync Router на сервер

## Файлы для загрузки:

1. **parental_control_sync_router.py** → `/opt/aladdin-backend/security/api/routers/`
2. **main.py** (обновленный) → `/opt/aladdin-backend/` (или где находится main.py)

## Команды для загрузки:

```bash
# 1. Загрузить router
scp parental_control_sync_router.py root@149.154.65.180:/opt/aladdin-backend/security/api/routers/

# 2. Загрузить обновленный main.py (если нужно)
scp main.py.server root@149.154.65.180:/opt/aladdin-backend/main.py

# 3. Перезапустить сервис
ssh root@149.154.65.180 "systemctl restart aladdin-main-api-gateway"
```

## Проверка:

```bash
# Проверить, что router загружен
ssh root@149.154.65.180 "ls -lh /opt/aladdin-backend/security/api/routers/parental_control_sync_router.py"

# Проверить логи сервиса
ssh root@149.154.65.180 "journalctl -u aladdin-main-api-gateway -n 50 | grep -i parental"
```

## Тестирование:

```bash
# Запустить тестовый скрипт
./test_parental_control_api.sh http://149.154.65.180:8000 family_001 child_123
```
