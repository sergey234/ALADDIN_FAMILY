# 🧪 S4-05: НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ (1,000 ПОЛЬЗОВАТЕЛЕЙ)

**Статус:** Ожидает выполнения  
**Приоритет:** Высокий  
**Время:** 2-3 часа

---

## 🎯 ЦЕЛЬ

Проверить производительность системы под нагрузкой 1,000 одновременных пользователей.

---

## 📋 ЧТО НУЖНО СДЕЛАТЬ

### 1. Установить инструменты тестирования

**Вариант A: Apache Bench (ab)**
```bash
# Ubuntu/Debian
apt-get install apache2-utils

# macOS
brew install httpd
```

**Вариант B: wrk**
```bash
# Ubuntu/Debian
apt-get install wrk

# macOS
brew install wrk
```

**Вариант C: Locust (Python)**
```bash
pip install locust
```

---

### 2. Подготовить тестовые сценарии

**Основные endpoints для тестирования:**
- `GET /api/health` - проверка здоровья
- `GET /api/metrics` - получение метрик
- `GET /api/alerts` - получение алертов
- `POST /api/auth/login` - авторизация
- `GET /api/user/profile` - профиль пользователя

---

### 3. Выполнить нагрузочное тестирование

**Apache Bench (1,000 запросов, 100 одновременных):**
```bash
ab -n 1000 -c 100 -k https://aladdin-ai.ru/api/health
```

**wrk (1,000 соединений, 10 потоков, 30 секунд):**
```bash
wrk -t10 -c1000 -d30s https://aladdin-ai.ru/api/health
```

**Locust (1,000 пользователей, скорость роста 10/сек):**
```python
# Создать файл locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def health_check(self):
        self.client.get("/api/health")
    
    @task(3)
    def get_metrics(self):
        self.client.get("/api/metrics")
    
    @task(2)
    def get_alerts(self):
        self.client.get("/api/alerts")

# Запуск
locust -f locustfile.py --host=https://aladdin-ai.ru --users 1000 --spawn-rate 10
```

---

### 4. Мониторинг во время тестирования

**На сервере:**
```bash
# CPU и RAM
top -b -n 1 | head -20

# Сетевые соединения
netstat -an | grep :8001 | wc -l

# Логи API Gateway
tail -f /var/log/aladdin/api_gateway/api_gateway.log

# Метрики системы
curl http://localhost:8001/api/metrics
```

---

### 5. Анализ результатов

**Что проверить:**
- ✅ Время отклика (должно быть < 200ms для 95% запросов)
- ✅ Количество успешных запросов (должно быть > 99%)
- ✅ Ошибки (должно быть < 1%)
- ✅ Использование CPU (не должно превышать 80%)
- ✅ Использование RAM (не должно превышать 80%)
- ✅ Количество открытых соединений

---

## 📊 КРИТЕРИИ УСПЕХА

1. ✅ Система выдерживает 1,000 одновременных пользователей
2. ✅ Время отклика < 200ms для 95% запросов
3. ✅ Успешность запросов > 99%
4. ✅ CPU < 80%
5. ✅ RAM < 80%
6. ✅ Нет критических ошибок в логах

---

## 📝 ОТЧЕТ

**Создать документ с результатами:**
- Время выполнения теста
- Количество запросов
- Успешность (%)
- Среднее время отклика
- Максимальное время отклика
- Использование ресурсов (CPU, RAM)
- Найденные проблемы
- Рекомендации

---

## 🔧 КОМАНДЫ ДЛЯ ВЫПОЛНЕНИЯ

**Полный набор команд находится в:** `docs/S4-05_COMMANDS.sh`

---

**Готово к выполнению!** 🚀

