# 🚀 ИНСТРУКЦИЯ ПО РАЗВЕРТЫВАНИЮ ALADDIN API GATEWAY

## Сервер: 149.154.65.180
## Пользователь: root
## Пароль: Sergio675
## Путь на сервере: /opt/aladdin-backend

## ШАГ 1: Загрузка файлов на сервер

Выполните в терминале (из директории проекта):

```bash
# Загрузка api_gateway_complete.py
scp api_gateway_complete.py root@149.154.65.180:/opt/aladdin-backend/

# Загрузка sfm_adapter.py
scp sfm_adapter.py root@149.154.65.180:/opt/aladdin-backend/
```

## ШАГ 2: Подключение к серверу и развертывание

```bash
ssh root@149.154.65.180
```

После подключения выполните:

```bash
cd /opt/aladdin-backend

# Создание backup
cp api_gateway.py api_gateway_backup_$(date +%Y%m%d_%H%M%S).py

# Проверка синтаксиса
python3 -m py_compile api_gateway_complete.py

# Замена api_gateway.py
cp api_gateway_complete.py api_gateway.py

# Перезапуск сервиса
systemctl restart aladdin-api-gateway || systemctl restart aladdin-main-api-gateway

# Ожидание 10 секунд
sleep 10

# Проверка health endpoint
curl http://127.0.0.1:8002/api/health | python3 -m json.tool
```

## ШАГ 3: Проверка извне

```bash
curl http://149.154.65.180/api/health
curl https://aladdin-ai.ru/api/health
```

## Альтернатива: Использование готовых скриптов

Если у вас установлен expect:

```bash
chmod +x deploy_api_gateway_final.exp
./deploy_api_gateway_final.exp
```

Или используйте bash скрипт:

```bash
chmod +x deploy_now.sh
./deploy_now.sh
```

Или Python скрипт:

```bash
python3 deploy_python.py
```



