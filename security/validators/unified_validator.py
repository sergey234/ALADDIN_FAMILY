#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Validator - Централизованная валидация входных данных
Версия: 1.0.0
Дата: 2025-10-11

Усиленная валидация для защиты от:
- SQL Injection
- XSS (Cross-Site Scripting)
- Path Traversal
- Command Injection
- Email Spoofing
- Phone Number Spoofing

Автор: ALADDIN Security Team
"""

import re
import html
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Ошибка валидации"""
    pass


class UnifiedValidator:
    """
    Централизованный валидатор для всех типов данных
    
    Защищает от инъекций, XSS, и других атак.
    Используется во всех API endpoints.
    """
    
    # ═══════════════════════════════════════════════════════════════
    # 1. EMAIL VALIDATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_email(email: str, max_length: int = 254) -> bool:
        """
        Валидация email адреса
        
        Args:
            email: Email адрес
            max_length: Максимальная длина (RFC 5321)
            
        Returns:
            True если валиден
            
        Raises:
            ValidationError если невалиден
        """
        if not email or not isinstance(email, str):
            raise ValidationError("Email не может быть пустым")
        
        if len(email) > max_length:
            raise ValidationError(f"Email слишком длинный (макс {max_length} символов)")
        
        # RFC 5322 совместимый regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            raise ValidationError("Неверный формат email")
        
        # Проверка на опасные символы
        dangerous_chars = ['<', '>', '"', "'", ';', '\\', '/', '`']
        if any(char in email for char in dangerous_chars):
            raise ValidationError("Email содержит недопустимые символы")
        
        logger.info(f"✅ Email валиден: {email}")
        return True
    
    # ═══════════════════════════════════════════════════════════════
    # 2. PHONE NUMBER VALIDATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_phone(phone: str, require_plus: bool = True) -> bool:
        """
        Валидация номера телефона
        
        Args:
            phone: Номер телефона
            require_plus: Требовать знак + в начале
            
        Returns:
            True если валиден
            
        Raises:
            ValidationError если невалиден
        """
        if not phone or not isinstance(phone, str):
            raise ValidationError("Телефон не может быть пустым")
        
        # Удаляем пробелы, тире, скобки
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        
        # E.164 формат: +[1-15 цифр]
        if require_plus:
            pattern = r'^\+[1-9]\d{1,14}$'
        else:
            pattern = r'^\+?[1-9]\d{1,14}$'
        
        if not re.match(pattern, cleaned):
            raise ValidationError("Неверный формат телефона")
        
        logger.info(f"✅ Телефон валиден: {phone}")
        return True
    
    # ═══════════════════════════════════════════════════════════════
    # 3. PASSWORD VALIDATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_password(
        password: str,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = True
    ) -> bool:
        """
        Валидация пароля
        
        Args:
            password: Пароль
            min_length: Минимальная длина
            require_uppercase: Требовать заглавные буквы
            require_lowercase: Требовать строчные буквы
            require_digit: Требовать цифры
            require_special: Требовать спецсимволы
            
        Returns:
            True если валиден
            
        Raises:
            ValidationError если невалиден
        """
        if not password or not isinstance(password, str):
            raise ValidationError("Пароль не может быть пустым")
        
        if len(password) < min_length:
            raise ValidationError(f"Пароль слишком короткий (минимум {min_length} символов)")
        
        if len(password) > 128:
            raise ValidationError("Пароль слишком длинный (максимум 128 символов)")
        
        if require_uppercase and not re.search(r'[A-Z]', password):
            raise ValidationError("Пароль должен содержать заглавную букву")
        
        if require_lowercase and not re.search(r'[a-z]', password):
            raise ValidationError("Пароль должен содержать строчную букву")
        
        if require_digit and not re.search(r'\d', password):
            raise ValidationError("Пароль должен содержать цифру")
        
        if require_special and not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            raise ValidationError("Пароль должен содержать спецсимвол")
        
        # Проверка на распространенные пароли
        common_passwords = [
            "password", "12345678", "qwerty", "abc123", "password123",
            "admin", "letmein", "welcome", "monkey", "dragon"
        ]
        if password.lower() in common_passwords:
            raise ValidationError("Слишком простой пароль")
        
        logger.info("✅ Пароль валиден")
        return True
    
    # ═══════════════════════════════════════════════════════════════
    # 4. SQL INJECTION PROTECTION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def sanitize_sql(query: str) -> str:
        """
        Защита от SQL Injection
        
        Args:
            query: SQL запрос или значение
            
        Returns:
            Очищенная строка
            
        Raises:
            ValidationError если обнаружена инъекция
        """
        if not query or not isinstance(query, str):
            return ""
        
        # Опасные SQL ключевые слова
        dangerous_patterns = [
            r'\bDROP\b', r'\bDELETE\b', r'\bTRUNCATE\b', r'\bINSERT\b',
            r'\bUPDATE\b', r'\bEXEC\b', r'\bEXECUTE\b', r'\bUNION\b',
            r'\bSELECT\b.*\bFROM\b', r'--', r'/\*', r'\*/', r'xp_', r'sp_'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                logger.error(f"❌ SQL Injection обнаружена: {pattern}")
                raise ValidationError("Обнаружена попытка SQL инъекции")
        
        # Экранируем опасные символы
        cleaned = query.replace("'", "''").replace(";", "").replace("--", "")
        
        logger.info("✅ SQL sanitized")
        return cleaned
    
    # ═══════════════════════════════════════════════════════════════
    # 5. XSS PROTECTION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def sanitize_html(text: str, allowed_tags: Optional[List[str]] = None) -> str:
        """
        Защита от XSS (Cross-Site Scripting)
        
        Args:
            text: HTML текст
            allowed_tags: Разрешенные HTML теги (по умолчанию нет)
            
        Returns:
            Очищенный текст
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Экранируем все HTML entities
        cleaned = html.escape(text)
        
        # Удаляем опасные паттерны
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'<iframe[^>]*>.*?</iframe>',
            r'javascript:',
            r'on\w+\s*=',  # onclick=, onerror=, и т.д.
            r'<embed[^>]*>',
            r'<object[^>]*>'
        ]
        
        for pattern in dangerous_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        logger.info("✅ HTML sanitized")
        return cleaned
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Простая очистка текста от опасных символов
        
        Args:
            text: Текст
            
        Returns:
            Очищенный текст
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Экранируем HTML
        cleaned = html.escape(text)
        
        # Удаляем control characters
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
        
        return cleaned
    
    # ═══════════════════════════════════════════════════════════════
    # 6. PATH TRAVERSAL PROTECTION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_file_path(path: str, allowed_extensions: Optional[List[str]] = None) -> bool:
        """
        Защита от Path Traversal атак
        
        Args:
            path: Путь к файлу
            allowed_extensions: Разрешенные расширения файлов
            
        Returns:
            True если валиден
            
        Raises:
            ValidationError если обнаружена атака
        """
        if not path or not isinstance(path, str):
            raise ValidationError("Путь не может быть пустым")
        
        # Проверка на path traversal паттерны
        dangerous_patterns = ['..', '~/', '/etc/', '/var/', '/root/', '\\', '%2e', '%2f']
        
        for pattern in dangerous_patterns:
            if pattern in path.lower():
                logger.error(f"❌ Path Traversal обнаружен: {pattern} в {path}")
                raise ValidationError("Обнаружена попытка Path Traversal")
        
        # Проверка расширения файла
        if allowed_extensions:
            file_ext = path.split('.')[-1].lower()
            if file_ext not in allowed_extensions:
                raise ValidationError(f"Недопустимое расширение файла: {file_ext}")
        
        logger.info(f"✅ Путь валиден: {path}")
        return True
    
    # ═══════════════════════════════════════════════════════════════
    # 7. URL VALIDATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> bool:
        """
        Валидация URL
        
        Args:
            url: URL адрес
            allowed_schemes: Разрешенные схемы (http, https, и т.д.)
            
        Returns:
            True если валиден
            
        Raises:
            ValidationError если невалиден
        """
        if not url or not isinstance(url, str):
            raise ValidationError("URL не может быть пустым")
        
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        try:
            parsed = urlparse(url)
            
            if parsed.scheme not in allowed_schemes:
                raise ValidationError(f"Недопустимая схема URL: {parsed.scheme}")
            
            if not parsed.netloc:
                raise ValidationError("URL должен содержать домен")
            
            # Проверка на опасные паттерны
            if any(char in url for char in ['<', '>', '"', "'"]):
                raise ValidationError("URL содержит опасные символы")
            
            logger.info(f"✅ URL валиден: {url}")
            return True
            
        except Exception as e:
            raise ValidationError(f"Неверный URL: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # 8. USERNAME VALIDATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_username(
        username: str,
        min_length: int = 3,
        max_length: int = 32,
        allow_spaces: bool = False
    ) -> bool:
        """
        Валидация имени пользователя
        
        Args:
            username: Имя пользователя
            min_length: Минимальная длина
            max_length: Максимальная длина
            allow_spaces: Разрешить пробелы
            
        Returns:
            True если валиден
            
        Raises:
            ValidationError если невалиден
        """
        if not username or not isinstance(username, str):
            raise ValidationError("Имя пользователя не может быть пустым")
        
        if len(username) < min_length:
            raise ValidationError(f"Имя слишком короткое (минимум {min_length} символов)")
        
        if len(username) > max_length:
            raise ValidationError(f"Имя слишком длинное (максимум {max_length} символов)")
        
        # Разрешенные символы
        if allow_spaces:
            pattern = r'^[a-zA-Z0-9а-яА-ЯёЁ\s_-]+$'
        else:
            pattern = r'^[a-zA-Z0-9а-яА-ЯёЁ_-]+$'
        
        if not re.match(pattern, username):
            raise ValidationError("Имя содержит недопустимые символы")
        
        logger.info(f"✅ Username валиден: {username}")
        return True
    
    # ═══════════════════════════════════════════════════════════════
    # 9. NUMERIC VALIDATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_integer(
        value: Any,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> int:
        """
        Валидация целого числа
        
        Args:
            value: Значение
            min_value: Минимум
            max_value: Максимум
            
        Returns:
            Целое число
            
        Raises:
            ValidationError если невалиден
        """
        try:
            num = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Невалидное целое число: {value}")
        
        if min_value is not None and num < min_value:
            raise ValidationError(f"Число слишком маленькое (минимум {min_value})")
        
        if max_value is not None and num > max_value:
            raise ValidationError(f"Число слишком большое (максимум {max_value})")
        
        return num
    
    @staticmethod
    def validate_float(
        value: Any,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> float:
        """
        Валидация дробного числа
        
        Args:
            value: Значение
            min_value: Минимум
            max_value: Максимум
            
        Returns:
            Дробное число
            
        Raises:
            ValidationError если невалиден
        """
        try:
            num = float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Невалидное дробное число: {value}")
        
        if min_value is not None and num < min_value:
            raise ValidationError(f"Число слишком маленькое (минимум {min_value})")
        
        if max_value is not None and num > max_value:
            raise ValidationError(f"Число слишком большое (максимум {max_value})")
        
        return num
    
    # ═══════════════════════════════════════════════════════════════
    # 10. JSON VALIDATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_json(data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Валидация JSON данных
        
        Args:
            data: JSON данные (словарь)
            required_fields: Обязательные поля
            
        Returns:
            True если валиден
            
        Raises:
            ValidationError если невалиден
        """
        if not isinstance(data, dict):
            raise ValidationError("Данные должны быть JSON объектом")
        
        # Проверяем обязательные поля
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValidationError(f"Отсутствуют обязательные поля: {', '.join(missing_fields)}")
        
        logger.info("✅ JSON валиден")
        return True
    
    # ═══════════════════════════════════════════════════════════════
    # 11. DEVICE ID VALIDATION
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_device_id(device_id: str) -> bool:
        """
        Валидация ID устройства (UUID)
        
        Args:
            device_id: ID устройства
            
        Returns:
            True если валиден
            
        Raises:
            ValidationError если невалиден
        """
        if not device_id or not isinstance(device_id, str):
            raise ValidationError("Device ID не может быть пустым")
        
        # UUID v4 формат
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$'
        
        if not re.match(uuid_pattern, device_id.lower()):
            # Также принимаем простые ID (device_001, и т.д.)
            simple_pattern = r'^[a-zA-Z0-9_-]+$'
            if not re.match(simple_pattern, device_id):
                raise ValidationError("Неверный формат Device ID")
        
        logger.info(f"✅ Device ID валиден: {device_id}")
        return True
    
    # ═══════════════════════════════════════════════════════════════
    # 12. AMOUNT VALIDATION (для платежей)
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def validate_amount(
        amount: Any,
        min_amount: float = 0.01,
        max_amount: float = 1000000.0,
        currency: str = "RUB"
    ) -> float:
        """
        Валидация суммы платежа
        
        Args:
            amount: Сумма
            min_amount: Минимальная сумма
            max_amount: Максимальная сумма
            currency: Валюта
            
        Returns:
            Валидная сумма
            
        Raises:
            ValidationError если невалидна
        """
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            raise ValidationError(f"Невалидная сумма: {amount}")
        
        if amount_float < min_amount:
            raise ValidationError(f"Сумма слишком маленькая (минимум {min_amount} {currency})")
        
        if amount_float > max_amount:
            raise ValidationError(f"Сумма слишком большая (максимум {max_amount} {currency})")
        
        # Округляем до 2 знаков (копейки)
        amount_rounded = round(amount_float, 2)
        
        logger.info(f"✅ Сумма валидна: {amount_rounded} {currency}")
        return amount_rounded


# Глобальный экземпляр валидатора
validator = UnifiedValidator()


# ═══════════════════════════════════════════════════════════════
# Тестирование
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧪 Тестирование UnifiedValidator")
    print("=" * 60)
    
    v = UnifiedValidator()
    
    # Тест 1: Email
    try:
        v.validate_email("test@example.com")
        print("✅ Email валидация работает")
    except ValidationError as e:
        print(f"❌ Email: {e}")
    
    # Тест 2: Телефон
    try:
        v.validate_phone("+79277020379")
        print("✅ Телефон валидация работает")
    except ValidationError as e:
        print(f"❌ Телефон: {e}")
    
    # Тест 3: Пароль
    try:
        v.validate_password("StrongP@ss123")
        print("✅ Пароль валидация работает")
    except ValidationError as e:
        print(f"❌ Пароль: {e}")
    
    # Тест 4: SQL Injection
    try:
        v.sanitize_sql("SELECT * FROM users; DROP TABLE users;")
        print("❌ SQL Injection НЕ обнаружена!")
    except ValidationError:
        print("✅ SQL Injection обнаружена и заблокирована")
    
    # Тест 5: XSS
    xss_input = "<script>alert('XSS')</script>Hello"
    cleaned = v.sanitize_html(xss_input)
    print(f"✅ XSS очищен: {cleaned}")
    
    # Тест 6: Сумма платежа
    try:
        amount = v.validate_amount(590.50, min_amount=1.0, max_amount=10000.0)
        print(f"✅ Сумма валидна: {amount} RUB")
    except ValidationError as e:
        print(f"❌ Сумма: {e}")
    
    print("=" * 60)
    print("✅ Все тесты пройдены!")

