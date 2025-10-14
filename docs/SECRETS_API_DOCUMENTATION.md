# 🔐 Secrets API Documentation

## Обзор

Secrets API предоставляет стандартизированный интерфейс для управления секретами в системе ALADDIN Security. API поддерживает создание, получение, обновление, удаление и ротацию секретов с полной поддержкой метаданных, тегов и интеграции с внешними системами.

## Быстрый старт

### Инициализация

```python
from security.secrets_api import get_secrets_api

# Получение глобального экземпляра API
api = get_secrets_api()

# Или создание нового экземпляра
from security.secrets_api import SecretsAPI
from security.secrets_manager import SecretsManager

secrets_manager = SecretsManager()
api = SecretsAPI(secrets_manager)
api.initialize()
```

### Базовые операции

```python
# Создание секрета
result = api.create_secret(
    name="database_password",
    value="super_secret_password",
    secret_type="password",
    description="Пароль для базы данных"
)

# Получение секрета
secret = api.get_secret(result["secret_id"])
print(f"Пароль: {secret['value']}")

# Удаление секрета
api.delete_secret(result["secret_id"])
```

## API Reference

### SecretsAPI

Основной класс для работы с секретами.

#### Методы

##### create_secret()

Создание нового секрета.

**Параметры:**
- `name` (str): Название секрета
- `value` (str): Значение секрета
- `secret_type` (str, optional): Тип секрета (по умолчанию "custom")
- `expires_in_days` (int, optional): Срок действия в днях
- `tags` (dict, optional): Теги для категоризации
- `description` (str, optional): Описание секрета
- `owner` (str, optional): Владелец секрета

**Возвращает:**
```python
{
    "success": True,
    "secret_id": "abc123...",
    "name": "database_password",
    "type": "password",
    "created_at": "2025-01-26T10:00:00",
    "expires_at": "2025-02-25T10:00:00",
    "status": "active"
}
```

**Пример:**
```python
result = api.create_secret(
    name="api_key_production",
    value="sk-1234567890abcdef",
    secret_type="api_key",
    expires_in_days=90,
    description="API ключ для продакшена",
    tags={"environment": "production", "service": "api"},
    owner="admin"
)
```

##### get_secret()

Получение секрета по ID или имени.

**Параметры:**
- `identifier` (str): ID секрета или имя
- `by_name` (bool, optional): Поиск по имени (по умолчанию False)

**Возвращает:**
```python
{
    "success": True,
    "secret_id": "abc123...",
    "name": "database_password",
    "value": "super_secret_password",
    "type": "password",
    "status": "active",
    "created_at": "2025-01-26T10:00:00",
    "expires_at": "2025-02-25T10:00:00",
    "access_count": 5,
    "version": 1
}
```

**Примеры:**
```python
# Получение по ID
secret = api.get_secret("abc123...")

# Получение по имени
secret = api.get_secret("database_password", by_name=True)
```

##### update_secret()

Обновление секрета.

**Параметры:**
- `identifier` (str): ID секрета или имя
- `new_value` (str, optional): Новое значение секрета
- `new_name` (str, optional): Новое имя секрета
- `new_description` (str, optional): Новое описание
- `new_tags` (dict, optional): Новые теги
- `by_name` (bool, optional): Поиск по имени

**Возвращает:**
```python
{
    "success": True,
    "secret_id": "abc123...",
    "message": "Секрет успешно обновлен"
}
```

**Пример:**
```python
result = api.update_secret(
    "database_password",
    new_value="new_password",
    new_description="Обновленный пароль",
    by_name=True
)
```

##### delete_secret()

Удаление секрета.

**Параметры:**
- `identifier` (str): ID секрета или имя
- `by_name` (bool, optional): Поиск по имени

**Возвращает:**
```python
{
    "success": True,
    "message": "Секрет database_password успешно удален"
}
```

**Пример:**
```python
result = api.delete_secret("database_password", by_name=True)
```

##### rotate_secret()

Ротация секрета.

**Параметры:**
- `identifier` (str): ID секрета или имя
- `new_value` (str, optional): Новое значение (если не указано, генерируется автоматически)
- `by_name` (bool, optional): Поиск по имени

**Возвращает:**
```python
{
    "success": True,
    "secret_id": "abc123...",
    "name": "database_password",
    "version": 2,
    "message": "Секрет успешно ротирован"
}
```

**Пример:**
```python
# Автоматическая ротация
result = api.rotate_secret("database_password", by_name=True)

# Ротация с новым значением
result = api.rotate_secret(
    "database_password",
    new_value="new_rotated_password",
    by_name=True
)
```

##### list_secrets()

Получение списка секретов с фильтрацией.

**Параметры:**
- `secret_type` (str, optional): Фильтр по типу секрета
- `status` (str, optional): Фильтр по статусу
- `owner` (str, optional): Фильтр по владельцу
- `tags` (dict, optional): Фильтр по тегам
- `limit` (int, optional): Максимальное количество результатов
- `offset` (int, optional): Смещение для пагинации

**Возвращает:**
```python
{
    "success": True,
    "secrets": [
        {
            "secret_id": "abc123...",
            "name": "database_password",
            "type": "password",
            "status": "active",
            "created_at": "2025-01-26T10:00:00",
            "expires_at": "2025-02-25T10:00:00",
            "access_count": 5,
            "version": 1
        }
    ],
    "total_count": 1,
    "returned_count": 1,
    "offset": 0,
    "limit": 10
}
```

**Примеры:**
```python
# Все секреты
secrets = api.list_secrets()

# Фильтрация по типу
passwords = api.list_secrets(secret_type="password")

# Фильтрация по тегам
production_secrets = api.list_secrets(
    tags={"environment": "production"}
)

# Пагинация
page1 = api.list_secrets(limit=10, offset=0)
page2 = api.list_secrets(limit=10, offset=10)
```

##### search_secrets()

Поиск секретов по тексту.

**Параметры:**
- `query` (str): Поисковый запрос
- `search_in` (list, optional): Поля для поиска (по умолчанию ["name", "description", "tags"])

**Возвращает:**
```python
{
    "success": True,
    "query": "database",
    "results": [
        {
            "secret_id": "abc123...",
            "name": "database_password",
            "type": "password",
            "status": "active",
            "created_at": "2025-01-26T10:00:00",
            "description": "Пароль для базы данных"
        }
    ],
    "count": 1
}
```

**Пример:**
```python
results = api.search_secrets("database")
results = api.search_secrets("production", search_in=["tags"])
```

##### get_secret_metadata()

Получение метаданных секрета.

**Параметры:**
- `identifier` (str): ID секрета или имя
- `by_name` (bool, optional): Поиск по имени

**Возвращает:**
```python
{
    "success": True,
    "metadata": {
        "secret_id": "abc123...",
        "name": "database_password",
        "secret_type": "password",
        "created_at": "2025-01-26T10:00:00",
        "expires_at": "2025-02-25T10:00:00",
        "tags": {"environment": "production"},
        "description": "Пароль для базы данных",
        "owner": "admin",
        "access_count": 5,
        "last_accessed": "2025-01-26T15:30:00",
        "status": "active",
        "version": 1
    }
}
```

##### update_secret_metadata()

Обновление метаданных секрета.

**Параметры:**
- `identifier` (str): ID секрета или имя
- `description` (str, optional): Новое описание
- `tags` (dict, optional): Новые теги
- `owner` (str, optional): Новый владелец
- `by_name` (bool, optional): Поиск по имени

**Возвращает:**
```python
{
    "success": True,
    "secret_id": "abc123...",
    "message": "Метаданные секрета обновлены"
}
```

##### get_statistics()

Получение статистики по секретам.

**Возвращает:**
```python
{
    "success": True,
    "statistics": {
        "total_secrets": 100,
        "type_distribution": {
            "password": 50,
            "api_key": 30,
            "jwt_token": 20
        },
        "status_distribution": {
            "active": 95,
            "expired": 5
        },
        "total_access_count": 1000,
        "expired_secrets": 5,
        "manager_metrics": {
            "secrets_count": 100,
            "access_count": 1000,
            "rotation_count": 10,
            "error_count": 0,
            "external_sync_count": 50
        }
    }
}
```

##### get_health_status()

Получение статуса здоровья системы секретов.

**Возвращает:**
```python
{
    "success": True,
    "health": {
        "api_status": "running",
        "manager_status": "healthy",
        "secrets_count": 100,
        "external_providers": {
            "vault": True,
            "aws": False
        },
        "storage_writable": True,
        "rotation_active": True
    }
}
```

### Массовые операции

##### bulk_create_secrets()

Массовое создание секретов.

**Параметры:**
- `secrets_data` (list): Список данных для создания секретов

**Возвращает:**
```python
{
    "success": True,
    "total": 3,
    "success_count": 2,
    "error_count": 1,
    "results": [
        {"success": True, "secret_id": "abc123..."},
        {"success": True, "secret_id": "def456..."},
        {"success": False, "error": "Название секрета должно быть непустой строкой"}
    ]
}
```

**Пример:**
```python
secrets_data = [
    {
        "name": "secret1",
        "value": "value1",
        "secret_type": "password"
    },
    {
        "name": "secret2",
        "value": "value2",
        "secret_type": "api_key"
    }
]

result = api.bulk_create_secrets(secrets_data)
```

##### bulk_delete_secrets()

Массовое удаление секретов.

**Параметры:**
- `identifiers` (list): Список ID секретов или имен
- `by_name` (bool, optional): Поиск по имени

**Возвращает:**
```python
{
    "success": True,
    "total": 3,
    "success_count": 2,
    "error_count": 1,
    "results": [
        {"success": True, "message": "Секрет secret1 успешно удален"},
        {"success": True, "message": "Секрет secret2 успешно удален"},
        {"success": False, "error": "Секрет с именем 'nonexistent' не найден"}
    ]
}
```

##### bulk_rotate_secrets()

Массовая ротация секретов.

**Параметры:**
- `identifiers` (list): Список ID секретов или имен
- `by_name` (bool, optional): Поиск по имени

**Возвращает:**
```python
{
    "success": True,
    "total": 3,
    "success_count": 2,
    "error_count": 1,
    "results": [
        {"success": True, "secret_id": "abc123...", "version": 2},
        {"success": True, "secret_id": "def456...", "version": 2},
        {"success": False, "error": "Секрет с именем 'nonexistent' не найден"}
    ]
}
```

## Типы секретов

API поддерживает следующие типы секретов:

- `password` - Пароли
- `api_key` - API ключи
- `jwt_token` - JWT токены
- `encryption_key` - Ключи шифрования
- `database_credentials` - Учетные данные базы данных
- `external_service_token` - Токены внешних сервисов
- `ssh_key` - SSH ключи
- `certificate` - Сертификаты
- `config_secret` - Конфигурационные секреты
- `custom` - Пользовательские секреты

## Статусы секретов

- `active` - Активный
- `expired` - Истекший
- `revoked` - Отозванный
- `pending_rotation` - Ожидает ротации
- `error` - Ошибка

## Обработка ошибок

Все методы API возвращают словарь с полем `success` (bool) и либо данными, либо полем `error` с описанием ошибки.

**Примеры ошибок:**

```python
# Неверный тип секрета
{
    "error": "Неизвестный тип секрета: invalid_type"
}

# Секрет не найден
{
    "error": "Секрет с ID 'nonexistent' не найден"
}

# Пустое имя
{
    "error": "Название секрета должно быть непустой строкой"
}
```

## Интеграция с внешними системами

### HashiCorp Vault

```python
config = {
    "storage_path": "data/secrets",
    "external_providers": {
        "vault": {
            "vault_url": "http://localhost:8200",
            "token": "your-vault-token",
            "mount_point": "secret"
        }
    }
}

secrets_manager = SecretsManager(config)
api = SecretsAPI(secrets_manager)
```

### AWS Secrets Manager

```python
config = {
    "storage_path": "data/secrets",
    "external_providers": {
        "aws": {
            "region": "us-east-1"
        }
    }
}

secrets_manager = SecretsManager(config)
api = SecretsAPI(secrets_manager)
```

## Безопасность

### Шифрование

Все секреты шифруются с использованием Fernet (AES 128 в режиме CBC с HMAC-SHA256 для аутентификации).

### Аутентификация

API не предоставляет встроенную аутентификацию. Рекомендуется использовать внешние системы аутентификации и авторизации.

### Аудит

Все операции с секретами логируются с указанием:
- Времени операции
- Типа операции
- Идентификатора секрета
- Результата операции

## Производительность

### Рекомендации

- Используйте пагинацию для больших списков секретов
- Кэшируйте часто используемые секреты
- Используйте массовые операции для множественных изменений
- Регулярно ротируйте секреты

### Ограничения

- Максимальный размер секрета: 1MB
- Максимальная длина имени: 1000 символов
- Максимальное количество секретов: ограничено доступной памятью

## Примеры использования

### Управление паролями

```python
# Создание пароля
result = api.create_secret(
    name="user_password",
    value="secure_password_123",
    secret_type="password",
    expires_in_days=90,
    description="Пароль пользователя",
    tags={"user": "john_doe", "environment": "production"}
)

# Получение пароля
secret = api.get_secret(result["secret_id"])
password = secret["value"]

# Ротация пароля
api.rotate_secret(result["secret_id"], "new_secure_password")
```

### Управление API ключами

```python
# Создание API ключа
result = api.create_secret(
    name="stripe_api_key",
    value="sk_test_1234567890",
    secret_type="api_key",
    description="Stripe API ключ для тестирования",
    tags={"service": "stripe", "environment": "test"}
)

# Получение API ключа
secret = api.get_secret(result["secret_id"])
api_key = secret["value"]

# Автоматическая ротация
api.rotate_secret(result["secret_id"])
```

### Управление JWT токенами

```python
# Создание JWT токена
result = api.create_secret(
    name="user_session_token",
    value="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    secret_type="jwt_token",
    expires_in_days=1,
    description="JWT токен сессии пользователя",
    tags={"user": "john_doe", "session": "active"}
)

# Проверка токена
secret = api.get_secret(result["secret_id"])
if secret and secret["status"] == "active":
    token = secret["value"]
    # Использование токена
```

### Массовые операции

```python
# Массовое создание секретов
secrets_data = [
    {
        "name": f"service_{i}_api_key",
        "value": f"api_key_{i}",
        "secret_type": "api_key",
        "description": f"API ключ для сервиса {i}",
        "tags": {"service": f"service_{i}", "environment": "production"}
    }
    for i in range(10)
]

result = api.bulk_create_secrets(secrets_data)
print(f"Создано {result['success_count']} из {result['total']} секретов")

# Массовая ротация
secret_ids = [s["secret_id"] for s in result["results"] if s["success"]]
rotation_result = api.bulk_rotate_secrets(secret_ids)
print(f"Ротировано {rotation_result['success_count']} секретов")
```

### Поиск и фильтрация

```python
# Поиск по описанию
results = api.search_secrets("база данных")
print(f"Найдено {results['count']} секретов")

# Фильтрация по типу
passwords = api.list_secrets(secret_type="password")
print(f"Найдено {passwords['total_count']} паролей")

# Фильтрация по тегам
production_secrets = api.list_secrets(
    tags={"environment": "production"}
)
print(f"Найдено {production_secrets['total_count']} продакшен секретов")

# Пагинация
page1 = api.list_secrets(limit=10, offset=0)
page2 = api.list_secrets(limit=10, offset=10)
```

### Мониторинг и статистика

```python
# Получение статистики
stats = api.get_statistics()
print(f"Всего секретов: {stats['statistics']['total_secrets']}")
print(f"Активных: {stats['statistics']['status_distribution']['active']}")
print(f"Истекших: {stats['statistics']['expired_secrets']}")

# Проверка здоровья
health = api.get_health_status()
print(f"Статус API: {health['health']['api_status']}")
print(f"Статус менеджера: {health['health']['manager_status']}")
print(f"Внешние провайдеры: {health['health']['external_providers']}")
```

## Troubleshooting

### Частые проблемы

1. **Секрет не найден**
   - Проверьте правильность ID или имени
   - Убедитесь, что секрет не истек
   - Проверьте статус секрета

2. **Ошибка шифрования**
   - Проверьте целостность ключа шифрования
   - Убедитесь, что файл ключа не поврежден

3. **Проблемы с внешними провайдерами**
   - Проверьте подключение к Vault/AWS
   - Убедитесь в правильности токенов и ключей
   - Проверьте статус здоровья провайдеров

4. **Производительность**
   - Используйте пагинацию для больших списков
   - Кэшируйте часто используемые секреты
   - Оптимизируйте запросы

### Логирование

Все операции логируются в стандартный логгер Python. Уровень логирования можно настроить через конфигурацию.

```python
import logging

# Настройка уровня логирования
logging.getLogger("security.secrets_api").setLevel(logging.DEBUG)
```

## Заключение

Secrets API предоставляет мощный и гибкий интерфейс для управления секретами в системе ALADDIN Security. API поддерживает все необходимые операции, включая создание, получение, обновление, удаление и ротацию секретов, а также интеграцию с внешними системами управления секретами.

Для получения дополнительной информации обращайтесь к документации по компонентам системы или к команде разработки.