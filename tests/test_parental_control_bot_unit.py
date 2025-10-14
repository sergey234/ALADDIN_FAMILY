# -*- coding: utf-8 -*-
"""
Unit тесты для ParentalControlBot
Версия: 2.5
Дата: 2025-09-21
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.bots.parental_control_bot import (
    ChildProfileData,
    ContentAnalysisRequest,
    TimeLimitData,
    AlertData,
    validate_child_data,
    validate_content_request
)


class TestValidationModels:
    """Тесты валидационных моделей"""

    def test_child_profile_data_valid(self):
        """Тест валидных данных профиля ребенка"""
        data = {
            'name': 'Test Child',
            'age': 10,
            'parent_id': 'parent_123',
            'time_limits': {'mobile': 120, 'desktop': 180},
            'restrictions': {'social_media': True, 'gaming': False},
            'safe_zones': [{'name': 'Home', 'location': '123 Main St'}]
        }
        
        profile = ChildProfileData(**data)
        
        assert profile.name == 'Test Child'
        assert profile.age == 10
        assert profile.parent_id == 'parent_123'
        assert profile.time_limits['mobile'] == 120
        assert profile.restrictions['social_media'] is True

    def test_child_profile_data_invalid_name(self):
        """Тест невалидного имени"""
        data = {
            'name': 'A',  # Слишком короткое
            'age': 10,
            'parent_id': 'parent_123'
        }
        
        with pytest.raises(ValueError) as exc_info:
            ChildProfileData(**data)
        
        assert "Имя должно содержать минимум 2 символа" in str(exc_info.value)

    def test_child_profile_data_invalid_age(self):
        """Тест невалидного возраста"""
        data = {
            'name': 'Test Child',
            'age': 25,  # Слишком большой
            'parent_id': 'parent_123'
        }
        
        with pytest.raises(ValueError) as exc_info:
            ChildProfileData(**data)
        
        assert "Возраст должен быть целым числом от 0 до 18 лет" in str(exc_info.value)

    def test_child_profile_data_invalid_parent_id(self):
        """Тест невалидного ID родителя"""
        data = {
            'name': 'Test Child',
            'age': 10,
            'parent_id': 'p'  # Слишком короткий
        }
        
        with pytest.raises(ValueError) as exc_info:
            ChildProfileData(**data)
        
        assert "ID родителя должен содержать минимум 3 символа" in str(exc_info.value)

    def test_child_profile_data_invalid_time_limits(self):
        """Тест невалидных лимитов времени"""
        data = {
            'name': 'Test Child',
            'age': 10,
            'parent_id': 'parent_123',
            'time_limits': {'mobile': -10}  # Отрицательное значение
        }
        
        with pytest.raises(ValueError) as exc_info:
            ChildProfileData(**data)
        
        assert "Лимит времени для mobile должен быть неотрицательным числом" in str(exc_info.value)

    def test_content_analysis_request_valid(self):
        """Тест валидного запроса анализа контента"""
        request = ContentAnalysisRequest(
            url='https://youtube.com',
            child_id='child_123'
        )
        
        assert request.url == 'https://youtube.com'
        assert request.child_id == 'child_123'

    def test_content_analysis_request_invalid_url(self):
        """Тест невалидного URL"""
        with pytest.raises(ValueError) as exc_info:
            ContentAnalysisRequest(
                url='invalid-url',
                child_id='child_123'
            )
        
        assert "URL должен начинаться с http:// или https://" in str(exc_info.value)

    def test_content_analysis_request_invalid_child_id(self):
        """Тест невалидного ID ребенка"""
        with pytest.raises(ValueError) as exc_info:
            ContentAnalysisRequest(
                url='https://youtube.com',
                child_id='c'  # Слишком короткий
            )
        
        assert "ID ребенка должен содержать минимум 3 символа" in str(exc_info.value)

    def test_time_limit_data_valid(self):
        """Тест валидных данных лимита времени"""
        time_data = TimeLimitData(
            device_type='mobile',
            minutes=120
        )
        
        assert time_data.device_type == 'mobile'
        assert time_data.minutes == 120

    def test_time_limit_data_invalid_device_type(self):
        """Тест невалидного типа устройства"""
        with pytest.raises(ValueError) as exc_info:
            TimeLimitData(
                device_type='invalid_device',
                minutes=120
            )
        
        assert "Тип устройства должен быть одним из" in str(exc_info.value)

    def test_time_limit_data_invalid_minutes(self):
        """Тест невалидного количества минут"""
        with pytest.raises(ValueError) as exc_info:
            TimeLimitData(
                device_type='mobile',
                minutes=2000  # Слишком много
            )
        
        assert "Лимит времени должен быть от 0 до 1440 минут" in str(exc_info.value)

    def test_alert_data_valid(self):
        """Тест валидных данных алерта"""
        alert_data = AlertData(
            child_id='child_123',
            alert_type='time_violation',
            severity='medium',
            message='Превышен лимит времени',
            data={'device_type': 'mobile'}
        )
        
        assert alert_data.child_id == 'child_123'
        assert alert_data.alert_type == 'time_violation'
        assert alert_data.severity == 'medium'
        assert alert_data.message == 'Превышен лимит времени'

    def test_alert_data_invalid_alert_type(self):
        """Тест невалидного типа алерта"""
        with pytest.raises(ValueError) as exc_info:
            AlertData(
                child_id='child_123',
                alert_type='invalid_type',
                severity='medium',
                message='Test message'
            )
        
        assert "Тип алерта должен быть одним из" in str(exc_info.value)

    def test_alert_data_invalid_severity(self):
        """Тест невалидного уровня серьезности"""
        with pytest.raises(ValueError) as exc_info:
            AlertData(
                child_id='child_123',
                alert_type='time_violation',
                severity='invalid_severity',
                message='Test message'
            )
        
        assert "Уровень серьезности должен быть одним из" in str(exc_info.value)

    def test_alert_data_invalid_message(self):
        """Тест невалидного сообщения"""
        with pytest.raises(ValueError) as exc_info:
            AlertData(
                child_id='child_123',
                alert_type='time_violation',
                severity='medium',
                message='Hi'  # Слишком короткое
            )
        
        assert "Сообщение должно содержать минимум 5 символов" in str(exc_info.value)


class TestValidationFunctions:
    """Тесты функций валидации"""

    def test_validate_child_data_valid(self):
        """Тест валидации валидных данных ребенка"""
        data = {
            'name': 'Test Child',
            'age': 10,
            'parent_id': 'parent_123'
        }
        
        is_valid, error = validate_child_data(data)
        
        assert is_valid is True
        assert error is None

    def test_validate_child_data_invalid(self):
        """Тест валидации невалидных данных ребенка"""
        data = {
            'name': 'A',
            'age': 25,
            'parent_id': 'p'
        }
        
        is_valid, error = validate_child_data(data)
        
        assert is_valid is False
        assert error is not None
        assert "Имя должно содержать минимум 2 символа" in error

    def test_validate_content_request_valid(self):
        """Тест валидации валидного запроса контента"""
        is_valid, error = validate_content_request('https://youtube.com', 'child_123')
        
        assert is_valid is True
        assert error is None

    def test_validate_content_request_invalid(self):
        """Тест валидации невалидного запроса контента"""
        is_valid, error = validate_content_request('invalid-url', 'c')
        
        assert is_valid is False
        assert error is not None
        assert "URL должен начинаться с http:// или https://" in error


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_child_profile_data_boundary_values(self):
        """Тест граничных значений для профиля ребенка"""
        # Минимальный возраст
        data_min_age = {
            'name': 'Test Child',
            'age': 0,
            'parent_id': 'parent_123'
        }
        profile_min = ChildProfileData(**data_min_age)
        assert profile_min.age == 0

        # Максимальный возраст
        data_max_age = {
            'name': 'Test Child',
            'age': 18,
            'parent_id': 'parent_123'
        }
        profile_max = ChildProfileData(**data_max_age)
        assert profile_max.age == 18

        # Минимальная длина имени
        data_min_name = {
            'name': 'AB',  # Ровно 2 символа
            'age': 10,
            'parent_id': 'parent_123'
        }
        profile_min_name = ChildProfileData(**data_min_name)
        assert profile_min_name.name == 'AB'

        # Минимальная длина parent_id
        data_min_parent = {
            'name': 'Test Child',
            'age': 10,
            'parent_id': 'ABC'  # Ровно 3 символа
        }
        profile_min_parent = ChildProfileData(**data_min_parent)
        assert profile_min_parent.parent_id == 'ABC'

    def test_time_limit_data_boundary_values(self):
        """Тест граничных значений для лимитов времени"""
        # Минимальное время
        time_min = TimeLimitData(device_type='mobile', minutes=0)
        assert time_min.minutes == 0

        # Максимальное время
        time_max = TimeLimitData(device_type='mobile', minutes=1440)
        assert time_max.minutes == 1440

    def test_alert_data_boundary_values(self):
        """Тест граничных значений для алертов"""
        # Минимальная длина сообщения
        alert_min_msg = AlertData(
            child_id='child_123',
            alert_type='time_violation',
            severity='low',
            message='Hello'  # Ровно 5 символов
        )
        assert alert_min_msg.message == 'Hello'

    def test_empty_optional_fields(self):
        """Тест пустых опциональных полей"""
        data = {
            'name': 'Test Child',
            'age': 10,
            'parent_id': 'parent_123',
            'time_limits': {},
            'restrictions': {},
            'safe_zones': [],
            'device_ids': []
        }
        
        profile = ChildProfileData(**data)
        
        assert profile.time_limits == {}
        assert profile.restrictions == {}
        assert profile.safe_zones == []
        assert profile.device_ids == []

    def test_whitespace_handling(self):
        """Тест обработки пробелов"""
        data = {
            'name': '  Test Child  ',  # С пробелами
            'age': 10,
            'parent_id': '  parent_123  '  # С пробелами
        }
        
        profile = ChildProfileData(**data)
        
        assert profile.name == 'Test Child'  # Пробелы должны быть удалены
        assert profile.parent_id == 'parent_123'  # Пробелы должны быть удалены


class TestDataTypes:
    """Тесты типов данных"""

    def test_string_coercion(self):
        """Тест приведения к строке"""
        data = {
            'name': 123,  # Число вместо строки
            'age': 10,
            'parent_id': 'parent_123'
        }
        
        with pytest.raises(ValueError):
            ChildProfileData(**data)

    def test_integer_coercion(self):
        """Тест приведения к целому числу"""
        data = {
            'name': 'Test Child',
            'age': '10',  # Строка вместо числа - Pydantic автоматически конвертирует
            'parent_id': 'parent_123'
        }
        
        # Pydantic автоматически конвертирует строку в число
        profile = ChildProfileData(**data)
        assert profile.age == 10  # Должно быть конвертировано в int

    def test_list_validation(self):
        """Тест валидации списков"""
        data = {
            'name': 'Test Child',
            'age': 10,
            'parent_id': 'parent_123',
            'device_ids': 'not_a_list'  # Не список
        }
        
        with pytest.raises(ValueError):
            ChildProfileData(**data)

    def test_dict_validation(self):
        """Тест валидации словарей"""
        data = {
            'name': 'Test Child',
            'age': 10,
            'parent_id': 'parent_123',
            'time_limits': 'not_a_dict'  # Не словарь
        }
        
        with pytest.raises(ValueError):
            ChildProfileData(**data)


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v", "--tb=short"])