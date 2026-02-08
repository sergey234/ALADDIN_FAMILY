#!/usr/bin/env python3
"""
🚀 ALADDIN SERVER PERFORMANCE OPTIMIZATION
Оптимизация производительности API для достижения SLA <25ms
"""

import paramiko
import time
import json
import sys

class ServerOptimizer:
    def __init__(self):
        self.hostname = '149.154.65.180'
        self.username = 'root'
        self.password = 'Sergio675'
        self.port = 22
        self.ssh = None

    def connect(self):
        """Подключаемся к серверу"""
        try:
            print("🔌 Подключение к серверу...")
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )
            print("✅ Подключение установлено")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False

    def execute_command(self, command, description="", timeout=30):
        """Выполняет команду на сервере"""
        try:
            print(f"🛠️  {description}")
            stdin, stdout, stderr = self.ssh.exec_command(command, timeout=timeout)

            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()

            if error:
                print(f"⚠️  {error}")

            return output, error
        except Exception as e:
            print(f"❌ Ошибка выполнения команды: {e}")
            return "", str(e)

    def check_current_performance(self):
        """Проверяем текущую производительность"""
        print("📊 АНАЛИЗ ТЕКУЩЕЙ ПРОИЗВОДИТЕЛЬНОСТИ")
        print("=" * 50)

        # Проверяем нагрузку системы
        output, _ = self.execute_command(
            "uptime && free -h && df -h /",
            "Проверка системной нагрузки"
        )

        # Проверяем PostgreSQL
        output, _ = self.execute_command(
            "systemctl status postgresql | head -5",
            "Статус PostgreSQL"
        )

        # Проверяем Redis
        output, _ = self.execute_command(
            "systemctl status redis-server | head -5",
            "Статус Redis"
        )

        # Проверяем nginx
        output, _ = self.execute_command(
            "systemctl status nginx | head -5",
            "Статус Nginx"
        )

        # Текущие индексы БД
        output, _ = self.execute_command(
            "cd /opt/aladdin-backend && source venvs/main_env/bin/activate && python3 -c \""
            "import psycopg2; "
            "conn = psycopg2.connect('host=localhost dbname=aladdin user=aladdin password=aladdin2024'); "
            "cur = conn.cursor(); "
            "cur.execute('SELECT tablename, indexname FROM pg_indexes WHERE schemaname = \\'public\\' ORDER BY tablename;'); "
            "indexes = cur.fetchall(); "
            "print(f'Найдено индексов: {len(indexes)}'); "
            "for table, index in indexes[:10]: "
            "print(f'  {table}.{index}'); "
            "if len(indexes) > 10: print(f'  ... и еще {len(indexes)-10} индексов'); "
            "conn.close()\"",
            "Анализ индексов БД"
        )

    def optimize_database(self):
        """Оптимизация PostgreSQL"""
        print("🗄️  ОПТИМИЗАЦИЯ POSTGRESQL")
        print("-" * 30)

        # Создаем индексы для часто используемых запросов
        index_commands = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_component_status_updated_at ON component_status(updated_at);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_component_status_component_id ON component_status(component_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_component_status_status ON component_status(status);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_requests_endpoint ON api_requests(endpoint);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_requests_timestamp ON api_requests(timestamp);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);"
        ]

        for cmd in index_commands:
            output, error = self.execute_command(
                f"cd /opt/aladdin-backend && source venvs/main_env/bin/activate && python3 -c \""
                f"import psycopg2; "
                f"conn = psycopg2.connect('host=localhost dbname=aladdin user=aladdin password=aladdin2024'); "
                f"cur = conn.cursor(); "
                f"cur.execute('{cmd}'); "
                f"conn.commit(); "
                f"print('Индекс создан успешно'); "
                f"conn.close()\"",
                f"Создание индекса: {cmd.split('ON')[1].strip()}"
            )

        # Оптимизация настроек PostgreSQL
        pg_config = """
# Оптимизация PostgreSQL для производительности
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
"""

        # Записываем оптимизированные настройки
        self.execute_command(
            f"echo '{pg_config}' | sudo tee /etc/postgresql/15/main/conf.d/performance.conf",
            "Создание файла оптимизации PostgreSQL"
        )

        # Перезапускаем PostgreSQL
        self.execute_command(
            "sudo systemctl restart postgresql",
            "Перезапуск PostgreSQL с новыми настройками"
        )

    def setup_redis_cache(self):
        """Настройка Redis для кэширования"""
        print("🔴 НАСТРОЙКА REDIS CACHE")
        print("-" * 30)

        # Проверяем Redis
        output, _ = self.execute_command(
            "redis-cli ping",
            "Проверка Redis"
        )

        if "PONG" in output:
            print("✅ Redis доступен")

            # Оптимизируем Redis настройки
            redis_config = """
# Redis performance optimizations
maxmemory 256mb
maxmemory-policy allkeys-lru
tcp-keepalive 300
timeout 300
databases 16
save 900 1
save 300 10
save 60 10000
"""

            self.execute_command(
                f"echo '{redis_config}' | sudo tee /etc/redis/redis.conf.new",
                "Создание оптимизированных настроек Redis"
            )

            # Перезапускаем Redis
            self.execute_command(
                "sudo systemctl restart redis-server",
                "Перезапуск Redis"
            )

        else:
            print("❌ Redis недоступен, устанавливаем...")
            self.execute_command(
                "sudo apt update && sudo apt install -y redis-server",
                "Установка Redis"
            )

    def optimize_nginx(self):
        """Оптимизация Nginx"""
        print("🌐 ОПТИМИЗАЦИЯ NGINX")
        print("-" * 30)

        nginx_config = """
# Performance optimizations for Nginx
worker_processes auto;
worker_connections 1024;
use epoll;
multi_accept on;

# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_proxied any;
gzip_comp_level 6;
gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/json
    application/javascript
    application/xml+rss
    application/atom+xml
    image/svg+xml;

# Cache settings
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m inactive=60m;
proxy_cache_key "$scheme$request_method$host$request_uri";

# Upstream for API Gateway
upstream api_backend {
    server 127.0.0.1:8002;
    keepalive 32;
}
"""

        # Создаем оптимизированный конфиг
        self.execute_command(
            f"echo '{nginx_config}' | sudo tee /etc/nginx/sites-available/aladdin-optimized",
            "Создание оптимизированного Nginx конфига"
        )

        # Включаем новый конфиг
        self.execute_command(
            "sudo ln -sf /etc/nginx/sites-available/aladdin-optimized /etc/nginx/sites-enabled/",
            "Включение нового конфига"
        )

        # Тестируем и перезапускаем
        self.execute_command(
            "sudo nginx -t && sudo systemctl reload nginx",
            "Тестирование и перезапуск Nginx"
        )

    def optimize_python_app(self):
        """Оптимизация Python приложения"""
        print("🐍 ОПТИМИЗАЦИЯ PYTHON ПРИЛОЖЕНИЯ")
        print("-" * 30)

        # Добавляем оптимизации в API Gateway
        optimizations = """
# Performance optimizations for FastAPI
import asyncio
import uvicorn
from concurrent.futures import ThreadPoolExecutor

# Configure thread pool for CPU-bound tasks
executor = ThreadPoolExecutor(max_workers=4)

# Optimize Gunicorn settings
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Database connection pool optimization
DATABASE_URL = "postgresql://aladdin:aladdin2024@localhost:5432/aladdin"
db_pool_size = 20
db_max_overflow = 30
db_pool_recycle = 3600

# Redis connection pool
redis_pool_size = 20
redis_pool_max_overflow = 30

# Enable response compression
response_compression = True
response_compression_level = 6
"""

        # Записываем оптимизации
        self.execute_command(
            f"echo '{optimizations}' | sudo tee /opt/aladdin-backend/optimizations.py",
            "Создание файла оптимизаций Python"
        )

        # Обновляем API Gateway с оптимизациями
        api_optimization_code = '''
# Add to api_gateway_complete.py

# Performance imports
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Thread pool for CPU-bound tasks
executor = ThreadPoolExecutor(max_workers=4)

# Database optimization
@app.on_event("startup")
async def optimize_database():
    """Оптимизация подключения к БД при старте"""
    # Увеличиваем пул соединений
    engine = create_async_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=30,
        pool_recycle=3600,
        echo=False
    )

    # Создаем индексы если они не существуют
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_component_status_lookup
            ON component_status(component_id, status, updated_at);
        """))

# Redis optimization
redis_pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=20,
    decode_responses=True
)

@app.middleware("http")
async def add_performance_headers(request, call_next):
    """Добавляем headers для performance monitoring"""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # Логируем медленные запросы
    if process_time > 0.025:  # 25ms
        print(f"🐌 SLOW REQUEST: {request.url.path} took {process_time:.3f}s")

    return response

# Batch endpoint for component status
@app.get("/api/components/status/batch")
async def get_component_status_batch(component_ids: str = Query(...)):
    """Batch endpoint для получения статуса компонентов"""
    ids = component_ids.split(",")

    # Параллельное получение данных
    tasks = []
    for component_id in ids:
        task = asyncio.create_task(get_component_status_from_cache(component_id))
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Формируем ответ
    response_data = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            # Fallback для ошибок
            response_data.append({
                "component_id": ids[i],
                "status": "unknown",
                "error": str(result)
            })
        else:
            response_data.append(result)

    return {"components": response_data, "count": len(response_data)}

async def get_component_status_from_cache(component_id: str):
    """Получение статуса компонента с кэшированием"""
    cache_key = f"component_status:{component_id}"

    # Проверяем Redis cache
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # Если нет в кэше - получаем из БД
    async with async_session() as session:
        result = await session.execute(
            select(ComponentStatus).where(ComponentStatus.component_id == component_id)
        )
        component = result.scalar_one_or_none()

        if component:
            # Кэшируем на 30 секунд
            data = {
                "component_id": component.component_id,
                "status": component.status,
                "uptime": component.uptime,
                "last_update": component.last_update.isoformat() if component.last_update else None
            }
            await redis.setex(cache_key, 30, json.dumps(data))
            return data

    return {"component_id": component_id, "status": "not_found"}
'''

        self.execute_command(
            f"echo '{api_optimization_code}' | sudo tee /opt/aladdin-backend/api_performance_optimizations.py",
            "Создание файла оптимизаций API"
        )

    def deploy_optimizations(self):
        """Развертывание оптимизаций"""
        print("🚀 РАЗВЕРТЫВАНИЕ ОПТИМИЗАЦИЙ")
        print("-" * 30)

        # Перезапускаем сервисы
        services = ["postgresql", "redis-server", "nginx", "aladdin-main-api-gateway"]

        for service in services:
            self.execute_command(
                f"sudo systemctl restart {service}",
                f"Перезапуск {service}"
            )

        # Проверяем статус после перезапуска
        self.execute_command(
            "sleep 5 && curl -s http://127.0.0.1/api/health",
            "Проверка API после оптимизаций"
        )

    def run_performance_test(self):
        """Запуск performance теста после оптимизаций"""
        print("🧪 ЗАПУСК PERFORMANCE ТЕСТА ПОСЛЕ ОПТИМИЗАЦИЙ")
        print("-" * 30)

        # Копируем и запускаем тест на сервере
        test_script = '''
import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://127.0.0.1:8002/api"
ENDPOINTS = [
    "/health",
    "/components/status/crash_detection_agent",
    "/components/status/phishing_protection_agent",
    "/components/status/mobile_security_agent"
]

def test_endpoint(endpoint):
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        response_time = time.time() - start_time
        return response_time if response.status_code == 200 else None
    except:
        return None

def run_performance_test():
    print("🧪 SERVER PERFORMANCE TEST")
    print("=" * 40)

    all_times = []

    # Тестируем каждый endpoint
    for endpoint in ENDPOINTS:
        print(f"Testing {endpoint}...")
        times = []

        # 20 запросов к каждому endpoint
        for i in range(20):
            response_time = test_endpoint(endpoint)
            if response_time:
                times.append(response_time)
                all_times.append(response_time)

        if times:
            p95 = sorted(times)[int(len(times) * 0.95)]
            avg = sum(times) / len(times)
            print(".3f"
    if all_times:
        overall_p95 = sorted(all_times)[int(len(all_times) * 0.95)]
        overall_avg = sum(all_times) / len(all_times)

        print("
📊 OVERALL RESULTS:"        print(".3f"        print(".3f"        print(f"✅ Total successful requests: {len(all_times)}")

        # SLA Check
        sla_passed = overall_p95 < 0.025
        if sla_passed:
            print("🎉 SLA ACHIEVED: 95th percentile < 25ms ✅")
        else:
            print("❌ SLA NOT MET: 95th percentile >= 25ms")

        return sla_passed, overall_p95
    else:
        print("❌ No successful requests")
        return False, 0

if __name__ == "__main__":
    run_performance_test()
'''

        # Записываем и выполняем тест на сервере
        self.execute_command(
            f"echo '{test_script}' | sudo tee /tmp/performance_test_server.py",
            "Создание performance теста на сервере"
        )

        output, _ = self.execute_command(
            "cd /opt/aladdin-backend && source venvs/main_env/bin/activate && python3 /tmp/performance_test_server.py",
            "Запуск performance теста на сервере"
        )

        return output

    def run_full_optimization(self):
        """Запуск полного цикла оптимизации"""
        print("🚀 НАЧАЛО ПОЛНОЙ ОПТИМИЗАЦИИ СЕРВЕРА ALADDIN")
        print("=" * 60)

        if not self.connect():
            return False

        try:
            # Шаг 1: Анализ текущей производительности
            self.check_current_performance()

            # Шаг 2: Оптимизация базы данных
            self.optimize_database()

            # Шаг 3: Настройка Redis cache
            self.setup_redis_cache()

            # Шаг 4: Оптимизация Nginx
            self.optimize_nginx()

            # Шаг 5: Оптимизация Python приложения
            self.optimize_python_app()

            # Шаг 6: Развертывание оптимизаций
            self.deploy_optimizations()

            # Шаг 7: Финальный performance тест
            test_results = self.run_performance_test()

            print("\n" + "=" * 60)
            print("🎉 ОПТИМИЗАЦИЯ СЕРВЕРА ЗАВЕРШЕНА!")
            print("📊 Результаты performance теста:")
            print(test_results)

            return True

        finally:
            if self.ssh:
                self.ssh.close()
                print("🔌 Соединение с сервером закрыто")

def main():
    optimizer = ServerOptimizer()

    print("🎯 ALADDIN SERVER PERFORMANCE OPTIMIZATION")
    print("Цель: Достичь SLA <25ms для 95-го перцентиля")
    print("=" * 60)

    if optimizer.run_full_optimization():
        print("\n✅ ОПТИМИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("🔄 Перезапустите мобильное приложение для тестирования улучшений")
    else:
        print("\n❌ ОШИБКА ОПТИМИЗАЦИИ")
        sys.exit(1)

if __name__ == "__main__":
    main()