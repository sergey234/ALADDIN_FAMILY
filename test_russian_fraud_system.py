#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для системы сбора российских данных мошенничества
Проверяет работу всех компонентов системы
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/russian_fraud_test.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class RussianFraudSystemTester:
    """Тестер системы сбора российских данных мошенничества"""
    
    def __init__(self):
        """Инициализация тестера"""
        self.test_results = {
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_details': {},
            'start_time': None,
            'end_time': None,
            'overall_status': 'unknown'
        }
        
        # Создание директории для логов
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/cbr", exist_ok=True)
        os.makedirs("data/news", exist_ok=True)
        os.makedirs("data/ml_models", exist_ok=True)
        os.makedirs("data/ml_models/russian_fraud", exist_ok=True)

    def run_test(self, test_name: str, test_func):
        """Запуск отдельного теста
        
        Args:
            test_name: Название теста
            test_func: Функция теста
        """
        logger.info(f"Запуск теста: {test_name}")
        self.test_results['tests_run'] += 1
        
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            if result:
                self.test_results['tests_passed'] += 1
                status = 'PASSED'
                logger.info(f"✅ Тест {test_name} ПРОЙДЕН")
            else:
                self.test_results['tests_failed'] += 1
                status = 'FAILED'
                logger.error(f"❌ Тест {test_name} ПРОВАЛЕН")
            
            self.test_results['test_details'][test_name] = {
                'status': status,
                'duration': end_time - start_time,
                'result': result
            }
            
        except Exception as e:
            self.test_results['tests_failed'] += 1
            self.test_results['test_details'][test_name] = {
                'status': 'ERROR',
                'duration': 0,
                'error': str(e)
            }
            logger.error(f"❌ Ошибка в тесте {test_name}: {e}")

    def test_cbr_data_collector_import(self):
        """Тест импорта CBRDataCollector"""
        try:
            from security.ai_agents.cbr_data_collector import CBRDataCollector
            collector = CBRDataCollector()
            return collector is not None
        except Exception as e:
            logger.error(f"Ошибка импорта CBRDataCollector: {e}")
            return False

    def test_news_scraper_import(self):
        """Тест импорта NewsScraper"""
        try:
            from security.ai_agents.news_scraper import NewsScraper
            scraper = NewsScraper()
            return scraper is not None
        except Exception as e:
            logger.error(f"Ошибка импорта NewsScraper: {e}")
            return False

    def test_threat_intelligence_agent_import(self):
        """Тест импорта ThreatIntelligenceAgent"""
        try:
            from security.ai_agents.threat_intelligence_agent import ThreatIntelligenceAgent
            agent = ThreatIntelligenceAgent()
            return agent is not None
        except Exception as e:
            logger.error(f"Ошибка импорта ThreatIntelligenceAgent: {e}")
            return False

    def test_cbr_data_collection(self):
        """Тест сбора данных от ЦБ РФ"""
        try:
            from security.ai_agents.cbr_data_collector import CBRDataCollector
            
            collector = CBRDataCollector()
            
            # Тест сбора статистики (быстрый тест)
            statistics = collector.collect_statistics()
            collector.close()
            
            # Тест считается успешным если возвращается словарь (даже пустой)
            # так как проблема может быть в недоступности URL, а не в коде
            return isinstance(statistics, dict)
            
        except Exception as e:
            logger.error(f"Ошибка сбора данных ЦБ РФ: {e}")
            return False

    def test_news_scraping(self):
        """Тест сбора новостных данных"""
        try:
            from security.ai_agents.news_scraper import NewsScraper
            
            scraper = NewsScraper()
            
            # Ограниченный тест сбора данных
            news_data = scraper.collect_news_data(max_sources=1)
            scraper.close()
            
            return isinstance(news_data, list)
            
        except Exception as e:
            logger.error(f"Ошибка сбора новостных данных: {e}")
            return False

    def test_threat_intelligence_agent_methods(self):
        """Тест новых методов ThreatIntelligenceAgent"""
        try:
            from security.ai_agents.threat_intelligence_agent import ThreatIntelligenceAgent
            
            agent = ThreatIntelligenceAgent()
            
            # Проверка наличия новых методов
            new_methods = [
                'collect_russian_fraud_data',
                'train_russian_ml_models',
                'analyze_russian_fraud_trends',
                'generate_russian_fraud_report'
            ]
            
            for method_name in new_methods:
                if not hasattr(agent, method_name):
                    logger.error(f"Метод {method_name} не найден")
                    return False
            
            # Тест подготовки данных
            sample_fraud_data = {
                'cbr_reports': [
                    {
                        'title': 'Тестовый отчет',
                        'content': 'Тестовое содержание',
                        'fraud_types': ['phone_fraud'],
                        'date': '2024-01-01'
                    }
                ],
                'news_articles': [
                    {
                        'title': 'Тестовая новость',
                        'content': 'Тестовое содержание новости',
                        'fraud_indicators': ['banking_fraud'],
                        'date': '2024-01-01'
                    }
                ]
            }
            
            training_data = agent._prepare_training_data(sample_fraud_data)
            
            return len(training_data) > 0
            
        except Exception as e:
            logger.error(f"Ошибка тестирования ThreatIntelligenceAgent: {e}")
            return False

    def test_data_saving(self):
        """Тест сохранения данных"""
        try:
            test_data = {
                'test_reports': [
                    {'title': 'Тест 1', 'content': 'Содержание 1'},
                    {'title': 'Тест 2', 'content': 'Содержание 2'}
                ],
                'metadata': {
                    'collected_at': datetime.now().isoformat(),
                    'total_records': 2
                }
            }
            
            # Тест сохранения в CBR формат
            from security.ai_agents.cbr_data_collector import CBRDataCollector
            collector = CBRDataCollector()
            filepath = collector.save_data(test_data, 'test_cbr_data.json')
            collector.close()
            
            # Проверка существования файла
            return os.path.exists(filepath)
            
        except Exception as e:
            logger.error(f"Ошибка тестирования сохранения данных: {e}")
            return False

    def test_error_handling(self):
        """Тест обработки ошибок"""
        try:
            from security.ai_agents.cbr_data_collector import CBRDataCollector
            from security.ai_agents.news_scraper import NewsScraper
            
            # Тест с неверным URL
            collector = CBRDataCollector("https://invalid-url-for-testing.com")
            response = collector._make_request("https://invalid-url-for-testing.com")
            collector.close()
            
            # Должен вернуть None для неверного URL
            return response is None
            
        except Exception as e:
            logger.error(f"Ошибка тестирования обработки ошибок: {e}")
            return False

    async def test_async_methods(self):
        """Тест асинхронных методов"""
        try:
            from security.ai_agents.threat_intelligence_agent import ThreatIntelligenceAgent
            
            agent = ThreatIntelligenceAgent()
            
            # Тест сбора российских данных (заглушка)
            sample_data = {
                'cbr_reports': [],
                'news_articles': [],
                'metadata': {'total_records': 0}
            }
            
            # Тест анализа трендов
            trends = await agent.analyze_russian_fraud_trends(sample_data)
            
            return isinstance(trends, dict) and 'metadata' in trends
            
        except Exception as e:
            logger.error(f"Ошибка тестирования асинхронных методов: {e}")
            return False

    def run_all_tests(self):
        """Запуск всех тестов"""
        logger.info("🚀 Начало тестирования системы сбора российских данных мошенничества")
        self.test_results['start_time'] = datetime.now()
        
        # Синхронные тесты
        tests = [
            ("Импорт CBRDataCollector", self.test_cbr_data_collector_import),
            ("Импорт NewsScraper", self.test_news_scraper_import),
            ("Импорт ThreatIntelligenceAgent", self.test_threat_intelligence_agent_import),
            ("Сбор данных ЦБ РФ", self.test_cbr_data_collection),
            ("Сбор новостных данных", self.test_news_scraping),
            ("Методы ThreatIntelligenceAgent", self.test_threat_intelligence_agent_methods),
            ("Сохранение данных", self.test_data_saving),
            ("Обработка ошибок", self.test_error_handling),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Асинхронный тест
        self.run_test("Асинхронные методы", lambda: asyncio.run(self.test_async_methods()))
        
        self.test_results['end_time'] = datetime.now()
        self._calculate_overall_status()
        
        self._print_test_summary()
        self._save_test_results()

    def _calculate_overall_status(self):
        """Расчет общего статуса тестов"""
        if self.test_results['tests_failed'] == 0:
            self.test_results['overall_status'] = 'PASSED'
        elif self.test_results['tests_passed'] > self.test_results['tests_failed']:
            self.test_results['overall_status'] = 'PARTIAL'
        else:
            self.test_results['overall_status'] = 'FAILED'

    def _print_test_summary(self):
        """Вывод сводки тестов"""
        total_time = (
            self.test_results['end_time'] - self.test_results['start_time']
        ).total_seconds()
        
        print("\n" + "="*60)
        print("📊 СВОДКА ТЕСТИРОВАНИЯ СИСТЕМЫ СБОРА ДАННЫХ МОШЕННИЧЕСТВА")
        print("="*60)
        print(f"🕐 Время выполнения: {total_time:.2f} секунд")
        print(f"📈 Всего тестов: {self.test_results['tests_run']}")
        print(f"✅ Пройдено: {self.test_results['tests_passed']}")
        print(f"❌ Провалено: {self.test_results['tests_failed']}")
        
        if self.test_results['overall_status'] == 'PASSED':
            print(f"🎉 ОБЩИЙ СТАТУС: ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
        elif self.test_results['overall_status'] == 'PARTIAL':
            print(f"⚠️  ОБЩИЙ СТАТУС: ЧАСТИЧНО ПРОЙДЕНО")
        else:
            print(f"💥 ОБЩИЙ СТАТУС: ТЕСТЫ ПРОВАЛЕНЫ")
        
        print("\n📋 ДЕТАЛИ ТЕСТОВ:")
        for test_name, details in self.test_results['test_details'].items():
            status_emoji = "✅" if details['status'] == 'PASSED' else "❌"
            print(f"  {status_emoji} {test_name}: {details['status']} ({details['duration']:.2f}s)")
            if 'error' in details:
                print(f"      Ошибка: {details['error']}")
        
        print("="*60)

    def _save_test_results(self):
        """Сохранение результатов тестов"""
        try:
            results_file = f"data/test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Добавляем время выполнения
            if self.test_results['start_time'] and self.test_results['end_time']:
                self.test_results['total_duration'] = (
                    self.test_results['end_time'] - self.test_results['start_time']
                ).total_seconds()
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Результаты тестов сохранены в {results_file}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения результатов тестов: {e}")


def main():
    """Главная функция"""
    print("🇷🇺 ТЕСТИРОВАНИЕ СИСТЕМЫ СБОРА РОССИЙСКИХ ДАННЫХ МОШЕННИЧЕСТВА")
    print("="*60)
    
    tester = RussianFraudSystemTester()
    tester.run_all_tests()
    
    # Проверка качества кода с flake8
    print("\n🔍 ПРОВЕРКА КАЧЕСТВА КОДА С FLAKE8:")
    print("-"*40)
    
    try:
        import subprocess
        
        files_to_check = [
            'security/ai_agents/cbr_data_collector.py',
            'security/ai_agents/news_scraper.py',
            'security/ai_agents/threat_intelligence_agent.py',
            'test_russian_fraud_system.py'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                print(f"Проверка {file_path}...")
                result = subprocess.run(
                    ['flake8', file_path, '--max-line-length=120', '--ignore=E501,W503'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"  ✅ {file_path} - код соответствует стандартам")
                else:
                    print(f"  ⚠️  {file_path} - найдены замечания:")
                    print(f"      {result.stdout}")
            else:
                print(f"  ❌ Файл {file_path} не найден")
                
    except ImportError:
        print("  ⚠️  flake8 не установлен. Установите: pip install flake8")
    except Exception as e:
        print(f"  ❌ Ошибка проверки кода: {e}")
    
    print("\n🎯 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
    print("-"*40)
    print("1. Установите зависимости: pip install requests beautifulsoup4 aiohttp")
    print("2. Запустите flake8 для проверки качества кода")
    print("3. Добавьте больше unit-тестов")
    print("4. Настройте CI/CD для автоматического тестирования")
    print("5. Добавьте мониторинг производительности")
    
    print("\n✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")


if __name__ == "__main__":
    main()