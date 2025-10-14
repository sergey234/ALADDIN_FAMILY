#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Валидаторы для системы экстренного реагирования
Применение Single Responsibility принципа
"""

import re


class PhoneValidator:
    """Валидатор номеров телефонов"""

    def __init__(self):
        """Инициализация валидатора телефонов"""
        pass

    @staticmethod
    def validate(phone: str) -> bool:
        """
        Валидация номера телефона

        Args:
            phone: Номер телефона для проверки

        Returns:
            bool: True если номер валиден
        """
        if not phone:
            return False

        # Удаляем все символы кроме цифр и +
        clean_phone = re.sub(r"[^\d+]", "", phone)

        # Проверяем формат
        if clean_phone.startswith("+"):
            # Международный формат
            return len(clean_phone) >= 10 and len(clean_phone) <= 15
        else:
            # Локальный формат
            return len(clean_phone) >= 7 and len(clean_phone) <= 15


class EmailValidator:
    """Валидатор email адресов"""

    def __init__(self):
        """Инициализация валидатора email"""
        pass

    @staticmethod
    def validate(email: str) -> bool:
        """
        Валидация email адреса

        Args:
            email: Email для проверки

        Returns:
            bool: True если email валиден
        """
        if not email:
            return True  # Email не обязателен

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))


class CoordinateValidator:
    """Валидатор географических координат"""

    def __init__(self):
        """Инициализация валидатора координат"""
        pass

    @staticmethod
    def validate(lat: float, lon: float) -> bool:
        """
        Валидация географических координат

        Args:
            lat: Широта
            lon: Долгота

        Returns:
            bool: True если координаты валидны
        """
        return -90 <= lat <= 90 and -180 <= lon <= 180


class EmergencyTypeValidator:
    """Валидатор типов экстренных ситуаций"""

    VALID_TYPES = {
        "medical",
        "fire",
        "police",
        "security",
        "accident",
        "natural",
        "technical",
        "personal",
    }

    def __init__(self):
        """Инициализация валидатора типов экстренных ситуаций"""
        pass

    @staticmethod
    def validate(emergency_type: str) -> bool:
        """
        Валидация типа экстренной ситуации

        Args:
            emergency_type: Тип для проверки

        Returns:
            bool: True если тип валиден
        """
        return emergency_type in EmergencyTypeValidator.VALID_TYPES


class SeverityValidator:
    """Валидатор уровней серьезности"""

    VALID_SEVERITIES = {"low", "medium", "high", "critical", "life"}

    def __init__(self):
        """Инициализация валидатора уровней серьезности"""
        pass

    @staticmethod
    def validate(severity: str) -> bool:
        """
        Валидация уровня серьезности

        Args:
            severity: Уровень для проверки

        Returns:
            bool: True если уровень валиден
        """
        return severity in SeverityValidator.VALID_SEVERITIES


class DescriptionValidator:
    """Валидатор описаний экстренных ситуаций"""

    MIN_LENGTH = 10
    SPAM_INDICATORS = {"test", "тест", "spam", "спам"}

    def __init__(self):
        """Инициализация валидатора описаний"""
        pass

    @staticmethod
    def validate(description: str) -> bool:
        """
        Валидация описания экстренной ситуации

        Args:
            description: Описание для проверки

        Returns:
            bool: True если описание валидно
        """
        if not description:
            return False

        # Проверяем длину
        if len(description) < DescriptionValidator.MIN_LENGTH:
            return False

        # Проверяем на спам
        description_lower = description.lower()
        if any(
            indicator in description_lower
            for indicator in DescriptionValidator.SPAM_INDICATORS
        ):
            return False

        return True
