"""
Тестирование всех компонентов производительности и дополнительных функций
"""

import logging as std_logging
import asyncio
import time
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импорты
from performance import (
    ALADDINConnectionCache, 
    ALADDINConnectionPool, 
    ALADDINAsyncProcessor,
    ALADDINPerformanceManager,
    PerformanceMode,
    PerformanceConfig,
    TaskPriority
)
from features import (
    ALADDINSplitTunneling,
    ALADDINMultiHop,
    ALADDINAutoReconnect,
    ReconnectConfig,
    ReconnectStrategy
)

# Настройка логирования
std_logging.basicConfig(level=std_logging.INFO)
logger = std_logging.getLogger(__name__)

async def test_connection_cache():
    """Тестирование кэширования соединений"""
    print("\n=== ТЕСТИРОВАНИЕ КЭШИРОВАНИЯ СОЕДИНЕНИЙ ===")
    
    cache = ALADDINConnectionCache(max_connections=5, ttl=60)
    
    # Тестируем кэширование
    for i in range(3):
        conn_id = f"test_conn_{i+1}"
        server_id = f"test_server_{i+1}"
        connection_data = {
            "protocol": "wireguard",
            "port": 51820,
            "encryption": "aes-256-gcm"
        }
        
        success = cache.cache_connection(conn_id, server_id, connection_data)
        print(f"✅ Кэширование соединения {conn_id}: {'Успех' if success else 'Ошибка'}")
    
    # Тестируем получение из кэша
    cached_conn = cache.get_connection("test_server_1")
    if cached_conn:
        print(f"✅ Получено из кэша: {cached_conn.connection_id}")
    else:
        print("❌ Не удалось получить из кэша")
    
    # Получаем статистику
    stats = cache.get_cache_stats()
    print(f"📊 Статистика кэша: {stats['total_connections']} соединений, "
          f"коэффициент попаданий: {stats['cache_hit_ratio']:.2%}")

async def test_connection_pool():
    """Тестирование пула соединений"""
    print("\n=== ТЕСТИРОВАНИЕ ПУЛА СОЕДИНЕНИЙ ===")
    
    def create_test_connection(server_id: str):
        return {
            "protocol": "wireguard",
            "server_id": server_id,
            "port": 51820,
            "encryption": "aes-256-gcm"
        }
    
    pool = ALADDINConnectionPool(
        min_connections=2,
        max_connections=5,
        connection_timeout=10,
        idle_timeout=60
    )
    
    pool.set_connection_factory(create_test_connection)
    
    # Инициализируем пул
    if pool.initialize_pool():
        print("✅ Пул инициализирован")
    else:
        print("❌ Ошибка инициализации пула")
        return
    
    # Тестируем получение соединений
    connections = []
    for i in range(3):
        conn = pool.get_connection(f"test_server_{i+1}")
        if conn:
            connections.append(conn)
            print(f"✅ Получено соединение: {conn.connection_id}")
        else:
            print(f"❌ Не удалось получить соединение для test_server_{i+1}")
    
    # Возвращаем соединения
    for conn in connections:
        if pool.return_connection(conn.connection_id):
            print(f"✅ Соединение {conn.connection_id} возвращено")
        else:
            print(f"❌ Ошибка возврата соединения {conn.connection_id}")
    
    # Получаем статистику
    stats = pool.get_pool_stats()
    print(f"📊 Статистика пула: {stats['total_connections']} соединений, "
          f"активных: {stats['active_connections']}, "
          f"доступных: {stats['available_connections']}")
    
    # Закрываем пул
    pool.close_pool()
    print("✅ Пул закрыт")

async def test_async_processor():
    """Тестирование асинхронного процессора"""
    print("\n=== ТЕСТИРОВАНИЕ АСИНХРОННОГО ПРОЦЕССОРА ===")
    
    async def test_task(task_id: str, delay: float):
        print(f"🔄 Выполнение задачи {task_id}...")
        await asyncio.sleep(delay)
        return f"Результат задачи {task_id}"
    
    processor = ALADDINAsyncProcessor(max_workers=3, max_tasks=100)
    
    # Запускаем процессор
    await processor.start()
    print("✅ Процессор запущен")
    
    try:
        # Отправляем задачи
        task_ids = []
        for i in range(5):
            task_id = await processor.submit_task(
                test_task, f"task_{i+1}", 1.0,
                priority=TaskPriority.LOW
            )
            task_ids.append(task_id)
            print(f"✅ Задача {task_id} отправлена")
        
        # Получаем результаты
        for task_id in task_ids:
            try:
                result = await processor.get_task_result(task_id, timeout=5.0)
                print(f"✅ Результат {task_id}: {result}")
            except asyncio.TimeoutError:
                print(f"⏰ Таймаут для задачи {task_id}")
            except Exception as e:
                print(f"❌ Ошибка для задачи {task_id}: {e}")
        
        # Получаем статистику
        stats = await processor.get_stats()
        print(f"📊 Статистика процессора: {stats['active_workers']} воркеров, "
              f"активных задач: {stats['active_tasks']}, "
              f"завершенных: {stats['completed_tasks']}")
        
    finally:
        # Останавливаем процессор
        await processor.stop()
        print("✅ Процессор остановлен")

async def test_split_tunneling():
    """Тестирование Split Tunneling"""
    print("\n=== ТЕСТИРОВАНИЕ SPLIT TUNNELING ===")
    
    split_tunnel = ALADDINSplitTunneling()
    split_tunnel.enable_split_tunneling()
    print("✅ Split Tunneling включен")
    
    # Тестируем различные домены
    test_domains = [
        "sberbank.ru",      # Банковский - должен обходить VPN
        "netflix.com",      # Стриминг - должен идти через VPN
        "steam.com",        # Игры - должен обходить VPN
        "facebook.com",     # Социальные сети - должен идти через VPN
        "google.com"        # По умолчанию
    ]
    
    print("🧪 Тестирование маршрутизации:")
    for domain in test_domains:
        routing, rule_id = split_tunnel.get_routing_decision(domain=domain)
        rule_name = split_tunnel.rules[rule_id].name if rule_id else "По умолчанию"
        print(f"  {domain}: {routing.value} ({rule_name})")
    
    # Тестируем обработку трафика
    print("\n📊 Тестирование обработки трафика:")
    for domain in test_domains[:3]:
        use_vpn = split_tunnel.process_traffic(
            domain=domain,
            port=443,
            protocol="https",
            packet_size=1024
        )
        print(f"  {domain}: {'VPN' if use_vpn else 'Bypass'}")
    
    # Получаем статистику
    stats = split_tunnel.get_traffic_stats()
    print(f"\n📈 Статистика трафика:")
    print(f"  Всего пакетов: {stats['total_packets']}")
    print(f"  Через VPN: {stats['vpn_packets']} ({stats['vpn_percentage']:.1f}%)")
    print(f"  Обход VPN: {stats['bypass_packets']} ({stats['bypass_percentage']:.1f}%)")

async def test_multi_hop():
    """Тестирование Multi-hop подключений"""
    print("\n=== ТЕСТИРОВАНИЕ MULTI-HOP ПОДКЛЮЧЕНИЙ ===")
    
    multi_hop = ALADDINMultiHop()
    
    # Получаем доступные цепочки
    chains = multi_hop.get_available_chains()
    print(f"📋 Доступные цепочки ({len(chains)}):")
    for chain in chains[:3]:  # Показываем первые 3
        print(f"  {chain['name']}: {chain['hop_count']} хопов, "
              f"задержка {chain['total_latency']:.1f}мс, "
              f"безопасность {chain['security_level']}/5")
    
    # Подключаемся к быстрой цепочке
    print(f"\n🔗 Подключение к быстрой цепочке...")
    if await multi_hop.connect_chain("fast_chain"):
        print("✅ Подключение успешно")
        
        # Получаем статистику
        stats = multi_hop.get_chain_stats("fast_chain")
        if stats:
            print(f"📊 Статистика цепочки:")
            print(f"  Подключено хопов: {stats['connected_hops']}/{stats['total_hops']}")
            print(f"  Общая задержка: {stats['total_latency']:.1f}мс")
            print(f"  Уровень безопасности: {stats['security_level']}/5")
        
        # Отключаемся
        if await multi_hop.disconnect_chain("fast_chain"):
            print("✅ Отключение успешно")
    else:
        print("❌ Ошибка подключения")

async def test_auto_reconnect():
    """Тестирование автоматического переподключения"""
    print("\n=== ТЕСТИРОВАНИЕ АВТОМАТИЧЕСКОГО ПЕРЕПОДКЛЮЧЕНИЯ ===")
    
    config = ReconnectConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=10.0,
        strategy=ReconnectStrategy.EXPONENTIAL,
        quality_threshold=0.7,
        health_check_interval=5.0,
        jitter=True
    )
    
    auto_reconnect = ALADDINAutoReconnect(config)
    
    # Устанавливаем callbacks
    async def on_reconnect_start():
        print("🔄 Начало переподключения...")
    
    async def on_reconnect_success():
        print("✅ Переподключение успешно!")
    
    async def on_reconnect_failure():
        print("❌ Переподключение не удалось")
    
    async def on_quality_change(quality):
        print(f"📊 Качество соединения: {quality.value}")
    
    auto_reconnect.set_callbacks(
        on_reconnect_start=on_reconnect_start,
        on_reconnect_success=on_reconnect_success,
        on_reconnect_failure=on_reconnect_failure,
        on_quality_change=on_quality_change
    )
    
    # Запускаем
    await auto_reconnect.start()
    print("✅ Автоматическое переподключение запущено")
    
    # Устанавливаем ID соединения
    auto_reconnect.set_connection_id("test_connection_123")
    print("✅ ID соединения установлен")
    
    try:
        # Ждем некоторое время для демонстрации
        print("⏳ Мониторинг соединения в течение 15 секунд...")
        await asyncio.sleep(15)
        
        # Получаем статистику
        stats = auto_reconnect.get_stats()
        print(f"📊 Статистика переподключений:")
        print(f"  Включено: {stats['is_enabled']}")
        print(f"  Качество: {stats['connection_quality']}")
        print(f"  Всего попыток: {stats['stats']['total_attempts']}")
        print(f"  Успешных: {stats['stats']['successful_reconnects']}")
        print(f"  Процент успеха: {stats['success_rate']:.1f}%")
        
    finally:
        # Останавливаем
        await auto_reconnect.stop()
        print("✅ Автоматическое переподключение остановлено")

async def test_performance_manager():
    """Тестирование менеджера производительности"""
    print("\n=== ТЕСТИРОВАНИЕ МЕНЕДЖЕРА ПРОИЗВОДИТЕЛЬНОСТИ ===")
    
    config = PerformanceConfig(
        mode=PerformanceMode.HIGH_PERFORMANCE,
        cache_size=50,
        pool_min_connections=5,
        pool_max_connections=20,
        async_workers=8,
        connection_ttl=300,
        task_timeout=60
    )
    
    manager = ALADDINPerformanceManager(config)
    
    # Инициализируем
    if await manager.initialize():
        print("✅ Менеджер инициализирован")
    else:
        print("❌ Ошибка инициализации")
        return
    
    try:
        # Тестируем получение соединений
        connections = []
        for i in range(3):
            server_id = f"test_server_{i+1}"
            conn = await manager.get_connection(server_id)
            if conn:
                connections.append(conn)
                print(f"✅ Получено соединение для {server_id}")
            else:
                print(f"❌ Ошибка получения соединения для {server_id}")
        
        # Возвращаем соединения
        for conn in connections:
            if manager.return_connection(conn.connection_id):
                print(f"✅ Соединение {conn.connection_id} возвращено")
            else:
                print(f"❌ Ошибка возврата соединения {conn.connection_id}")
        
        # Тестируем асинхронные задачи
        async def test_async_task(task_id: str):
            await asyncio.sleep(0.5)
            return f"Результат {task_id}"
        
        task_id = await manager.submit_async_task(test_async_task, "test_task_1")
        print(f"✅ Асинхронная задача {task_id} отправлена")
        
        try:
            result = await manager.get_async_result(task_id, timeout=5.0)
            print(f"✅ Результат задачи: {result}")
        except Exception as e:
            print(f"❌ Ошибка получения результата: {e}")
        
        # Получаем статистику
        stats = manager.get_performance_stats()
        print(f"\n📊 Статистика производительности:")
        print(f"  Режим: {stats['manager_status']['mode']}")
        print(f"  Кэш: {stats['cache_stats']['total_connections']} соединений")
        print(f"  Пул: {stats['pool_stats']['total_connections']} соединений")
        print(f"  Эффективность: {stats['efficiency']['overall_efficiency']:.2%}")
        
        # Оптимизация
        manager.optimize_performance()
        print("✅ Оптимизация выполнена")
        
    finally:
        # Завершаем работу
        await manager.shutdown()
        print("✅ Менеджер завершен")

async def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ ВСЕХ КОМПОНЕНТОВ ALADDIN VPN")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Тестируем все компоненты
        await test_connection_cache()
        await test_connection_pool()
        await test_async_processor()
        await test_split_tunneling()
        await test_multi_hop()
        await test_auto_reconnect()
        await test_performance_manager()
        
        total_time = time.time() - start_time
        print(f"\n🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
        print(f"⏱️ Общее время выполнения: {total_time:.2f} секунд")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА В ТЕСТАХ: {e}")
        logger.error(f"Ошибка в тестах: {e}")

if __name__ == "__main__":
    asyncio.run(main())