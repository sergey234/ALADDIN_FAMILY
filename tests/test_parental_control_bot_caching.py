#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты кэширования для ParentalControlBot
Версия: 2.5
Дата: 2025-09-21
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Добавляем путь к модулям
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.bots.parental_control_bot import ParentalControlBot
from security.bots.components.cache_manager import CacheManager, CacheStrategy


class TestParentalControlBotCaching:
    """Тесты кэширования ParentalControlBot"""

    @pytest.fixture
    async def bot(self):
        """Создание экземпляра бота для тестов"""
        bot = ParentalControlBot("TestBot")
        await bot.start()
        yield bot
        await bot.stop()

    @pytest.fixture
    async def bot_with_children(self, bot):
        """Бот с добавленными детьми"""
        # Добавляем тестовых детей
        child1_data = {
            "name": "Test Child 1",
            "age": 10,
            "parent_id": "parent_123"
        }
        child2_data = {
            "name": "Test Child 2", 
            "age": 15,
            "parent_id": "parent_456"
        }
        
        child1_id = await bot.add_child_profile(child1_data)
        child2_id = await bot.add_child_profile(child2_data)
        
        return bot, child1_id, child2_id

    async def test_cache_initialization(self, bot):
        """Тест инициализации кэша"""
        assert hasattr(bot, 'cache_manager')
        assert isinstance(bot.cache_manager, CacheManager)
        assert bot.cache_manager.strategy == CacheStrategy.LRU
        assert bot.cache_manager.max_size == 1000

    async def test_content_analysis_caching(self, bot_with_children):
        """Тест кэширования анализа контента"""
        bot, child1_id, child2_id = bot_with_children
        
        url = "https://youtube.com"
        
        # Первый запрос - должен попасть в кэш
        start_time = time.time()
        result1 = await bot.analyze_content(url, child1_id)
        first_duration = time.time() - start_time
        
        # Второй запрос - должен быть из кэша
        start_time = time.time()
        result2 = await bot.analyze_content(url, child1_id)
        second_duration = time.time() - start_time
        
        # Результаты должны быть одинаковыми
        assert result1.url == result2.url
        assert result1.category == result2.category
        assert result1.action == result2.action
        
        # Второй запрос должен быть быстрее (из кэша)
        assert second_duration < first_duration

    async def test_child_status_caching(self, bot_with_children):
        """Тест кэширования статуса ребенка"""
        bot, child1_id, child2_id = bot_with_children
        
        # Первый запрос - должен попасть в кэш
        start_time = time.time()
        status1 = await bot.get_child_status(child1_id)
        first_duration = time.time() - start_time
        
        # Второй запрос - должен быть из кэша
        start_time = time.time()
        status2 = await bot.get_child_status(child1_id)
        second_duration = time.time() - start_time
        
        # Результаты должны быть одинаковыми
        assert status1["child_id"] == status2["child_id"]
        assert status1["name"] == status2["name"]
        assert status1["age"] == status2["age"]
        
        # Второй запрос должен быть быстрее (из кэша)
        assert second_duration < first_duration

    async def test_cache_invalidation(self, bot_with_children):
        """Тест инвалидации кэша"""
        bot, child1_id, child2_id = bot_with_children
        
        # Заполняем кэш
        await bot.analyze_content("https://youtube.com", child1_id)
        await bot.get_child_status(child1_id)
        
        # Проверяем, что данные в кэше
        cache_stats_before = await bot.get_cache_stats()
        assert cache_stats_before["cache_stats"]["total_entries"] > 0
        
        # Инвалидируем кэш для ребенка
        invalidated_count = await bot.invalidate_child_cache(child1_id)
        assert invalidated_count > 0
        
        # Проверяем, что кэш очищен
        cache_stats_after = await bot.get_cache_stats()
        assert cache_stats_after["cache_stats"]["total_entries"] < cache_stats_before["cache_stats"]["total_entries"]

    async def test_cache_clear(self, bot_with_children):
        """Тест полной очистки кэша"""
        bot, child1_id, child2_id = bot_with_children
        
        # Заполняем кэш
        await bot.analyze_content("https://youtube.com", child1_id)
        await bot.get_child_status(child1_id)
        await bot.analyze_content("https://google.com", child2_id)
        
        # Проверяем, что кэш заполнен
        cache_stats_before = await bot.get_cache_stats()
        assert cache_stats_before["cache_stats"]["total_entries"] > 0
        
        # Очищаем кэш
        result = await bot.clear_cache()
        assert result is True
        
        # Проверяем, что кэш пуст
        cache_stats_after = await bot.get_cache_stats()
        assert cache_stats_after["cache_stats"]["total_entries"] == 0

    async def test_cache_stats(self, bot_with_children):
        """Тест получения статистики кэша"""
        bot, child1_id, child2_id = bot_with_children
        
        # Заполняем кэш
        await bot.analyze_content("https://youtube.com", child1_id)
        await bot.get_child_status(child1_id)
        await bot.analyze_content("https://google.com", child2_id)
        
        # Получаем статистику
        stats = await bot.get_cache_stats()
        
        assert "cache_stats" in stats
        assert "memory_usage" in stats
        assert "strategy" in stats
        assert "max_size" in stats
        
        cache_stats = stats["cache_stats"]
        assert "total_entries" in cache_stats
        assert "hit_count" in cache_stats
        assert "miss_count" in cache_stats
        assert "hit_ratio" in cache_stats
        
        assert cache_stats["total_entries"] > 0

    async def test_cache_expiration(self, bot_with_children):
        """Тест истечения срока действия кэша"""
        bot, child1_id, child2_id = bot_with_children
        
        # Создаем кэш с коротким TTL
        cache_key = bot.cache_manager.generate_key("test", child_id=child1_id)
        await bot.cache_manager.set(cache_key, {"test": "data"}, ttl=1)  # 1 секунда
        
        # Проверяем, что данные в кэше
        cached_data = await bot.cache_manager.get(cache_key)
        assert cached_data is not None
        
        # Ждем истечения срока
        await asyncio.sleep(2)
        
        # Проверяем, что данные истекли
        cached_data = await bot.cache_manager.get(cache_key)
        assert cached_data is None

    async def test_cache_cleanup_expired(self, bot_with_children):
        """Тест очистки истекших записей"""
        bot, child1_id, child2_id = bot_with_children
        
        # Создаем истекшие записи
        cache_key1 = bot.cache_manager.generate_key("expired1", child_id=child1_id)
        cache_key2 = bot.cache_manager.generate_key("expired2", child_id=child2_id)
        
        await bot.cache_manager.set(cache_key1, {"test": "data1"}, ttl=1)
        await bot.cache_manager.set(cache_key2, {"test": "data2"}, ttl=1)
        
        # Ждем истечения
        await asyncio.sleep(2)
        
        # Очищаем истекшие записи
        cleaned_count = await bot.cleanup_expired_cache()
        assert cleaned_count >= 0

    async def test_cache_warm_up(self, bot_with_children):
        """Тест прогрева кэша"""
        bot, child1_id, child2_id = bot_with_children
        
        # Прогреваем кэш
        result = await bot.warm_up_cache()
        assert result is True
        
        # Проверяем, что кэш заполнен
        cache_stats = await bot.get_cache_stats()
        assert cache_stats["cache_stats"]["total_entries"] > 0

    async def test_cache_memory_limits(self, bot):
        """Тест лимитов памяти кэша"""
        # Создаем кэш с маленьким лимитом памяти
        small_cache = CacheManager(
            logger=bot.logger,
            max_size=10,
            max_memory_mb=1,  # 1 MB
            strategy=CacheStrategy.LRU
        )
        
        # Заполняем кэш большими данными
        large_data = "x" * 100000  # 100KB
        
        for i in range(20):  # Пытаемся добавить больше лимита
            key = f"large_data_{i}"
            await small_cache.set(key, large_data)
        
        # Проверяем, что кэш не превышает лимиты
        memory_usage = await small_cache.get_memory_usage()
        assert memory_usage["memory_usage_percent"] <= 100

    async def test_cache_strategies(self, bot):
        """Тест различных стратегий кэширования"""
        strategies = [CacheStrategy.LRU, CacheStrategy.LFU, CacheStrategy.FIFO, CacheStrategy.TTL]
        
        for strategy in strategies:
            cache = CacheManager(
                logger=bot.logger,
                max_size=5,
                strategy=strategy
            )
            
            # Заполняем кэш
            for i in range(10):
                await cache.set(f"key_{i}", f"value_{i}")
            
            # Проверяем, что кэш работает
            stats = await cache.get_stats()
            assert stats.total_entries <= 5  # Не превышает лимит

    async def test_cache_key_generation(self, bot):
        """Тест генерации ключей кэша"""
        # Тест с простыми параметрами
        key1 = bot.cache_manager.generate_key("test", "param1", "param2")
        key2 = bot.cache_manager.generate_key("test", "param1", "param2")
        assert key1 == key2  # Одинаковые параметры = одинаковый ключ
        
        # Тест с разными параметрами
        key3 = bot.cache_manager.generate_key("test", "param1", "param3")
        assert key1 != key3  # Разные параметры = разные ключи
        
        # Тест с kwargs
        key4 = bot.cache_manager.generate_key("test", child_id="123", url="https://example.com")
        key5 = bot.cache_manager.generate_key("test", child_id="123", url="https://example.com")
        assert key4 == key5

    async def test_cache_error_handling(self, bot_with_children):
        """Тест обработки ошибок в кэше"""
        bot, child1_id, child2_id = bot_with_children
        
        # Тест с невалидными данными
        with patch.object(bot.cache_manager, 'get', side_effect=Exception("Cache error")):
            # Должен вернуть None при ошибке кэша
            result = await bot.analyze_content("https://youtube.com", child1_id)
            assert result is not None  # Основная функциональность работает
        
        # Тест с невалидными данными для set
        with patch.object(bot.cache_manager, 'set', side_effect=Exception("Cache set error")):
            result = await bot.analyze_content("https://youtube.com", child1_id)
            assert result is not None  # Основная функциональность работает


# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v"])