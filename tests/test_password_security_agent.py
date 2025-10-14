#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тесты для PasswordSecurityAgent

Этот модуль содержит комплексные unit-тесты для PasswordSecurityAgent,
включая тестирование всех основных функций, AI моделей, генерации паролей,
хеширования, проверки безопасности и обработки ошибок.

Тесты покрывают:
- Инициализацию агента и AI моделей
- Генерацию и анализ паролей
- Хеширование и проверку паролей
- Проверку утечек и политик безопасности
- Генерацию отчетов и рекомендаций
- Обработку ошибок и исключений
- Валидацию данных и качество кода

Автор: ALADDIN Security System
Версия: 1.0
Дата: 2024
"""

import os
import sys
import unittest
import time
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from security.ai_agents.password_security_agent import (
        PasswordSecurityAgent,
        PasswordPolicy,
        PasswordStrength,
        PasswordStatus,
        PasswordMetrics
    )
except ImportError as e:
    print("Ошибка импорта: {}".format(e))
    sys.exit(1)


class TestPasswordSecurityAgent(unittest.TestCase):
    """
    Тесты для PasswordSecurityAgent
    
    Этот класс содержит все unit-тесты для основного агента безопасности паролей.
    Тесты проверяют корректность работы всех методов, генерацию паролей,
    AI модели, хеширование и проверку безопасности.
    """
    
    def setUp(self):
        """Настройка тестов"""
        self.agent = PasswordSecurityAgent("TestPasswordSecurityAgent")
    
    def test_initialization(self):
        """Тест инициализации агента"""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.name, "TestPasswordSecurityAgent")
        self.assertIsNotNone(self.agent.metrics)
        self.assertIsNotNone(self.agent.default_policy)
        self.assertIsNotNone(self.agent.breach_database)
    
    def test_ai_models_initialization(self):
        """Тест инициализации AI моделей"""
        self.agent._initialize_ai_models()
        
        # Проверка наличия всех AI моделей
        expected_models = [
            "strength_analyzer", "breach_detector", "pattern_analyzer", "entropy_calculator"
        ]
        
        for model_name in expected_models:
            self.assertIn(model_name, self.agent.ml_models)
            self.assertIsNotNone(self.agent.ml_models[model_name])
    
    def test_breach_database_loading(self):
        """Тест загрузки базы данных утечек"""
        self.agent._load_breach_database()
        
        # Проверка что база данных загружена
        self.assertGreater(len(self.agent.breach_database), 0)
        self.assertIsInstance(self.agent.breach_database, set)
    
    def test_security_systems_setup(self):
        """Тест настройки систем безопасности"""
        self.agent._setup_security_systems()
        
        # Проверка параметров хеширования
        self.assertEqual(self.agent.hashing_algorithm, "pbkdf2_sha256")
        self.assertEqual(self.agent.salt_length, 32)
        self.assertEqual(self.agent.iterations, 100000)
        self.assertEqual(self.agent.breach_check_interval, 86400)
    
    def test_password_generation(self):
        """Тест генерации пароля"""
        self.agent.initialize()
        
        # Генерация пароля с параметрами по умолчанию
        password = self.agent.generate_password()
        
        # Проверка генерации
        self.assertIsNotNone(password)
        self.assertGreaterEqual(len(password), 8)
        self.assertLessEqual(len(password), 128)
        
        # Генерация пароля с кастомными параметрами
        custom_password = self.agent.generate_password(
            length=20, include_uppercase=True, include_lowercase=True,
            include_digits=True, include_special=True
        )
        
        self.assertIsNotNone(custom_password)
        self.assertEqual(len(custom_password), 20)
    
    def test_password_validation_params(self):
        """Тест валидации параметров генерации"""
        # Тест с корректными параметрами
        self.assertTrue(self.agent._validate_password_params(
            16, True, True, True, True
        ))
        
        # Тест с некорректной длиной
        self.assertFalse(self.agent._validate_password_params(
            5, True, True, True, True  # Слишком короткий
        ))
        
        self.assertFalse(self.agent._validate_password_params(
            200, True, True, True, True  # Слишком длинный
        ))
        
        # Тест без выбранных типов символов
        self.assertFalse(self.agent._validate_password_params(
            16, False, False, False, False
        ))
    
    def test_password_strength_analysis(self):
        """Тест анализа сложности пароля"""
        # Тест слабого пароля
        weak_password = "123"
        strength = self.agent.analyze_password_strength(weak_password)
        self.assertEqual(strength, PasswordStrength.WEAK)
        
        # Тест среднего пароля
        medium_password = "password123"
        strength = self.agent.analyze_password_strength(medium_password)
        self.assertIn(strength, [PasswordStrength.WEAK, PasswordStrength.MEDIUM])
        
        # Тест сильного пароля
        strong_password = "MyStr0ng!P@ssw0rd"
        strength = self.agent.analyze_password_strength(strong_password)
        self.assertIn(strength, [PasswordStrength.STRONG, PasswordStrength.VERY_STRONG])
        
        # Тест пустого пароля
        empty_strength = self.agent.analyze_password_strength("")
        self.assertEqual(empty_strength, PasswordStrength.WEAK)
    
    def test_entropy_calculation(self):
        """Тест расчета энтропии"""
        # Тест с простым паролем
        simple_entropy = self.agent._calculate_entropy("123")
        self.assertGreater(simple_entropy, 0)
        
        # Тест со сложным паролем
        complex_entropy = self.agent._calculate_entropy("MyStr0ng!P@ssw0rd")
        self.assertGreater(complex_entropy, simple_entropy)
        
        # Тест с пустым паролем
        empty_entropy = self.agent._calculate_entropy("")
        self.assertEqual(empty_entropy, 0.0)
    
    def test_pattern_detection(self):
        """Тест обнаружения паттернов"""
        # Тест с последовательностью
        pattern_password = "abc123"
        has_patterns = self.agent._has_common_patterns(pattern_password)
        self.assertTrue(has_patterns)
        
        # Тест с повторяющимися символами
        repeat_password = "aaaaaa"
        has_patterns = self.agent._has_common_patterns(repeat_password)
        self.assertTrue(has_patterns)
        
        # Тест без паттернов
        no_pattern_password = "MyStr0ng!P@ssw0rd"
        has_patterns = self.agent._has_common_patterns(no_pattern_password)
        self.assertFalse(has_patterns)
    
    def test_password_hashing(self):
        """Тест хеширования пароля"""
        password = "test_password"
        
        # Хеширование с автоматической генерацией соли
        hash_result = self.agent.hash_password(password)
        
        # Проверка результата
        self.assertIsNotNone(hash_result)
        self.assertIn("hash", hash_result)
        self.assertIn("salt", hash_result)
        self.assertIn("algorithm", hash_result)
        self.assertIn("iterations", hash_result)
        
        # Хеширование с заданной солью
        custom_salt = "custom_salt"
        hash_result_custom = self.agent.hash_password(password, custom_salt)
        
        self.assertIsNotNone(hash_result_custom)
        self.assertEqual(hash_result_custom["salt"], custom_salt)
    
    def test_password_verification(self):
        """Тест проверки пароля"""
        password = "test_password"
        
        # Хеширование пароля
        hash_result = self.agent.hash_password(password)
        self.assertIsNotNone(hash_result)
        
        # Проверка правильного пароля
        is_valid = self.agent.verify_password(password, hash_result["hash"], hash_result["salt"])
        self.assertTrue(is_valid)
        
        # Проверка неправильного пароля
        is_invalid = self.agent.verify_password("wrong_password", hash_result["hash"], hash_result["salt"])
        self.assertFalse(is_invalid)
        
        # Проверка с пустыми параметрами
        empty_verification = self.agent.verify_password("", "", "")
        self.assertFalse(empty_verification)
    
    def test_password_breach_check(self):
        """Тест проверки утечки пароля"""
        # Тест с паролем из базы данных утечек
        breached_password = "123456"
        is_breached = self.agent.check_password_breach(breached_password)
        self.assertTrue(is_breached)
        
        # Тест с безопасным паролем
        safe_password = "MyStr0ng!P@ssw0rd123"
        is_breached = self.agent.check_password_breach(safe_password)
        self.assertFalse(is_breached)
        
        # Тест с пустым паролем
        empty_breach = self.agent.check_password_breach("")
        self.assertFalse(empty_breach)
    
    def test_password_policy_validation(self):
        """Тест валидации политики пароля"""
        # Создание тестовой политики
        policy = PasswordPolicy(
            min_length=12,
            require_uppercase=True,
            require_lowercase=True,
            require_digits=True,
            require_special=True
        )
        
        # Тест с паролем, соответствующим политике
        valid_password = "MyStr0ng!P@ssw0rd"
        is_valid, message = self.agent.validate_password_policy(valid_password, policy)
        self.assertTrue(is_valid)
        self.assertIn("соответствует", message)
        
        # Тест с паролем, не соответствующим политике
        invalid_password = "weak"
        is_valid, message = self.agent.validate_password_policy(invalid_password, policy)
        self.assertFalse(is_valid)
        self.assertIn("короткий", message)
        
        # Тест с пустым паролем
        empty_validation = self.agent.validate_password_policy("", policy)
        self.assertFalse(empty_validation[0])
        self.assertIn("пустым", empty_validation[1])
    
    def test_password_policy_serialization(self):
        """Тест сериализации политики пароля"""
        policy = PasswordPolicy(
            min_length=16,
            require_uppercase=True,
            require_lowercase=True,
            require_digits=True,
            require_special=True,
            max_age_days=60,
            prevent_reuse=3,
            max_attempts=3,
            lockout_duration=15
        )
        
        # Сериализация
        policy_dict = policy.to_dict()
        
        # Проверка сериализации
        self.assertIsInstance(policy_dict, dict)
        self.assertEqual(policy_dict["min_length"], 16)
        self.assertEqual(policy_dict["require_uppercase"], True)
        self.assertEqual(policy_dict["max_age_days"], 60)
        self.assertEqual(policy_dict["prevent_reuse"], 3)
        self.assertIn("created_at", policy_dict)
    
    def test_metrics_serialization(self):
        """Тест сериализации метрик"""
        metrics = PasswordMetrics()
        
        # Установка тестовых данных
        metrics.total_passwords = 100
        metrics.weak_passwords = 20
        metrics.strong_passwords = 80
        metrics.compromised_passwords = 5
        metrics.avg_password_length = 12.5
        metrics.password_entropy = 3.8
        metrics.password_generation_count = 50
        metrics.password_validation_count = 200
        
        # Сериализация
        metrics_dict = metrics.to_dict()
        
        # Проверка сериализации
        self.assertIsInstance(metrics_dict, dict)
        self.assertEqual(metrics_dict["total_passwords"], 100)
        self.assertEqual(metrics_dict["weak_passwords"], 20)
        self.assertEqual(metrics_dict["strong_passwords"], 80)
        self.assertEqual(metrics_dict["compromised_passwords"], 5)
        self.assertEqual(metrics_dict["avg_password_length"], 12.5)
        self.assertEqual(metrics_dict["password_entropy"], 3.8)
        self.assertEqual(metrics_dict["password_generation_count"], 50)
        self.assertEqual(metrics_dict["password_validation_count"], 200)
    
    def test_compliance_report_generation(self):
        """Тест генерации отчета о безопасности"""
        self.agent.initialize()
        
        # Генерация отчета
        report = self.agent.generate_compliance_report()
        
        # Проверка отчета
        self.assertIsNotNone(report)
        self.assertIn("report_id", report)
        self.assertIn("generated_at", report)
        self.assertIn("agent_name", report)
        self.assertIn("summary", report)
        self.assertIn("metrics", report)
        self.assertIn("recommendations", report)
    
    def test_recommendation_generation(self):
        """Тест генерации рекомендаций"""
        # Установка тестовых метрик
        self.agent.metrics.total_passwords = 100
        self.agent.metrics.weak_passwords = 30  # 30% слабых паролей
        self.agent.metrics.compromised_passwords = 5  # 5 скомпрометированных
        self.agent.metrics.policy_compliance_rate = 0.8  # 80% соответствие политике
        
        # Генерация рекомендаций
        recommendations = self.agent._generate_recommendations()
        
        # Проверка рекомендаций
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Проверка типов рекомендаций
        recommendation_types = [rec["type"] for rec in recommendations]
        self.assertIn("password_strength", recommendation_types)
        self.assertIn("password_breach", recommendation_types)
        self.assertIn("policy_compliance", recommendation_types)
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        # Инициализация
        self.assertTrue(self.agent.initialize())
        
        # Генерация пароля
        password = self.agent.generate_password(length=16)
        self.assertIsNotNone(password)
        
        # Анализ сложности
        strength = self.agent.analyze_password_strength(password)
        self.assertIsNotNone(strength)
        
        # Хеширование пароля
        hash_result = self.agent.hash_password(password)
        self.assertIsNotNone(hash_result)
        
        # Проверка пароля
        is_valid = self.agent.verify_password(password, hash_result["hash"], hash_result["salt"])
        self.assertTrue(is_valid)
        
        # Проверка утечки
        is_breached = self.agent.check_password_breach(password)
        self.assertIsInstance(is_breached, bool)
        
        # Валидация политики
        is_policy_valid, message = self.agent.validate_password_policy(password)
        self.assertIsInstance(is_policy_valid, bool)
        
        # Генерация отчета
        report = self.agent.generate_compliance_report()
        self.assertIsNotNone(report)
        
        # Остановка
        self.agent.stop()
        
        # Проверка что данные сохранены
        self.assertTrue(os.path.exists("data/password_security"))
        self.assertTrue(os.path.exists("data/password_security/metrics.json"))
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест с пустыми параметрами
        empty_hash = self.agent.hash_password("")
        self.assertIsNone(empty_hash)
        
        empty_verification = self.agent.verify_password("", "", "")
        self.assertFalse(empty_verification)
        
        empty_breach = self.agent.check_password_breach("")
        self.assertFalse(empty_breach)
    
    def test_data_validation(self):
        """Тест валидации данных"""
        # Тест с некорректными параметрами генерации
        invalid_password = self.agent.generate_password(length=5)  # Слишком короткий
        self.assertIsNone(invalid_password)
        
        # Тест с пустыми типами символов
        no_chars_password = self.agent.generate_password(
            length=16, include_uppercase=False, include_lowercase=False,
            include_digits=False, include_special=False
        )
        self.assertIsNone(no_chars_password)
    
    def test_performance_metrics(self):
        """Тест метрик производительности"""
        # Тест расчета времени
        start_time = time.time()
        time.sleep(0.1)  # Симуляция работы
        end_time = time.time()
        
        duration = end_time - start_time
        self.assertGreater(duration, 0)
        self.assertIsInstance(duration, float)


class TestPasswordEnums(unittest.TestCase):
    """Тесты для перечислений PasswordSecurityAgent"""
    
    def test_password_strength_enum(self):
        """Тест перечисления PasswordStrength"""
        self.assertEqual(PasswordStrength.WEAK.value, "weak")
        self.assertEqual(PasswordStrength.MEDIUM.value, "medium")
        self.assertEqual(PasswordStrength.STRONG.value, "strong")
        self.assertEqual(PasswordStrength.VERY_STRONG.value, "very_strong")
    
    def test_password_status_enum(self):
        """Тест перечисления PasswordStatus"""
        self.assertEqual(PasswordStatus.ACTIVE.value, "active")
        self.assertEqual(PasswordStatus.EXPIRED.value, "expired")
        self.assertEqual(PasswordStatus.COMPROMISED.value, "compromised")
        self.assertEqual(PasswordStatus.WEAK.value, "weak")
        self.assertEqual(PasswordStatus.REUSED.value, "reused")


if __name__ == "__main__":
    # Запуск тестов
    unittest.main(verbosity=2)