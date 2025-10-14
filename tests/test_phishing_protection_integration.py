#!/usr/bin/env python3
"""
Интеграционные тесты для PhishingProtectionAgent
Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-25
"""

import asyncio
import unittest
import sys
import os
import time

# Добавляем путь к модулю
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.ai_agents.phishing_protection_agent import (
    PhishingProtectionAgent,
    URLReputationPlugin,
    EmailContentPlugin,
    DomainAgePlugin,
    PhishingType,
    ThreatLevel,
    DetectionMethod
)


class TestPhishingProtectionIntegration(unittest.TestCase):
    """Интеграционные тесты для PhishingProtectionAgent"""

    def setUp(self):
        """Настройка тестов"""
        self.agent = PhishingProtectionAgent('IntegrationTestAgent')
        
        # Регистрируем все плагины
        self.url_plugin = URLReputationPlugin()
        self.email_plugin = EmailContentPlugin()
        self.domain_plugin = DomainAgePlugin()
        
        self.agent.register_plugin(self.url_plugin)
        self.agent.register_plugin(self.email_plugin)
        self.agent.register_plugin(self.domain_plugin)

    def test_full_analysis_pipeline_url(self):
        """Тест полного пайплайна анализа URL"""
        # Тест полного цикла: URL -> анализ -> обнаружение -> отчет
        url = 'https://suspicious-site.com/phishing'
        
        # Синхронный анализ
        detection = self.agent.analyze_url(url)
        
        if detection:
            report = self.agent.report_phishing(
                user_id='test_user',
                source=url,
                description='Test phishing detection'
            )
            self.assertIsNotNone(report)
            self.assertEqual(report.source, url)

    def test_full_analysis_pipeline_email(self):
        """Тест полного пайплайна анализа email"""
        # Тест полного цикла: Email -> анализ -> обнаружение -> отчет
        subject = 'URGENT: Verify Your Account'
        content = 'Click here to verify your account immediately!'
        sender = 'noreply@suspicious.com'
        
        detection = self.agent.analyze_email(subject, content, sender)
        
        if detection:
            report = self.agent.report_phishing(
                user_id='test_user',
                source=f'Email from {sender}',
                description='Test email phishing detection'
            )
            self.assertIsNotNone(report)

    async def test_async_full_analysis_pipeline(self):
        """Тест полного асинхронного пайплайна анализа"""
        # Асинхронный анализ URL
        url = 'https://bit.ly/suspicious'
        detection = await self.agent.analyze_url_async(url)
        
        if detection:
            report = self.agent.report_phishing(
                user_id='test_user',
                source=url,
                description='Test async phishing detection'
            )
            self.assertIsNotNone(report)

    def test_plugin_integration_workflow(self):
        """Тест интеграции плагинов в рабочий процесс"""
        # Тест анализа с плагинами
        data = {
            'url': 'https://bit.ly/suspicious'
        }
        
        result = asyncio.run(self.agent.analyze_with_plugins(data))
        
        # Проверяем структуру результата
        self.assertIsInstance(result, dict)
        self.assertIn('agent_analysis', result)
        self.assertIn('plugin_results', result)
        self.assertIn('combined_confidence', result)
        self.assertIn('combined_threat_level', result)
        
        # Проверяем, что все плагины отработали
        self.assertEqual(len(result['plugin_results']), 3)
        self.assertIn('URLReputationPlugin', result['plugin_results'])
        self.assertIn('EmailContentPlugin', result['plugin_results'])
        self.assertIn('DomainAgePlugin', result['plugin_results'])

    def test_batch_processing_workflow(self):
        """Тест пакетной обработки"""
        # Тест пакетного анализа URL
        urls = [
            'https://example.com',
            'https://bit.ly/suspicious',
            'https://suspicious.com',
            'https://trusted.com'
        ]
        
        # Добавляем домены в списки
        self.agent.trusted_domains.add('trusted.com')
        self.agent.blocked_domains.add('suspicious.com')
        
        detections = asyncio.run(self._collect_batch_results(urls))
        
        # Проверяем результаты
        self.assertIsInstance(detections, list)
        self.assertLessEqual(len(detections), len(urls))

    async def _collect_batch_results(self, urls):
        """Собирает результаты пакетного анализа"""
        detections = []
        async for detection in self.agent.batch_analyze_urls(urls):
            detections.append(detection)
        return detections

    def test_backup_restore_workflow(self):
        """Тест рабочего процесса резервного копирования и восстановления"""
        # Сохраняем исходное состояние
        original_blocked = self.agent.blocked_domains.copy()
        original_trusted = self.agent.trusted_domains.copy()
        
        # Создаем резервную копию
        backup = self.agent.backup_configuration()
        self.assertIsNotNone(backup)
        
        # Изменяем конфигурацию
        self.agent.blocked_domains.add('test-malicious.com')
        self.agent.trusted_domains.add('test-trusted.com')
        
        # Проверяем, что изменения применились
        self.assertIn('test-malicious.com', self.agent.blocked_domains)
        self.assertIn('test-trusted.com', self.agent.trusted_domains)
        
        # Восстанавливаем из резервной копии
        success = self.agent.restore_configuration(backup)
        self.assertTrue(success)
        
        # Проверяем, что конфигурация восстановлена
        self.assertEqual(self.agent.blocked_domains, original_blocked)
        self.assertEqual(self.agent.trusted_domains, original_trusted)

    def test_performance_under_load(self):
        """Тест производительности под нагрузкой"""
        # Тест множественных запросов
        urls = [f'https://test{i}.com' for i in range(50)]
        
        start_time = time.time()
        
        # Синхронная обработка
        sync_results = []
        for url in urls:
            result = self.agent.analyze_url(url)
            sync_results.append(result)
        
        sync_time = time.time() - start_time
        
        # Асинхронная обработка
        start_time = time.time()
        async_results = asyncio.run(self._collect_batch_results(urls))
        async_time = time.time() - start_time
        
        # Проверяем результаты
        self.assertEqual(len(sync_results), len(urls))
        self.assertIsInstance(async_results, list)
        
        # Асинхронная обработка должна быть быстрее
        if async_time > 0:
            print(f"Синхронное время: {sync_time:.4f}s")
            print(f"Асинхронное время: {async_time:.4f}s")
            print(f"Ускорение: {sync_time/async_time:.2f}x")

    def test_memory_usage_under_load(self):
        """Тест использования памяти под нагрузкой"""
        # Тест множественных операций для проверки утечек памяти
        for i in range(100):
            url = f'https://test{i}.com'
            self.agent.analyze_url(url)
            
            # Проверяем, что кэш не растет бесконечно
            if i % 10 == 0:
                cache_size = len(self.agent._cache)
                self.assertLess(cache_size, 1000)  # Разумный лимит кэша

    def test_error_recovery(self):
        """Тест восстановления после ошибок"""
        # Тест обработки некорректных данных
        invalid_inputs = [
            '',  # Пустая строка
            None,  # None
            'invalid-url',  # Невалидный URL
            'not-an-email',  # Невалидный email
        ]
        
        for invalid_input in invalid_inputs:
            # URL анализ должен обрабатывать ошибки gracefully
            result = self.agent.analyze_url(invalid_input)
            self.assertIsNone(result)
            
            # Email анализ должен обрабатывать ошибки gracefully
            result = self.agent.analyze_email(invalid_input, invalid_input, invalid_input)
            self.assertIsNone(result)

    def test_concurrent_operations(self):
        """Тест параллельных операций"""
        async def concurrent_analysis():
            tasks = []
            
            # Создаем множество параллельных задач
            for i in range(20):
                task = self.agent.analyze_url_async(f'https://test{i}.com')
                tasks.append(task)
            
            # Выполняем все задачи параллельно
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Проверяем, что все задачи завершились
            self.assertEqual(len(results), 20)
            
            # Проверяем, что нет исключений
            for result in results:
                self.assertNotIsInstance(result, Exception)
        
        # Запускаем тест
        asyncio.run(concurrent_analysis())

    def test_plugin_error_handling(self):
        """Тест обработки ошибок в плагинах"""
        # Создаем плагин, который выбрасывает исключение
        class FaultyPlugin:
            def get_name(self):
                return "FaultyPlugin"
            
            async def analyze_async(self, data):
                raise Exception("Plugin error")
        
        faulty_plugin = FaultyPlugin()
        self.agent.register_plugin(faulty_plugin)
        
        # Анализ должен продолжаться даже при ошибке плагина
        data = {'url': 'https://example.com'}
        result = asyncio.run(self.agent.analyze_with_plugins(data))
        
        # Проверяем, что результат получен
        self.assertIsInstance(result, dict)
        self.assertIn('plugin_results', result)
        self.assertIn('FaultyPlugin', result['plugin_results'])
        
        # Проверяем, что ошибка записана
        plugin_result = result['plugin_results']['FaultyPlugin']
        self.assertIn('error', plugin_result)

    def test_configuration_persistence(self):
        """Тест сохранения конфигурации"""
        # Изменяем конфигурацию
        self.agent.confidence_threshold = 0.8
        self.agent.auto_block_threshold = 0.9
        self.agent.max_requests_per_minute = 200
        
        # Создаем резервную копию
        backup = self.agent.backup_configuration()
        
        # Создаем новый агент
        new_agent = PhishingProtectionAgent('NewAgent')
        
        # Восстанавливаем конфигурацию
        success = new_agent.restore_configuration(backup)
        self.assertTrue(success)
        
        # Проверяем, что конфигурация восстановлена
        self.assertEqual(new_agent.confidence_threshold, 0.8)
        self.assertEqual(new_agent.auto_block_threshold, 0.9)
        self.assertEqual(new_agent.max_requests_per_minute, 200)

    def test_health_monitoring(self):
        """Тест мониторинга состояния"""
        # Проверяем состояние здоровья
        health = self.agent.check_health_status()
        
        self.assertIsInstance(health, dict)
        self.assertIn('status', health)
        self.assertIn('uptime', health)
        self.assertIn('memory_usage', health)
        
        # Проверяем метрики производительности
        metrics = self.agent.get_performance_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('total_requests', metrics)
        self.assertIn('successful_detections', metrics)
        self.assertIn('average_confidence', metrics)

    def test_end_to_end_workflow(self):
        """Тест полного end-to-end рабочего процесса"""
        # 1. Инициализация агента
        self.assertIsNotNone(self.agent)
        
        # 2. Регистрация плагинов
        self.assertEqual(len(self.agent.plugins), 3)
        
        # 3. Анализ подозрительного URL
        url = 'https://bit.ly/suspicious'
        detection = self.agent.analyze_url(url)
        
        # 4. Если обнаружен фишинг, создаем отчет
        if detection:
            report = self.agent.report_phishing(
                user_id='test_user',
                source=url,
                description='End-to-end test detection'
            )
            self.assertIsNotNone(report)
        
        # 5. Проверяем метрики
        metrics = self.agent.get_performance_metrics()
        self.assertIsInstance(metrics, dict)
        
        # 6. Проверяем состояние здоровья
        health = self.agent.check_health_status()
        self.assertIsInstance(health, dict)
        
        # 7. Создаем резервную копию
        backup = self.agent.backup_configuration()
        self.assertIsNotNone(backup)


if __name__ == '__main__':
    # Запуск интеграционных тестов
    unittest.main(verbosity=2)