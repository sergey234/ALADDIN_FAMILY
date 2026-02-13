#!/usr/bin/env python3
"""
🔧 АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ METRICS ROUTER НА СЕРВЕРЕ
Дата: 2026-02-13
Цель: Проверить и исправить подключение metrics_router для продакшн
"""

import os
import sys
import re
from datetime import datetime

# Цвета для вывода
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def print_step(step, message):
    print(f"\n{BLUE}{step}{NC} {message}")

def print_success(message):
    print(f"{GREEN}✅{NC} {message}")

def print_error(message):
    print(f"{RED}❌{NC} {message}")

def print_warning(message):
    print(f"{YELLOW}⚠️{NC} {message}")

def main():
    print("=" * 60)
    print("🔧 АВТОМАТИЧЕСКОЕ ИСПРАВЛЕНИЕ METRICS ROUTER")
    print("=" * 60)
    
    backend_path = "/opt/aladdin-backend"
    main_py = os.path.join(backend_path, "main.py")
    metrics_router_py = os.path.join(backend_path, "security/api/routers/metrics_router.py")
    backup_file = f"{main_py}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Проверка 1: Файл metrics_router.py
    print_step("1️⃣", "Проверка файла metrics_router.py...")
    if not os.path.exists(metrics_router_py):
        print_error(f"Файл {metrics_router_py} НЕ найден!")
        return 1
    print_success(f"Файл {metrics_router_py} существует")
    
    # Проверка 2: Префикс роутера
    print_step("2️⃣", "Проверка префикса роутера...")
    with open(metrics_router_py, 'r', encoding='utf-8') as f:
        content = f.read()
        prefix_match = re.search(r'prefix=["\']([^"\']+)["\']', content)
        if prefix_match:
            prefix = prefix_match.group(1)
            print(f"   Найден префикс: {prefix}")
            if prefix == "/metrics":
                print_success("Префикс правильный (/metrics)")
            elif prefix == "/api/metrics":
                print_warning("Префикс неправильный (/api/metrics) - нужно исправить на /metrics")
                # Исправляем
                content = content.replace('prefix="/api/metrics"', 'prefix="/metrics"')
                content = content.replace("prefix='/api/metrics'", "prefix='/metrics'")
                with open(metrics_router_py, 'w', encoding='utf-8') as fw:
                    fw.write(content)
                print_success("Префикс исправлен на /metrics")
            else:
                print_warning(f"Неожиданный префикс: {prefix}")
    
    # Проверка 3: Подключение в main.py
    print_step("3️⃣", "Проверка подключения в main.py...")
    if not os.path.exists(main_py):
        print_error(f"Файл {main_py} НЕ найден!")
        return 1
    
    # Создаем резервную копию
    import shutil
    shutil.copy2(main_py, backup_file)
    print_success(f"Резервная копия создана: {backup_file}")
    
    with open(main_py, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # Проверяем импорт
    has_import = "from security.api.routers.metrics_router import" in main_content
    has_available_check = "metrics_router_available" in main_content
    
    if not has_import:
        print_warning("Импорт metrics_router не найден - добавляем...")
        # Находим место после других импортов роутеров
        import_pattern = r'(from security\.api\.routers\.\w+_router import router as \w+_router)'
        matches = list(re.finditer(import_pattern, main_content))
        if matches:
            last_match = matches[-1]
            insert_pos = last_match.end()
            import_code = """
try:
    from security.api.routers.metrics_router import router as metrics_router
    metrics_router_available = True
except ImportError as e:
    print(f"⚠️ metrics_router недоступен: {e}")
    metrics_router_available = False
    metrics_router = None
"""
            main_content = main_content[:insert_pos] + import_code + main_content[insert_pos:]
            print_success("Импорт добавлен")
        else:
            print_error("Не найдено место для добавления импорта")
            return 1
    
    # Проверяем подключение роутера
    if "app.include_router(metrics_router)" not in main_content:
        print_warning("Роутер не подключен - добавляем...")
        # Находим место после других роутеров
        router_pattern = r'(app\.include_router\(\w+_router\))'
        matches = list(re.finditer(router_pattern, main_content))
        if matches:
            last_match = matches[-1]
            insert_pos = last_match.end()
            router_code = """

if metrics_router_available:
    try:
        app.include_router(metrics_router)
        print("✅ Роутер Metrics подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Metrics: {e}")
"""
            main_content = main_content[:insert_pos] + router_code + main_content[insert_pos:]
            print_success("Роутер добавлен")
        else:
            print_error("Не найдено место для добавления роутера")
            return 1
    else:
        # Проверяем, независим ли роутер
        print_step("4️⃣", "Проверка независимости подключения...")
        # Ищем блоки с metrics_router
        if re.search(r'if system_router_available:.*?if metrics_router_available:', main_content, re.DOTALL):
            print_warning("Роутер подключен условно (зависит от system_router) - исправляем...")
            # Исправляем: делаем независимым
            pattern = r'(if system_router_available:.*?app\.include_router\(system_router\).*?\n)(\s+if metrics_router_available:.*?app\.include_router\(metrics_router\).*?\n)'
            def fix_independence(match):
                system_block = match.group(1)
                metrics_block = match.group(2)
                # Убираем отступы из metrics_block
                metrics_independent = re.sub(r'^\s+', '', metrics_block, flags=re.MULTILINE)
                return system_block + "\n# Независимо от system_router\nif metrics_router_available:\n    try:\n        app.include_router(metrics_router)\n        print(\"✅ Роутер Metrics подключен\")\n    except Exception as e:\n        print(f\"❌ Ошибка подключения Metrics: {e}\")\n"
            main_content = re.sub(pattern, fix_independence, main_content, flags=re.DOTALL)
            print_success("Роутер сделан независимым")
        else:
            print_success("Роутер уже подключен независимо")
    
    # Сохраняем изменения
    with open(main_py, 'w', encoding='utf-8') as f:
        f.write(main_content)
    print_success("Изменения сохранены в main.py")
    
    # Проверка синтаксиса
    print_step("5️⃣", "Проверка синтаксиса Python...")
    import py_compile
    try:
        py_compile.compile(main_py, doraise=True)
        print_success("Синтаксис правильный")
    except py_compile.PyCompileError as e:
        print_error(f"Ошибка синтаксиса: {e}")
        print_warning("Восстанавливаем резервную копию...")
        shutil.copy2(backup_file, main_py)
        return 1
    
    # Инструкции по перезапуску
    print("\n" + "=" * 60)
    print_success("ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!")
    print("=" * 60)
    print("\n📋 СЛЕДУЮЩИЕ ШАГИ:")
    print("\n1. Перезапустить сервис:")
    print("   sudo systemctl restart aladdin-production-api")
    print("\n2. Проверить статус:")
    print("   systemctl status aladdin-production-api")
    print("\n3. Проверить логи:")
    print("   journalctl -u aladdin-production-api -n 20 --no-pager | grep -i metrics")
    print("\n4. Протестировать endpoint:")
    print("   curl -X POST https://aladdin-ai.ru/api/metrics/upload \\")
    print("     -H \"Content-Type: application/json\" \\")
    print("     -d '{\"deviceId\":\"test\",\"appVersion\":\"1.0.0\",\"platform\":\"ios\",\"metrics\":[]}'")
    print("\n" + "=" * 60)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print_error(f"Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
