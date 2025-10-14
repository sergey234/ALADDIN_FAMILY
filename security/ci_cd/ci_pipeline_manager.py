# -*- coding: utf-8 -*-
"""
CI/CD Pipeline Manager - Автоматизация развертывания
ALADDIN Security System

Автор: AI Assistant
Дата: 2025-09-04
Версия: 1.0
"""

from datetime import timedelta
from core.security_base import SecurityBase
import os
import sys
import json
import time
import logging
import subprocess
import threading
from datetime import datetime
# from typing import Dict, List, Optional, Any, Union  # Python 2.7 compatibility
from enum import Enum

# Добавляем путь к модулям безопасности


class PipelineStatus(Enum):
    """Статусы CI/CD пайплайна"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class BuildStatus(Enum):
    """Статусы сборки"""
    PENDING = "pending"
    BUILDING = "building"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TestStatus(Enum):
    """Статусы тестирования"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class DeploymentStatus(Enum):
    """Статусы развертывания"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLBACK = "rollback"


class Environment(Enum):
    """Окружения развертывания"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class PipelineStage(Enum):
    """Этапы пайплайна"""
    BUILD = "build"
    TEST = "test"
    SECURITY_SCAN = "security_scan"
    DEPLOY = "deploy"
    MONITOR = "monitor"
    CLEANUP = "cleanup"


class PipelineConfig:
    """Конфигурация пайплайна"""

    def __init__(self, config=None):
        self.config = config or {}

        # Настройки по умолчанию
        self.default_config = {
            "build_timeout": 1800,  # 30 минут
            "test_timeout": 900,    # 15 минут
            "deploy_timeout": 1200,  # 20 минут
            "max_retries": 3,
            "parallel_jobs": 4,
            "notifications": True,
            "auto_deploy": False,
            "security_scan": True,
            "code_quality_check": True,
            "performance_test": True,
            "environments": {
                "development": {
                    "auto_deploy": True,
                    "notifications": False,
                    "security_scan": False
                },
                "staging": {
                    "auto_deploy": True,
                    "notifications": True,
                    "security_scan": True
                },
                "production": {
                    "auto_deploy": False,
                    "notifications": True,
                    "security_scan": True,
                    "approval_required": True
                }
            }
        }

        # Объединяем конфигурации
        self._merge_configs()

    def _merge_configs(self):
        """Объединяет пользовательскую конфигурацию с настройками по умолчанию"""
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, dict) and isinstance(self.config[key], dict):
                for sub_key, sub_value in value.items():
                    if sub_key not in self.config[key]:
                        self.config[key][sub_key] = sub_value


class PipelineStageInstance:
    """Экземпляр этапа пайплайна"""

    def __init__(self, name, stage_type,
                 command, timeout=300,
                 retries=0, parallel=False):
        self.name = name
        self.stage_type = stage_type
        self.command = command
        self.timeout = timeout
        self.retries = retries
        self.parallel = parallel
        self.status = TestStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.duration = 0
        self.output = ""
        self.error = ""
        self.retry_count = 0

    def to_dict(self):
        """Преобразует этап в словарь"""
        return {
            "name": self.name,
            "stage_type": self.stage_type.value,
            "command": self.command,
            "timeout": self.timeout,
            "retries": self.retries,
            "parallel": self.parallel,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "output": self.output,
            "error": self.error,
            "retry_count": self.retry_count
        }


class Pipeline:
    """CI/CD пайплайн"""

    def __init__(self, name, environment, config):
        self.name = name
        self.environment = environment
        self.config = config
        self.status = PipelineStatus.PENDING
        self.stages = []
        self.start_time = None
        self.end_time = None
        self.duration = 0
        self.triggered_by = "manual"
        self.commit_hash = ""
        self.branch = ""
        self.build_number = 0
        self.artifacts = []
        self.logs = []
        self.metrics = {}

    def add_stage(self, stage):
        """Добавляет этап в пайплайн"""
        self.stages.append(stage)

    def to_dict(self):
        """Преобразует пайплайн в словарь"""
        return {
            "name": self.name,
            "environment": self.environment.value,
            "status": self.status.value,
            "stages": [stage.to_dict() for stage in self.stages],
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "triggered_by": self.triggered_by,
            "commit_hash": self.commit_hash,
            "branch": self.branch,
            "build_number": self.build_number,
            "artifacts": self.artifacts,
            "logs": self.logs,
            "metrics": self.metrics
        }


class CIPipelineManager(SecurityBase):
    """Менеджер CI/CD пайплайнов"""

    def __init__(self, name="CIPipelineManager",
                 config=None):
        super(CIPipelineManager, self).__init__(name)

        # Конфигурация
        self.pipeline_config = PipelineConfig(config)
        self.config = self.pipeline_config.config

        # Состояние
        self.pipelines = {}
        self.active_pipelines = {}
        self.pipeline_history = []
        self.max_history = 100

        # Настройки
        self.auto_cleanup = True
        self.cleanup_after_days = 30
        self.notification_webhooks = []

        # Логирование
        self.logger = logging.getLogger("CIPipelineManager")

        # Метрики
        self.metrics = {
            "total_pipelines": 0,
            "successful_pipelines": 0,
            "failed_pipelines": 0,
            "average_duration": 0,
            "success_rate": 0.0
        }

    def initialize(self):
        """Инициализация менеджера пайплайнов"""
        try:
            self.logger.info("Инициализация CIPipelineManager")

            # Создаем директории
            self._create_directories()

            # Загружаем историю пайплайнов
            self._load_pipeline_history()

            # Инициализируем базовые пайплайны
            self._initialize_default_pipelines()

            self.logger.info("CIPipelineManager инициализирован успешно")
            return True

        except Exception as e:
            self.logger.error("Ошибка инициализации CIPipelineManager: {}".format(str(e)))
            return False

    def _create_directories(self):
        """Создает необходимые директории"""
        directories = [
            "data/ci_cd/pipelines",
            "data/ci_cd/logs",
            "data/ci_cd/artifacts",
            "data/ci_cd/configs"
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def _load_pipeline_history(self):
        """Загружает историю пайплайнов"""
        try:
            history_file = "data/ci_cd/pipeline_history.json"
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    self.pipeline_history = json.load(f)
        except Exception as e:
            self.logger.warning("Не удалось загрузить историю пайплайнов: {}".format(str(e)))

    def _save_pipeline_history(self):
        """Сохраняет историю пайплайнов"""
        try:
            history_file = "data/ci_cd/pipeline_history.json"
            with open(history_file, 'w') as f:
                json.dump(self.pipeline_history, f, indent=2)
        except Exception as e:
            self.logger.error("Не удалось сохранить историю пайплайнов: {}".format(str(e)))

    def _initialize_default_pipelines(self):
        """Инициализирует базовые пайплайны"""
        # Пайплайн для разработки
        self.create_pipeline(
            "development_pipeline",
            Environment.DEVELOPMENT
        )

        # Пайплайн для тестирования
        self.create_pipeline(
            "staging_pipeline",
            Environment.STAGING
        )

        # Пайплайн для продакшена
        self.create_pipeline(
            "production_pipeline",
            Environment.PRODUCTION
        )

    def create_pipeline(self, name, environment, config=None):
        """Создает новый пайплайн"""
        try:
            pipeline_config = PipelineConfig(config)
            pipeline = Pipeline(name, environment, pipeline_config)

            # Добавляем базовые этапы
            self._add_default_stages(pipeline)

            self.pipelines[name] = pipeline
            self.logger.info("Создан пайплайн: {} для окружения: {}".format(name, environment.value))

            return pipeline

        except Exception as e:
            self.logger.error("Ошибка создания пайплайна {}: {}".format(name, str(e)))
            raise

    def _add_default_stages(self, pipeline):
        """Добавляет базовые этапы в пайплайн"""
        # Этап сборки
        build_stage = PipelineStage(
            "build",
            PipelineStage.BUILD,
            "python -m pip install -r requirements.txt && python -m build",
            timeout=self.config["build_timeout"],
            retries=self.config["max_retries"]
        )
        pipeline.add_stage(build_stage)

        # Этап тестирования
        test_stage = PipelineStage(
            "test",
            PipelineStage.TEST,
            "python -m pytest tests/ -v --cov=security --cov-report=html",
            timeout=self.config["test_timeout"],
            retries=self.config["max_retries"]
        )
        pipeline.add_stage(test_stage)

        # Этап проверки безопасности
        if self.config["security_scan"]:
            security_stage = PipelineStage(
                "security_scan",
                PipelineStage.SECURITY_SCAN,
                "python -m bandit -r security/ -f json -o security_report.json",
                timeout=600,
                retries=1
            )
            pipeline.add_stage(security_stage)

        # Этап проверки качества кода
        if self.config["code_quality_check"]:
            quality_stage = PipelineStage(
                "code_quality",
                PipelineStage.TEST,
                "python -m flake8 security/ --max-line-length=120 --format=json",
                timeout=300,
                retries=1
            )
            pipeline.add_stage(quality_stage)

        # Этап развертывания
        deploy_stage = PipelineStage(
            "deploy",
            PipelineStage.DEPLOY,
            "python scripts/deploy.py --environment={}".format(pipeline.environment.value),
            timeout=self.config["deploy_timeout"],
            retries=self.config["max_retries"]
        )
        pipeline.add_stage(deploy_stage)

    def run_pipeline(self, pipeline_name,
                     triggered_by="manual",
                     commit_hash="",
                     branch="main"):
        """Запускает пайплайн"""
        try:
            if pipeline_name not in self.pipelines:
                self.logger.error("Пайплайн {} не найден".format(pipeline_name))
                return False

            pipeline = self.pipelines[pipeline_name]

            # Проверяем, не запущен ли уже пайплайн
            if pipeline_name in self.active_pipelines:
                self.logger.warning("Пайплайн {} уже запущен".format(pipeline_name))
                return False

            # Настраиваем пайплайн
            pipeline.triggered_by = triggered_by
            pipeline.commit_hash = commit_hash
            pipeline.branch = branch
            pipeline.build_number = self.metrics["total_pipelines"] + 1
            pipeline.status = PipelineStatus.RUNNING
            pipeline.start_time = datetime.now()

            # Добавляем в активные
            self.active_pipelines[pipeline_name] = pipeline

            # Запускаем в отдельном потоке
            thread = threading.Thread(
                target=self._execute_pipeline,
                args=(pipeline,)
            )
            thread.daemon = True
            thread.start()

            self.logger.info("Запущен пайплайн: {} (build #{})".format(pipeline_name, pipeline.build_number))
            return True

        except Exception as e:
            self.logger.error("Ошибка запуска пайплайна {}: {}".format(pipeline_name, str(e)))
            return False

    def _execute_pipeline(self, pipeline):
        """Выполняет пайплайн"""
        try:
            self.logger.info("Выполнение пайплайна: {}".format(pipeline.name))

            # Выполняем этапы последовательно
            for stage in pipeline.stages:
                if pipeline.status == PipelineStatus.CANCELLED:
                    break

                self._execute_stage(pipeline, stage)

                # Если этап не удался и не настроены повторы
                if stage.status == TestStatus.FAILED and stage.retry_count >= stage.retries:
                    pipeline.status = PipelineStatus.FAILED
                    break

            # Завершаем пайплайн
            pipeline.end_time = datetime.now()
            pipeline.duration = (pipeline.end_time - pipeline.start_time).total_seconds()

            if pipeline.status == PipelineStatus.RUNNING:
                pipeline.status = PipelineStatus.SUCCESS

            # Обновляем метрики
            self._update_metrics(pipeline)

            # Сохраняем в историю
            self._save_pipeline_to_history(pipeline)

            # Уведомления
            if self.config["notifications"]:
                self._send_notifications(pipeline)

            # Удаляем из активных
            if pipeline.name in self.active_pipelines:
                del self.active_pipelines[pipeline.name]

            self.logger.info("Пайплайн {} завершен со статусом: {}".format(
                pipeline.name, pipeline.status.value
            ))

        except Exception as e:
            self.logger.error("Ошибка выполнения пайплайна {}: {}".format(pipeline.name, str(e)))
            pipeline.status = PipelineStatus.FAILED
            pipeline.end_time = datetime.now()
            pipeline.duration = (pipeline.end_time - pipeline.start_time).total_seconds()

    def _execute_stage(self, pipeline, stage):
        """Выполняет этап пайплайна"""
        try:
            self.logger.info("Выполнение этапа: {} в пайплайне: {}".format(stage.name, pipeline.name))

            stage.status = TestStatus.RUNNING
            stage.start_time = datetime.now()

            # Выполняем команду
            result = subprocess.run(
                stage.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=stage.timeout
            )

            stage.end_time = datetime.now()
            stage.duration = (stage.end_time - stage.start_time).total_seconds()
            stage.output = result.stdout
            stage.error = result.stderr

            if result.returncode == 0:
                stage.status = TestStatus.PASSED
                self.logger.info("Этап {} выполнен успешно".format(stage.name))
            else:
                stage.status = TestStatus.FAILED
                self.logger.error("Этап {} завершился с ошибкой".format(stage.name))

                # Повторяем при необходимости
                if stage.retry_count < stage.retries:
                    stage.retry_count += 1
                    self.logger.info("Повтор этапа {} (попытка {}/{})".format(
                        stage.name, stage.retry_count, stage.retries
                    ))
                    time.sleep(5)  # Пауза перед повтором
                    self._execute_stage(pipeline, stage)

        except subprocess.TimeoutExpired:
            stage.status = TestStatus.FAILED
            stage.error = "Timeout: этап превысил максимальное время выполнения"
            self.logger.error("Этап {} превысил время выполнения".format(stage.name))

        except Exception as e:
            stage.status = TestStatus.FAILED
            stage.error = str(e)
            self.logger.error("Ошибка выполнения этапа {}: {}".format(stage.name, str(e)))

    def _update_metrics(self, pipeline):
        """Обновляет метрики"""
        self.metrics["total_pipelines"] += 1

        if pipeline.status == PipelineStatus.SUCCESS:
            self.metrics["successful_pipelines"] += 1
        elif pipeline.status == PipelineStatus.FAILED:
            self.metrics["failed_pipelines"] += 1

        # Обновляем среднюю продолжительность
        total_duration = self.metrics["average_duration"] * (self.metrics["total_pipelines"] - 1)
        total_duration += pipeline.duration
        self.metrics["average_duration"] = total_duration / self.metrics["total_pipelines"]

        # Обновляем процент успеха
        if self.metrics["total_pipelines"] > 0:
            self.metrics["success_rate"] = (
                self.metrics["successful_pipelines"] / self.metrics["total_pipelines"]
            ) * 100

    def _save_pipeline_to_history(self, pipeline):
        """Сохраняет пайплайн в историю"""
        self.pipeline_history.append(pipeline.to_dict())

        # Ограничиваем размер истории
        if len(self.pipeline_history) > self.max_history:
            self.pipeline_history = self.pipeline_history[-self.max_history:]

        self._save_pipeline_history()

    def _send_notifications(self, pipeline):
        """Отправляет уведомления о завершении пайплайна"""
        try:
            # Здесь можно добавить отправку уведомлений
            # через webhooks, email, Slack и т.д.
            self.logger.info("Отправка уведомлений для пайплайна: {}".format(pipeline.name))

        except Exception as e:
            self.logger.error("Ошибка отправки уведомлений: {}".format(str(e)))

    def get_pipeline_status(self, pipeline_name):
        """Получает статус пайплайна"""
        if pipeline_name in self.pipelines:
            return self.pipelines[pipeline_name].to_dict()
        return None

    def get_active_pipelines(self):
        """Получает список активных пайплайнов"""
        return [pipeline.to_dict() for pipeline in self.active_pipelines.values()]

    def get_pipeline_history(self, limit=50):
        """Получает историю пайплайнов"""
        return self.pipeline_history[-limit:] if self.pipeline_history else []

    def cancel_pipeline(self, pipeline_name):
        """Отменяет пайплайн"""
        try:
            if pipeline_name in self.active_pipelines:
                pipeline = self.active_pipelines[pipeline_name]
                pipeline.status = PipelineStatus.CANCELLED
                self.logger.info("Пайплайн {} отменен".format(pipeline_name))
                return True
            return False
        except Exception as e:
            self.logger.error("Ошибка отмены пайплайна {}: {}".format(pipeline_name, str(e)))
            return False

    def get_metrics(self):
        """Получает метрики пайплайнов"""
        return self.metrics.copy()

    def cleanup_old_pipelines(self):
        """Очищает старые пайплайны"""
        try:
            if not self.auto_cleanup:
                return

            cutoff_date = datetime.now() - timedelta(days=self.cleanup_after_days)

            # Фильтруем историю
            self.pipeline_history = [
                pipeline for pipeline in self.pipeline_history
                if datetime.fromisoformat(pipeline["start_time"]) > cutoff_date
            ]

            self._save_pipeline_history()
            self.logger.info("Очистка старых пайплайнов завершена")

        except Exception as e:
            self.logger.error("Ошибка очистки пайплайнов: {}".format(str(e)))

    def stop(self):
        """Остановка менеджера пайплайнов"""
        try:
            self.logger.info("Остановка CIPipelineManager")

            # Отменяем все активные пайплайны
            for pipeline_name in list(self.active_pipelines.keys()):
                self.cancel_pipeline(pipeline_name)

            # Очищаем старые пайплайны
            self.cleanup_old_pipelines()

            self.logger.info("CIPipelineManager остановлен")

        except Exception as e:
            self.logger.error("Ошибка остановки CIPipelineManager: {}".format(str(e)))


# Дополнительные импорты для работы с датами
