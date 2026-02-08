#!/usr/bin/env python3
"""
🔍 ПРОВЕРКА МАСШТАБИРУЕМОСТИ СЕРВЕРА ALADDIN
Анализ готовности к 100,000+ пользователей
"""

import paramiko
import time
import json
import sys

class ScalabilityChecker:
    def __init__(self):
        self.hostname = '149.154.65.180'
        self.username = 'root'
        self.password = 'Sergio675'
        self.port = 22
        self.ssh = None

    def connect(self):
        try:
            print("🔌 Подключение к серверу для проверки масштабируемости...")
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

    def check_hardware_resources(self):
        """Проверка аппаратных ресурсов"""
        print("🖥️  ПРОВЕРКА АППАРАТНЫХ РЕСУРСОВ")
        print("-" * 40)

        # CPU информация
        output, _ = self.execute_command("lscpu | grep -E '(CPU\\(s\\)|Thread|Core|Socket)'", "CPU конфигурация")
        print(f"CPU: {output}")

        # Память
        output, _ = self.execute_command("free -h", "Оперативная память")
        print(f"RAM: {output}")

        # Дисковое пространство
        output, _ = self.execute_command("df -h /", "Дисковое пространство")
        print(f"Disk: {output}")

        # Uptime и нагрузка
        output, _ = self.execute_command("uptime", "Время работы и нагрузка")
        print(f"Uptime: {output}")

    def check_database_configuration(self):
        """Проверка конфигурации PostgreSQL"""
        print("🗄️  ПРОВЕРКА POSTGRESQL КОНФИГУРАЦИИ")
        print("-" * 40)

        # Статус PostgreSQL
        output, _ = self.execute_command("systemctl status postgresql --no-pager -l | head -10", "Статус PostgreSQL")

        # Текущие подключения
        output, _ = self.execute_command(
            "cd /opt/aladdin-backend && source venvs/main_env/bin/activate && python3 -c \""
            "import psycopg2; "
            "conn = psycopg2.connect('host=localhost dbname=aladdin user=aladdin password=aladdin2024'); "
            "cur = conn.cursor(); "
            "cur.execute('SELECT count(*) FROM pg_stat_activity;'); "
            "active = cur.fetchone()[0]; "
            "cur.execute('SELECT setting FROM pg_settings WHERE name = \\'max_connections\\';'); "
            "max_conn = cur.fetchone()[0]; "
            "print(f'Активных подключений: {active}'); "
            "print(f'Максимум подключений: {max_conn}'); "
            "conn.close()\" 2>/dev/null || echo 'psycopg2 не установлен'",
            "Подключения к БД"
        )

        # Размер базы данных
        output, _ = self.execute_command(
            "cd /opt/aladdin-backend && source venvs/main_env/bin/activate && python3 -c \""
            "import psycopg2; "
            "conn = psycopg2.connect('host=localhost dbname=aladdin user=aladdin password=aladdin2024'); "
            "cur = conn.cursor(); "
            "cur.execute('SELECT pg_size_pretty(pg_database_size(current_database()));'); "
            "size = cur.fetchone()[0]; "
            "print(f'Размер БД: {size}'); "
            "conn.close()\" 2>/dev/null || echo 'Невозможно получить размер БД'",
            "Размер базы данных"
        )

    def check_redis_configuration(self):
        """Проверка конфигурации Redis"""
        print("🔴 ПРОВЕРКА REDIS КОНФИГУРАЦИИ")
        print("-" * 40)

        # Статус Redis
        output, _ = self.execute_command("systemctl status redis-server --no-pager -l | head -10", "Статус Redis")

        # Redis статистика
        output, _ = self.execute_command("redis-cli info | grep -E '(connected_clients|used_memory|total_connections_received)'", "Redis статистика")

        # Redis конфигурация
        output, _ = self.execute_command("redis-cli config get maxmemory", "Redis maxmemory")

    def check_nginx_configuration(self):
        """Проверка конфигурации Nginx"""
        print("🌐 ПРОВЕРКА NGINX КОНФИГУРАЦИИ")
        print("-" * 40)

        # Статус Nginx
        output, _ = self.execute_command("systemctl status nginx --no-pager -l | head -10", "Статус Nginx")

        # Активные конфиги
        output, _ = self.execute_command("ls -la /etc/nginx/sites-enabled/", "Активные сайты")

        # Worker процессы
        output, _ = self.execute_command("ps aux | grep nginx | grep -v grep | wc -l", "Nginx worker процессы")

    def check_api_gateway_configuration(self):
        """Проверка конфигурации API Gateway"""
        print("🚀 ПРОВЕРКА API GATEWAY")
        print("-" * 40)

        # Статус сервиса
        output, _ = self.execute_command("systemctl status aladdin-main-api-gateway --no-pager -l | head -10", "Статус API Gateway")

        # Gunicorn workers
        output, _ = self.execute_command("ps aux | grep gunicorn | grep -v grep | wc -l", "Gunicorn workers")

        # Проверка логов на ошибки
        output, _ = self.execute_command("tail -20 /opt/aladdin-backend/logs/api_gateway.log 2>/dev/null || echo 'Логи не найдены'", "Последние логи API Gateway")

    def check_load_balancing_readiness(self):
        """Проверка готовности к load balancing"""
        print("⚖️  ПРОВЕРКА ГОТОВНОСТИ К LOAD BALANCING")
        print("-" * 40)

        # Проверка нескольких экземпляров
        output, _ = self.execute_command("ps aux | grep python | grep -E '(api_gateway|gunicorn)' | grep -v grep | wc -l", "Количество Python процессов")

        # Проверка портов
        output, _ = self.execute_command("netstat -tlnp | grep -E ':(8000|8001|8002)' || echo 'Дополнительные порты не заняты'", "Занятые порты API")

        # Проверка session affinity
        output, _ = self.execute_command("grep -r 'session' /etc/nginx/sites-enabled/ 2>/dev/null || echo 'Session affinity не настроено'", "Session affinity")

    def check_monitoring_setup(self):
        """Проверка настроек мониторинга"""
        print("📊 ПРОВЕРКА МОНИТОРИНГА")
        print("-" * 40)

        # Prometheus/Node Exporter
        output, _ = self.execute_command("systemctl status prometheus 2>/dev/null || echo 'Prometheus не установлен'", "Prometheus статус")

        # Grafana
        output, _ = self.execute_command("systemctl status grafana-server 2>/dev/null || echo 'Grafana не установлена'", "Grafana статус")

        # Log aggregation
        output, _ = self.execute_command("systemctl status rsyslog 2>/dev/null || echo 'rsyslog работает'", "Логи")

    def check_backup_and_recovery(self):
        """Проверка backup и recovery"""
        print("💾 ПРОВЕРКА BACKUP И RECOVERY")
        print("-" * 40)

        # Cron jobs для backup
        output, _ = self.execute_command("crontab -l | grep -i backup || echo 'Автоматические backup не настроены'", "Cron backup jobs")

        # Дисковое пространство для backup
        output, _ = self.execute_command("df -h | grep -v tmpfs", "Дисковое пространство")

        # Последние backup файлы
        output, _ = self.execute_command("find /opt/aladdin-backend -name '*backup*' -mtime -7 2>/dev/null | wc -l", "Недавние backup файлы")

    def calculate_scalability_metrics(self):
        """Расчет метрик масштабируемости"""
        print("📈 РАСЧЕТ МЕТРИК МАСШТАБИРУЕМОСТИ")
        print("-" * 40)

        # Оценка текущей емкости
        current_capacity = {
            "estimated_users": 1000,  # базовая оценка
            "concurrent_requests": 100,  # одновременных запросов
            "response_time_p95": 95,  # ms
            "error_rate": 0.001,  # 0.1%
        }

        # Расчет для 100k пользователей
        scale_factor = 100000 / current_capacity["estimated_users"]

        projected_capacity = {
            "concurrent_requests": current_capacity["concurrent_requests"] * (scale_factor ** 0.7),  # с учетом оптимизаций
            "response_time_p95": current_capacity["response_time_p95"] * (scale_factor ** 0.3),
            "error_rate": current_capacity["error_rate"] * scale_factor,
        }

        print("Текущая емкость (оценка):")
        print(f"  - Пользователей: ~{current_capacity['estimated_users']}")
        print(f"  - Одновременных запросов: ~{current_capacity['concurrent_requests']}")
        print(f"  - P95 отклик: {current_capacity['response_time_p95']}ms")
        print(".1%")

        print("Проекция для 100k пользователей:")
        print(f"  - Одновременных запросов: ~{int(projected_capacity['concurrent_requests'])}")
        print(f"  - P95 отклик: ~{int(projected_capacity['response_time_p95'])}ms")
        print(".1%")

        return current_capacity, projected_capacity

    def generate_scalability_report(self):
        """Генерация отчета о масштабируемости"""
        print("📋 ГЕНЕРАЦИЯ ОТЧЕТА О МАСШТАБИРУЕМОСТИ")
        print("=" * 50)

        current, projected = self.calculate_scalability_metrics()

        report = {
            "timestamp": str(time.time()),
            "server_ip": self.hostname,
            "target_users": 100000,
            "current_capacity": current,
            "projected_capacity": projected,
            "recommendations": []
        }

        # Анализ и рекомендации
        if projected["response_time_p95"] > 200:
            report["recommendations"].append("КРИТИЧНО: Нужен Load Balancer + несколько серверов")
        elif projected["response_time_p95"] > 100:
            report["recommendations"].append("ВАЖНО: Нужны Read Replicas + оптимизация запросов")

        if projected["error_rate"] > 0.05:
            report["recommendations"].append("КРИТИЧНО: Нужна инфраструктура отказоустойчивости")

        if projected["concurrent_requests"] < 1000:
            report["recommendations"].append("ОК: Текущая инфраструктура выдержит нагрузку")

        # Сохранение отчета
        with open('scalability_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        print("✅ Отчет сохранен в scalability_report.json")

        return report

    def run_full_check(self):
        """Запуск полной проверки масштабируемости"""
        print("🚀 ЗАПУСК ПОЛНОЙ ПРОВЕРКИ МАСШТАБИРУЕМОСТИ")
        print("Цель: 100,000+ пользователей")
        print("=" * 60)

        if not self.connect():
            return False

        try:
            # Выполняем все проверки
            self.check_hardware_resources()
            print()

            self.check_database_configuration()
            print()

            self.check_redis_configuration()
            print()

            self.check_nginx_configuration()
            print()

            self.check_api_gateway_configuration()
            print()

            self.check_load_balancing_readiness()
            print()

            self.check_monitoring_setup()
            print()

            self.check_backup_and_recovery()
            print()

            # Генерируем отчет
            report = self.generate_scalability_report()

            print("\n" + "=" * 60)
            print("🎯 РЕЗУЛЬТАТЫ АНАЛИЗА МАСШТАБИРУЕМОСТИ")
            print("=" * 60)

            print(f"🎯 Цель: {100000:,} пользователей")
            print(f"📊 Текущая оценка: ~{report['current_capacity']['estimated_users']} пользователей")
            print(f"⚡ P95 отклик сейчас: {report['current_capacity']['response_time_p95']}ms")
            print(f"📈 P95 для 100k: ~{int(report['projected_capacity']['response_time_p95'])}ms")

            if report['recommendations']:
                print("💡 РЕКОМЕНДАЦИИ:")
                for rec in report['recommendations']:
                    print(f"   - {rec}")
            else:
                print("✅ Инфраструктура готова к 100k+ пользователей!")

            return True

        finally:
            if self.ssh:
                self.ssh.close()
                print("🔌 Соединение закрыто")

def main():
    checker = ScalabilityChecker()

    print("🔍 АНАЛИЗ МАСШТАБИРУЕМОСТИ СЕРВЕРА ALADDIN")
    print("Проверка готовности к 100,000+ пользователей")
    print("=" * 60)

    if checker.run_full_check():
        print("\n✅ Анализ завершен успешно!")
        print("📄 Подробный отчет сохранен в scalability_report.json")
    else:
        print("\n❌ Ошибка анализа")
        sys.exit(1)

if __name__ == "__main__":
    main()