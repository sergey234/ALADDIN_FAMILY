# 🛡️ ALADDIN Enhanced Services

Улучшенные версии Interactive API Docs и Real-time Architecture Visualizer с реальной интеграцией с системой безопасности ALADDIN.

## 🚀 Возможности

### 📡 Enhanced API Docs (Порт 8080)
- **Реальная интеграция с ALADDIN**: Автоматическое сканирование API endpoints из security/microservices/
- **Безопасность**: JWT аутентификация, rate limiting, роли пользователей
- **Интерактивное тестирование**: Реальные HTTP запросы к API endpoints
- **История тестов**: Сохранение результатов в SQLite базе данных
- **Экспорт данных**: JSON/CSV форматы
- **Улучшенный UI**: Поиск, фильтрация, темная/светлая тема

### 🏗️ Enhanced Architecture Visualizer (Порт 8081)
- **Мониторинг без Docker**: Использование psutil для мониторинга Python процессов
- **Real-time обновления**: WebSocket соединения для живых обновлений
- **Мониторинг портов**: Отслеживание статуса портов 8006-8012
- **Системные метрики**: CPU, RAM, диск, сеть
- **Алерты**: Автоматическое обнаружение проблем
- **3D визуализация**: Интерактивная диаграмма архитектуры

## 📋 Требования

### Системные требования
- Python 3.8+
- macOS/Linux/Windows
- Минимум 2GB RAM
- Свободные порты 8080, 8081

### Python зависимости
```bash
pip install fastapi uvicorn psutil httpx sqlite3
```

### Опциональные зависимости для полной интеграции
- ALADDIN Security System
- Redis (для кэширования)
- PostgreSQL (для расширенной аналитики)

## 🚀 Быстрый старт

### 1. Автоматический запуск (рекомендуется)
```bash
cd ALADDIN_NEW
python3 start_enhanced_services.py
```

### 2. Ручной запуск

#### Enhanced API Docs
```bash
cd ALADDIN_NEW
python3 enhanced_api_docs.py
```

#### Enhanced Architecture Visualizer
```bash
cd ALADDIN_NEW
python3 enhanced_architecture_visualizer.py
```

## 🌐 Доступ к сервисам

После запуска сервисы будут доступны по адресам:

- **Enhanced API Docs**: http://localhost:8080
- **Enhanced Architecture Visualizer**: http://localhost:8081

## 🔧 Конфигурация

### Переменные окружения
```bash
# Порт для API Docs (по умолчанию 8080)
export API_DOCS_PORT=8080

# Порт для Architecture Visualizer (по умолчанию 8081)
export ARCH_VISUALIZER_PORT=8081

# Режим интеграции с ALADDIN (true/false)
export ALADDIN_INTEGRATION=true

# JWT секретный ключ
export JWT_SECRET_KEY=your_secret_key_here
```

### Конфигурация портов ALADDIN
Порты для мониторинга настраиваются в файле `enhanced_architecture_visualizer.py`:

```python
self.aladdin_ports = {
    "API Gateway": 8006,
    "Load Balancer": 8007,
    "Rate Limiter": 8008,
    "Circuit Breaker": 8009,
    "User Interface Manager": 8010,
    "SafeFunctionManager": 8011,
    "Service Mesh": 8012
}
```

## 📊 Мониторинг и метрики

### API Docs метрики
- Количество обнаруженных endpoints
- Количество выполненных тестов
- Процент успешных тестов
- Время отклика API

### Architecture Visualizer метрики
- Статус сервисов (running/stopped/error)
- Использование CPU и RAM
- Сетевые соединения
- Системные алерты

### База данных
Метрики сохраняются в SQLite базах данных:
- `api_docs.db` - история тестов API
- `architecture_monitor.db` - метрики архитектуры

## 🔐 Безопасность

### JWT Аутентификация
```python
# Получение токена
curl -X POST "http://localhost:8080/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Использование токена
curl -X GET "http://localhost:8080/api/endpoints" \
  -H "Authorization: Bearer your_jwt_token"
```

### Rate Limiting
- 1000 запросов в час для обычных пользователей
- 10000 запросов в час для администраторов
- Автоматическая блокировка при превышении лимитов

## 🧪 Тестирование API

### Интерактивное тестирование через UI
1. Откройте http://localhost:8080
2. Выберите endpoint из списка
3. Выберите HTTP метод
4. Нажмите "Тестировать"
5. Просмотрите результаты

### Программное тестирование
```python
import httpx

async def test_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8080/api/test",
            params={
                "endpoint": "/health",
                "method": "GET"
            },
            headers={"Authorization": "Bearer your_token"}
        )
        print(response.json())
```

## 📈 Экспорт данных

### JSON экспорт
```bash
curl "http://localhost:8080/api/export/json" \
  -H "Authorization: Bearer your_token"
```

### CSV экспорт
```bash
curl "http://localhost:8080/api/export/csv" \
  -H "Authorization: Bearer your_token"
```

## 🔄 WebSocket обновления

### Подключение к Architecture Visualizer
```javascript
const ws = new WebSocket('ws://localhost:8081/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Architecture update:', data);
};
```

## 🐛 Устранение неполадок

### Проблемы с запуском
1. **Порт занят**: Измените порт в конфигурации
2. **Зависимости не установлены**: Выполните `pip install -r requirements.txt`
3. **ALADDIN не найден**: Проверьте пути к модулям

### Проблемы с интеграцией
1. **Mock режим**: Убедитесь, что модули ALADDIN доступны
2. **Порты недоступны**: Проверьте, что сервисы ALADDIN запущены
3. **Ошибки аутентификации**: Проверьте JWT токены

### Логи и отладка
```bash
# Включить подробные логи
export LOG_LEVEL=DEBUG
python3 start_enhanced_services.py
```

## 📚 API Документация

### Enhanced API Docs Endpoints
- `GET /` - Главная страница
- `GET /api/endpoints` - Список всех endpoints
- `GET /api/services` - Статус сервисов
- `POST /api/test` - Тестирование endpoint
- `GET /api/test-history` - История тестов
- `GET /api/export/{format}` - Экспорт данных

### Enhanced Architecture Visualizer Endpoints
- `GET /` - Главная страница
- `GET /api/architecture` - Полная архитектура
- `GET /api/services` - Статус сервисов
- `GET /api/metrics` - Системные метрики
- `GET /api/alerts` - Активные алерты
- `WebSocket /ws` - Real-time обновления

## 🤝 Интеграция с ALADDIN

### Требования для полной интеграции
1. Установленная система ALADDIN
2. Запущенные сервисы на портах 8006-8012
3. Доступ к SafeFunctionManager
4. Настроенная Redis (опционально)

### Настройка интеграции
```python
# В enhanced_api_docs.py
ALADDIN_AVAILABLE = True
ALADDIN_BASE_PATH = "/path/to/aladdin"

# В enhanced_architecture_visualizer.py
ALADDIN_PORTS = {
    "API Gateway": 8006,
    # ... другие порты
}
```

## 📝 Changelog

### Версия 2.0 (2025-01-06)
- ✅ Реальная интеграция с ALADDIN системой
- ✅ Мониторинг без Docker через psutil
- ✅ WebSocket real-time обновления
- ✅ JWT аутентификация и безопасность
- ✅ Интерактивное тестирование API
- ✅ Экспорт данных в JSON/CSV
- ✅ Улучшенный UI с поиском и фильтрацией
- ✅ 3D визуализация архитектуры
- ✅ Автоматическое обнаружение алертов

### Версия 1.0 (Предыдущая)
- Базовая функциональность
- Mock данные
- Простой UI

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в консоли
2. Убедитесь, что все зависимости установлены
3. Проверьте доступность портов
4. Обратитесь к документации ALADDIN

## 📄 Лицензия

MIT License - см. файл LICENSE для подробностей.

---

**🛡️ ALADDIN Security System** - Защита вашей цифровой жизни