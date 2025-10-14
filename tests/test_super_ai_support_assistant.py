# -*- coding: utf-8 -*-
"""
Тесты для Super AI Support Assistant
ALADDIN Security System

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-04
"""

import unittest
import sys
import os
import time
from datetime import datetime, timedelta

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from security.ai.super_ai_support_assistant import (
        SuperAISupportAssistant,
        SupportCategory,
        EmotionType,
        PriorityLevel,
        SupportStatus,
        Language,
        UserProfile,
        SupportRequest,
        EmotionalAnalysis,
        SupportMetrics
    )
except ImportError as e:
    print("Ошибка импорта: {}".format(e))
    # Создаем мок-классы для тестирования
    class MockEnum:
        def __init__(self, value):
            self.value = value
    
    SupportCategory = type('SupportCategory', (), {
        'CYBERSECURITY': MockEnum('cybersecurity'),
        'FAMILY_SUPPORT': MockEnum('family_support'),
        'MEDICAL_SUPPORT': MockEnum('medical_support'),
        'EDUCATION': MockEnum('education'),
        'FINANCE': MockEnum('finance'),
        'HOUSEHOLD': MockEnum('household')
    })
    
    EmotionType = type('EmotionType', (), {
        'HAPPY': MockEnum('happy'),
        'SAD': MockEnum('sad'),
        'ANGRY': MockEnum('angry'),
        'NEUTRAL': MockEnum('neutral'),
        'STRESSED': MockEnum('stressed')
    })
    
    PriorityLevel = type('PriorityLevel', (), {
        'LOW': MockEnum('low'),
        'MEDIUM': MockEnum('medium'),
        'HIGH': MockEnum('high'),
        'CRITICAL': MockEnum('critical')
    })
    
    SupportStatus = type('SupportStatus', (), {
        'PENDING': MockEnum('pending'),
        'IN_PROGRESS': MockEnum('in_progress'),
        'RESOLVED': MockEnum('resolved'),
        'ESCALATED': MockEnum('escalated')
    })
    
    Language = type('Language', (), {
        'RUSSIAN': MockEnum('ru'),
        'ENGLISH': MockEnum('en')
    })

class TestSuperAISupportAssistant(unittest.TestCase):
    """Тесты для Super AI Support Assistant"""
    
    def setUp(self):
        """Настройка тестов"""
        self.assistant = SuperAISupportAssistant("TestAssistant")
        
    def test_initialization(self):
        """Тест инициализации ассистента"""
        self.assertEqual(self.assistant.name, "TestAssistant")
        self.assertEqual(self.assistant.status, "INITIALIZING")
        self.assertIsNotNone(self.assistant.logger)
        self.assertIsNotNone(self.assistant.user_profiles)
        self.assertIsNotNone(self.assistant.support_requests)
        self.assertIsNotNone(self.assistant.metrics)
        
    def test_initialize(self):
        """Тест инициализации ассистента"""
        result = self.assistant.initialize()
        self.assertTrue(result)
        self.assertEqual(self.assistant.status, "RUNNING")
        
    def test_create_user_profile(self):
        """Тест создания профиля пользователя"""
        # Инициализация ассистента
        self.assistant.initialize()
        
        profile = self.assistant.create_user_profile(
            user_id="test_user",
            name="Тестовый Пользователь",
            age=25,
            preferences={"language": "ru"}
        )
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user_id, "test_user")
        self.assertEqual(profile.name, "Тестовый Пользователь")
        self.assertEqual(profile.age, 25)
        self.assertIn("test_user", self.assistant.user_profiles)
        
    def test_analyze_emotion(self):
        """Тест анализа эмоций"""
        # Инициализация ассистента
        self.assistant.initialize()
        
        # Создание профиля пользователя
        self.assistant.create_user_profile("test_user")
        
        # Тест анализа положительных эмоций
        emotion = self.assistant.analyze_emotion("Мне очень хорошо и я счастлив!", "test_user")
        self.assertIsNotNone(emotion)
        self.assertEqual(emotion.emotion.value, "happy")
        self.assertGreater(emotion.confidence, 0.5)
        
        # Тест анализа отрицательных эмоций
        emotion = self.assistant.analyze_emotion("Мне очень грустно и плохо", "test_user")
        self.assertIsNotNone(emotion)
        self.assertEqual(emotion.emotion.value, "sad")
        self.assertGreater(emotion.confidence, 0.5)
        
        # Тест анализа стресса
        emotion = self.assistant.analyze_emotion("Я очень устал и в стрессе", "test_user")
        self.assertIsNotNone(emotion)
        self.assertEqual(emotion.emotion.value, "stressed")
        self.assertGreater(emotion.confidence, 0.5)
        
    def test_process_support_request(self):
        """Тест обработки запроса поддержки"""
        # Инициализация ассистента
        self.assistant.initialize()
        
        # Создание профиля пользователя
        self.assistant.create_user_profile("test_user")
        
        # Тест обработки запроса по кибербезопасности
        request = self.assistant.process_support_request(
            user_id="test_user",
            category=SupportCategory.CYBERSECURITY,
            description="У меня проблемы с безопасностью",
            priority=PriorityLevel.HIGH
        )
        
        self.assertIsNotNone(request)
        self.assertEqual(request.user_id, "test_user")
        self.assertEqual(request.category.value, "cybersecurity")
        self.assertEqual(request.priority.value, "high")
        self.assertIn(request.request_id, self.assistant.support_requests)
        
        # Тест обработки запроса по семейной поддержке
        request = self.assistant.process_support_request(
            user_id="test_user",
            category=SupportCategory.FAMILY_SUPPORT,
            description="У нас проблемы в семье",
            priority=PriorityLevel.MEDIUM
        )
        
        self.assertIsNotNone(request)
        self.assertEqual(request.category.value, "family_support")
        
    def test_get_personalized_recommendations(self):
        """Тест получения персонализированных рекомендаций"""
        # Инициализация ассистента
        self.assistant.initialize()
        
        # Создание профиля пользователя
        self.assistant.create_user_profile("test_user", age=30)
        
        # Получение рекомендаций
        recommendations = self.assistant.get_personalized_recommendations("test_user")
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Тест рекомендаций для несовершеннолетнего
        self.assistant.create_user_profile("young_user", age=16)
        young_recommendations = self.assistant.get_personalized_recommendations("young_user")
        self.assertGreater(len(young_recommendations), 0)
        
        # Тест рекомендаций для пожилого человека
        self.assistant.create_user_profile("elderly_user", age=70)
        elderly_recommendations = self.assistant.get_personalized_recommendations("elderly_user")
        self.assertGreater(len(elderly_recommendations), 0)
        
    def test_learn_from_interaction(self):
        """Тест обучения на основе взаимодействия"""
        # Инициализация ассистента
        self.assistant.initialize()
        
        # Создание профиля пользователя
        self.assistant.create_user_profile("test_user")
        
        # Обработка запроса
        request = self.assistant.process_support_request(
            user_id="test_user",
            category=SupportCategory.CYBERSECURITY,
            description="Тестовый запрос",
            priority=PriorityLevel.MEDIUM
        )
        
        # Обучение на основе обратной связи
        self.assistant.learn_from_interaction(
            user_id="test_user",
            request_id=request.request_id,
            feedback="Отличное решение!",
            satisfaction_rating=5
        )
        
        # Проверка обновления метрик
        metrics = self.assistant.get_support_metrics()
        self.assertGreater(metrics["learning_improvements"], 0)
        
    def test_get_support_metrics(self):
        """Тест получения метрик поддержки"""
        # Инициализация ассистента
        self.assistant.initialize()
        
        # Создание профиля пользователя
        self.assistant.create_user_profile("test_user")
        
        # Обработка нескольких запросов
        for i in range(5):
            self.assistant.process_support_request(
                user_id="test_user",
                category=SupportCategory.CYBERSECURITY,
                description="Тестовый запрос {}".format(i),
                priority=PriorityLevel.MEDIUM
            )
        
        # Получение метрик
        metrics = self.assistant.get_support_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertGreater(metrics["total_requests"], 0)
        self.assertGreaterEqual(metrics["resolved_requests"], 0)
        self.assertGreaterEqual(metrics["automation_rate"], 0)
        
    def test_get_user_insights(self):
        """Тест получения инсайтов пользователя"""
        # Инициализация ассистента
        self.assistant.initialize()
        
        # Создание профиля пользователя
        self.assistant.create_user_profile("test_user", age=30)
        
        # Обработка запросов
        for i in range(3):
            self.assistant.process_support_request(
                user_id="test_user",
                category=SupportCategory.CYBERSECURITY,
                description="Тестовый запрос {}".format(i),
                priority=PriorityLevel.MEDIUM
            )
        
        # Получение инсайтов
        insights = self.assistant.get_user_insights("test_user")
        
        self.assertIsNotNone(insights)
        self.assertIn("user_profile", insights)
        self.assertIn("total_requests", insights)
        self.assertIn("recommendations", insights)
        self.assertEqual(insights["total_requests"], 3)
        
    def test_stop(self):
        """Тест остановки ассистента"""
        # Инициализация ассистента
        self.assistant.initialize()
        
        # Остановка ассистента
        result = self.assistant.stop()
        
        self.assertTrue(result)
        self.assertEqual(self.assistant.status, "STOPPED")
        
    def test_emotional_analysis_integration(self):
        """Тест интеграции эмоционального анализа"""
        # Инициализация ассистента
        self.assistant.initialize()
        
        # Создание профиля пользователя
        self.assistant.create_user_profile("test_user")
        
        # Анализ эмоций в запросе
        request = self.assistant.process_support_request(
            user_id="test_user",
            category=SupportCategory.FAMILY_SUPPORT,
            description="Я очень злой и расстроен из-за проблем в семье!",
            priority=PriorityLevel.MEDIUM
        )
        
        # Проверка, что эмоции учтены в контексте
        self.assertIn("emotion", request.context)
        self.assertEqual(request.context["emotion"], "angry")
        self.assertEqual(request.priority.value, "high")  # Приоритет должен повыситься
        
    def test_multilingual_support(self):
        """Тест многоязычной поддержки"""
        # Инициализация ассистента
        self.assistant.initialize()
        
        # Проверка поддерживаемых языков
        self.assertGreater(len(self.assistant.supported_languages), 10)
        self.assertIn(Language.RUSSIAN, self.assistant.supported_languages)
        self.assertIn(Language.ENGLISH, self.assistant.supported_languages)
        
    def test_category_coverage(self):
        """Тест покрытия категорий"""
        # Инициализация ассистента
        self.assistant.initialize()
        
        # Проверка поддерживаемых категорий
        self.assertGreater(len(self.assistant.supported_categories), 15)
        self.assertIn(SupportCategory.CYBERSECURITY, self.assistant.supported_categories)
        self.assertIn(SupportCategory.FAMILY_SUPPORT, self.assistant.supported_categories)
        self.assertIn(SupportCategory.MEDICAL_SUPPORT, self.assistant.supported_categories)
        self.assertIn(SupportCategory.EDUCATION, self.assistant.supported_categories)
        self.assertIn(SupportCategory.FINANCE, self.assistant.supported_categories)
        self.assertIn(SupportCategory.HOUSEHOLD, self.assistant.supported_categories)
        
    def test_automation_capabilities(self):
        """Тест возможностей автоматизации"""
        # Инициализация ассистента
        self.assistant.initialize()
        
        # Создание профиля пользователя
        self.assistant.create_user_profile("test_user")
        
        # Обработка запросов, которые должны решаться автоматически
        automated_requests = 0
        total_requests = 10
        
        for i in range(total_requests):
            request = self.assistant.process_support_request(
                user_id="test_user",
                category=SupportCategory.CYBERSECURITY,
                description="Стандартный запрос по безопасности {}".format(i),
                priority=PriorityLevel.MEDIUM
            )
            
            if request.status.value == "resolved":
                automated_requests += 1
        
        # Проверка уровня автоматизации
        automation_rate = automated_requests / total_requests
        self.assertGreater(automation_rate, 0.5)  # Должно быть больше 50%
        
    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тест с неинициализированным ассистентом
        assistant = SuperAISupportAssistant("TestAssistant")
        
        # Попытка обработки запроса без инициализации
        request = assistant.process_support_request(
            user_id="test_user",
            category=SupportCategory.CYBERSECURITY,
            description="Тестовый запрос"
        )
        
        self.assertIsNone(request)
        
        # Тест с несуществующим пользователем
        assistant.initialize()
        request = assistant.process_support_request(
            user_id="nonexistent_user",
            category=SupportCategory.CYBERSECURITY,
            description="Тестовый запрос"
        )
        
        self.assertIsNotNone(request)  # Должен обработаться даже без профиля


def run_tests():
    """Запуск тестов"""
    print("🧪 ТЕСТИРОВАНИЕ SUPER AI SUPPORT ASSISTANT")
    print("=" * 50)
    
    # Создание тестового набора
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSuperAISupportAssistant)
    
    # Запуск тестов
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Подсчет результатов
    total_tests = result.testsRun
    failed_tests = len(result.failures)
    error_tests = len(result.errors)
    passed_tests = total_tests - failed_tests - error_tests
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("   Всего тестов: {}".format(total_tests))
    print("   ✅ Пройдено: {}".format(passed_tests))
    print("   ❌ Провалено: {}".format(failed_tests))
    print("   ⚠️  Ошибок: {}".format(error_tests))
    print("   📈 Успешность: {:.1f}%".format((passed_tests / total_tests) * 100))
    
    if failed_tests > 0:
        print("\n❌ ПРОВАЛЕННЫЕ ТЕСТЫ:")
        for test, traceback in result.failures:
            print("   - {}: {}".format(test, traceback.split('\n')[-2]))
    
    if error_tests > 0:
        print("\n⚠️  ТЕСТЫ С ОШИБКАМИ:")
        for test, traceback in result.errors:
            print("   - {}: {}".format(test, traceback.split('\n')[-2]))
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)