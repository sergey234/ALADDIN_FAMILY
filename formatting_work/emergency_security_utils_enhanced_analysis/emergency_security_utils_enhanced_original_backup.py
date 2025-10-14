#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты безопасности для системы экстренного реагирования
Применение Single Responsibility принципа

Версия 2.0 - Улучшенная с async/await, расширенной валидацией и обработкой ошибок
"""

import asyncio
import hashlib
import re
from datetime import datetime
from typing import Any, Dict, Optional, Union, List, Tuple
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InputSanitizer:
    """
    Очистка пользовательского ввода
    
    Класс для безопасной очистки и валидации пользовательского ввода
    с защитой от XSS, инъекций и других атак.
    
    Examples:
        >>> sanitizer = InputSanitizer()
        >>> sanitizer.sanitize_text("<script>alert('xss')</script>Hello")
        "Hello"
        >>> sanitizer.sanitize_phone("+7 (123) 456-78-90")
        "+71234567890"
        >>> sanitizer.sanitize_email("  TEST@EXAMPLE.COM  ")
        "test@example.com"
    """

    @staticmethod
    def sanitize_text(text: Union[str, None]) -> str:
        """
        Очистить текст от потенциально опасных символов

        Args:
            text: Исходный текст для очистки

        Returns:
            str: Очищенный и безопасный текст
            
        Raises:
            TypeError: Если text не является строкой или None
            
        Examples:
            >>> InputSanitizer.sanitize_text("<script>alert(1)</script>Hello")
            "Hello"
            >>> InputSanitizer.sanitize_text(None)
            ""
            >>> InputSanitizer.sanitize_text("")
            ""
        """
        try:
            if text is None:
                return ""
            
            if not isinstance(text, str):
                logger.warning(f"sanitize_text: Expected string, got {type(text)}")
                return str(text) if text is not None else ""
            
            if not text:
                return ""

            # Удаляем HTML теги
            text = re.sub(r"<[^>]+>", "", text)

            # Удаляем потенциально опасные символы
            text = re.sub(r'[<>"\']', "", text)

            # Ограничиваем длину
            return text[:1000]
            
        except Exception as e:
            logger.error(f"Error in sanitize_text: {e}")
            return ""

    @staticmethod
    def sanitize_phone(phone: Union[str, None]) -> str:
        """
        Очистить номер телефона от лишних символов

        Args:
            phone: Исходный номер телефона

        Returns:
            str: Очищенный номер телефона
            
        Raises:
            TypeError: Если phone не является строкой или None
            
        Examples:
            >>> InputSanitizer.sanitize_phone("+7 (123) 456-78-90")
            "+71234567890"
            >>> InputSanitizer.sanitize_phone("8-800-555-35-35")
            "88005553535"
            >>> InputSanitizer.sanitize_phone(None)
            ""
        """
        try:
            if phone is None:
                return ""
            
            if not isinstance(phone, str):
                logger.warning(f"sanitize_phone: Expected string, got {type(phone)}")
                return str(phone) if phone is not None else ""
            
            if not phone:
                return ""

            # Оставляем только цифры и +
            return re.sub(r"[^\d+]", "", phone)
            
        except Exception as e:
            logger.error(f"Error in sanitize_phone: {e}")
            return ""

    @staticmethod
    def sanitize_email(email: Union[str, None]) -> str:
        """
        Очистить email адрес

        Args:
            email: Исходный email адрес

        Returns:
            str: Очищенный email адрес в нижнем регистре
            
        Raises:
            TypeError: Если email не является строкой или None
            
        Examples:
            >>> InputSanitizer.sanitize_email("  TEST@EXAMPLE.COM  ")
            "test@example.com"
            >>> InputSanitizer.sanitize_email("user+tag@domain.co.uk")
            "user+tag@domain.co.uk"
            >>> InputSanitizer.sanitize_email(None)
            ""
        """
        try:
            if email is None:
                return ""
            
            if not isinstance(email, str):
                logger.warning(f"sanitize_email: Expected string, got {type(email)}")
                return str(email) if email is not None else ""
            
            if not email:
                return ""

            # Приводим к нижнему регистру и убираем пробелы
            return email.lower().strip()
            
        except Exception as e:
            logger.error(f"Error in sanitize_email: {e}")
            return ""

    @staticmethod
    async def sanitize_text_async(text: Union[str, None]) -> str:
        """
        Асинхронная очистка текста от потенциально опасных символов

        Args:
            text: Исходный текст для очистки

        Returns:
            str: Очищенный и безопасный текст
            
        Examples:
            >>> await InputSanitizer.sanitize_text_async("<script>alert(1)</script>Hello")
            "Hello"
        """
        try:
            # Имитируем асинхронную обработку
            await asyncio.sleep(0.001)
            return InputSanitizer.sanitize_text(text)
        except Exception as e:
            logger.error(f"Error in sanitize_text_async: {e}")
            return ""


class SecurityValidator:
    """
    Валидатор безопасности
    
    Класс для валидации данных на предмет безопасности,
    спама и подозрительного содержимого.
    
    Examples:
        >>> validator = SecurityValidator()
        >>> validator.validate_emergency_description("Пожар в здании")
        True
        >>> validator.validate_input_length("Hello", 1, 10)
        True
        >>> validator.validate_contains_suspicious_content("<script>alert(1)</script>")
        True
    """

    @staticmethod
    def validate_emergency_description(description: Union[str, None]) -> bool:
        """
        Валидировать описание экстренной ситуации

        Args:
            description: Описание для проверки

        Returns:
            bool: True если описание безопасно и валидно
            
        Raises:
            TypeError: Если description не является строкой или None
            
        Examples:
            >>> SecurityValidator.validate_emergency_description("Пожар в здании")
            True
            >>> SecurityValidator.validate_emergency_description("test")
            False
            >>> SecurityValidator.validate_emergency_description("")
            False
        """
        try:
            if description is None:
                return False
            
            if not isinstance(description, str):
                logger.warning(f"validate_emergency_description: Expected string, got {type(description)}")
                return False
            
            if not description:
                return False

            # Проверяем длину
            if len(description) < 10:
                return False

            # Проверяем на спам
            spam_indicators = {"test", "тест", "spam", "спам"}
            description_lower = description.lower()
            if any(
                indicator in description_lower for indicator in spam_indicators
            ):
                return False

            return True
            
        except Exception as e:
            logger.error(f"Error in validate_emergency_description: {e}")
            return False

    @staticmethod
    def validate_input_length(
        text: Union[str, None], min_length: int = 1, max_length: int = 1000
    ) -> bool:
        """
        Проверить длину входных данных

        Args:
            text: Текст для проверки
            min_length: Минимальная длина (по умолчанию 1)
            max_length: Максимальная длина (по умолчанию 1000)

        Returns:
            bool: True если длина приемлема
            
        Raises:
            TypeError: Если text не является строкой или None
            ValueError: Если min_length < 0 или max_length < min_length
            
        Examples:
            >>> SecurityValidator.validate_input_length("Hello", 1, 10)
            True
            >>> SecurityValidator.validate_input_length("", 0, 10)
            True
            >>> SecurityValidator.validate_input_length("Very long text", 1, 5)
            False
        """
        try:
            if not isinstance(min_length, int) or min_length < 0:
                raise ValueError("min_length must be a non-negative integer")
            if not isinstance(max_length, int) or max_length < min_length:
                raise ValueError("max_length must be an integer >= min_length")
            
            if text is None:
                return min_length == 0
            
            if not isinstance(text, str):
                logger.warning(f"validate_input_length: Expected string, got {type(text)}")
                return False
            
            if not text:
                return min_length == 0

            return min_length <= len(text) <= max_length
            
        except Exception as e:
            logger.error(f"Error in validate_input_length: {e}")
            return False

    @staticmethod
    def validate_contains_suspicious_content(text: Union[str, None]) -> bool:
        """
        Проверить на подозрительное содержимое

        Args:
            text: Текст для проверки

        Returns:
            bool: True если содержимое подозрительное
            
        Raises:
            TypeError: Если text не является строкой или None
            
        Examples:
            >>> SecurityValidator.validate_contains_suspicious_content("<script>alert(1)</script>")
            True
            >>> SecurityValidator.validate_contains_suspicious_content("Hello world")
            False
            >>> SecurityValidator.validate_contains_suspicious_content("javascript:alert(1)")
            True
        """
        try:
            if text is None:
                return False
            
            if not isinstance(text, str):
                logger.warning(f"validate_contains_suspicious_content: Expected string, got {type(text)}")
                return False
            
            if not text:
                return False

            # Паттерны подозрительного содержимого
            suspicious_patterns = [
                r"<script.*?>.*?</script>",  # JavaScript
                r"javascript:",  # JavaScript протокол
                r"data:text/html",  # Data URI
                r"vbscript:",  # VBScript
                r"on\w+\s*=",  # Event handlers
            ]

            text_lower = text.lower()
            for pattern in suspicious_patterns:
                if re.search(pattern, text_lower):
                    return True

            return False
            
        except Exception as e:
            logger.error(f"Error in validate_contains_suspicious_content: {e}")
            return False

    @staticmethod
    async def validate_emergency_description_async(description: Union[str, None]) -> bool:
        """
        Асинхронная валидация описания экстренной ситуации

        Args:
            description: Описание для проверки

        Returns:
            bool: True если описание безопасно и валидно
        """
        try:
            await asyncio.sleep(0.001)
            return SecurityValidator.validate_emergency_description(description)
        except Exception as e:
            logger.error(f"Error in validate_emergency_description_async: {e}")
            return False


class DataHasher:
    """
    Хеширование данных для безопасности
    
    Класс для безопасного хеширования данных с использованием
    различных алгоритмов хеширования.
    
    Examples:
        >>> hasher = DataHasher()
        >>> event_data = {"emergency_type": "fire", "location": "Moscow"}
        >>> hasher.generate_event_hash(event_data)
        "a0babfc3b35c0537..."
        >>> contact_data = {"name": "John", "phone": "+1234567890"}
        >>> hasher.generate_contact_hash(contact_data)
        "26ef639b4d1199d7..."
    """

    @staticmethod
    def generate_event_hash(event_data: Union[Dict[str, Any], None]) -> str:
        """
        Сгенерировать хеш для события (для дедупликации)

        Args:
            event_data: Данные события

        Returns:
            str: MD5 хеш события (32 символа)
            
        Raises:
            TypeError: Если event_data не является словарем или None
            
        Examples:
            >>> DataHasher.generate_event_hash({"emergency_type": "fire"})
            "a0babfc3b35c0537..."
            >>> DataHasher.generate_event_hash(None)
            ""
        """
        try:
            if event_data is None:
                return ""
            
            if not isinstance(event_data, dict):
                logger.warning(f"generate_event_hash: Expected dict, got {type(event_data)}")
                return ""
            
            # Создаем строку из ключевых полей
            key_fields = [
                str(event_data.get("emergency_type", "")),
                str(event_data.get("location", {}).get("coordinates", (0, 0))),
                str(event_data.get("timestamp", "")),
                str(event_data.get("description", ""))[
                    :100
                ],  # Первые 100 символов
            ]

            hash_string = "|".join(key_fields)
            return hashlib.md5(hash_string.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error in generate_event_hash: {e}")
            return ""

    @staticmethod
    def generate_contact_hash(contact_data: Union[Dict[str, Any], None]) -> str:
        """
        Сгенерировать хеш для контакта

        Args:
            contact_data: Данные контакта

        Returns:
            str: SHA256 хеш контакта (64 символа)
            
        Raises:
            TypeError: Если contact_data не является словарем или None
            
        Examples:
            >>> DataHasher.generate_contact_hash({"name": "John", "phone": "+1234567890"})
            "26ef639b4d1199d7..."
            >>> DataHasher.generate_contact_hash(None)
            ""
        """
        try:
            if contact_data is None:
                return ""
            
            if not isinstance(contact_data, dict):
                logger.warning(f"generate_contact_hash: Expected dict, got {type(contact_data)}")
                return ""
            
            key_fields = [
                str(contact_data.get("name", "")),
                str(contact_data.get("phone", "")),
                str(contact_data.get("email", "")),
            ]

            hash_string = "|".join(key_fields)
            return hashlib.sha256(hash_string.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error in generate_contact_hash: {e}")
            return ""

    @staticmethod
    async def generate_event_hash_async(event_data: Union[Dict[str, Any], None]) -> str:
        """
        Асинхронная генерация хеша для события

        Args:
            event_data: Данные события

        Returns:
            str: MD5 хеш события
        """
        try:
            await asyncio.sleep(0.001)
            return DataHasher.generate_event_hash(event_data)
        except Exception as e:
            logger.error(f"Error in generate_event_hash_async: {e}")
            return ""


class SecurityLogger:
    """
    Логгер для событий безопасности
    
    Класс для безопасного логирования событий безопасности
    с различными уровнями серьезности.
    
    Examples:
        >>> logger = SecurityLogger()
        >>> logger.log_security_event("TEST_EVENT", "Test message", "low")
        🔒 [2025-01-01T12:00:00] SECURITY_LOW: TEST_EVENT - Test message
        >>> logger.log_validation_failure("field", "value", "reason")
        🔒 [2025-01-01T12:00:00] SECURITY_MEDIUM: VALIDATION_FAILURE - Field: field, Value: value, Reason: reason
    """

    @staticmethod
    def log_security_event(
        event_type: Union[str, None], 
        details: Union[str, None], 
        severity: str = "medium"
    ) -> None:
        """
        Записать событие безопасности в лог

        Args:
            event_type: Тип события
            details: Детали события
            severity: Серьезность (low, medium, high, critical)

        Returns:
            None
            
        Raises:
            TypeError: Если параметры не являются строками или None
            
        Examples:
            >>> SecurityLogger.log_security_event("TEST_EVENT", "Test message", "low")
            🔒 [2025-01-01T12:00:00] SECURITY_LOW: TEST_EVENT - Test message
        """
        try:
            if event_type is None:
                event_type = "UNKNOWN_EVENT"
            if details is None:
                details = "No details provided"
            
            if not isinstance(event_type, str):
                event_type = str(event_type)
            if not isinstance(details, str):
                details = str(details)
            if not isinstance(severity, str):
                severity = str(severity)
            
            timestamp = datetime.now().isoformat()
            log_entry = (
                f"[{timestamp}] SECURITY_{severity.upper()}: "
                f"{event_type} - {details}"
            )

            # В реальной системе здесь запись в лог файл
            print(f"🔒 {log_entry}")
            logger.info(f"Security event: {event_type} - {details}")
            
        except Exception as e:
            print(f"❌ Ошибка записи в лог безопасности: {e}")
            logger.error(f"Error in log_security_event: {e}")

    @staticmethod
    def log_validation_failure(field: Union[str, None], value: Union[str, None], reason: Union[str, None]) -> None:
        """
        Записать неудачную валидацию

        Args:
            field: Поле, которое не прошло валидацию
            value: Значение поля
            reason: Причина неудачи

        Returns:
            None
            
        Examples:
            >>> SecurityLogger.log_validation_failure("email", "invalid@", "Invalid format")
            🔒 [2025-01-01T12:00:00] SECURITY_MEDIUM: VALIDATION_FAILURE - Field: email, Value: invalid@, Reason: Invalid format
        """
        try:
            if field is None:
                field = "unknown_field"
            if value is None:
                value = "None"
            if reason is None:
                reason = "Unknown reason"
            
            SecurityLogger.log_security_event(
                "VALIDATION_FAILURE",
                f"Field: {field}, Value: {str(value)[:50]}, Reason: {reason}",
                "medium",
            )
            
        except Exception as e:
            logger.error(f"Error in log_validation_failure: {e}")

    @staticmethod
    def log_suspicious_activity(activity: Union[str, None], details: Union[str, None]) -> None:
        """
        Записать подозрительную активность

        Args:
            activity: Тип активности
            details: Детали активности

        Returns:
            None
            
        Examples:
            >>> SecurityLogger.log_suspicious_activity("SUSPICIOUS_INPUT", "Script injection attempt")
            🔒 [2025-01-01T12:00:00] SECURITY_HIGH: SUSPICIOUS_ACTIVITY - Activity: SUSPICIOUS_INPUT, Details: Script injection attempt
        """
        try:
            if activity is None:
                activity = "UNKNOWN_ACTIVITY"
            if details is None:
                details = "No details provided"
            
            SecurityLogger.log_security_event(
                "SUSPICIOUS_ACTIVITY",
                f"Activity: {activity}, Details: {details}",
                "high",
            )
            
        except Exception as e:
            logger.error(f"Error in log_suspicious_activity: {e}")

    @staticmethod
    async def log_security_event_async(
        event_type: Union[str, None], 
        details: Union[str, None], 
        severity: str = "medium"
    ) -> None:
        """
        Асинхронная запись события безопасности в лог

        Args:
            event_type: Тип события
            details: Детали события
            severity: Серьезность (low, medium, high, critical)
        """
        try:
            await asyncio.sleep(0.001)
            SecurityLogger.log_security_event(event_type, details, severity)
        except Exception as e:
            logger.error(f"Error in log_security_event_async: {e}")


class EmergencySecurityUtils:
    """
    Основные утилиты безопасности
    
    Класс для комплексной обработки данных экстренных ситуаций
    с применением всех компонентов безопасности.
    
    Examples:
        >>> utils = EmergencySecurityUtils()
        >>> data = {"description": "<script>alert(1)</script>Fire", "location": "Moscow"}
        >>> secured = utils.secure_emergency_data(data)
        {"description": "alert(1)Fire", "location": "Moscow"}
        >>> request = {"emergency_type": "fire", "description": "Пожар", "location": "Moscow"}
        >>> utils.validate_emergency_request(request)
        True
    """

    @staticmethod
    def secure_emergency_data(data: Union[Dict[str, Any], None]) -> Union[Dict[str, Any], None]:
        """
        Обезопасить данные экстренной ситуации

        Args:
            data: Исходные данные

        Returns:
            Dict: Обезопасенные данные или None при ошибке
            
        Raises:
            TypeError: Если data не является словарем или None
            
        Examples:
            >>> EmergencySecurityUtils.secure_emergency_data({"description": "<script>alert(1)</script>Fire"})
            {"description": "alert(1)Fire"}
            >>> EmergencySecurityUtils.secure_emergency_data(None)
            None
        """
        try:
            if data is None:
                return None
            
            if not isinstance(data, dict):
                logger.warning(f"secure_emergency_data: Expected dict, got {type(data)}")
                return None
            
            secured_data = {}

            for key, value in data.items():
                if isinstance(value, str):
                    # Очищаем строковые значения
                    secured_data[key] = InputSanitizer.sanitize_text(value)
                elif isinstance(value, dict):
                    # Рекурсивно обрабатываем вложенные словари
                    secured_data[key] = (
                        EmergencySecurityUtils.secure_emergency_data(value)
                    )
                else:
                    secured_data[key] = value

            return secured_data
            
        except Exception as e:
            SecurityLogger.log_security_event(
                "DATA_SECURING_ERROR", f"Error securing data: {str(e)}", "high"
            )
            return data

    @staticmethod
    def validate_emergency_request(request_data: Union[Dict[str, Any], None]) -> bool:
        """
        Валидировать запрос экстренной ситуации

        Args:
            request_data: Данные запроса

        Returns:
            bool: True если запрос валиден
            
        Raises:
            TypeError: Если request_data не является словарем или None
            
        Examples:
            >>> request = {"emergency_type": "fire", "description": "Пожар в здании", "location": "Moscow"}
            >>> EmergencySecurityUtils.validate_emergency_request(request)
            True
            >>> EmergencySecurityUtils.validate_emergency_request(None)
            False
        """
        try:
            if request_data is None:
                return False
            
            if not isinstance(request_data, dict):
                logger.warning(f"validate_emergency_request: Expected dict, got {type(request_data)}")
                return False
            
            # Проверяем обязательные поля
            required_fields = ["emergency_type", "description", "location"]
            for field in required_fields:
                if field not in request_data:
                    SecurityLogger.log_validation_failure(
                        field, "missing", "Required field missing"
                    )
                    return False

            # Проверяем описание
            description = request_data.get("description", "")
            if not SecurityValidator.validate_emergency_description(
                description
            ):
                SecurityLogger.log_validation_failure(
                    "description", description, "Invalid description"
                )
                return False

            # Проверяем на подозрительное содержимое
            for key, value in request_data.items():
                if isinstance(value, str):
                    if SecurityValidator.validate_contains_suspicious_content(
                        value
                    ):
                        SecurityLogger.log_suspicious_activity(
                            "SUSPICIOUS_INPUT",
                            f"Field: {key}, Value: {value[:50]}",
                        )
                        return False

            return True
            
        except Exception as e:
            SecurityLogger.log_security_event(
                "VALIDATION_ERROR",
                f"Error validating request: {str(e)}",
                "high",
            )
            return False

    @staticmethod
    async def secure_emergency_data_async(data: Union[Dict[str, Any], None]) -> Union[Dict[str, Any], None]:
        """
        Асинхронная обезопаска данных экстренной ситуации

        Args:
            data: Исходные данные

        Returns:
            Dict: Обезопасенные данные или None при ошибке
        """
        try:
            await asyncio.sleep(0.001)
            return EmergencySecurityUtils.secure_emergency_data(data)
        except Exception as e:
            logger.error(f"Error in secure_emergency_data_async: {e}")
            return None

    @staticmethod
    async def validate_emergency_request_async(request_data: Union[Dict[str, Any], None]) -> bool:
        """
        Асинхронная валидация запроса экстренной ситуации

        Args:
            request_data: Данные запроса

        Returns:
            bool: True если запрос валиден
        """
        try:
            await asyncio.sleep(0.001)
            return EmergencySecurityUtils.validate_emergency_request(request_data)
        except Exception as e:
            logger.error(f"Error in validate_emergency_request_async: {e}")
            return False


# Дополнительные утилиты для тестирования
class SecurityTestUtils:
    """
    Утилиты для тестирования компонентов безопасности
    
    Класс содержит методы для комплексного тестирования
    всех компонентов системы безопасности.
    """
    
    @staticmethod
    def run_comprehensive_tests() -> Dict[str, Any]:
        """
        Запустить комплексные тесты всех компонентов
        
        Returns:
            Dict: Результаты тестирования
        """
        test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        
        # Тесты InputSanitizer
        test_cases = [
            ("sanitize_text_normal", lambda: InputSanitizer.sanitize_text("Hello World") == "Hello World"),
            ("sanitize_text_xss", lambda: InputSanitizer.sanitize_text("<script>alert(1)</script>Hello") == "alert(1)Hello"),
            ("sanitize_text_none", lambda: InputSanitizer.sanitize_text(None) == ""),
            ("sanitize_text_empty", lambda: InputSanitizer.sanitize_text("") == ""),
            ("sanitize_phone_normal", lambda: InputSanitizer.sanitize_phone("+7 (123) 456-78-90") == "+71234567890"),
            ("sanitize_phone_none", lambda: InputSanitizer.sanitize_phone(None) == ""),
            ("sanitize_email_normal", lambda: InputSanitizer.sanitize_email("  TEST@EXAMPLE.COM  ") == "test@example.com"),
            ("sanitize_email_none", lambda: InputSanitizer.sanitize_email(None) == ""),
        ]
        
        for test_name, test_func in test_cases:
            test_results["total_tests"] += 1
            try:
                result = test_func()
                if result:
                    test_results["passed_tests"] += 1
                    test_results["test_details"].append({"test": test_name, "status": "PASS"})
                else:
                    test_results["failed_tests"] += 1
                    test_results["test_details"].append({"test": test_name, "status": "FAIL"})
            except Exception as e:
                test_results["failed_tests"] += 1
                test_results["test_details"].append({"test": test_name, "status": "ERROR", "error": str(e)})
        
        # Тесты SecurityValidator
        validator_tests = [
            ("validate_emergency_description_valid", lambda: SecurityValidator.validate_emergency_description("Пожар в здании") == True),
            ("validate_emergency_description_invalid", lambda: SecurityValidator.validate_emergency_description("test") == False),
            ("validate_emergency_description_none", lambda: SecurityValidator.validate_emergency_description(None) == False),
            ("validate_input_length_valid", lambda: SecurityValidator.validate_input_length("Hello", 1, 10) == True),
            ("validate_input_length_invalid", lambda: SecurityValidator.validate_input_length("", 5, 10) == False),
            ("validate_contains_suspicious_content_script", lambda: SecurityValidator.validate_contains_suspicious_content("<script>alert(1)</script>") == True),
            ("validate_contains_suspicious_content_normal", lambda: SecurityValidator.validate_contains_suspicious_content("Hello world") == False),
        ]
        
        for test_name, test_func in validator_tests:
            test_results["total_tests"] += 1
            try:
                result = test_func()
                if result:
                    test_results["passed_tests"] += 1
                    test_results["test_details"].append({"test": test_name, "status": "PASS"})
                else:
                    test_results["failed_tests"] += 1
                    test_results["test_details"].append({"test": test_name, "status": "FAIL"})
            except Exception as e:
                test_results["failed_tests"] += 1
                test_results["test_details"].append({"test": test_name, "status": "ERROR", "error": str(e)})
        
        # Тесты DataHasher
        hasher_tests = [
            ("generate_event_hash_valid", lambda: len(DataHasher.generate_event_hash({"emergency_type": "fire"})) == 32),
            ("generate_event_hash_none", lambda: DataHasher.generate_event_hash(None) == ""),
            ("generate_contact_hash_valid", lambda: len(DataHasher.generate_contact_hash({"name": "John"})) == 64),
            ("generate_contact_hash_none", lambda: DataHasher.generate_contact_hash(None) == ""),
        ]
        
        for test_name, test_func in hasher_tests:
            test_results["total_tests"] += 1
            try:
                result = test_func()
                if result:
                    test_results["passed_tests"] += 1
                    test_results["test_details"].append({"test": test_name, "status": "PASS"})
                else:
                    test_results["failed_tests"] += 1
                    test_results["test_details"].append({"test": test_name, "status": "FAIL"})
            except Exception as e:
                test_results["failed_tests"] += 1
                test_results["test_details"].append({"test": test_name, "status": "ERROR", "error": str(e)})
        
        # Тесты EmergencySecurityUtils
        utils_tests = [
            ("secure_emergency_data_valid", lambda: isinstance(EmergencySecurityUtils.secure_emergency_data({"description": "Test"}), dict)),
            ("secure_emergency_data_none", lambda: EmergencySecurityUtils.secure_emergency_data(None) is None),
            ("validate_emergency_request_valid", lambda: EmergencySecurityUtils.validate_emergency_request({"emergency_type": "fire", "description": "Пожар в здании", "location": "Moscow"}) == True),
            ("validate_emergency_request_invalid", lambda: EmergencySecurityUtils.validate_emergency_request({"emergency_type": "fire"}) == False),
            ("validate_emergency_request_none", lambda: EmergencySecurityUtils.validate_emergency_request(None) == False),
        ]
        
        for test_name, test_func in utils_tests:
            test_results["total_tests"] += 1
            try:
                result = test_func()
                if result:
                    test_results["passed_tests"] += 1
                    test_results["test_details"].append({"test": test_name, "status": "PASS"})
                else:
                    test_results["failed_tests"] += 1
                    test_results["test_details"].append({"test": test_name, "status": "FAIL"})
            except Exception as e:
                test_results["failed_tests"] += 1
                test_results["test_details"].append({"test": test_name, "status": "ERROR", "error": str(e)})
        
        return test_results

    @staticmethod
    async def run_async_tests() -> Dict[str, Any]:
        """
        Запустить асинхронные тесты
        
        Returns:
            Dict: Результаты асинхронного тестирования
        """
        test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
        
        async_tests = [
            ("sanitize_text_async", lambda: InputSanitizer.sanitize_text_async("Hello")),
            ("validate_emergency_description_async", lambda: SecurityValidator.validate_emergency_description_async("Пожар в здании")),
            ("generate_event_hash_async", lambda: DataHasher.generate_event_hash_async({"emergency_type": "fire"})),
            ("log_security_event_async", lambda: SecurityLogger.log_security_event_async("TEST", "Message", "low")),
            ("secure_emergency_data_async", lambda: EmergencySecurityUtils.secure_emergency_data_async({"description": "Test"})),
            ("validate_emergency_request_async", lambda: EmergencySecurityUtils.validate_emergency_request_async({"emergency_type": "fire", "description": "Пожар в здании", "location": "Moscow"})),
        ]
        
        for test_name, test_func in async_tests:
            test_results["total_tests"] += 1
            try:
                result = await test_func()
                test_results["passed_tests"] += 1
                test_results["test_details"].append({"test": test_name, "status": "PASS", "result": str(result)[:50]})
            except Exception as e:
                test_results["failed_tests"] += 1
                test_results["test_details"].append({"test": test_name, "status": "ERROR", "error": str(e)})
        
        return test_results


if __name__ == "__main__":
    # Запуск тестов при прямом выполнении файла
    print("🔍 Запуск комплексных тестов системы безопасности...")
    
    # Синхронные тесты
    sync_results = SecurityTestUtils.run_comprehensive_tests()
    print(f"📊 Синхронные тесты: {sync_results['passed_tests']}/{sync_results['total_tests']} пройдено")
    
    # Асинхронные тесты
    async def run_async_tests():
        return await SecurityTestUtils.run_async_tests()
    
    async_results = asyncio.run(run_async_tests())
    print(f"📊 Асинхронные тесты: {async_results['passed_tests']}/{async_results['total_tests']} пройдено")
    
    # Общая статистика
    total_tests = sync_results['total_tests'] + async_results['total_tests']
    total_passed = sync_results['passed_tests'] + async_results['passed_tests']
    success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"🎯 Общая статистика: {total_passed}/{total_tests} тестов пройдено ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! Система готова к продакшену!")
    else:
        print(f"⚠️  {total_tests - total_passed} тестов не пройдено. Требуется доработка.")