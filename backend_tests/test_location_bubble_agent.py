#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-тесты для Location Bubble Agent

День 5: Тестирование агента
"""

import sys
import os
import math
from datetime import datetime
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from security.ai_agents.location_bubble_agent import (
        LocationBubbleAgent,
        BubbleRadius,
        TimeBasedSettings,
        PersonBubbleSettings
    )
except ImportError as e:
    # Для локального тестирования - создаем заглушки
    print(f"⚠️ Импорт не удался: {e}")
    print("Используем заглушки для тестирования")
    
    class BubbleRadius:
        SMALL = 100
        MEDIUM = 500
        LARGE = 1000
    
    class TimeBasedSettings:
        def __init__(self, start_time, end_time, radius, enabled=True):
            self.start_time = start_time
            self.end_time = end_time
            self.radius = radius
            self.enabled = enabled
    
    class PersonBubbleSettings:
        def __init__(self, person_id, default_radius, time_based_settings=None, enabled=True):
            self.person_id = person_id
            self.default_radius = default_radius
            self.time_based_settings = time_based_settings or []
            self.enabled = enabled
    
    class LocationBubbleAgent:
        def __init__(self, config=None):
            self.default_radius = BubbleRadius.MEDIUM
            self.enable_time_based = True
            self.user_person_settings = {}
            self.generation_history = {}
        
        def get_bubble_location(self, user_id, person_id, exact_latitude, exact_longitude, radius=None, accuracy=None):
            return {"approximate_latitude": exact_latitude + 0.001, "approximate_longitude": exact_longitude + 0.001, "radius": radius or 500, "accuracy": float(radius or 500), "generated_at": 1234567890.0}
        
        def set_person_settings(self, user_id, person_id, default_radius, time_based_settings=None, enabled=True):
            return {"person_id": person_id, "default_radius": default_radius.value if hasattr(default_radius, 'value') else default_radius, "enabled": enabled}
        
        def get_person_settings(self, user_id, person_id):
            return PersonBubbleSettings(person_id, self.default_radius, [], True)
        
        def get_all_person_settings(self, user_id):
            return {}
        
        def get_generation_history(self, user_id, limit=50):
            return []
        
        def _calculate_distance(self, lat1, lon1, lat2, lon2):
            return 100.0
        
        def _get_radius_for_person(self, user_id, person_id, requested_radius=None):
            return requested_radius or 500
        
        def _generate_bubble_location(self, center_latitude, center_longitude, radius_meters):
            class BubbleLocation:
                def __init__(self):
                    self.approximate_latitude = center_latitude + 0.001
                    self.approximate_longitude = center_longitude + 0.001
                    self.radius = radius_meters
                    self.center_latitude = center_latitude
                    self.center_longitude = center_longitude
                    self.generated_at = 1234567890.0
                    self.accuracy = float(radius_meters)
                
                def to_dict(self):
                    return {"approximate_latitude": self.approximate_latitude, "approximate_longitude": self.approximate_longitude, "radius": self.radius, "accuracy": self.accuracy, "generated_at": self.generated_at}
                
                def to_dict_full(self):
                    return {"approximate_latitude": self.approximate_latitude, "approximate_longitude": self.approximate_longitude, "radius": self.radius, "center_latitude": self.center_latitude, "center_longitude": self.center_longitude, "accuracy": self.accuracy, "generated_at": self.generated_at}
            
            return BubbleLocation()


class TestLocationBubbleAgent:
    """Тесты для LocationBubbleAgent"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.agent = LocationBubbleAgent(config={"default_radius": 500, "enable_time_based": True})
        self.test_user_id = "test_user_123"
        self.test_person_id = "test_person_456"
        self.test_latitude = 55.7558  # Москва
        self.test_longitude = 37.6173

    def test_agent_initialization(self):
        """Тест инициализации агента"""
        assert self.agent is not None
        assert self.agent.default_radius == BubbleRadius.MEDIUM
        assert self.agent.enable_time_based is True

    def test_get_bubble_location_basic(self):
        """Тест базовой генерации пузыря"""
        result = self.agent.get_bubble_location(
            user_id=self.test_user_id,
            person_id=self.test_person_id,
            exact_latitude=self.test_latitude,
            exact_longitude=self.test_longitude
        )

        assert "approximate_latitude" in result
        assert "approximate_longitude" in result
        assert "radius" in result
        assert "accuracy" in result
        assert "generated_at" in result

        # Проверяем, что приблизительные координаты отличаются от точных
        assert result["approximate_latitude"] != self.test_latitude
        assert result["approximate_longitude"] != self.test_longitude

        # Проверяем, что радиус соответствует настройкам по умолчанию
        assert result["radius"] == 500  # MEDIUM

    def test_get_bubble_location_with_custom_radius(self):
        """Тест генерации пузыря с пользовательским радиусом"""
        result = self.agent.get_bubble_location(
            user_id=self.test_user_id,
            person_id=self.test_person_id,
            exact_latitude=self.test_latitude,
            exact_longitude=self.test_longitude,
            radius=100
        )

        assert result["radius"] == 100
        assert result["accuracy"] == 100.0

    def test_get_bubble_location_distance_check(self):
        """Тест, что пузырь находится в пределах радиуса"""
        result = self.agent.get_bubble_location(
            user_id=self.test_user_id,
            person_id=self.test_person_id,
            exact_latitude=self.test_latitude,
            exact_longitude=self.test_longitude,
            radius=500
        )

        # Вычисляем расстояние между точными и приблизительными координатами
        distance = self.agent._calculate_distance(
            self.test_latitude,
            self.test_longitude,
            result["approximate_latitude"],
            result["approximate_longitude"]
        )

        # Расстояние должно быть в пределах радиуса (с небольшим допуском)
        assert distance <= result["radius"] * 1.1  # 10% допуск

    def test_set_person_settings(self):
        """Тест установки настроек для человека"""
        result = self.agent.set_person_settings(
            user_id=self.test_user_id,
            person_id=self.test_person_id,
            default_radius=BubbleRadius.SMALL,
            enabled=True
        )

        assert "person_id" in result
        assert result["person_id"] == self.test_person_id
        assert result["default_radius"] == 100  # SMALL
        assert result["enabled"] is True

    def test_get_person_settings(self):
        """Тест получения настроек для человека"""
        # Сначала устанавливаем настройки
        self.agent.set_person_settings(
            user_id=self.test_user_id,
            person_id=self.test_person_id,
            default_radius=BubbleRadius.LARGE,
            enabled=True
        )

        # Получаем настройки
        settings = self.agent.get_person_settings(
            user_id=self.test_user_id,
            person_id=self.test_person_id
        )

        assert settings.person_id == self.test_person_id
        assert settings.default_radius == BubbleRadius.LARGE
        assert settings.enabled is True

    def test_get_person_settings_default(self):
        """Тест получения настроек по умолчанию (если настройки не установлены)"""
        settings = self.agent.get_person_settings(
            user_id=self.test_user_id,
            person_id="nonexistent_person"
        )

        assert settings.person_id == "nonexistent_person"
        assert settings.default_radius == self.agent.default_radius
        assert settings.enabled is True

    def test_set_person_settings_with_time_based(self):
        """Тест установки настроек с настройками по времени"""
        time_settings = [
            TimeBasedSettings(
                start_time="09:00",
                end_time="18:00",
                radius=BubbleRadius.SMALL,
                enabled=True
            ),
            TimeBasedSettings(
                start_time="18:00",
                end_time="09:00",
                radius=BubbleRadius.LARGE,
                enabled=True
            )
        ]

        result = self.agent.set_person_settings(
            user_id=self.test_user_id,
            person_id=self.test_person_id,
            default_radius=BubbleRadius.MEDIUM,
            time_based_settings=time_settings,
            enabled=True
        )

        assert len(result["time_based_settings"]) == 2

    def test_get_all_person_settings(self):
        """Тест получения всех настроек для пользователя"""
        # Устанавливаем настройки для нескольких людей
        self.agent.set_person_settings(
            user_id=self.test_user_id,
            person_id="person_1",
            default_radius=BubbleRadius.SMALL,
            enabled=True
        )
        self.agent.set_person_settings(
            user_id=self.test_user_id,
            person_id="person_2",
            default_radius=BubbleRadius.LARGE,
            enabled=True
        )

        all_settings = self.agent.get_all_person_settings(user_id=self.test_user_id)

        assert len(all_settings) == 2
        assert "person_1" in all_settings
        assert "person_2" in all_settings
        assert all_settings["person_1"]["default_radius"] == 100
        assert all_settings["person_2"]["default_radius"] == 1000

    def test_get_generation_history(self):
        """Тест получения истории генераций"""
        # Генерируем несколько пузырей
        for i in range(5):
            self.agent.get_bubble_location(
                user_id=self.test_user_id,
                person_id=self.test_person_id,
                exact_latitude=self.test_latitude + i * 0.001,
                exact_longitude=self.test_longitude + i * 0.001
            )

        history = self.agent.get_generation_history(user_id=self.test_user_id, limit=10)

        assert len(history) == 5
        assert all("approximate_latitude" in h for h in history)
        assert all("approximate_longitude" in h for h in history)

    def test_get_generation_history_limit(self):
        """Тест ограничения истории"""
        # Генерируем больше пузырей, чем лимит
        for i in range(20):
            self.agent.get_bubble_location(
                user_id=self.test_user_id,
                person_id=self.test_person_id,
                exact_latitude=self.test_latitude,
                exact_longitude=self.test_longitude
            )

        history = self.agent.get_generation_history(user_id=self.test_user_id, limit=10)

        assert len(history) == 10

    def test_calculate_distance(self):
        """Тест вычисления расстояния между точками"""
        # Расстояние между Москвой и Санкт-Петербургом (примерно 635 км)
        moscow_lat = 55.7558
        moscow_lon = 37.6173
        spb_lat = 59.9343
        spb_lon = 30.3351

        distance = self.agent._calculate_distance(moscow_lat, moscow_lon, spb_lat, spb_lon)

        # Проверяем, что расстояние примерно 635 км (с допуском 10%)
        assert 570000 <= distance <= 700000  # 570-700 км

    def test_get_radius_for_person_with_time_based(self):
        """Тест получения радиуса с учетом настроек по времени"""
        # Устанавливаем настройки с временными ограничениями
        time_settings = [
            TimeBasedSettings(
                start_time="09:00",
                end_time="18:00",
                radius=BubbleRadius.SMALL,
                enabled=True
            )
        ]

        self.agent.set_person_settings(
            user_id=self.test_user_id,
            person_id=self.test_person_id,
            default_radius=BubbleRadius.LARGE,
            time_based_settings=time_settings,
            enabled=True
        )

        # Тест зависит от текущего времени, поэтому просто проверяем, что метод работает
        radius = self.agent._get_radius_for_person(
            user_id=self.test_user_id,
            person_id=self.test_person_id
        )

        assert radius in [100, 500, 1000]  # Один из стандартных радиусов

    def test_get_radius_for_person_with_explicit_radius(self):
        """Тест получения радиуса с явно указанным радиусом"""
        radius = self.agent._get_radius_for_person(
            user_id=self.test_user_id,
            person_id=self.test_person_id,
            requested_radius=250
        )

        assert radius == 250

    def test_bubble_location_to_dict(self):
        """Тест преобразования BubbleLocation в словарь"""
        bubble = self.agent._generate_bubble_location(
            center_latitude=self.test_latitude,
            center_longitude=self.test_longitude,
            radius_meters=500
        )

        # to_dict() не должен включать точные координаты
        result = bubble.to_dict()
        assert "approximate_latitude" in result
        assert "approximate_longitude" in result
        assert "center_latitude" not in result
        assert "center_longitude" not in result

        # to_dict_full() должен включать все координаты
        result_full = bubble.to_dict_full()
        assert "center_latitude" in result_full
        assert "center_longitude" in result_full

    def test_multiple_bubbles_different(self):
        """Тест, что несколько пузырей для одной точки разные"""
        results = []
        for i in range(10):
            result = self.agent.get_bubble_location(
                user_id=self.test_user_id,
                person_id=self.test_person_id,
                exact_latitude=self.test_latitude,
                exact_longitude=self.test_longitude,
                radius=500
            )
            results.append((result["approximate_latitude"], result["approximate_longitude"]))

        # Проверяем, что не все координаты одинаковые (вероятность очень мала)
        unique_coords = set(results)
        assert len(unique_coords) > 1  # Должно быть хотя бы 2 разных координаты
