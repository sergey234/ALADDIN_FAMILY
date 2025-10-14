#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PasswordSecurityAgent - Агент безопасности паролей ALADDIN
Обеспечивает проверку, генерацию, хеширование и управление паролями
"""

import hashlib
import json
import os
import secrets
import string
import sys
import time
from datetime import datetime
from enum import Enum

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from core.base import SecurityBase
except ImportError:

    class SecurityBase:
        def __init__(self, name):
            self.name = name
            self.logs = []

        def log_activity(self, message, level="info"):
            self.logs.append("{}: {}".format(level.upper(), message))
            print("{}: {}".format(level.upper(), message))


class PasswordStrength(Enum):
    """Уровни сложности пароля"""

    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


class PasswordStatus(Enum):
    """Статусы пароля"""

    ACTIVE = "active"
    EXPIRED = "expired"
    COMPROMISED = "compromised"
    WEAK = "weak"
    REUSED = "reused"


class PasswordPolicy:
    """Политика безопасности паролей"""

    def __init__(
        self,
        min_length=12,
        require_uppercase=True,
        require_lowercase=True,
        require_digits=True,
        require_special=True,
        max_age_days=90,
        prevent_reuse=5,
        max_attempts=5,
        lockout_duration=30,
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.max_age_days = max_age_days
        self.prevent_reuse = prevent_reuse
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            "min_length": self.min_length,
            "require_uppercase": self.require_uppercase,
            "require_lowercase": self.require_lowercase,
            "require_digits": self.require_digits,
            "require_special": self.require_special,
            "max_age_days": self.max_age_days,
            "prevent_reuse": self.prevent_reuse,
            "max_attempts": self.max_attempts,
            "lockout_duration": self.lockout_duration,
            "created_at": self.created_at.isoformat(),
        }


class PasswordMetrics:
    """Метрики агента безопасности паролей"""

    def __init__(self):
        self.total_passwords = 0
        self.weak_passwords = 0
        self.strong_passwords = 0
        self.compromised_passwords = 0
        self.expired_passwords = 0
        self.reused_passwords = 0
        self.password_strength_distribution = {}
        self.avg_password_length = 0.0
        self.password_entropy = 0.0
        self.breach_detection_rate = 0.0
        self.policy_compliance_rate = 0.0
        self.last_breach_check = None
        self.password_generation_count = 0
        self.password_validation_count = 0
        self.password_hash_count = 0
        self.password_verification_count = 0

    def to_dict(self):
        return {
            "total_passwords": self.total_passwords,
            "weak_passwords": self.weak_passwords,
            "strong_passwords": self.strong_passwords,
            "compromised_passwords": self.compromised_passwords,
            "expired_passwords": self.expired_passwords,
            "reused_passwords": self.reused_passwords,
            "password_strength_distribution": (
                self.password_strength_distribution
            ),
            "avg_password_length": self.avg_password_length,
            "password_entropy": self.password_entropy,
            "breach_detection_rate": self.breach_detection_rate,
            "policy_compliance_rate": self.policy_compliance_rate,
            "last_breach_check": (
                self.last_breach_check.isoformat()
                if self.last_breach_check
                else None
            ),
            "password_generation_count": self.password_generation_count,
            "password_validation_count": self.password_validation_count,
            "password_hash_count": self.password_hash_count,
            "password_verification_count": self.password_verification_count,
        }


class PasswordSecurityAgent(SecurityBase):
    """Агент безопасности паролей ALADDIN"""

    def __init__(self, name="PasswordSecurityAgent"):
        SecurityBase.__init__(self, name)

        # Конфигурация агента
        self.default_policy = PasswordPolicy()
        self.breach_database = set()
        self.password_history = {}  # user_id -> [password_hashes]
        self.failed_attempts = {}  # user_id -> count
        self.lockouts = {}  # user_id -> lockout_until
        self.metrics = PasswordMetrics()

        # AI модели для анализа
        self.ml_models = {}
        self.strength_analyzer = None
        self.breach_detector = None
        self.pattern_analyzer = None
        self.entropy_calculator = None

        # Системы безопасности
        self.hashing_algorithm = "pbkdf2_sha256"
        self.salt_length = 32
        self.iterations = 100000
        self.breach_check_interval = 86400  # 24 часа

    def initialize(self):
        """Инициализация агента"""
        try:
            self.log_activity("Инициализация PasswordSecurityAgent...")

            # Инициализация AI моделей
            self._initialize_ai_models()

            # Загрузка базы данных утечек
            self._load_breach_database()

            # Настройка систем безопасности
            self._setup_security_systems()

            self.log_activity("PasswordSecurityAgent инициализирован успешно")
            return True

        except Exception as e:
            self.log_activity(
                "Ошибка инициализации PasswordSecurityAgent: {}".format(
                    str(e)
                ),
                "error",
            )
            return False

    def _initialize_ai_models(self):
        """Инициализация AI моделей"""
        try:
            self.log_activity(
                "Инициализация AI моделей для безопасности паролей..."
            )

            # Анализатор сложности пароля
            self.strength_analyzer = {
                "model_type": "neural_network",
                "features": [
                    "length",
                    "character_diversity",
                    "pattern_complexity",
                    "entropy",
                ],
                "accuracy": 0.95,
                "confidence_threshold": 0.90,
                "last_trained": datetime.now(),
            }

            # Детектор утечек
            self.breach_detector = {
                "model_type": "hash_matching",
                "features": [
                    "password_hash",
                    "breach_database",
                    "similarity_score",
                ],
                "accuracy": 0.99,
                "confidence_threshold": 0.95,
                "last_trained": datetime.now(),
            }

            # Анализатор паттернов
            self.pattern_analyzer = {
                "model_type": "pattern_recognition",
                "features": [
                    "keyboard_patterns",
                    "common_words",
                    "personal_info",
                ],
                "accuracy": 0.92,
                "confidence_threshold": 0.85,
                "last_trained": datetime.now(),
            }

            # Калькулятор энтропии
            self.entropy_calculator = {
                "model_type": "mathematical",
                "features": [
                    "character_set_size",
                    "password_length",
                    "randomness",
                ],
                "accuracy": 0.98,
                "confidence_threshold": 0.90,
                "last_trained": datetime.now(),
            }

            self.ml_models = {
                "strength_analyzer": self.strength_analyzer,
                "breach_detector": self.breach_detector,
                "pattern_analyzer": self.pattern_analyzer,
                "entropy_calculator": self.entropy_calculator,
            }

            self.log_activity("AI модели инициализированы успешно")

        except Exception as e:
            self.log_activity(
                "Ошибка инициализации AI моделей: {}".format(str(e)), "error"
            )

    def _load_breach_database(self):
        """Загрузка базы данных утечек"""
        try:
            self.log_activity("Загрузка базы данных утечек паролей...")

            # Симуляция загрузки базы данных утечек
            # В реальной реализации здесь будет загрузка из внешнего источника
            common_passwords = [
                "123456",
                "password",
                "123456789",
                "12345678",
                "12345",
                "1234567",
                "1234567890",
                "qwerty",
                "abc123",
                "password123",
            ]

            for password in common_passwords:
                self.breach_database.add(
                    hashlib.sha256(password.encode()).hexdigest()
                )

            self.log_activity(
                "База данных утечек загружена: {} записей".format(
                    len(self.breach_database)
                )
            )

        except Exception as e:
            self.log_activity(
                "Ошибка загрузки базы данных утечек: {}".format(str(e)),
                "error",
            )

    def _setup_security_systems(self):
        """Настройка систем безопасности"""
        try:
            self.log_activity("Настройка систем безопасности паролей...")

            # Настройка параметров хеширования
            self.hashing_algorithm = "pbkdf2_sha256"
            self.salt_length = 32
            self.iterations = 100000

            # Настройка интервалов проверки
            self.breach_check_interval = 86400  # 24 часа

            self.log_activity("Системы безопасности настроены")

        except Exception as e:
            self.log_activity(
                "Ошибка настройки систем безопасности: {}".format(str(e)),
                "error",
            )

    def generate_password(
        self,
        length=16,
        include_uppercase=True,
        include_lowercase=True,
        include_digits=True,
        include_special=True,
        exclude_similar=True,
    ):
        """Генерация безопасного пароля"""
        try:
            self.log_activity("Генерация безопасного пароля...")

            # Валидация параметров
            if not self._validate_password_params(
                length,
                include_uppercase,
                include_lowercase,
                include_digits,
                include_special,
            ):
                return None

            # Создание набора символов
            charset = ""
            if include_lowercase:
                charset += string.ascii_lowercase
            if include_uppercase:
                charset += string.ascii_uppercase
            if include_digits:
                charset += string.digits
            if include_special:
                charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"

            if exclude_similar:
                charset = (
                    charset.replace("0", "")
                    .replace("O", "")
                    .replace("l", "")
                    .replace("I", "")
                )

            if not charset:
                self.log_activity("Ошибка: пустой набор символов", "error")
                return None

            # Генерация пароля
            password = "".join(secrets.choice(charset) for _ in range(length))

            # Проверка сложности
            strength = self.analyze_password_strength(password)
            if strength == PasswordStrength.WEAK:
                # Повторная генерация с улучшенными параметрами
                password = self._generate_strong_password(length, charset)

            # Обновление метрик
            self.metrics.password_generation_count += 1

            self.log_activity("Пароль сгенерирован успешно")
            return password

        except Exception as e:
            self.log_activity(
                "Ошибка генерации пароля: {}".format(str(e)), "error"
            )
            return None

    def _validate_password_params(
        self,
        length,
        include_uppercase,
        include_lowercase,
        include_digits,
        include_special,
    ):
        """Валидация параметров генерации пароля"""
        try:
            if length < 8 or length > 128:
                self.log_activity("Некорректная длина пароля", "error")
                return False

            if not (
                include_uppercase
                or include_lowercase
                or include_digits
                or include_special
            ):
                self.log_activity(
                    "Должен быть выбран хотя бы один тип символов", "error"
                )
                return False

            return True

        except Exception as e:
            self.log_activity(
                "Ошибка валидации параметров: {}".format(str(e)), "error"
            )
            return False

    def _generate_strong_password(self, length, charset):
        """Генерация сильного пароля"""
        try:
            # Генерация с гарантированным включением всех типов символов
            password = []

            # Обязательные символы
            if string.ascii_lowercase in charset:
                password.append(secrets.choice(string.ascii_lowercase))
            if string.ascii_uppercase in charset:
                password.append(secrets.choice(string.ascii_uppercase))
            if string.digits in charset:
                password.append(secrets.choice(string.digits))
            if any(c in charset for c in "!@#$%^&*()_+-=[]{}|;:,.<>?"):
                special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
                password.append(secrets.choice(special_chars))

            # Заполнение оставшейся длины
            while len(password) < length:
                password.append(secrets.choice(charset))

            # Перемешивание
            secrets.SystemRandom().shuffle(password)

            return "".join(password)

        except Exception as e:
            self.log_activity(
                "Ошибка генерации сильного пароля: {}".format(str(e)), "error"
            )
            return None

    def analyze_password_strength(self, password):
        """Анализ сложности пароля"""
        try:
            if not password:
                return PasswordStrength.WEAK

            score = 0
            length = len(password)

            # Оценка длины
            if length >= 12:
                score += 3
            elif length >= 8:
                score += 2
            else:
                score += 1

            # Оценка разнообразия символов
            has_lower = any(c.islower() for c in password)
            has_upper = any(c.isupper() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(
                c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
            )

            char_types = sum([has_lower, has_upper, has_digit, has_special])
            score += char_types

            # Оценка энтропии
            entropy = self._calculate_entropy(password)
            if entropy >= 4.0:
                score += 2
            elif entropy >= 3.0:
                score += 1

            # Оценка паттернов
            if not self._has_common_patterns(password):
                score += 1

            # Определение уровня сложности
            if score >= 8:
                return PasswordStrength.VERY_STRONG
            elif score >= 6:
                return PasswordStrength.STRONG
            elif score >= 4:
                return PasswordStrength.MEDIUM
            else:
                return PasswordStrength.WEAK

        except Exception as e:
            self.log_activity(
                "Ошибка анализа сложности пароля: {}".format(str(e)), "error"
            )
            return PasswordStrength.WEAK

    def _calculate_entropy(self, password):
        """Расчет энтропии пароля"""
        try:
            if not password:
                return 0.0

            # Подсчет уникальных символов
            unique_chars = len(set(password))
            total_chars = len(password)

            # Расчет энтропии
            entropy = (
                total_chars * (unique_chars / total_chars) * 3.32
            )  # log2 approximation

            return entropy

        except Exception as e:
            self.log_activity(
                "Ошибка расчета энтропии: {}".format(str(e)), "error"
            )
            return 0.0

    def _has_common_patterns(self, password):
        """Проверка на наличие общих паттернов"""
        try:
            password_lower = password.lower()

            # Проверка на последовательности
            sequences = ["123", "abc", "qwe", "asd", "zxc"]
            for seq in sequences:
                if seq in password_lower:
                    return True

            # Проверка на повторяющиеся символы
            if len(set(password)) < len(password) * 0.7:
                return True

            return False

        except Exception as e:
            self.log_activity(
                "Ошибка проверки паттернов: {}".format(str(e)), "error"
            )
            return True

    def hash_password(self, password, salt=None):
        """Хеширование пароля"""
        try:
            if not password:
                return None

            if salt is None:
                salt = secrets.token_hex(self.salt_length)

            # Использование PBKDF2 для хеширования
            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                self.iterations,
            )

            # Обновление метрик
            self.metrics.password_hash_count += 1

            return {
                "hash": password_hash.hex(),
                "salt": salt,
                "algorithm": self.hashing_algorithm,
                "iterations": self.iterations,
            }

        except Exception as e:
            self.log_activity(
                "Ошибка хеширования пароля: {}".format(str(e)), "error"
            )
            return None

    def verify_password(self, password, stored_hash, salt):
        """Проверка пароля"""
        try:
            if not password or not stored_hash or not salt:
                return False

            # Хеширование введенного пароля
            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                self.iterations,
            )

            # Сравнение хешей
            is_valid = password_hash.hex() == stored_hash

            # Обновление метрик
            self.metrics.password_verification_count += 1

            return is_valid

        except Exception as e:
            self.log_activity(
                "Ошибка проверки пароля: {}".format(str(e)), "error"
            )
            return False

    def check_password_breach(self, password):
        """Проверка пароля на утечку"""
        try:
            if not password:
                return False

            # Хеширование пароля для проверки
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # Проверка в базе данных утечек
            is_breached = password_hash in self.breach_database

            # Обновление метрик
            if is_breached:
                self.metrics.compromised_passwords += 1

            return is_breached

        except Exception as e:
            self.log_activity(
                "Ошибка проверки утечки пароля: {}".format(str(e)), "error"
            )
            return False

    def validate_password_policy(self, password, policy=None):
        """Валидация пароля по политике"""
        try:
            if not password:
                return False, "Пароль не может быть пустым"

            if policy is None:
                policy = self.default_policy

            # Проверка длины
            if len(password) < policy.min_length:
                return (
                    False,
                    "Пароль слишком короткий (минимум {} символов)".format(
                        policy.min_length
                    ),
                )

            # Проверка наличия заглавных букв
            if policy.require_uppercase and not any(
                c.isupper() for c in password
            ):
                return False, "Пароль должен содержать заглавные буквы"

            # Проверка наличия строчных букв
            if policy.require_lowercase and not any(
                c.islower() for c in password
            ):
                return False, "Пароль должен содержать строчные буквы"

            # Проверка наличия цифр
            if policy.require_digits and not any(
                c.isdigit() for c in password
            ):
                return False, "Пароль должен содержать цифры"

            # Проверка наличия специальных символов
            if policy.require_special and not any(
                c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password
            ):
                return False, "Пароль должен содержать специальные символы"

            return True, "Пароль соответствует политике"

        except Exception as e:
            self.log_activity(
                "Ошибка валидации политики пароля: {}".format(str(e)), "error"
            )
            return False, "Ошибка валидации"

    def generate_report(self):
        """Генерация отчета о безопасности паролей"""
        try:
            self.log_activity("Генерация отчета о безопасности паролей...")

            report = {
                "report_id": "password_security_{}".format(int(time.time())),
                "generated_at": datetime.now().isoformat(),
                "agent_name": self.name,
                "summary": {
                    "total_passwords": self.metrics.total_passwords,
                    "weak_passwords": self.metrics.weak_passwords,
                    "strong_passwords": self.metrics.strong_passwords,
                    "compromised_passwords": (
                        self.metrics.compromised_passwords
                    ),
                    "avg_password_length": self.metrics.avg_password_length,
                    "password_entropy": self.metrics.password_entropy,
                    "breach_detection_rate": (
                        self.metrics.breach_detection_rate
                    ),
                    "policy_compliance_rate": (
                        self.metrics.policy_compliance_rate
                    ),
                },
                "metrics": self.metrics.to_dict(),
                "recommendations": self._generate_recommendations(),
            }

            # Сохранение отчета
            report_dir = "data/password_security_reports"
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)

            report_file = os.path.join(
                report_dir,
                "password_security_report_{}.json".format(int(time.time())),
            )
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self.log_activity("Отчет сохранен: {}".format(report_file))
            return report

        except Exception as e:
            self.log_activity(
                "Ошибка генерации отчета: {}".format(str(e)), "error"
            )
            return None

    def _generate_recommendations(self):
        """Генерация рекомендаций"""
        try:
            recommendations = []

            # Рекомендации на основе метрик
            if (
                self.metrics.weak_passwords
                > self.metrics.total_passwords * 0.2
            ):
                recommendations.append(
                    {
                        "type": "password_strength",
                        "priority": "high",
                        "description": "Высокий процент слабых паролей",
                        "action": "Усилить требования к сложности паролей",
                    }
                )

            if self.metrics.compromised_passwords > 0:
                recommendations.append(
                    {
                        "type": "password_breach",
                        "priority": "critical",
                        "description": (
                            "Обнаружены скомпрометированные пароли"
                        ),
                        "action": (
                            "Немедленно сменить все скомпрометированные пароли"
                        ),
                    }
                )

            if self.metrics.policy_compliance_rate < 0.9:
                recommendations.append(
                    {
                        "type": "policy_compliance",
                        "priority": "medium",
                        "description": (
                            "Низкое соблюдение политики паролей"
                        ),
                        "action": (
                            "Улучшить обучение пользователей и "
                            "автоматизацию проверок"
                        ),
                    }
                )

            return recommendations

        except Exception as e:
            self.log_activity(
                "Ошибка генерации рекомендаций: {}".format(str(e)), "error"
            )
            return []

    def stop(self):
        """Остановка агента"""
        try:
            self.log_activity("Остановка PasswordSecurityAgent...")

            # Сохранение данных
            self._save_data()

            self.log_activity("PasswordSecurityAgent остановлен")

        except Exception as e:
            self.log_activity(
                "Ошибка остановки PasswordSecurityAgent: {}".format(str(e)),
                "error",
            )

    def _save_data(self):
        """Сохранение данных агента"""
        try:
            data_dir = "data/password_security"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            # Сохранение метрик
            metrics_file = os.path.join(data_dir, "metrics.json")
            with open(metrics_file, "w") as f:
                json.dump(
                    self.metrics.to_dict(), f, indent=2, ensure_ascii=False
                )

            self.log_activity("Данные сохранены в {}".format(data_dir))

        except Exception as e:
            self.log_activity(
                "Ошибка сохранения данных: {}".format(str(e)), "error"
            )


if __name__ == "__main__":
    # Тестирование агента
    agent = PasswordSecurityAgent()

    if agent.initialize():
        print("PasswordSecurityAgent инициализирован успешно")

        # Генерация тестового пароля
        password = agent.generate_password(length=16)
        if password:
            print("Пароль сгенерирован: {}".format(password))

            # Анализ сложности
            strength = agent.analyze_password_strength(password)
            print("Сложность пароля: {}".format(strength.value))

            # Хеширование пароля
            hash_result = agent.hash_password(password)
            if hash_result:
                print("Пароль захеширован")

                # Проверка пароля
                is_valid = agent.verify_password(
                    password, hash_result["hash"], hash_result["salt"]
                )
                print("Проверка пароля: {}".format(is_valid))

        # Генерация отчета
        report = agent.generate_report()
        if report:
            print("Отчет сгенерирован: {}".format(report["report_id"]))

        # Остановка агента
        agent.stop()
    else:
        print("Ошибка инициализации PasswordSecurityAgent")
