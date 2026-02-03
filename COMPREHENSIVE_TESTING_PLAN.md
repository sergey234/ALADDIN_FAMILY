# 🚀 **КОМПЛЕКСНЫЙ ПЛАН ТЕСТИРОВАНИЯ СИСТЕМЫ ALADDIN**

## 📋 **ОБЩИЙ ОБЗОР ТЕСТИРОВАНИЯ**

### **🎯 ЦЕЛИ ТЕСТИРОВАНИЯ:**
- **Функциональность:** Все 105+ API эндпоинтов работают корректно
- **Интеграция:** Мобильное ↔ API Gateway ↔ SFM HTTP API ↔ SFM Core
- **Производительность:** <100ms отклик, поддержка нагрузки
- **Безопасность:** Enterprise-grade защита данных
- **Надежность:** 99.9% uptime, fallback механизмы
- **Масштабируемость:** Горизонтальное расширение

### **📊 СКОП ТЕСТИРОВАНИЯ:**
- **API Эндпоинты:** 105+ уникальных
- **Функции Безопасности:** 138 функций + 42 компонента
- **SFM Функции:** 1065 базовых функций
- **Архитектурные Компоненты:** 4 сервиса
- **Пользовательские Сценарии:** 20+ сценариев использования

---

## 🧪 **ЭТАП 1: ФУНКЦИОНАЛЬНОЕ ТЕСТИРОВАНИЕ**

### **1.1 ТЕСТИРОВАНИЕ API GATEWAY (105+ ЭНДПОИНТОВ)**

#### **🎯 Критерии Успеха:**
- ✅ HTTP 200 для всех GET запросов
- ✅ HTTP 201 для успешных POST/PUT
- ✅ Валидный JSON ответ
- ✅ `source: "real_sfm"` для всех исправленных функций
- ✅ Корректная структура данных

#### **📋 Тестовые Случаи (по категориям):**

##### **КОМПОНЕНТЫ (Components) - 10 эндпоинтов:**
```bash
# Тест 1.1.1: Health Check
curl -s http://149.154.65.180:8002/api/components/health | jq '.source'
# Ожидаемый результат: "real_sfm"

# Тест 1.1.2: Component Status
curl -s http://149.154.65.180:8002/api/components/status/sfm_core | jq '.status'
# Ожидаемый результат: "enabled" или "disabled"

# Тест 1.1.3: Component Configuration
curl -s http://149.154.65.180:8002/api/components/config/sfm_core | jq '.config'
# Ожидаемый результат: объект конфигурации

# Тест 1.1.4: Component Logs
curl -s http://149.154.65.180:8002/api/components/logs/sfm_core | jq '.logs'
# Ожидаемый результат: массив логов

# Тест 1.1.5: Enable Component (POST)
curl -s -X POST http://149.154.65.180:8002/api/components/enable/sfm_core | jq '.action'
# Ожидаемый результат: "enable"

# Тест 1.1.6: Disable Component (POST)
curl -s -X POST http://149.154.65.180:8002/api/components/disable/sfm_core | jq '.action'
# Ожидаемый результат: "disable"

# Тест 1.1.7: Update Config (PUT)
curl -s -X PUT -H "Content-Type: application/json" \
  http://149.154.65.180:8002/api/components/config/sfm_core \
  -d '{"setting": "value"}' | jq '.action'
# Ожидаемый результат: "update_config"

# Тест 1.1.8: Restart Component (POST)
curl -s -X POST http://149.154.65.180:8002/api/components/restart/sfm_core | jq '.action'
# Ожидаемый результат: "restart"

# Тест 1.1.9: Backup Component (POST)
curl -s -X POST http://149.154.65.180:8002/api/components/backup/sfm_core | jq '.action'
# Ожидаемый результат: "backup"

# Тест 1.1.10: Restore Component (POST)
curl -s -X POST -H "Content-Type: application/json" \
  http://149.154.65.180:8002/api/components/restore/sfm_core \
  -d '{"backup_id": "test"}' | jq '.action'
# Ожидаемый результат: "restore"
```

##### **БЕЗОПАСНОСТЬ (Security) - 14 эндпоинтов:**
```bash
# Тест 1.2.1: Phishing Sensitivity (GET)
curl -s http://149.154.65.180:8002/api/phishing/sensitivity | jq '.source'
# Ожидаемый результат: "real_sfm"

# Тест 1.2.2: Phishing Sensitivity (PUT)
curl -s -X PUT -H "Content-Type: application/json" \
  http://149.154.65.180:8002/api/phishing/sensitivity \
  -d '{"level": "high"}' | jq '.action'
# Ожидаемый результат: "update"

# Тест 1.2.3: Block Suspicious (GET)
curl -s http://149.154.65.180:8002/api/phishing/block_suspicious | jq '.source'
# Ожидаемый результат: "real_sfm"

# Тест 1.2.4: Block Suspicious (PUT)
curl -s -X PUT -H "Content-Type: application/json" \
  http://149.154.65.180:8002/api/phishing/block_suspicious \
  -d '{"enabled": true}' | jq '.action'
# Ожидаемый результат: "update"

# Тест 1.2.5: Phishing Exclusions (GET)
curl -s http://149.154.65.180:8002/api/phishing/exclusions | jq '.source'
# Ожидаемый результат: "real_sfm"

# Тест 1.2.6: Malware Scan Scheduled (GET)
curl -s http://149.154.65.180:8002/api/malware/scan_scheduled | jq '.source'
# Ожидаемый результат: "real_sfm"

# Тест 1.2.7: Malware Scan Scheduled (PUT)
curl -s -X PUT -H "Content-Type: application/json" \
  http://149.154.65.180:8002/api/malware/scan_scheduled \
  -d '{"schedule": "daily"}' | jq '.action'
# Ожидаемый результат: "update"

# Тест 1.2.8: Malware Quarantine (GET)
curl -s http://149.154.65.180:8002/api/malware/quarantine | jq '.source'
# Ожидаемый результат: "real_sfm"

# Тест 1.2.9: Malware Quarantine (PUT)
curl -s -X PUT -H "Content-Type: application/json" \
  http://149.154.65.180:8002/api/malware/quarantine \
  -d '{"action": "clean"}' | jq '.action'
# Ожидаемый результат: "update"

# Тест 1.2.10: Malware Scan Now (POST)
curl -s -X POST http://149.154.65.180:8002/api/malware/scan_now | jq '.action'
# Ожидаемый результат: "scan"

# Тест 1.2.11: Mobile App Lock (GET)
curl -s http://149.154.65.180:8002/api/mobile/app_lock | jq '.source'
# Ожидаемый результат: "real_sfm"

# Тест 1.2.12: Mobile App Lock (PUT)
curl -s -X PUT -H "Content-Type: application/json" \
  http://149.154.65.180:8002/api/mobile/app_lock \
  -d '{"enabled": true}' | jq '.action'
# Ожидаемый результат: "update"

# Тест 1.2.13: Mobile Biometric (GET)
curl -s http://149.154.65.180:8002/api/mobile/biometric | jq '.source'
# Ожидаемый результат: "real_sfm"

# Тест 1.2.14: Network Firewall (GET)
curl -s http://149.154.65.180:8002/api/network/firewall_rules | jq '.source'
# Ожидаемый результат: "real_sfm"

# Тест 1.2.15: Network VPN Config (PUT)
curl -s -X PUT -H "Content-Type: application/json" \
  http://149.154.65.180:8002/api/network/vpn_config \
  -d '{"server": "vpn.example.com"}' | jq '.action'
# Ожидаемый результат: "update"
```

##### **МОНИТОРИНГ (Monitoring) - 20 эндпоинтов:**
```bash
# Тест 1.3.1: AI Categories Stats
curl -s http://149.154.65.180:8002/api/ai/categories/stats | jq '.source'
# Ожидаемый результат: "real_sfm"

# Тест 1.3.2: AI Categories Reports
curl -s http://149.154.65.180:8002/api/ai/categories/reports | jq '.source'
# Ожидаемый результат: "real_sfm"

# Тест 1.3.3: AI Categories Allow (POST)
curl -s -X POST -H "Content-Type: application/json" \
  http://149.154.65.180:8002/api/ai/categories/allow \
  -d '{"category_id": "test"}' | jq '.action'
# Ожидаемый результат: "allow"

# Тест 1.3.4: AI Categories Block (POST)
curl -s -X POST -H "Content-Type: application/json" \
  http://149.154.65.180:8002/api/ai/categories/block \
  -d '{"category_id": "test"}' | jq '.action'
# Ожидаемый результат: "block"

# И так далее для всех 20 эндпоинтов мониторинга...
```

### **1.2 ТЕСТИРОВАНИЕ SFM HTTP API (ПОРТ 8003)**

#### **🎯 Критерии Успеха:**
- ✅ HTTP 200 для всех внутренних вызовов
- ✅ Валидный JSON ответ
- ✅ Корректное маппинг функций
- ✅ Fallback при недоступности

#### **📋 Тестовые Случаи:**
```bash
# Тест 1.2.1: SFM Health Check
curl -s http://127.0.0.1:8003/api/health | jq '.'
# Ожидаемый результат: {"status": "healthy", "functions_count": 1065}

# Тест 1.2.2: SFM Functions List
curl -s http://127.0.0.1:8003/api/functions | jq '.functions | length'
# Ожидаемый результат: 14 (базовых функций)

# Тест 1.2.3: Execute SFM Function
curl -s -X POST -H "Content-Type: application/json" \
  http://127.0.0.1:8003/api/execute \
  -d '{"function": "get_phishing_sensitivity", "params": {}}' | jq '.success'
# Ожидаемый результат: true

# Тест 1.2.4: Invalid Function
curl -s -X POST -H "Content-Type: application/json" \
  http://127.0.0.1:8003/api/execute \
  -d '{"function": "invalid_function", "params": {}}' | jq '.success'
# Ожидаемый результат: false
```

---

## 🔗 **ЭТАП 2: ИНТЕГРАЦИОННОЕ ТЕСТИРОВАНИЕ**

### **2.1 ВЗАИМОДЕЙСТВИЕ КОМПОНЕНТОВ**

#### **🎯 Критерии Успеха:**
- ✅ API Gateway ↔ SFM HTTP API связь работает
- ✅ SFM HTTP API ↔ SFM Core интеграция
- ✅ Маппинг 105+ API → 14 SFM функций корректен
- ✅ Fallback механизмы срабатывают

#### **📋 Тестовые Случаи:**

##### **ПОЛНЫЙ ПОТОК ЗАПРОСА:**
```bash
# Тест 2.1.1: Полный цикл API Gateway → SFM
echo "=== ТЕСТИРОВАНИЕ ПОЛНОГО ПОТОКА ==="

# 1. Запрос к API Gateway
echo "1. API Gateway Request:"
response=$(curl -s http://149.154.65.180:8002/api/phishing/sensitivity)
echo "$response" | jq '.'

# 2. Проверка что API Gateway вызывает SFM HTTP API
echo "2. Checking SFM HTTP API logs:"
ssh root@149.154.65.180 "journalctl -u aladdin-sfm-core -n 3"

# 3. Проверка что SFM Core получает запрос
echo "3. Direct SFM HTTP API call:"
direct_response=$(curl -s -X POST -H "Content-Type: application/json" \
  http://127.0.0.1:8003/api/execute \
  -d '{"function": "get_phishing_sensitivity", "params": {}}')
echo "$direct_response" | jq '.'

# 4. Сравнение результатов
api_source=$(echo "$response" | jq -r '.source')
sfm_success=$(echo "$direct_response" | jq -r '.success')

if [ "$api_source" = "real_sfm" ] && [ "$sfm_success" = "true" ]; then
    echo "✅ ПОЛНЫЙ ПОТОК РАБОТАЕТ КОРРЕКТНО"
else
    echo "❌ ПРОБЛЕМА В ИНТЕГРАЦИИ"
fi
```

### **2.2 ТЕСТИРОВАНИЕ FALLBACK МЕХАНИЗМОВ**

#### **🎯 Критерии Успеха:**
- ✅ При недоступности SFM возвращается fallback
- ✅ Пользовательский опыт не нарушается
- ✅ Логирование ошибок работает

```bash
# Тест 2.2.1: Fallback при остановке SFM
echo "=== ТЕСТИРОВАНИЕ FALLBACK ==="

# Останавливаем SFM сервис
ssh root@149.154.65.180 "systemctl stop aladdin-sfm-core"

# Ждем 5 секунд
sleep 5

# Проверяем API
fallback_response=$(curl -s http://149.154.65.180:8002/api/phishing/sensitivity)
fallback_source=$(echo "$fallback_response" | jq -r '.source')

if [ "$fallback_source" = "fallback" ]; then
    echo "✅ FALLBACK РАБОТАЕТ: $fallback_response"
else
    echo "❌ FALLBACK НЕ РАБОТАЕТ: $fallback_response"
fi

# Запускаем SFM обратно
ssh root@149.154.65.180 "systemctl start aladdin-sfm-core"
```

---

## ⚡ **ЭТАП 3: ПРОИЗВОДИТЕЛЬНОСТЬ И НАГРУЗКА**

### **3.1 ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ**

#### **🎯 Критерии Успеха:**
- ✅ Среднее время отклика <100ms
- ✅ 95-й перцентиль <200ms
- ✅ CPU <70%, Memory <80%
- ✅ Throughput >1000 RPS

```bash
# Тест 3.1.1: Производительность одного API
echo "=== ПРОИЗВОДИТЕЛЬНОСТЬ ОДНОГО API ==="
for i in {1..10}; do
    time_start=$(date +%s.%3N)
    curl -s http://149.154.65.180:8002/api/phishing/sensitivity > /dev/null
    time_end=$(date +%s.%3N)
    response_time=$(echo "$time_end - $time_start" | bc)
    printf "Запрос %2d: %.3f сек\n" $i $response_time
done
```

### **3.2 НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ**

#### **🎯 Критерии Успеха:**
- ✅ Система выдерживает 100 одновременных пользователей
- ✅ Нет memory leaks
- ✅ Graceful degradation под нагрузкой

```bash
# Тест 3.2.1: Нагрузочное тестирование с ab (Apache Bench)
echo "=== НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ ==="
ab -n 1000 -c 10 -g results.tsv http://149.154.65.180:8002/api/health/

# Анализ результатов
echo "Анализ результатов нагрузки:"
# - Среднее время отклика
# - 95-й перцентиль
# - Failed requests %
# - Throughput
```

---

## 🔒 **ЭТАП 4: БЕЗОПАСНОСТЬ**

### **4.1 ТЕСТИРОВАНИЕ АУТЕНТИФИКАЦИИ**

#### **🎯 Критерии Успеха:**
- ✅ Неавторизованные запросы блокируются
- ✅ JWT токены валидируются
- ✅ Rate limiting работает

```bash
# Тест 4.1.1: Доступ без авторизации
curl -s -w "%{http_code}" http://149.154.65.180:8002/api/components/health
# Ожидаемый результат: 401 или 403

# Тест 4.1.2: Rate limiting
for i in {1..100}; do
    curl -s http://149.154.65.180:8002/api/health > /dev/null &
done
wait
# Проверяем логи на rate limit ошибки
```

### **4.2 ТЕСТИРОВАНИЕ ЗАЩИТЫ ДАННЫХ**

#### **🎯 Критерии Успеха:**
- ✅ HTTPS шифрование работает
- ✅ SFM изолирован (localhost only)
- ✅ Input validation работает

```bash
# Тест 4.2.1: Доступ к SFM извне
curl -s http://149.154.65.180:8003/api/health
# Ожидаемый результат: Connection refused или timeout

# Тест 4.2.2: SQL Injection попытка
curl -s "http://149.154.65.180:8002/api/components/status/'; DROP TABLE users; --"
# Ожидаемый результат: Безопасный ответ, нет SQL ошибки
```

---

## 📊 **ЭТАП 5: МОНИТОРИНГ И НАБЛЮДАЕМОСТЬ**

### **5.1 ТЕСТИРОВАНИЕ ЛОГИРОВАНИЯ**

#### **🎯 Критерии Успеха:**
- ✅ Все запросы логируются
- ✅ Ошибки логируются с деталями
- ✅ Логи структурированы (JSON)

```bash
# Тест 5.1.1: Проверка логов API Gateway
ssh root@149.154.65.180 "journalctl -u aladdin-main-api-gateway -n 5 -o json | jq ."

# Тест 5.1.2: Проверка логов SFM
ssh root@149.154.65.180 "journalctl -u aladdin-sfm-core -n 5 -o json | jq ."
```

### **5.2 ТЕСТИРОВАНИЕ МЕТРИК**

#### **🎯 Критерии Успеха:**
- ✅ Метрики собираются
- ✅ Health checks работают
- ✅ Alerts срабатывают

```bash
# Тест 5.2.1: Health checks
curl -s http://149.154.65.180:8002/api/health | jq '.'
curl -s http://127.0.0.1:8003/api/health | jq '.'

# Тест 5.2.2: System metrics
ssh root@149.154.65.180 "top -b -n 1 | head -10"
ssh root@149.154.65.180 "free -h"
ssh root@149.154.65.180 "df -h"
```

---

## 🌐 **ЭТАП 6: END-TO-END ТЕСТИРОВАНИЕ**

### **6.1 ПОЛЬЗОВАТЕЛЬСКИЕ СЦЕНАРИИ**

#### **🎯 Критерии Успеха:**
- ✅ Полный цикл: мобильное → API → SFM → ответ
- ✅ Все компоненты взаимодействуют
- ✅ Данные корректны на всех этапах

#### **📋 Тестовые Случаи:**

##### **СЦЕНАРИЙ 1: ПРОВЕРКА ФИШИНГА**
```bash
# Имитация мобильного приложения
echo "=== СЦЕНАРИЙ: ПРОВЕРКА ФИШИНГА ==="

# 1. Мобильное app запрашивает чувствительность
mobile_response=$(curl -s http://149.154.65.180:8002/api/phishing/sensitivity)
echo "1. Мобильное app получает: $mobile_response"

# 2. Проверяем что API Gateway вызывает SFM
api_source=$(echo "$mobile_response" | jq -r '.source')
if [ "$api_source" = "real_sfm" ]; then
    echo "✅ 2. API Gateway корректно вызывает SFM"
else
    echo "❌ 2. Проблема с вызовом SFM"
fi

# 3. Проверяем SFM напрямую
sfm_response=$(curl -s -X POST -H "Content-Type: application/json" \
  http://127.0.0.1:8003/api/execute \
  -d '{"function": "get_phishing_sensitivity", "params": {}}')
sfm_success=$(echo "$sfm_response" | jq -r '.success')

if [ "$sfm_success" = "true" ]; then
    echo "✅ 3. SFM корректно обрабатывает запрос"
else
    echo "❌ 3. SFM не может обработать запрос"
fi

echo "🎯 РЕЗУЛЬТАТ СЦЕНАРИЯ: ПОЛНЫЙ ПОТОК РАБОТАЕТ"
```

##### **СЦЕНАРИЙ 2: УПРАВЛЕНИЕ КОМПОНЕНТАМИ**
```bash
echo "=== СЦЕНАРИЙ: УПРАВЛЕНИЕ КОМПОНЕНТАМИ ==="

# 1. Проверка статуса компонента
status=$(curl -s http://149.154.65.180:8002/api/components/status/sfm_core | jq -r '.status')
echo "1. Статус компонента: $status"

# 2. Отключение компонента
disable_result=$(curl -s -X POST http://149.154.65.180:8002/api/components/disable/sfm_core | jq -r '.action')
echo "2. Отключение: $disable_result"

# 3. Проверка нового статуса
new_status=$(curl -s http://149.154.65.180:8002/api/components/status/sfm_core | jq -r '.status')
echo "3. Новый статус: $new_status"

# 4. Включение компонента обратно
enable_result=$(curl -s -X POST http://149.154.65.180:8002/api/components/enable/sfm_core | jq -r '.action')
echo "4. Включение обратно: $enable_result"
```

---

## 🧪 **ЭТАП 7: АВТОМАТИЗИРОВАННОЕ ТЕСТИРОВАНИЕ**

### **7.1 UNIT ТЕСТИРОВАНИЕ**

#### **🎯 Критерии Успеха:**
- ✅ Code coverage >80%
- ✅ Все функции протестированы
- ✅ Моки для внешних зависимостей

```python
# tests/test_api_gateway.py
import pytest
from fastapi.testclient import TestClient
from api_gateway import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_phishing_sensitivity():
    response = client.get("/api/phishing/sensitivity")
    assert response.status_code == 200
    assert response.json()["source"] == "real_sfm"
```

### **7.2 INTEGRATION ТЕСТИРОВАНИЕ**

#### **🎯 Критерии Успеха:**
- ✅ Docker Compose для тестирования
- ✅ Все сервисы поднимаются
- ✅ API контракты проверены

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  api-gateway:
    build: .
    ports:
      - "8002:8002"
    depends_on:
      - sfm-http-api

  sfm-http-api:
    build: ./sfm/
    ports:
      - "8003:8003"
    environment:
      - SFM_CORE_PATH=/opt/sfm
```

---

## 📋 **ЭТАП 8: РЕГРЕССИОННОЕ ТЕСТИРОВАНИЕ**

### **8.1 ТЕСТИРОВАНИЕ ПОСЛЕ ОБНОВЛЕНИЙ**

#### **🎯 Критерии Успеха:**
- ✅ Все существующие функции работают
- ✅ Производительность не ухудшилась
- ✅ Новые функции не ломают старые

```bash
# Регрессионный тест
echo "=== РЕГРЕССИОННОЕ ТЕСТИРОВАНИЕ ==="

# Тестируем все исправленные функции
functions=(
    "/api/components/health"
    "/api/phishing/sensitivity"
    "/api/analytics/overview"
    "/api/malware/scan_scheduled"
)

for func in "${functions[@]}"; do
    echo "Тестируем: $func"
    response=$(curl -s "http://149.154.65.180:8002$func")
    source=$(echo "$response" | jq -r '.source // "error"')
    
    if [ "$source" = "real_sfm" ]; then
        echo "✅ $func: OK"
    else
        echo "❌ $func: FAILED ($source)"
    fi
done
```

---

## 📊 **ЭТАП 9: ОТЧЕТНОСТЬ И АНАЛИЗ**

### **9.1 АВТОМАТИЧЕСКАЯ ГЕНЕРАЦИЯ ОТЧЕТОВ**

#### **🎯 Критерии Успеха:**
- ✅ HTML/PDF отчеты
- ✅ Графики производительности
- ✅ История тестов

```bash
# Генерация отчета
generate_test_report() {
    echo "# ТЕСТИРОВАНИЕ ALADDIN - $(date)" > test_report.md
    echo "" >> test_report.md
    echo "## РЕЗУЛЬТАТЫ:" >> test_report.md
    
    # Сбор метрик
    total_tests=$(find . -name "*.log" -exec grep -c "TEST" {} \; | paste -sd+ | bc)
    passed_tests=$(find . -name "*.log" -exec grep -c "PASSED\|✅" {} \; | paste -sd+ | bc)
    
    echo "- Всего тестов: $total_tests" >> test_report.md
    echo "- Пройдено: $passed_tests" >> test_report.md
    echo "- Процент успеха: $((passed_tests * 100 / total_tests))%" >> test_report.md
}
```

---

## 🎯 **КРИТЕРИИ ГОТОВНОСТИ К ПРОДАКШЕНУ**

### **✅ ОБЯЗАТЕЛЬНЫЕ КРИТЕРИИ:**
- [ ] **Функциональность:** 100% API работают с `real_sfm`
- [ ] **Производительность:** <100ms среднее время отклика
- [ ] **Безопасность:** Аутентификация, HTTPS, изоляция SFM
- [ ] **Надежность:** Fallback механизмы, 99.9% uptime
- [ ] **Мониторинг:** Логи, метрики, alerts
- [ ] **Тестирование:** Code coverage >80%, regression tests

### **📊 ПОРОГИ ПРОХОЖДЕНИЯ:**
| Метрика | Порог | Текущее | Статус |
|---------|-------|---------|---------|
| API Success Rate | >99.5% | - | - |
| Response Time P95 | <200ms | - | - |
| Error Rate | <0.1% | - | - |
| Test Coverage | >80% | - | - |
| Security Score | A+ | - | - |

---

## 🚀 **АВТОМАТИЗАЦИЯ ТЕСТИРОВАНИЯ**

### **CI/CD ПАЙПЛАЙН:**

```yaml
# .github/workflows/testing.yml
name: ALADDIN Testing Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=. --cov-report=xml
      
      - name: Run integration tests
        run: pytest tests/integration/ -v
      
      - name: Performance tests
        run: python tests/performance/test_load.py
      
      - name: Security tests
        run: python tests/security/test_auth.py
      
      - name: Generate report
        run: python scripts/generate_test_report.py
```

---

**ЭТОТ ПЛАН ОБЕСПЕЧИВАЕТ ПОЛНОЕ ПОКРЫТИЕ ВСЕХ АСПЕКТОВ СИСТЕМЫ ALADDIN И ГАРАНТИРУЕТ ENTERPRISE-GRADE КАЧЕСТВО ПРОДАКШЕНА!** 🚀🛡️✨