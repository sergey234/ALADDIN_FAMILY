#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утилиты безопасности для системы экстренного реагирования
Применение Single Responsibility принципа
"""

import hashlib
import re
from datetime import datetime
from typing import Any, Dict


class InputSanitizer:
    """Очистка пользовательского ввода"""

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Очистить текст от потенциально опасных символов

        Args:
            text: Исходный текст

        Returns:
            str: Очищенный текст
        """
        if not text:
            return ""

        # Удаляем HTML теги
        text = re.sub(r"<[^>]+>", "", text)

        # Удаляем потенциально опасные символы
        text = re.sub(r'[<>"\']', "", text)

        # Ограничиваем длину
        return text[:1000]

    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """
        Очистить номер телефона

        Args:
            phone: Исходный номер

        Returns:
            str: Очищенный номер
        """
        if not phone:
            return ""

        # Оставляем только цифры и +
        return re.sub(r"[^\d+]", "", phone)

    @staticmethod
    def sanitize_email(email: str) -> str:
        """
        Очистить email адрес

        Args:
            email: Исходный email

        Returns:
            str: Очищенный email
        """
        if not email:
            return ""

        # Приводим к нижнему регистру и убираем пробелы
        return email.lower().strip()


class SecurityValidator:
    """Валидатор безопасности"""

    @staticmethod
    def validate_emergency_description(description: str) -> bool:
        """
        Валидировать описание экстренной ситуации

        Args:
            description: Описание для проверки

        Returns:
            bool: True если описание безопасно
        """
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

    @staticmethod
    def validate_input_length(
        text: str, min_length: int = 1, max_length: int = 1000
    ) -> bool:
        """
        Проверить длину входных данных

        Args:
            text: Текст для проверки
            min_length: Минимальная длина
            max_length: Максимальная длина

        Returns:
            bool: True если длина приемлема
        """
        if not text:
            return min_length == 0

        return min_length <= len(text) <= max_length

    @staticmethod
    def validate_contains_suspicious_content(text: str) -> bool:
        """
        Проверить на подозрительное содержимое

        Args:
            text: Текст для проверки

        Returns:
            bool: True если содержимое подозрительное
        """
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


class DataHasher:
    """Хеширование данных для безопасности"""

    @staticmethod
    def generate_event_hash(event_data: Dict[str, Any]) -> str:
        """
        Сгенерировать хеш для события (для дедупликации)

        Args:
            event_data: Данные события

        Returns:
            str: Хеш события
        """
        try:
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
        except Exception:
            return ""

    @staticmethod
    def generate_contact_hash(contact_data: Dict[str, Any]) -> str:
        """
        Сгенерировать хеш для контакта

        Args:
            contact_data: Данные контакта

        Returns:
            str: Хеш контакта
        """
        try:
            key_fields = [
                str(contact_data.get("name", "")),
                str(contact_data.get("phone", "")),
                str(contact_data.get("email", "")),
            ]

            hash_string = "|".join(key_fields)
            return hashlib.sha256(hash_string.encode()).hexdigest()
        except Exception:
            return ""


class SecurityLogger:
    """Логгер для событий безопасности"""

    @staticmethod
    def log_security_event(
        event_type: str, details: str, severity: str = "medium"
    ) -> None:
        """
        Записать событие безопасности в лог

        Args:
            event_type: Тип события
            details: Детали события
            severity: Серьезность (low, medium, high, critical)
        """
        try:
            timestamp = datetime.now().isoformat()
            log_entry = (
                f"[{timestamp}] SECURITY_{severity.upper()}: "
                f"{event_type} - {details}"
            )

            # В реальной системе здесь запись в лог файл
            print(f"🔒 {log_entry}")
        except Exception as e:
            print(f"❌ Ошибка записи в лог безопасности: {e}")

    @staticmethod
    def log_validation_failure(field: str, value: str, reason: str) -> None:
        """
        Записать неудачную валидацию

        Args:
            field: Поле, которое не прошло валидацию
            value: Значение поля
            reason: Причина неудачи
        """
        SecurityLogger.log_security_event(
            "VALIDATION_FAILURE",
            f"Field: {field}, Value: {value[:50]}, Reason: {reason}",
            "medium",
        )

    @staticmethod
    def log_suspicious_activity(activity: str, details: str) -> None:
        """
        Записать подозрительную активность

        Args:
            activity: Тип активности
            details: Детали активности
        """
        SecurityLogger.log_security_event(
            "SUSPICIOUS_ACTIVITY",
            f"Activity: {activity}, Details: {details}",
            "high",
        )


class EmergencySecurityUtils:
    """Основные утилиты безопасности"""

    @staticmethod
    def secure_emergency_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обезопасить данные экстренной ситуации

        Args:
            data: Исходные данные

        Returns:
            Dict: Обезопасенные данные
        """
        try:
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
    def validate_emergency_request(request_data: Dict[str, Any]) -> bool:
        """
        Валидировать запрос экстренной ситуации

        Args:
            request_data: Данные запроса

        Returns:
            bool: True если запрос валиден
        """
        try:
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
