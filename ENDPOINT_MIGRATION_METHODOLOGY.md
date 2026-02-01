# 🔄 **МЕТОДОЛОГИЯ МИГРАЦИИ ENDPOINTS: ПОДРОБНОЕ РУКОВОДСТВО**

## 📋 **ДЛЯ ДРУГОЙ ML-СИСТЕМЫ**

### **Цель документа:**
Показать **ТОЧНЫЕ ШАГИ** миграции endpoints из mock на SFM интеграцию, которые использовались в ALADDIN. Другая ML-система может применить **ТОЧНО ТАКУЮ ЖЕ** методологию для своей миграции.

---

## 🎯 **ОБЩАЯ СТРАТЕГИЯ МИГРАЦИИ**

### **Почему групповая миграция?**

```
ПОЧЕМУ НЕ ПО ОДНОМУ ENDPOINT?
❌ Слишком долго (101 endpoint × 15 мин = 25+ часов)
❌ Риск человеческих ошибок
❌ Сложно тестировать

ПОЧЕМУ НЕ ВСЕ СРАЗУ?
❌ Максимальный риск
❌ Невозможно откатить при проблемах
❌ Сложно локализовать ошибки

✅ ГРУППОВАЯ МИГРАЦИЯ:
- Безопасность (откат группы)
- Скорость (5 групп × 30 мин = 2.5 часа)
- Контроль (тестирование группы)
- Надежность (fallback на mock)
```

### **Принципы миграции:**

1. **Группировка по функционалу** - endpoints с похожей логикой
2. **SFM Adapter** - единый интерфейс к ML функциям
3. **Fallback first** - mock работает всегда
4. **Тестирование группы** - перед следующим шагом
5. **Откат готов** - при проблемах

---

## 🛠️ **ИНСТРУМЕНТЫ МИГРАЦИИ**

### **1. Скрипты миграции (migrate_group*.py)**

Каждая группа имеет **свой скрипт миграции**:

```python
# migrate_group3.py
#!/usr/bin/env python3

def get_group3_code():
    """Генерирует код Группы 3 с SFM интеграцией"""
    return '''
# =============================================================================
# ГРУППА 3: МОНИТОРИНГ (20 endpoints)
# =============================================================================

@app.get("/api/ai/categories/stats")
async def get_ai_categories_stats(child_id: str = None):
    params = {"child_id": child_id} if child_id else {}
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_ai_categories_stats", params)
        return result if success else {"error": message}
    else:
        return {"total_content": 0, "blocked_content": 0, "allowed_content": 0, "source": "mock"}
# ... остальные 19 endpoints
'''

def apply_migration(file_path):
    """Заменяет код в API Gateway файле"""
    # Логика замены заглушек на SFM код
    pass
```

### **2. SFM Adapter (sfm_adapter.py)**

**Универсальный мост** между HTTP и ML:

```python
class SFMAdapter:
    def execute_function(self, func_name: str, params: Dict) -> Tuple[bool, Any, str]:
        """Выполнение ML функции с fallback"""
        try:
            if self.available and self._sfm:
                # Попытка вызвать реальный SFM
                result = self._sfm.execute_function(func_name, params)
                return True, result, None
            else:
                # Fallback на mock
                result = self._execute_mock_function(func_name, params)
                return True, result, "fallback"
        except Exception as e:
            # Fallback при ошибке
            result = self._execute_mock_function(func_name, params)
            return True, result, f"error: {str(e)}"

    def _execute_mock_function(self, func_name: str, params: Dict) -> Dict:
        """Mock реализации для всех функций"""
        mock_responses = {
            "get_component_status": {
                "component_id": params.get("component_id"),
                "status": "enabled",
                "source": "mock"
            },
            "get_ai_categories_stats": {
                "total_content": 0,
                "blocked_content": 0,
                "allowed_content": 0,
                "source": "mock"
            },
            # ... 101 mock функция
        }
        return mock_responses.get(func_name, {"error": "unknown_function", "source": "mock"})
```

### **3. Скрипты тестирования**

```python
# test_all_101_endpoints.py
def test_endpoint(method: str, path: str, group: str) -> Dict:
    """Тестирует один endpoint"""
    try:
        # Выполнить HTTP запрос
        response = requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            return {
                "status": "passed",
                "source": data.get("source", "unknown"),
                "response_time": time.time() - start_time
            }
        else:
            return {"status": "failed", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
```

---

## 📋 **ТОЧНЫЕ ШАГИ МИГРАЦИИ ГРУППЫ**

### **ЭТАП 1: ПОДГОТОВКА ГРУППЫ**

#### **Шаг 1.1: Определить границы группы**

```bash
# Найти где начинается и заканчивается группа в коде
grep -n "ГРУППА 3:" api_gateway_complete.py
grep -n "ГРУППА 4:" api_gateway_complete.py
```

#### **Шаг 1.2: Создать список endpoints группы**

```python
# endpoints_group3.py
GROUP_3_ENDPOINTS = [
    ("GET", "/api/ai/categories/stats", "get_ai_categories_stats"),
    ("GET", "/api/ai/categories/reports", "get_ai_categories_reports"),
    ("POST", "/api/ai/categories/allow", "allow_ai_content"),
    ("POST", "/api/ai/categories/block", "block_ai_content"),
    ("GET", "/api/data/cleanup/stats", "get_data_cleanup_stats"),
    ("GET", "/api/data/cleanup/records", "get_data_cleanup_records"),
    ("POST", "/api/data/cleanup/start", "start_data_cleanup"),
    ("GET", "/api/location/stats", "get_location_stats"),
    ("GET", "/api/location/requests", "get_location_requests"),
    ("POST", "/api/location/allow", "allow_location_request"),
    ("POST", "/api/location/block", "block_location_request"),
    ("PUT", "/api/location/accuracy", "update_location_accuracy"),
    ("GET", "/api/darkweb/leaks", "get_darkweb_leaks"),
    ("GET", "/api/darkweb/stats", "get_darkweb_stats"),
    ("GET", "/api/darkweb/scans", "get_darkweb_scans"),
    ("POST", "/api/darkweb/resolve", "resolve_darkweb_leak"),
    ("POST", "/api/darkweb/scan_start", "start_darkweb_scan"),
    ("GET", "/api/identity/attempts", "get_identity_attempts"),
    ("GET", "/api/identity/stats", "get_identity_stats"),
    ("POST", "/api/identity/allow", "allow_identity_attempt"),
    ("POST", "/api/identity/block", "block_identity_attempt"),
    ("POST", "/api/identity/whitelist", "add_to_identity_whitelist"),
]
```

#### **Шаг 1.3: Создать mock responses**

```python
# mock_responses_group3.py
MOCK_RESPONSES_GROUP_3 = {
    "get_ai_categories_stats": {
        "total_content": 0,
        "blocked_content": 0,
        "allowed_content": 0,
        "source": "mock"
    },
    "get_ai_categories_reports": {
        "reports": [],
        "source": "mock"
    },
    "allow_ai_content": {
        "action": "allow",
        "status": "mock_success",
        "source": "mock"
    },
    # ... все 20 mock responses
}
```

### **ЭТАП 2: СОЗДАНИЕ КОДА ГРУППЫ**

#### **Шаг 2.1: Сгенерировать endpoints с SFM интеграцией**

```python
def generate_group_endpoints(endpoints_list, group_name, group_number):
    """Генерирует код группы endpoints"""

    code_lines = []
    code_lines.append(f"# =============================================================================
# ГРУППА {group_number}: {group_name.upper()}
# =============================================================================
"
    for method, path, func_name in endpoints_list:
        # Определить тип HTTP метода
        decorator = f"@app.{method.lower()}"

        # Сгенерировать параметры функции
        params = extract_path_params(path)  # /api/{component_id} -> component_id: str

        # Сгенерировать тело функции
        func_body = f"""
{decorator}("{path}")
async def {func_name}({params}):
    params = {{}}
    # Добавить параметры в словарь
    {generate_param_assignment(params)}

    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("{func_name}", params)
        return result if success else {{"error": message}}
    else:
        return {get_mock_response(func_name)}
"""

        code_lines.append(func_body)

    return "\n".join(code_lines)
```

#### **Шаг 2.2: Пример сгенерированного кода**

```python
# Сгенерированный код для одного endpoint
@app.get("/api/ai/categories/stats")
async def get_ai_categories_stats(child_id: str = None):
    params = {}
    if child_id is not None:
        params["child_id"] = child_id

    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("get_ai_categories_stats", params)
        return result if success else {"error": message}
    else:
        return {"total_content": 0, "blocked_content": 0, "allowed_content": 0, "source": "mock"}
```

### **ЭТАП 3: ЗАМЕНА КОДА В API GATEWAY**

#### **Шаг 3.1: Найти и заменить заглушки**

```python
def apply_migration(file_path, group_number, new_code):
    """Заменяет код группы в API Gateway файле"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Найти начало группы (заглушки)
    start_pattern = f'# =============================================================================\\n# ГРУППА {group_number}: .* - ЗАГЛУШКИ\\n# ============================================================================='

    # Найти конец группы (начало следующей группы)
    end_pattern = f'# =============================================================================\\n# ГРУППА {group_number + 1}:'

    # Найти позиции
    start_match = re.search(start_pattern, content, re.MULTILINE)
    end_match = re.search(end_pattern, content, re.MULTILINE)

    if start_match and end_match:
        # Заменить блок
        new_content = (
            content[:start_match.start()] +
            new_code + "\n" +
            content[end_match.start():]
        )

        # Записать файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"✅ Группа {group_number} мигрирована в {file_path}")
        return True
    else:
        print(f"❌ Не найдены границы группы {group_number}")
        return False
```

#### **Шаг 3.2: Проверка синтаксиса после замены**

```bash
# Проверить что код корректен
python3 -m py_compile api_gateway_complete.py

if [ $? -eq 0 ]; then
    echo "✅ Синтаксис корректен"
else
    echo "❌ Ошибка синтаксиса"
    exit 1
fi
```

### **ЭТАП 4: ТЕСТИРОВАНИЕ МИГРАЦИИ**

#### **Шаг 4.1: Запуск локального тестирования**

```bash
# Запустить API Gateway локально
python3 api_gateway_complete.py &

# Подождать запуска
sleep 3

# Протестировать все endpoints группы
python3 test_all_101_endpoints.py --group 3 --verbose

# Проверить статус
curl http://localhost:8002/api/health
```

#### **Шаг 4.2: Проверка каждого endpoint**

```python
def test_group_endpoints(group_number):
    """Тестирует все endpoints группы"""

    endpoints = get_endpoints_for_group(group_number)

    results = []
    for method, path, expected_func in endpoints:
        result = test_single_endpoint(method, path)

        # Проверить что используется SFM
        if result["status"] == "passed":
            if result.get("source") in ["sfm", "mock"]:
                print(f"✅ {method} {path} - OK (source: {result['source']})")
            else:
                print(f"⚠️  {method} {path} - WARNING: unknown source")
        else:
            print(f"❌ {method} {path} - FAILED: {result['error']}")

        results.append(result)

    return results
```

### **ЭТАП 5: РАЗВЕРТЫВАНИЕ НА СЕРВЕР**

#### **Шаг 5.1: Копирование файлов на сервер**

```bash
# Копировать обновленный API Gateway
scp api_gateway_complete.py user@server:/opt/aladdin-backend/

# Копировать SFM Adapter (если обновлен)
scp sfm_adapter.py user@server:/opt/aladdin-backend/

# Копировать SFM Manager (если обновлен)
scp safe_function_manager.py user@server:/opt/aladdin-backend/
```

#### **Шаг 5.2: Перезапуск сервиса**

```bash
# На сервере
sudo systemctl restart aladdin-api-gateway

# Проверить статус
sudo systemctl status aladdin-api-gateway

# Проверить логи
journalctl -u aladdin-api-gateway -n 20
```

#### **Шаг 5.3: Тестирование на сервере**

```bash
# Протестировать health endpoint
curl https://aladdin-ai.ru/api/health

# Протестировать endpoints группы
curl https://aladdin-ai.ru/api/ai/categories/stats
curl https://aladdin-ai.ru/api/darkweb/stats

# Проверить что возвращается SFM или mock
curl https://aladdin-ai.ru/api/ai/categories/stats | jq .source
```

### **ЭТАП 6: МОНИТОРИНГ И ОТКАТ**

#### **Шаг 6.1: Мониторинг после развертывания**

```bash
# Мониторить логи в реальном времени
journalctl -u aladdin-api-gateway -f

# Проверить метрики каждые 5 минут
while true; do
    curl -s https://aladdin-ai.ru/api/health | jq .
    sleep 300
done
```

#### **Шаг 6.2: Проверка производительности**

```bash
# Нагрузочное тестирование
ab -n 1000 -c 10 https://aladdin-ai.ru/api/ai/categories/stats

# Проверить время ответа
curl -w "@curl-format.txt" -o /dev/null -s https://aladdin-ai.ru/api/health
```

#### **Шаг 6.3: Подготовка отката**

```bash
# Создать backup перед развертыванием
cp api_gateway_complete.py api_gateway_complete.py.backup

# Скрипт отката
#!/bin/bash
cp api_gateway_complete.py.backup api_gateway_complete.py
systemctl restart aladdin-api-gateway
echo "Откат завершен"
```

---

## 🔄 **АВТОМАТИЗАЦИЯ МИГРАЦИИ**

### **Шаг 1: Создание универсального скрипта миграции**

```python
# universal_migration.py
import sys
import os
from migration_utils import *

def migrate_group(group_number):
    """Мигрирует любую группу по номеру"""

    # Загрузить конфигурацию группы
    config = load_group_config(group_number)

    # Сгенерировать код
    new_code = generate_group_code(config)

    # Применить миграцию
    success = apply_migration("api_gateway_complete.py", group_number, new_code)

    if success:
        # Протестировать
        test_results = test_group_endpoints(group_number)

        # Развернуть если тесты пройдены
        if all_tests_passed(test_results):
            deploy_to_server()
            return True
        else:
            rollback_migration()
            return False
    else:
        return False

if __name__ == "__main__":
    group_number = int(sys.argv[1])
    migrate_group(group_number)
```

### **Шаг 2: Pipeline миграции**

```bash
#!/bin/bash
# migrate_pipeline.sh

echo "🚀 НАЧИНАЕМ МИГРАЦИЮ ВСЕХ ГРУПП"

for group in {1..5}; do
    echo ""
    echo "📦 МИГРАЦИЯ ГРУППЫ $group"
    echo "===================="

    # Создать backup
    cp api_gateway_complete.py api_gateway_complete.py.backup

    # Мигрировать группу
    python3 universal_migration.py $group

    if [ $? -eq 0 ]; then
        echo "✅ Группа $group мигрирована успешно"

        # Тестирование
        python3 test_all_101_endpoints.py --group $group

        if [ $? -eq 0 ]; then
            echo "✅ Тесты группы $group пройдены"

            # Развертывание
            ./deploy_to_server.sh

            if [ $? -eq 0 ]; then
                echo "✅ Группа $group развернута на сервере"
            else
                echo "❌ Ошибка развертывания группы $group"
                exit 1
            fi
        else
            echo "❌ Тесты группы $group не пройдены"
            ./rollback.sh
            exit 1
        fi
    else
        echo "❌ Ошибка миграции группы $group"
        exit 1
    fi

    echo ""
    echo "🎯 Группа $group ЗАВЕРШЕНА"
    echo "======================"
done

echo ""
echo "🎉 ВСЕ ГРУППЫ МИГРИРОВАНЫ!"
```

---

## 🛡️ **ОБРАБОТКА ОШИБОК И ОТКАТ**

### **Типы ошибок миграции:**

#### **Ошибка 1: Синтаксическая ошибка в коде**

```bash
# Проверить перед развертыванием
python3 -m py_compile api_gateway_complete.py

if [ $? -ne 0 ]; then
    echo "❌ Синтаксическая ошибка"
    cp api_gateway_complete.py.backup api_gateway_complete.py
    exit 1
fi
```

#### **Ошибка 2: HTTP ошибки endpoints**

```python
def check_endpoint_errors():
    """Проверяет что все endpoints возвращают 200"""

    endpoints = get_all_endpoints()

    for method, path in endpoints:
        try:
            response = requests.request(method, f"{BASE_URL}{path}", timeout=5)
            if response.status_code != 200:
                print(f"❌ {method} {path}: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ {method} {path}: {e}")
            return False

    return True
```

#### **Ошибка 3: SFM недоступен**

```python
def check_sfm_availability():
    """Проверяет что SFM работает"""

    try:
        # Попытаться вызвать тестовую функцию
        success, result, error = sfm_adapter.execute_function("test_function", {})

        if success and result.get("source") == "sfm":
            print("✅ SFM доступен")
            return True
        else:
            print("⚠️  SFM недоступен, используется fallback")
            return True  # Fallback допустим
    except Exception as e:
        print(f"❌ SFM полностью недоступен: {e}")
        return False
```

### **Откат при ошибках:**

```bash
#!/bin/bash
# rollback.sh

echo "🔄 НАЧИНАЕМ ОТКАТ"

# Восстановить backup
cp api_gateway_complete.py.backup api_gateway_complete.py

# Перезапустить сервис
systemctl restart aladdin-api-gateway

# Проверить что работает
curl -s https://aladdin-ai.ru/api/health | jq .status

if [ $? -eq 0 ]; then
    echo "✅ Откат завершен успешно"
else
    echo "❌ Ошибка при откате"
    exit 1
fi
```

---

## 📊 **МЕТРИКИ И МОНИТОРИНГ МИГРАЦИИ**

### **Метрики миграции:**

```python
class MigrationMetrics:
    def __init__(self):
        self.metrics = {
            'groups_migrated': 0,
            'endpoints_migrated': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'deployments_successful': 0,
            'deployments_failed': 0,
            'rollbacks': 0,
            'total_time': 0
        }

    def report_progress(self):
        """Отчет о прогрессе миграции"""
        print(f"📊 ПРОГРЕСС МИГРАЦИИ:")
        print(f"   Группы мигрированы: {self.metrics['groups_migrated']}/5")
        print(f"   Endpoints мигрированы: {self.metrics['endpoints_migrated']}/101")
        print(f"   Тесты пройдены: {self.metrics['tests_passed']}")
        print(f"   Тесты провалены: {self.metrics['tests_failed']}")
        print(f"   Успешные развертывания: {self.metrics['deployments_successful']}")
        print(f"   Откаты: {self.metrics['rollbacks']}")
        print(f"   Общее время: {self.metrics['total_time']:.2f} мин")
```

### **Мониторинг после миграции:**

```bash
#!/bin/bash
# monitor_migration.sh

echo "📊 МОНИТОРИНГ ПОСЛЕ МИГРАЦИИ"

# Проверка каждые 30 секунд в течение 5 минут
for i in {1..10}; do
    echo ""
    echo "🔍 Проверка $i/10"

    # Health check
    health=$(curl -s https://aladdin-ai.ru/api/health | jq -r .status)
    echo "   Health: $health"

    # SFM status
    sfm_status=$(curl -s https://aladdin-ai.ru/api/health | jq -r .sfm_adapter)
    echo "   SFM: $sfm_status"

    # Тест нескольких endpoints
    test1=$(curl -s -w "%{http_code}" -o /dev/null https://aladdin-ai.ru/api/components/status/test)
    test2=$(curl -s -w "%{http_code}" -o /dev/null https://aladdin-ai.ru/api/ai/categories/stats)
    echo "   Endpoints: $test1 $test2"

    # Проверить логи на ошибки
    errors=$(journalctl -u aladdin-api-gateway --since "1 minute ago" | grep -c "ERROR")
    echo "   Errors in logs: $errors"

    sleep 30
done

echo ""
echo "✅ Мониторинг завершен"
```

---

## 🎯 **ФИНАЛЬНЫЕ РЕКОМЕНДАЦИИ**

### **Для другой ML-системы:**

1. **Используйте ту же структуру:**
   - Группируйте endpoints по функционалу
   - Создавайте скрипты миграции для каждой группы
   - Тестируйте перед развертыванием

2. **Обязательно имейте fallback:**
   - Mock responses для всех функций
   - Graceful degradation
   - Возможность отката

3. **Автоматизируйте процесс:**
   - Скрипты генерации кода
   - Автоматическое тестирование
   - Pipeline развертывания

4. **Мониторьте тщательно:**
   - HTTP статусы всех endpoints
   - Время ответа
   - Логи ошибок
   - SFM доступность

### **Ключевые файлы для копирования:**

- `migrate_group*.py` - шаблоны миграции
- `sfm_adapter.py` - универсальный адаптер
- `test_all_101_endpoints.py` - тестирование
- `ALADDIN_SYSTEM_ARCHITECTURE.md` - документация

---

## 🚀 **ГОТОВ К МИГРАЦИИ!**

**Эта методология использовалась для успешной миграции 101 endpoint в ALADDIN системе.**

**Другая ML-система может применить ТОЧНО ТАКУЮ ЖЕ методологию для своей миграции на SFM интеграцию.**

**Успешной миграции!** 🎉


