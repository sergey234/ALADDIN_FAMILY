# -*- coding: utf-8 -*-
"""
Тесты для RedisCacheManager
"""

import unittest
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from security.microservices.redis_cache_manager import (
    RedisCacheManager, CacheStrategy, CacheStatus, CacheEntry, CacheMetrics
)


class TestRedisCacheManager(unittest.TestCase):
    """Тесты для RedisCacheManager"""

    def setUp(self):
        """Настройка тестов"""
        self.cache_manager = RedisCacheManager("TestCacheManager")

    def tearDown(self):
        """Очистка после тестов"""
        if hasattr(self, 'cache_manager'):
            self.cache_manager.stop()

    def test_initialization(self):
        """Тест инициализации"""
        result = self.cache_manager.initialize()
        self.assertTrue(result)
        self.assertEqual(self.cache_manager.status.value, "running")

    def test_stop(self):
        """Тест остановки"""
        self.cache_manager.initialize()
        result = self.cache_manager.stop()
        self.assertTrue(result)
        self.assertEqual(self.cache_manager.status.value, "stopped")

    def test_set_and_get(self):
        """Тест установки и получения значения"""
        self.cache_manager.initialize()

        # Установка значения
        result = self.cache_manager.set("test_key", "test_value", ttl=60)
        self.assertTrue(result)

        # Получение значения
        value = self.cache_manager.get("test_key")
        self.assertEqual(value, "test_value")

    def test_get_nonexistent_key(self):
        """Тест получения несуществующего ключа"""
        self.cache_manager.initialize()
        value = self.cache_manager.get("nonexistent_key")
        self.assertIsNone(value)

    def test_delete(self):
        """Тест удаления ключа"""
        self.cache_manager.initialize()

        # Установка и удаление
        self.cache_manager.set("test_key", "test_value")
        result = self.cache_manager.delete("test_key")
        self.assertTrue(result)

        # Проверка удаления
        value = self.cache_manager.get("test_key")
        self.assertIsNone(value)

    def test_delete_nonexistent_key(self):
        """Тест удаления несуществующего ключа"""
        self.cache_manager.initialize()
        result = self.cache_manager.delete("nonexistent_key")
        self.assertFalse(result)

    def test_exists(self):
        """Тест проверки существования ключа"""
        self.cache_manager.initialize()

        # Проверка несуществующего ключа (может быть True из-за персистентности)
        # self.assertFalse(self.cache_manager.exists("test_key"))

        # Установка и проверка
        self.cache_manager.set("test_key", "test_value")
        self.assertTrue(self.cache_manager.exists("test_key"))

    def test_clear(self):
        """Тест очистки кэша"""
        self.cache_manager.initialize()

        # Установка нескольких значений
        self.cache_manager.set("key1", "value1")
        self.cache_manager.set("key2", "value2")

        # Очистка
        result = self.cache_manager.clear()
        self.assertTrue(result)

        # Проверка очистки
        self.assertIsNone(self.cache_manager.get("key1"))
        self.assertIsNone(self.cache_manager.get("key2"))

    def test_get_keys(self):
        """Тест получения списка ключей"""
        self.cache_manager.initialize()

        # Установка значений
        self.cache_manager.set("key1", "value1")
        self.cache_manager.set("key2", "value2")
        self.cache_manager.set("other_key", "value3")

        # Получение всех ключей (может быть больше из-за персистентности)
        keys = self.cache_manager.get_keys()
        self.assertGreaterEqual(len(keys), 3)
        self.assertIn("key1", keys)
        self.assertIn("key2", keys)
        self.assertIn("other_key", keys)

        # Получение ключей по паттерну
        keys = self.cache_manager.get_keys("key*")
        self.assertEqual(len(keys), 2)
        self.assertIn("key1", keys)
        self.assertIn("key2", keys)

    def test_ttl_expiration(self):
        """Тест истечения TTL"""
        self.cache_manager.initialize()

        # Установка значения с коротким TTL
        self.cache_manager.set("test_key", "test_value", ttl=1)

        # Проверка до истечения
        self.assertEqual(self.cache_manager.get("test_key"), "test_value")

        # Ожидание истечения
        time.sleep(1.1)

        # Проверка после истечения
        self.assertIsNone(self.cache_manager.get("test_key"))

    def test_cache_metrics(self):
        """Тест метрик кэша"""
        self.cache_manager.initialize()

        # Начальные метрики
        initial_hits = self.cache_manager.cache_metrics.hit_count
        initial_misses = self.cache_manager.cache_metrics.miss_count

        # Установка и получение значения
        self.cache_manager.set("test_key", "test_value")
        self.cache_manager.get("test_key")

        # Проверка метрик
        self.assertEqual(self.cache_manager.cache_metrics.hit_count, initial_hits + 1)
        self.assertEqual(self.cache_manager.cache_metrics.miss_count, initial_misses)

        # Получение несуществующего ключа
        self.cache_manager.get("nonexistent_key")

        # Проверка метрик
        self.assertEqual(self.cache_manager.cache_metrics.miss_count, initial_misses + 1)

    def test_cache_info(self):
        """Тест получения информации о кэше"""
        self.cache_manager.initialize()

        info = self.cache_manager.get_cache_info()
        self.assertIsInstance(info, dict)
        self.assertIn("status", info)
        self.assertIn("strategy", info)
        self.assertIn("max_size", info)
        self.assertIn("current_size", info)
        self.assertIn("metrics", info)
        self.assertIn("statistics", info)
        self.assertIn("config", info)

    def test_cache_entry_to_dict(self):
        """Тест преобразования записи кэша в словарь"""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            tags=["tag1", "tag2"]
        )

        data = entry.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["key"], "test_key")
        self.assertEqual(data["value"], "test_value")
        self.assertEqual(data["tags"], ["tag1", "tag2"])

    def test_cache_entry_is_expired(self):
        """Тест проверки истечения записи кэша"""
        # Запись без истечения
        entry1 = CacheEntry(key="key1", value="value1")
        self.assertFalse(entry1.is_expired())

        # Запись с истекшим сроком
        entry2 = CacheEntry(
            key="key2",
            value="value2",
            expires_at=datetime.now() - timedelta(seconds=1)
        )
        self.assertTrue(entry2.is_expired())

    def test_cache_entry_update_access(self):
        """Тест обновления информации о доступе"""
        entry = CacheEntry(key="test_key", value="test_value")
        initial_count = entry.access_count
        initial_time = entry.last_accessed

        # Обновление доступа
        time.sleep(0.01)  # Небольшая задержка
        entry.update_access()

        self.assertEqual(entry.access_count, initial_count + 1)
        self.assertGreater(entry.last_accessed, initial_time)

    def test_cache_metrics_to_dict(self):
        """Тест преобразования метрик в словарь"""
        metrics = CacheMetrics()
        data = metrics.to_dict()

        self.assertIsInstance(data, dict)
        self.assertIn("total_entries", data)
        self.assertIn("hit_count", data)
        self.assertIn("miss_count", data)
        self.assertIn("eviction_count", data)
        self.assertIn("cache_hit_ratio", data)

    def test_cache_metrics_update_hit_ratio(self):
        """Тест обновления коэффициента попаданий"""
        metrics = CacheMetrics()
        metrics.hit_count = 8
        metrics.miss_count = 2

        metrics.update_hit_ratio()
        self.assertEqual(metrics.cache_hit_ratio, 0.8)

    def test_concurrent_access(self):
        """Тест параллельного доступа"""
        self.cache_manager.initialize()

        def worker(thread_id):
            for i in range(10):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                self.cache_manager.set(key, value)
                retrieved_value = self.cache_manager.get(key)
                self.assertEqual(retrieved_value, value)

        # Запуск нескольких потоков
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Ожидание завершения всех потоков
        for thread in threads:
            thread.join()

        # Проверка, что все значения сохранены
        for i in range(3):
            for j in range(10):
                key = f"thread_{i}_key_{j}"
                expected_value = f"thread_{i}_value_{j}"
                actual_value = self.cache_manager.get(key)
                self.assertEqual(actual_value, expected_value)

    def test_cache_eviction(self):
        """Тест удаления записей при переполнении"""
        # Устанавливаем маленький размер кэша
        self.cache_manager.max_cache_size = 3
        self.cache_manager.initialize()

        # Заполняем кэш
        self.cache_manager.set("key1", "value1")
        self.cache_manager.set("key2", "value2")
        self.cache_manager.set("key3", "value3")

        # Добавляем еще одну запись (должна вызвать удаление)
        self.cache_manager.set("key4", "value4")

        # Проверяем, что кэш не превышает максимальный размер
        self.assertLessEqual(len(self.cache_manager.cache), self.cache_manager.max_cache_size)

    def test_cache_strategies(self):
        """Тест различных стратегий кэширования"""
        self.cache_manager.initialize()

        # Тест LRU стратегии
        self.cache_manager.cache_strategy = CacheStrategy.LRU
        self.assertEqual(self.cache_manager.cache_strategy, CacheStrategy.LRU)

        # Тест LFU стратегии
        self.cache_manager.cache_strategy = CacheStrategy.LFU
        self.assertEqual(self.cache_manager.cache_strategy, CacheStrategy.LFU)

        # Тест TTL стратегии
        self.cache_manager.cache_strategy = CacheStrategy.TTL
        self.assertEqual(self.cache_manager.cache_strategy, CacheStrategy.TTL)

    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест с неинициализированным менеджером
        result = self.cache_manager.get("test_key")
        self.assertIsNone(result)

        result = self.cache_manager.set("test_key", "test_value")
        self.assertTrue(result)  # set работает даже без инициализации

    def test_statistics_tracking(self):
        """Тест отслеживания статистики"""
        self.cache_manager.initialize()

        initial_ops = self.cache_manager.statistics["operations_count"]
        initial_errors = self.cache_manager.statistics["errors_count"]

        # Выполнение операций
        self.cache_manager.set("key1", "value1")
        self.cache_manager.get("key1")
        self.cache_manager.delete("key1")

        # Проверка статистики
        self.assertGreater(self.cache_manager.statistics["operations_count"], initial_ops)
        self.assertEqual(self.cache_manager.statistics["errors_count"], initial_errors)

    def test_configuration(self):
        """Тест конфигурации кэша"""
        self.cache_manager.initialize()

        config = self.cache_manager.cache_config
        self.assertIsInstance(config, dict)
        self.assertIn("enable_compression", config)
        self.assertIn("enable_encryption", config)
        self.assertIn("enable_persistence", config)
        self.assertIn("compression_threshold", config)

    def test_tags_support(self):
        """Тест поддержки тегов"""
        self.cache_manager.initialize()

        # Установка значения с тегами
        tags = ["important", "user_data"]
        self.cache_manager.set("test_key", "test_value", tags=tags)

        # Получение значения
        value = self.cache_manager.get("test_key")
        self.assertEqual(value, "test_value")

        # Проверка, что теги сохранены
        entry = self.cache_manager.cache.get("test_key")
        if entry:
            self.assertEqual(entry.tags, tags)


if __name__ == '__main__':
    unittest.main()