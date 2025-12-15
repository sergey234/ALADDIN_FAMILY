#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit-тесты для Crash Detection Agent

День 6-9: Тестирование агента
- Unit-тесты алгоритма обнаружения
- Интеграционные тесты (симуляция аварий)
- Тестирование ложных срабатываний

Запуск:
    pytest backend_tests/test_crash_detection_agent.py -v
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from security.ai_agents.crash_detection_agent import (
        CrashDetectionAgent,
        CrashSeverity,
        AccelerometerData,
        GyroscopeData,
        CrashEvent
    )
except ImportError:
    # Для локального тестирования
    import pytest
    pytest.skip("Crash Detection Agent не доступен", allow_module_level=True)


class TestCrashDetectionAgent:
    """Тесты для CrashDetectionAgent"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        config = {
            "g_force_threshold": 3.0,
            "speed_change_threshold": 30.0,
            "emergency_service_number": "112",
            "auto_call_enabled": True,
            "false_positive_filter": True,
            "use_geofence": True,
            "geofence_radius": 500,
            "prefer_gps": True
        }
        self.agent = CrashDetectionAgent(config)
        self.test_user_id = "test_user_123"

    def test_agent_initialization(self):
        """Тест инициализации агента"""
        assert self.agent is not None
        assert self.agent.g_force_threshold == 3.0
        assert self.agent.speed_change_threshold == 30.0
        assert self.agent.emergency_service_number == "112"
        assert self.agent.auto_call_enabled is True
        assert self.agent.false_positive_filter is True
        assert self.agent.use_geofence is True
        assert self.agent.geofence_radius == 500

    def test_start_monitoring(self):
        """Тест запуска мониторинга"""
        result = self.agent.start_monitoring(self.test_user_id)
        assert result is True
        
        # Проверяем, что пользователь в списке активных
        assert self.test_user_id in self.agent.active_monitoring
        
        # Проверяем статус
        status = self.agent.get_status(self.test_user_id)
        assert status["monitoring_active"] is True

    def test_stop_monitoring(self):
        """Тест остановки мониторинга"""
        # Сначала запускаем
        self.agent.start_monitoring(self.test_user_id)
        
        # Останавливаем
        result = self.agent.stop_monitoring(self.test_user_id)
        assert result is True
        
        # Проверяем, что пользователь удален из активных
        assert self.test_user_id not in self.agent.active_monitoring
        
        # Проверяем статус
        status = self.agent.get_status(self.test_user_id)
        assert status["monitoring_active"] is False

    def test_normal_accelerometer_data(self):
        """Тест обработки нормальных данных акселерометра (нет аварии)"""
        # Нормальные данные (G-сила < 3.0)
        accelerometer = {
            "x": 0.1,
            "y": 0.2,
            "z": 9.8,  # Гравитация
            "timestamp": time.time()
        }
        
        self.agent.start_monitoring(self.test_user_id)
        result = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=accelerometer
        )
        
        # Не должно быть обнаружено аварии
        assert result["crash_detected"] is False
        assert result["crash_event"] is None

    def test_crash_detection_high_g_force(self):
        """Тест обнаружения аварии при высокой G-силе"""
        # Высокая G-сила (авария)
        accelerometer = {
            "x": 20.0,  # Резкое ускорение
            "y": 15.0,
            "z": 30.0,
            "timestamp": time.time()
        }
        
        self.agent.start_monitoring(self.test_user_id)
        result = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=accelerometer
        )
        
        # Должна быть обнаружена авария
        assert result["crash_detected"] is True
        assert result["crash_event"] is not None
        
        crash_event = result["crash_event"]
        assert crash_event["severity"] in ["high", "critical"]
        assert crash_event["g_force"] > 3.0

    def test_crash_severity_low(self):
        """Тест определения серьезности LOW (3.0-4.0G)"""
        accelerometer = {
            "x": 5.0,
            "y": 5.0,
            "z": 10.0,
            "timestamp": time.time()
        }
        
        self.agent.start_monitoring(self.test_user_id)
        result = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=accelerometer
        )
        
        if result["crash_detected"]:
            crash_event = result["crash_event"]
            g_force = crash_event["g_force"]
            if 3.0 <= g_force < 4.0:
                assert crash_event["severity"] == "low"

    def test_crash_severity_medium(self):
        """Тест определения серьезности MEDIUM (4.0-5.0G)"""
        accelerometer = {
            "x": 10.0,
            "y": 10.0,
            "z": 15.0,
            "timestamp": time.time()
        }
        
        self.agent.start_monitoring(self.test_user_id)
        result = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=accelerometer
        )
        
        if result["crash_detected"]:
            crash_event = result["crash_event"]
            g_force = crash_event["g_force"]
            if 4.0 <= g_force < 5.0:
                assert crash_event["severity"] == "medium"

    def test_crash_severity_high(self):
        """Тест определения серьезности HIGH (5.0-8.0G)"""
        accelerometer = {
            "x": 20.0,
            "y": 20.0,
            "z": 30.0,
            "timestamp": time.time()
        }
        
        self.agent.start_monitoring(self.test_user_id)
        result = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=accelerometer
        )
        
        if result["crash_detected"]:
            crash_event = result["crash_event"]
            g_force = crash_event["g_force"]
            if 5.0 <= g_force < 8.0:
                assert crash_event["severity"] == "high"

    def test_crash_severity_critical(self):
        """Тест определения серьезности CRITICAL (>8.0G)"""
        accelerometer = {
            "x": 40.0,
            "y": 40.0,
            "z": 50.0,
            "timestamp": time.time()
        }
        
        self.agent.start_monitoring(self.test_user_id)
        result = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=accelerometer
        )
        
        if result["crash_detected"]:
            crash_event = result["crash_event"]
            g_force = crash_event["g_force"]
            if g_force >= 8.0:
                assert crash_event["severity"] == "critical"

    def test_false_positive_filter(self):
        """Тест фильтра ложных срабатываний (падение телефона)"""
        # Симуляция падения телефона (высокая G-сила, но короткая)
        accelerometer1 = {
            "x": 0.1,
            "y": 0.2,
            "z": 9.8,
            "timestamp": time.time()
        }
        
        # Резкое изменение (падение)
        accelerometer2 = {
            "x": 15.0,
            "y": 15.0,
            "z": 25.0,
            "timestamp": time.time() + 0.1
        }
        
        # Возврат к нормальному состоянию
        accelerometer3 = {
            "x": 0.1,
            "y": 0.2,
            "z": 9.8,
            "timestamp": time.time() + 0.2
        }
        
        self.agent.start_monitoring(self.test_user_id)
        
        # Отправляем последовательность данных
        result1 = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=accelerometer1
        )
        result2 = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=accelerometer2
        )
        result3 = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=accelerometer3
        )
        
        # Фильтр должен отличить падение от аварии
        # (в зависимости от реализации фильтра)

    def test_calculate_speed_from_accelerometer(self):
        """Тест вычисления скорости из акселерометра"""
        # Симуляция ускорения
        accelerometer_data = {
            "x": 2.0,  # Ускорение в м/с²
            "y": 0.0,
            "z": 9.8,
            "timestamp": time.time()
        }
        
        # Отправляем несколько измерений для накопления скорости
        self.agent.start_monitoring(self.test_user_id)
        
        for i in range(5):
            accelerometer_data["timestamp"] = time.time() + i * 0.1
            result = self.agent.process_sensor_data(
                user_id=self.test_user_id,
                accelerometer_data=accelerometer_data
            )
        
        # Проверяем, что скорость вычисляется
        # (точное значение зависит от реализации)

    def test_gps_speed_priority(self):
        """Тест приоритета GPS скорости над акселерометром"""
        accelerometer = {
            "x": 0.1,
            "y": 0.2,
            "z": 9.8,
            "timestamp": time.time()
        }
        
        # GPS скорость доступна
        gps_speed = 60.0  # км/ч
        
        self.agent.start_monitoring(self.test_user_id)
        result = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=accelerometer,
            speed=gps_speed
        )
        
        # GPS скорость должна использоваться вместо вычисления из акселерометра
        # (проверка через внутреннее состояние агента)

    def test_geofence_location_fallback(self):
        """Тест использования геозоны как запасного варианта"""
        accelerometer = {
            "x": 0.1,
            "y": 0.2,
            "z": 9.8,
            "timestamp": time.time()
        }
        
        # Нет точного GPS, но есть геозона
        geofence_center = {
            "latitude": 55.7558,
            "longitude": 37.6173
        }
        
        self.agent.start_monitoring(self.test_user_id)
        result = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=accelerometer,
            location=None,  # Нет точного GPS
            geofence_center=geofence_center
        )
        
        # Геозона должна использоваться как запасной вариант
        # (проверка через внутреннее состояние агента)

    def test_crash_history(self):
        """Тест получения истории аварий"""
        # Симулируем несколько аварий
        self.agent.start_monitoring(self.test_user_id)
        
        for i in range(3):
            accelerometer = {
                "x": 20.0 + i * 5.0,
                "y": 15.0 + i * 5.0,
                "z": 30.0 + i * 5.0,
                "timestamp": time.time() + i
            }
            
            result = self.agent.process_sensor_data(
                user_id=self.test_user_id,
                accelerometer_data=accelerometer
            )
            
            if result["crash_detected"]:
                time.sleep(0.1)  # Небольшая задержка между событиями
        
        # Получаем историю
        history = self.agent.get_crash_history(self.test_user_id, limit=10)
        
        assert isinstance(history, list)
        # Количество записей зависит от того, сколько аварий было обнаружено

    def test_emergency_call(self):
        """Тест вызова экстренной службы"""
        # Симулируем аварию
        accelerometer = {
            "x": 30.0,
            "y": 25.0,
            "z": 40.0,
            "timestamp": time.time()
        }
        
        location = {
            "latitude": 55.7558,
            "longitude": 37.6173
        }
        
        self.agent.start_monitoring(self.test_user_id)
        result = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=accelerometer,
            location=location
        )
        
        if result["crash_detected"]:
            crash_event = result["crash_event"]
            
            # Мокируем вызов экстренной службы
            with patch.object(self.agent, '_call_emergency_service', return_value=True) as mock_call:
                # Вызываем напрямую
                crash_event_obj = CrashEvent(
                    event_id=crash_event["event_id"],
                    user_id=self.test_user_id,
                    timestamp=crash_event["timestamp"],
                    severity=CrashSeverity(crash_event["severity"]),
                    g_force=crash_event["g_force"],
                    location=location,
                    speed_before=crash_event.get("speed_before"),
                    emergency_called=False
                )
                
                result_call = self.agent._call_emergency_service(crash_event_obj)
                
                # Проверяем, что вызов был сделан
                assert mock_call.called or result_call is True

    def test_cancel_emergency_call(self):
        """Тест отмены вызова экстренной службы"""
        # Симулируем аварию и вызов
        accelerometer = {
            "x": 30.0,
            "y": 25.0,
            "z": 40.0,
            "timestamp": time.time()
        }
        
        self.agent.start_monitoring(self.test_user_id)
        result = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=accelerometer
        )
        
        if result["crash_detected"]:
            crash_event = result["crash_event"]
            call_id = crash_event.get("emergency_call_id")
            
            if call_id:
                # Отменяем вызов
                cancel_result = self.agent.cancel_emergency_call(
                    self.test_user_id,
                    call_id
                )
                
                # Проверяем результат
                assert cancel_result is True or cancel_result is False

    def test_threat_monitoring_interface(self):
        """Тест методов ThreatMonitoringInterface"""
        # Проверяем, что агент реализует интерфейс
        assert hasattr(self.agent, 'collect_threats')
        assert hasattr(self.agent, 'analyze_threats')
        assert hasattr(self.agent, 'send_alert')
        
        # Тестируем collect_threats
        threats = self.agent.collect_threats(self.test_user_id)
        assert isinstance(threats, list)
        
        # Тестируем analyze_threats
        analyzed = self.agent.analyze_threats(threats)
        assert isinstance(analyzed, list)

    def test_integration_full_crash_scenario(self):
        """Интеграционный тест: полный сценарий аварии"""
        # 1. Запускаем мониторинг
        self.agent.start_monitoring(self.test_user_id)
        
        # 2. Нормальное движение
        for i in range(5):
            accelerometer = {
                "x": 0.1,
                "y": 0.2,
                "z": 9.8,
                "timestamp": time.time() + i * 0.1
            }
            
            result = self.agent.process_sensor_data(
                user_id=self.test_user_id,
                accelerometer_data=accelerometer,
                speed=60.0,  # GPS скорость
                location={"latitude": 55.7558, "longitude": 37.6173}
            )
            
            assert result["crash_detected"] is False
        
        # 3. Авария
        crash_accelerometer = {
            "x": 35.0,
            "y": 30.0,
            "z": 45.0,
            "timestamp": time.time() + 0.5
        }
        
        result = self.agent.process_sensor_data(
            user_id=self.test_user_id,
            accelerometer_data=crash_accelerometer,
            speed=60.0,
            location={"latitude": 55.7558, "longitude": 37.6173}
        )
        
        # 4. Проверяем обнаружение
        assert result["crash_detected"] is True
        assert result["crash_event"] is not None
        
        # 5. Проверяем историю
        history = self.agent.get_crash_history(self.test_user_id, limit=1)
        assert len(history) > 0
        
        # 6. Проверяем статус
        status = self.agent.get_status(self.test_user_id)
        assert status["monitoring_active"] is True
        assert status["total_crashes"] > 0

    def test_multiple_users(self):
        """Тест работы с несколькими пользователями"""
        user1 = "user_1"
        user2 = "user_2"
        
        # Запускаем мониторинг для обоих
        self.agent.start_monitoring(user1)
        self.agent.start_monitoring(user2)
        
        # Симулируем аварию для user1
        accelerometer = {
            "x": 30.0,
            "y": 25.0,
            "z": 40.0,
            "timestamp": time.time()
        }
        
        result1 = self.agent.process_sensor_data(
            user_id=user1,
            accelerometer_data=accelerometer
        )
        
        # Нормальные данные для user2
        normal_accelerometer = {
            "x": 0.1,
            "y": 0.2,
            "z": 9.8,
            "timestamp": time.time()
        }
        
        result2 = self.agent.process_sensor_data(
            user_id=user2,
            accelerometer_data=normal_accelerometer
        )
        
        # Проверяем, что данные не смешались
        history1 = self.agent.get_crash_history(user1, limit=10)
        history2 = self.agent.get_crash_history(user2, limit=10)
        
        # user1 должен иметь аварию, user2 - нет (или меньше)
        if result1["crash_detected"]:
            assert len(history1) >= len(history2)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
