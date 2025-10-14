# 📖 РУКОВОДСТВО ПО ИСПОЛЬЗОВАНИЮ SFM (PRIORITY 3)

## 🎯 Введение

**Safe Function Manager (SFM)** - это центральный компонент системы безопасности ALADDIN, обеспечивающий безопасное выполнение функций с полным мониторингом, кэшированием и интеграцией с другими компонентами системы.

## 🚀 Быстрый старт

### Установка и импорт

```python
from security.safe_function_manager import SafeFunctionManager, SecurityLevel
from core.base import ComponentStatus
```

### Создание экземпляра SFM

```python
# Базовое создание
sfm = SafeFunctionManager("MySFM")

# С конфигурацией
config = {
    "max_concurrent_functions": 100,
    "function_timeout": 600,
    "enable_sleep_mode": True,
    "auto_test_interval": 1800
}
sfm = SafeFunctionManager("MySFM", config)
```

## 📝 Основные операции

### 1. Регистрация функций

```python
# Простая функция
def calculate_sum(a: int, b: int) -> int:
    return a + b

# Регистрация
success = sfm.register_function(
    function_id="calc_sum_001",
    name="Calculator Sum",
    description="Вычисляет сумму двух чисел",
    function_type="calculator",
    handler=calculate_sum,
    security_level=SecurityLevel.MEDIUM
)

if success:
    print("✅ Функция зарегистрирована успешно")
else:
    print("❌ Ошибка регистрации функции")
```

### 2. Выполнение функций

```python
# Синхронное выполнение
success, result, message = sfm.execute_function(
    "calc_sum_001", 
    {"a": 10, "b": 20}
)

if success:
    print(f"✅ Результат: {result}")
else:
    print(f"❌ Ошибка: {message}")

# Асинхронное выполнение
import asyncio

async def run_async():
    success, result, message = await sfm.execute_function_async(
        "calc_sum_001", 
        {"a": 15, "b": 25}
    )
    return success, result, message

# Запуск
success, result, message = asyncio.run(run_async())
```

### 3. Управление функциями

```python
# Включение функции
sfm.enable_function("calc_sum_001")

# Отключение функции
sfm.disable_function("calc_sum_001")

# Перевод в спящий режим
sfm.sleep_function("calc_sum_001", hours=24)

# Пробуждение функции
sfm.wake_function("calc_sum_001")

# Получение статуса
status = sfm.get_function_status("calc_sum_001")
print(f"Статус функции: {status}")
```

## 🔧 Расширенные возможности

### 1. Работа с зависимостями

```python
# Функция с зависимостями
def complex_calculation(x: int, y: int, use_cache: bool = True) -> dict:
    # Логика с использованием кэша
    return {"result": x * y, "cached": use_cache}

# Регистрация с зависимостями
sfm.register_function(
    function_id="complex_calc_001",
    name="Complex Calculator",
    description="Сложные вычисления с кэшированием",
    function_type="advanced_calculator",
    handler=complex_calculation,
    security_level=SecurityLevel.HIGH
)

# Добавление зависимостей
sfm.add_function_dependency("complex_calc_001", "calc_sum_001")
```

### 2. Мониторинг и метрики

```python
# Получение статистики
stats = sfm.get_statistics()
print(f"Всего выполнений: {stats['total_executions']}")
print(f"Успешных: {stats['successful_executions']}")
print(f"Неудачных: {stats['failed_executions']}")

# Получение метрик производительности
metrics = sfm.get_performance_metrics()
print(f"CPU использование: {metrics.get('cpu_usage', 'N/A')}%")
print(f"Использование памяти: {metrics.get('memory_usage', 'N/A')}%")

# Получение списка функций
functions = sfm.list_functions()
for func_id, func_info in functions.items():
    print(f"Функция: {func_id}, Статус: {func_info['status']}")
```

### 3. Работа с событиями

```python
# Подписка на события
def on_function_executed(event_data):
    print(f"Функция выполнена: {event_data}")

def on_function_failed(event_data):
    print(f"Функция не выполнена: {event_data}")

# Регистрация обработчиков
sfm.add_event_listener("function_executed", on_function_executed)
sfm.add_event_listener("function_failed", on_function_failed)
```

## 🛡️ Безопасность

### 1. Уровни безопасности

```python
from core.base import SecurityLevel

# Функции с разными уровнями безопасности
sfm.register_function(
    function_id="public_api_001",
    name="Public API",
    description="Публичный API",
    function_type="api",
    handler=public_handler,
    security_level=SecurityLevel.LOW
)

sfm.register_function(
    function_id="admin_function_001",
    name="Admin Function",
    description="Административная функция",
    function_type="admin",
    handler=admin_handler,
    security_level=SecurityLevel.CRITICAL
)
```

### 2. Валидация параметров

```python
def safe_division(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Деление на ноль недопустимо")
    return a / b

# SFM автоматически обработает исключения
success, result, message = sfm.execute_function(
    "safe_division_001", 
    {"a": 10, "b": 0}
)
# success = False, message содержит информацию об ошибке
```

## ⚡ Оптимизация производительности

### 1. Настройка кэширования

```python
# Конфигурация кэширования
cache_config = {
    "enable_redis": True,
    "redis_url": "redis://localhost:6379",
    "cache_ttl": 3600,  # 1 час
    "max_cache_size": 1000
}

sfm = SafeFunctionManager("OptimizedSFM", cache_config)
```

### 2. Настройка параллельности

```python
# Конфигурация для высокой нагрузки
high_load_config = {
    "max_concurrent_functions": 200,
    "function_timeout": 30,
    "thread_pool_workers": 50,
    "enable_async": True
}

sfm = SafeFunctionManager("HighLoadSFM", high_load_config)
```

### 3. Мониторинг производительности

```python
# Получение детальных метрик
detailed_metrics = sfm.get_detailed_metrics()
print(f"Среднее время выполнения: {detailed_metrics['avg_execution_time']}ms")
print(f"Максимальное время: {detailed_metrics['max_execution_time']}ms")
print(f"Активные функции: {detailed_metrics['active_functions']}")
```

## 🔄 Интеграция с другими компонентами

### 1. Service Mesh

```python
# SFM автоматически интегрируется с Service Mesh
# Дополнительная настройка не требуется
sfm = SafeFunctionManager("IntegratedSFM")
```

### 2. Load Balancer

```python
# Load Balancer автоматически распределяет нагрузку
# Настройка через конфигурацию
load_balancer_config = {
    "enable_load_balancing": True,
    "load_balancer_algorithm": "round_robin"
}
```

### 3. Zero Trust

```python
# Zero Trust автоматически проверяет каждое выполнение
# Дополнительная настройка не требуется
```

## 🐛 Отладка и диагностика

### 1. Включение отладочного режима

```python
# Создание SFM с отладкой
debug_config = {
    "debug_mode": True,
    "log_level": "DEBUG",
    "enable_tracing": True
}

sfm = SafeFunctionManager("DebugSFM", debug_config)
```

### 2. Получение логов

```python
# Получение логов выполнения
logs = sfm.get_execution_logs(limit=100)
for log in logs:
    print(f"{log['timestamp']}: {log['message']}")
```

### 3. Диагностика проблем

```python
# Проверка состояния SFM
health = sfm.health_check()
print(f"Состояние SFM: {health['status']}")
print(f"Активные компоненты: {health['active_components']}")
print(f"Проблемы: {health['issues']}")
```

## 📊 Примеры использования

### 1. Простой калькулятор

```python
class Calculator:
    def __init__(self):
        self.sfm = SafeFunctionManager("CalculatorSFM")
        self._register_functions()
    
    def _register_functions(self):
        # Сложение
        self.sfm.register_function(
            "add", "Addition", "Сложение двух чисел",
            "math", self._add, SecurityLevel.LOW
        )
        
        # Вычитание
        self.sfm.register_function(
            "subtract", "Subtraction", "Вычитание двух чисел",
            "math", self._subtract, SecurityLevel.LOW
        )
    
    def _add(self, a: float, b: float) -> float:
        return a + b
    
    def _subtract(self, a: float, b: float) -> float:
        return a - b
    
    def calculate(self, operation: str, a: float, b: float) -> dict:
        success, result, message = self.sfm.execute_function(
            operation, {"a": a, "b": b}
        )
        return {
            "success": success,
            "result": result,
            "message": message
        }

# Использование
calc = Calculator()
result = calc.calculate("add", 5, 3)
print(f"5 + 3 = {result['result']}")
```

### 2. API Gateway

```python
class APIGateway:
    def __init__(self):
        self.sfm = SafeFunctionManager("APIGatewaySFM")
        self._register_endpoints()
    
    def _register_endpoints(self):
        # Регистрация всех API endpoints как функций
        endpoints = [
            ("/users", "get_users", self._get_users),
            ("/users/{id}", "get_user", self._get_user),
            ("/users", "create_user", self._create_user),
        ]
        
        for endpoint, func_id, handler in endpoints:
            self.sfm.register_function(
                func_id, f"API {endpoint}", f"API endpoint {endpoint}",
                "api", handler, SecurityLevel.MEDIUM
            )
    
    def handle_request(self, method: str, path: str, data: dict = None) -> dict:
        # Маршрутизация запроса к соответствующей функции
        func_id = self._route_request(method, path)
        if func_id:
            success, result, message = self.sfm.execute_function(
                func_id, data or {}
            )
            return {
                "status": "success" if success else "error",
                "data": result,
                "message": message
            }
        else:
            return {"status": "error", "message": "Endpoint not found"}
```

## 🎯 Лучшие практики

### 1. Именование функций

```python
# ✅ Хорошо
sfm.register_function("user_authentication_001", ...)
sfm.register_function("data_processing_batch_001", ...)

# ❌ Плохо
sfm.register_function("func1", ...)
sfm.register_function("temp_function", ...)
```

### 2. Обработка ошибок

```python
def robust_function(param1: str, param2: int) -> dict:
    try:
        # Валидация входных данных
        if not isinstance(param1, str):
            raise ValueError("param1 должен быть строкой")
        if not isinstance(param2, int):
            raise ValueError("param2 должен быть числом")
        
        # Основная логика
        result = process_data(param1, param2)
        
        return {"success": True, "data": result}
    
    except Exception as e:
        # Логирование ошибки
        logger.error(f"Ошибка в robust_function: {e}")
        return {"success": False, "error": str(e)}
```

### 3. Мониторинг производительности

```python
# Регулярная проверка метрик
def monitor_performance():
    metrics = sfm.get_performance_metrics()
    
    # Проверка критических метрик
    if metrics['success_rate'] < 95:
        logger.warning(f"Низкий процент успешных выполнений: {metrics['success_rate']}%")
    
    if metrics['avg_execution_time'] > 5000:  # 5 секунд
        logger.warning(f"Высокое время выполнения: {metrics['avg_execution_time']}ms")

# Запуск мониторинга каждые 5 минут
import threading
import time

def start_monitoring():
    while True:
        monitor_performance()
        time.sleep(300)  # 5 минут

monitoring_thread = threading.Thread(target=start_monitoring, daemon=True)
monitoring_thread.start()
```

## 🆘 Решение проблем

### Частые проблемы и решения

| Проблема | Причина | Решение |
|----------|---------|---------|
| Функция не выполняется | Не зарегистрирована | Проверить регистрацию через `list_functions()` |
| Ошибка импорта | Отсутствует модуль | Проверить зависимости в `requirements.txt` |
| Медленная работа | Недостаточно ресурсов | Увеличить `max_concurrent_functions` |
| Ошибки кэширования | Проблемы с Redis | Проверить подключение к Redis |

### Получение помощи

```python
# Диагностическая информация
def get_diagnostic_info():
    return {
        "sfm_version": sfm.get_version(),
        "total_functions": len(sfm.functions),
        "active_functions": len([f for f in sfm.functions.values() if f.status == FunctionStatus.ENABLED]),
        "system_health": sfm.health_check(),
        "performance_metrics": sfm.get_performance_metrics()
    }

# Отправка диагностики
diagnostic = get_diagnostic_info()
print(json.dumps(diagnostic, indent=2, ensure_ascii=False))
```

## 📚 Дополнительные ресурсы

- **Архитектурная диаграмма**: `sfm_architecture_diagram.md`
- **API документация**: `sfm_api_reference.md`
- **Примеры кода**: `examples/` директория
- **Тесты**: `tests/test_safe_function_manager.py`

---

**Версия документации**: 1.0  
**Дата обновления**: 2025-09-28  
**Автор**: ALADDIN Security Team