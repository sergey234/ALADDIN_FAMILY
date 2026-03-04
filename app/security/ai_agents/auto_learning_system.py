#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Learning System - Система автоматического обучения ML моделей 24/7
"""

import asyncio
import json
import logging
import os
import schedule
import sys
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Добавляем путь к модулям

try:
    from security.ai_agents.russian_fraud_ml_models import RussianFraudMLModels
    from security.ai_agents.threat_intelligence_agent import ThreatIntelligenceAgent
except ImportError:
    # Fallback для случаев, когда модули недоступны
    RussianFraudMLModels = None
    ThreatIntelligenceAgent = None

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_learning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoLearningSystem:
    """
    Система автоматического обучения ML моделей 24/7
    """

    def __init__(self):
        """Инициализация системы автоматического обучения"""
        self.is_running = False
        self.learning_thread = None
        self.ml_models = None
        self.last_update = None
        self.update_interval = 3600  # 1 час в секундах
        self.data_collection_interval = 1800  # 30 минут в секундах

        # Создаем директории
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data/auto_learning', exist_ok=True)

        logger.info("🚀 Система автоматического обучения инициализирована")

    def start_auto_learning(self):
        """Запуск автоматического обучения"""
        if self.is_running:
            logger.warning("⚠️ Система уже запущена")
            return

        self.is_running = True
        logger.info("🎯 Запуск автоматического обучения 24/7")

        # Настройка расписания
        self._setup_schedule()

        # Запуск в отдельном потоке
        self.learning_thread = threading.Thread(target=self._run_scheduler)
        self.learning_thread.daemon = True
        self.learning_thread.start()

        logger.info("✅ Автоматическое обучение запущено")

    def stop_auto_learning(self):
        """Остановка автоматического обучения"""
        self.is_running = False
        logger.info("🛑 Остановка автоматического обучения")

    def _setup_schedule(self):
        """Настройка расписания задач"""
        # Сбор новых данных каждые 30 минут
        schedule.every(30).minutes.do(self._collect_new_data)

        # Переобучение моделей каждый час
        schedule.every().hour.do(self._retrain_models)

        # Анализ трендов каждые 6 часов
        schedule.every(6).hours.do(self._analyze_trends)

        # Генерация отчетов каждый день в 00:00
        schedule.every().day.at("00:00").do(self._generate_daily_report)

        # Очистка старых данных каждую неделю
        schedule.every().week.do(self._cleanup_old_data)

        logger.info("📅 Расписание задач настроено")

    def _run_scheduler(self):
        """Запуск планировщика задач"""
        logger.info("⏰ Планировщик задач запущен")

        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Проверка каждую минуту
            except Exception as e:
                logger.error(f"❌ Ошибка в планировщике: {e}")
                time.sleep(300)  # Пауза 5 минут при ошибке

    def _collect_new_data(self):
        """Сбор новых данных"""
        try:
            logger.info("📊 Начало сбора новых данных...")

            # Инициализация компонентов
            if not self.ml_models:
                self.ml_models = RussianFraudMLModels()

            # Сбор данных через ThreatIntelligenceAgent
            threat_agent = ThreatIntelligenceAgent()

            # Асинхронный сбор данных
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            new_data = loop.run_until_complete(
                threat_agent.collect_russian_fraud_data()
            )

            # Сохранение новых данных
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            data_file = f'data/auto_learning/new_data_{timestamp}.json'

            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)

            # Обновление статистики
            self._update_data_statistics(new_data)

            logger.info(f"✅ Новые данные собраны и сохранены: {data_file}")

        except Exception as e:
            logger.error(f"❌ Ошибка сбора данных: {e}")

    def _retrain_models(self):
        """Переобучение ML моделей"""
        try:
            logger.info("🤖 Начало переобучения ML моделей...")

            if not self.ml_models:
                self.ml_models = RussianFraudMLModels()

            # Переобучение моделей
            self.ml_models.create_region_analyzer()
            self.ml_models.create_fraud_classifier()
            self.ml_models.create_severity_predictor()

            # Сохранение обновленных моделей
            self.ml_models.save_models()

            # Сохранение метрик
            metrics = self.ml_models.generate_model_report()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            metrics_file = f'data/auto_learning/model_metrics_{timestamp}.json'

            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)

            self.last_update = datetime.now()

            logger.info("✅ ML модели переобучены и сохранены")

        except Exception as e:
            logger.error(f"❌ Ошибка переобучения моделей: {e}")

    def _analyze_trends(self):
        """Анализ трендов"""
        try:
            logger.info("📈 Начало анализа трендов...")

            threat_agent = ThreatIntelligenceAgent()

            # Загрузка последних данных
            latest_data = self._load_latest_data()
            if not latest_data:
                logger.warning("⚠️ Нет данных для анализа трендов")
                return

            # Асинхронный анализ
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            trends = loop.run_until_complete(
                threat_agent.analyze_russian_fraud_trends(latest_data)
            )

            # Сохранение анализа
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            trends_file = f'data/auto_learning/trends_{timestamp}.json'

            with open(trends_file, 'w', encoding='utf-8') as f:
                json.dump(trends, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ Анализ трендов завершен: {trends_file}")

        except Exception as e:
            logger.error(f"❌ Ошибка анализа трендов: {e}")

    def _generate_daily_report(self):
        """Генерация ежедневного отчета"""
        try:
            logger.info("📋 Генерация ежедневного отчета...")

            # Сбор статистики за день
            daily_stats = self._collect_daily_statistics()

            # Генерация отчета
            report = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'timestamp': datetime.now().isoformat(),
                'daily_statistics': daily_stats,
                'model_performance': self._get_model_performance(),
                'data_collection_summary': self._get_data_collection_summary(),
                'recommendations': self._generate_recommendations()
            }

            # Сохранение отчета
            report_file = f'data/auto_learning/daily_report_{datetime.now().strftime("%Y%m%d")}.json'

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ Ежедневный отчет создан: {report_file}")

        except Exception as e:
            logger.error(f"❌ Ошибка генерации отчета: {e}")

    def _cleanup_old_data(self):
        """Очистка старых данных"""
        try:
            logger.info("🧹 Очистка старых данных...")

            # Удаление файлов старше 30 дней
            cutoff_date = datetime.now() - timedelta(days=30)
            auto_learning_dir = 'data/auto_learning'

            if os.path.exists(auto_learning_dir):
                for filename in os.listdir(auto_learning_dir):
                    file_path = os.path.join(auto_learning_dir, filename)
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                        if file_time < cutoff_date:
                            os.remove(file_path)
                            logger.info(f"🗑️ Удален старый файл: {filename}")

            logger.info("✅ Очистка старых данных завершена")

        except Exception as e:
            logger.error(f"❌ Ошибка очистки данных: {e}")

    def _update_data_statistics(self, new_data: Dict[str, Any]):
        """Обновление статистики данных"""
        try:
            stats_file = 'data/auto_learning/data_statistics.json'

            # Загрузка существующей статистики
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
            else:
                stats = {
                    'total_collections': 0,
                    'total_records': 0,
                    'last_update': None,
                    'daily_collections': {}
                }

            # Обновление статистики
            stats['total_collections'] += 1
            stats['total_records'] += new_data.get('metadata', {}).get('total_records', 0)
            stats['last_update'] = datetime.now().isoformat()

            today = datetime.now().strftime('%Y-%m-%d')
            if today not in stats['daily_collections']:
                stats['daily_collections'][today] = 0
            stats['daily_collections'][today] += 1

            # Сохранение статистики
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"❌ Ошибка обновления статистики: {e}")

    def _load_latest_data(self) -> Dict[str, Any]:
        """Загрузка последних данных"""
        try:
            auto_learning_dir = 'data/auto_learning'
            if not os.path.exists(auto_learning_dir):
                return {}

            # Поиск последнего файла данных
            data_files = [f for f in os.listdir(auto_learning_dir) if f.startswith('new_data_')]
            if not data_files:
                return {}

            latest_file = sorted(data_files)[-1]
            with open(os.path.join(auto_learning_dir, latest_file), 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"❌ Ошибка загрузки данных: {e}")
            return {}

    def _collect_daily_statistics(self) -> Dict[str, Any]:
        """Сбор ежедневной статистики"""
        try:
            stats_file = 'data/auto_learning/data_statistics.json'
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"❌ Ошибка сбора статистики: {e}")
            return {}

    def _get_model_performance(self) -> Dict[str, Any]:
        """Получение производительности моделей"""
        try:
            if self.ml_models and hasattr(self.ml_models, 'model_metrics'):
                return self.ml_models.model_metrics
            return {}
        except Exception as e:
            logger.error(f"❌ Ошибка получения производительности: {e}")
            return {}

    def _get_data_collection_summary(self) -> Dict[str, Any]:
        """Получение сводки сбора данных"""
        try:
            auto_learning_dir = 'data/auto_learning'
            if not os.path.exists(auto_learning_dir):
                return {}

            files = os.listdir(auto_learning_dir)
            return {
                'total_data_files': len([f for f in files if f.startswith('new_data_')]),
                'total_trends_files': len([f for f in files if f.startswith('trends_')]),
                'total_metrics_files': len([f for f in files if f.startswith('model_metrics_')]),
                'last_collection': self.last_update.isoformat() if self.last_update else None
            }
        except Exception as e:
            logger.error(f"❌ Ошибка получения сводки: {e}")
            return {}

    def _generate_recommendations(self) -> List[str]:
        """Генерация рекомендаций"""
        recommendations = []

        # Проверка производительности моделей
        if self.ml_models and hasattr(self.ml_models, 'model_metrics'):
            for model_name, metrics in self.ml_models.model_metrics.items():
                if 'r2_score' in metrics and metrics['r2_score'] < 0.9:
                    recommendations.append(f"Улучшить точность модели {model_name}")
                elif 'accuracy' in metrics and metrics['accuracy'] < 0.8:
                    recommendations.append(f"Повысить точность модели {model_name}")

        # Проверка объема данных
        stats = self._collect_daily_statistics()
        if stats.get('total_records', 0) < 1000:
            recommendations.append("Увеличить объем собираемых данных")

        # Проверка частоты обновлений
        if not self.last_update or (datetime.now() - self.last_update).seconds > 7200:
            recommendations.append("Проверить работу системы сбора данных")

        return recommendations

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        return {
            'is_running': self.is_running,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'update_interval': self.update_interval,
            'data_collection_interval': self.data_collection_interval,
            'next_collection': schedule.next_run().isoformat() if schedule.jobs else None,
            'statistics': self._collect_daily_statistics()
        }


def main():
    """Основная функция для запуска системы автоматического обучения"""
    print("🚀 СИСТЕМА АВТОМАТИЧЕСКОГО ОБУЧЕНИЯ ML МОДЕЛЕЙ 24/7")
    print("=" * 60)

    # Создание и запуск системы
    auto_learning = AutoLearningSystem()

    try:
        # Запуск системы
        auto_learning.start_auto_learning()

        print("✅ Система автоматического обучения запущена!")
        print("📊 Сбор данных: каждые 30 минут")
        print("🤖 Переобучение моделей: каждый час")
        print("📈 Анализ трендов: каждые 6 часов")
        print("📋 Ежедневные отчеты: в 00:00")
        print("🧹 Очистка данных: еженедельно")
        print("\n⏰ Система работает 24/7. Нажмите Ctrl+C для остановки")

        # Основной цикл
        while True:
            time.sleep(60)

            # Вывод статуса каждый час
            if datetime.now().minute == 0:
                status = auto_learning.get_status()
                print(f"\n📊 Статус системы ({datetime.now().strftime('%H:%M')}):")
                print(f"   Сборов данных: {status['statistics'].get('total_collections', 0)}")
                print(f"   Записей: {status['statistics'].get('total_records', 0)}")
                print(f"   Последнее обновление: {status['last_update'] or 'Не было'}")

    except KeyboardInterrupt:
        print("\n🛑 Остановка системы...")
        auto_learning.stop_auto_learning()
        print("✅ Система остановлена")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        logger.error(f"Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
