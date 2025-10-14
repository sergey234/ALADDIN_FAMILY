#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор уникальных ID для системы экстренного реагирования
Применение Single Responsibility принципа
"""

import time
import uuid
from datetime import datetime
from typing import Optional


class EmergencyIDGenerator:
    """Генератор уникальных ID для экстренных событий"""

    @staticmethod
    def create_event_id() -> str:
        """
        Создать уникальный ID события

        Returns:
            str: Уникальный ID события
        """
        timestamp = int(time.time() * 1000)
        return f"emerg_{timestamp}"

    @staticmethod
    def create_response_id() -> str:
        """
        Создать уникальный ID ответа

        Returns:
            str: Уникальный ID ответа
        """
        timestamp = int(time.time() * 1000)
        return f"resp_{timestamp}"

    @staticmethod
    def create_location_id() -> str:
        """
        Создать уникальный ID местоположения

        Returns:
            str: Уникальный ID местоположения
        """
        timestamp = int(time.time() * 1000)
        return f"loc_{timestamp}"

    @staticmethod
    def create_contact_id() -> str:
        """
        Создать уникальный ID контакта

        Returns:
            str: Уникальный ID контакта
        """
        timestamp = int(time.time() * 1000)
        return f"contact_{timestamp}"

    @staticmethod
    def create_uuid() -> str:
        """
        Создать UUID

        Returns:
            str: UUID строка
        """
        return str(uuid.uuid4())

    @staticmethod
    def create_timestamped_id(prefix: str) -> str:
        """
        Создать ID с временной меткой

        Args:
            prefix: Префикс для ID

        Returns:
            str: ID с временной меткой
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        return f"{prefix}_{timestamp}"

    @staticmethod
    def create_short_id(length: int = 8) -> str:
        """
        Создать короткий ID

        Args:
            length: Длина ID

        Returns:
            str: Короткий ID
        """
        import random
        import string

        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))

    @staticmethod
    def validate_id_format(id_string: str, expected_prefix: str) -> bool:
        """
        Проверить формат ID

        Args:
            id_string: ID для проверки
            expected_prefix: Ожидаемый префикс

        Returns:
            bool: True если формат корректный
        """
        if not id_string:
            return False

        return id_string.startswith(expected_prefix)

    @staticmethod
    def extract_timestamp_from_id(id_string: str) -> Optional[datetime]:
        """
        Извлечь временную метку из ID

        Args:
            id_string: ID для анализа

        Returns:
            Optional[datetime]: Временная метка или None
        """
        try:
            # Ищем числовую часть после префикса
            parts = id_string.split("_")
            if len(parts) >= 2:
                timestamp_str = parts[-1]
                if timestamp_str.isdigit():
                    timestamp = int(timestamp_str)
                    return datetime.fromtimestamp(timestamp / 1000)
        except Exception:
            pass

        return None
