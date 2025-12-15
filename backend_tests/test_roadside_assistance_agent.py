#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-тесты для Roadside Assistance Agent

Тестирование:
- Вызов помощи на дороге
- Отслеживание статуса
- Отмена запросов
- История запросов
- Различные типы проблем

Дата создания: 14 декабря 2025
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from security.ai_agents.roadside_assistance_agent import (
        RoadsideAssistanceAgent,
        ProblemType,
        AssistanceStatus,
        PartnerType,
        Location,
        VehicleInfo,
        AssistanceRequest
    )
except ImportError as e:
    print(f"⚠️ Импорт не удался: {e}")
    print("Используем заглушки для тестирования")
    exit(1)


class TestRoadsideAssistanceAgent:
    """Тесты для Roadside Assistance Agent"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.config = {
            "default_partner": "manual",
            "status_check_interval_seconds": 30,
            "max_wait_time_minutes": 120
        }
        self.agent = RoadsideAssistanceAgent(self.config)
        self.user_id = "test_user_123"
        self.location = Location(
            latitude=55.7558,
            longitude=37.6173,
            address="Москва, Ленинградский проспект, 10"
        )

    def test_agent_initialization(self):
        """Тест инициализации агента"""
        assert self.agent is not None
        assert self.agent.default_partner == "manual"
        assert self.agent.status_check_interval_seconds == 30
        assert self.agent.max_wait_time_minutes == 120

    def test_call_assistance_tire_change(self):
        """Тест вызова помощи для замены колеса"""
        request = self.agent.call_assistance(
            user_id=self.user_id,
            problem_type=ProblemType.TIRE_CHANGE,
            location=self.location,
            description="Прокол переднего левого колеса"
        )

        assert request is not None
        assert request.user_id == self.user_id
        assert request.problem_type == ProblemType.TIRE_CHANGE
        assert request.status == AssistanceStatus.PENDING
        assert request.partner == "manual"
        assert request.location.latitude == 55.7558
        assert request.location.longitude == 37.6173
        assert request.request_id.startswith("RSA-")

    def test_call_assistance_towing(self):
        """Тест вызова помощи для буксировки"""
        vehicle_info = VehicleInfo(
            make="Toyota",
            model="Camry",
            year=2020
        )

        request = self.agent.call_assistance(
            user_id=self.user_id,
            problem_type=ProblemType.TOWING,
            location=self.location,
            description="Двигатель не заводится",
            vehicle_info=vehicle_info
        )

        assert request is not None
        assert request.problem_type == ProblemType.TOWING
        assert request.vehicle_info is not None
        assert request.vehicle_info.make == "Toyota"
        assert request.vehicle_info.model == "Camry"

    def test_call_assistance_jump_start(self):
        """Тест вызова помощи для запуска двигателя"""
        request = self.agent.call_assistance(
            user_id=self.user_id,
            problem_type=ProblemType.JUMP_START,
            location=self.location,
            description="Села батарея"
        )

        assert request is not None
        assert request.problem_type == ProblemType.JUMP_START

    def test_call_assistance_lockout(self):
        """Тест вызова помощи для открытия замка"""
        request = self.agent.call_assistance(
            user_id=self.user_id,
            problem_type=ProblemType.LOCKOUT,
            location=self.location,
            description="Ключи остались в машине"
        )

        assert request is not None
        assert request.problem_type == ProblemType.LOCKOUT

    def test_call_assistance_fuel_delivery(self):
        """Тест вызова помощи для доставки топлива"""
        request = self.agent.call_assistance(
            user_id=self.user_id,
            problem_type=ProblemType.FUEL_DELIVERY,
            location=self.location,
            description="Закончился бензин"
        )

        assert request is not None
        assert request.problem_type == ProblemType.FUEL_DELIVERY

    def test_call_assistance_invalid_location(self):
        """Тест вызова помощи с некорректным местоположением"""
        invalid_location = Location(latitude=0, longitude=0)

        try:
            self.agent.call_assistance(
                user_id=self.user_id,
                problem_type=ProblemType.TIRE_CHANGE,
                location=invalid_location
            )
            assert False, "Должна быть ошибка ValueError"
        except ValueError:
            assert True

    def test_call_assistance_empty_user_id(self):
        """Тест вызова помощи с пустым user_id"""
        try:
            self.agent.call_assistance(
                user_id="",
                problem_type=ProblemType.TIRE_CHANGE,
                location=self.location
            )
            assert False, "Должна быть ошибка ValueError"
        except ValueError:
            assert True

    def test_get_status_existing_request(self):
        """Тест получения статуса существующего запроса"""
        # Создаем запрос
        request = self.agent.call_assistance(
            user_id=self.user_id,
            problem_type=ProblemType.TIRE_CHANGE,
            location=self.location
        )

        # Получаем статус
        status = self.agent.get_status(request.request_id)

        assert status is not None
        assert status.request_id == request.request_id
        assert status.user_id == self.user_id
        assert status.status == AssistanceStatus.PENDING

    def test_get_status_nonexistent_request(self):
        """Тест получения статуса несуществующего запроса"""
        status = self.agent.get_status("NONEXISTENT-123")

        assert status is None

    def test_cancel_request(self):
        """Тест отмены запроса"""
        # Создаем запрос
        request = self.agent.call_assistance(
            user_id=self.user_id,
            problem_type=ProblemType.TIRE_CHANGE,
            location=self.location
        )

        # Отменяем запрос
        cancelled = self.agent.cancel_request(request.request_id)

        assert cancelled is True

        # Проверяем статус
        status = self.agent.get_status(request.request_id)
        assert status.status == AssistanceStatus.CANCELLED

    def test_cancel_nonexistent_request(self):
        """Тест отмены несуществующего запроса"""
        cancelled = self.agent.cancel_request("NONEXISTENT-123")

        assert cancelled is False

    def test_cancel_completed_request(self):
        """Тест отмены завершенного запроса"""
        # Создаем запрос
        request = self.agent.call_assistance(
            user_id=self.user_id,
            problem_type=ProblemType.TIRE_CHANGE,
            location=self.location
        )

        # Помечаем как завершенный
        request.status = AssistanceStatus.COMPLETED

        # Пытаемся отменить
        cancelled = self.agent.cancel_request(request.request_id)

        assert cancelled is False

    def test_get_history(self):
        """Тест получения истории запросов"""
        # Создаем несколько запросов
        request1 = self.agent.call_assistance(
            user_id=self.user_id,
            problem_type=ProblemType.TIRE_CHANGE,
            location=self.location
        )

        request2 = self.agent.call_assistance(
            user_id=self.user_id,
            problem_type=ProblemType.JUMP_START,
            location=self.location
        )

        # Получаем историю
        history = self.agent.get_history(self.user_id, limit=10)

        assert len(history) >= 2
        assert any(req.request_id == request1.request_id for req in history)
        assert any(req.request_id == request2.request_id for req in history)

    def test_get_history_limit(self):
        """Тест ограничения истории запросов"""
        # Создаем несколько запросов
        for i in range(5):
            self.agent.call_assistance(
                user_id=self.user_id,
                problem_type=ProblemType.TIRE_CHANGE,
                location=self.location
            )

        # Получаем историю с лимитом
        history = self.agent.get_history(self.user_id, limit=3)

        assert len(history) == 3

    def test_get_history_different_users(self):
        """Тест истории для разных пользователей"""
        # Создаем запросы для разных пользователей
        request1 = self.agent.call_assistance(
            user_id="user1",
            problem_type=ProblemType.TIRE_CHANGE,
            location=self.location
        )

        request2 = self.agent.call_assistance(
            user_id="user2",
            problem_type=ProblemType.JUMP_START,
            location=self.location
        )

        # Получаем историю для user1
        history1 = self.agent.get_history("user1", limit=10)
        assert len(history1) == 1
        assert history1[0].request_id == request1.request_id

        # Получаем историю для user2
        history2 = self.agent.get_history("user2", limit=10)
        assert len(history2) == 1
        assert history2[0].request_id == request2.request_id

    def test_all_problem_types(self):
        """Тест всех типов проблем"""
        problem_types = [
            ProblemType.TOWING,
            ProblemType.JUMP_START,
            ProblemType.TIRE_CHANGE,
            ProblemType.LOCKOUT,
            ProblemType.FUEL_DELIVERY,
            ProblemType.BATTERY_REPLACEMENT,
            ProblemType.WINDSHIELD_REPAIR,
            ProblemType.OTHER
        ]

        for problem_type in problem_types:
            request = self.agent.call_assistance(
                user_id=self.user_id,
                problem_type=problem_type,
                location=self.location
            )
            assert request is not None
            assert request.problem_type == problem_type

    def test_request_to_dict(self):
        """Тест преобразования запроса в словарь"""
        request = self.agent.call_assistance(
            user_id=self.user_id,
            problem_type=ProblemType.TIRE_CHANGE,
            location=self.location,
            description="Прокол колеса"
        )

        request_dict = request.to_dict()

        assert isinstance(request_dict, dict)
        assert request_dict["request_id"] == request.request_id
        assert request_dict["user_id"] == self.user_id
        assert request_dict["problem_type"] == "tire_change"
        assert request_dict["status"] == "pending"
        assert request_dict["location"]["latitude"] == 55.7558
        assert request_dict["description"] == "Прокол колеса"

    def test_location_to_dict(self):
        """Тест преобразования местоположения в словарь"""
        location_dict = self.location.to_dict()

        assert isinstance(location_dict, dict)
        assert location_dict["latitude"] == 55.7558
        assert location_dict["longitude"] == 37.6173
        assert location_dict["address"] == "Москва, Ленинградский проспект, 10"

    def test_vehicle_info_to_dict(self):
        """Тест преобразования информации о транспортном средстве в словарь"""
        vehicle_info = VehicleInfo(
            make="Toyota",
            model="Camry",
            year=2020,
            color="Белый",
            license_plate="А123БВ777"
        )

        vehicle_dict = vehicle_info.to_dict()

        assert isinstance(vehicle_dict, dict)
        assert vehicle_dict["make"] == "Toyota"
        assert vehicle_dict["model"] == "Camry"
        assert vehicle_dict["year"] == 2020
        assert vehicle_dict["color"] == "Белый"
        assert vehicle_dict["license_plate"] == "А123БВ777"


def run_tests():
    """Запуск всех тестов"""
    import unittest

    # Создаем test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRoadsideAssistanceAgent)

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Возвращаем результат
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
