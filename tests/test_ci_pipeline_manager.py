# -*- coding: utf-8 -*-
"""
Тесты для CIPipelineManager
ALADDIN Security System

Автор: AI Assistant
Дата: 2025-09-04
Версия: 1.0
"""

import unittest
import os
import sys
import tempfile
import shutil
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from security.ci_cd.ci_pipeline_manager import (
    CIPipelineManager,
    PipelineStatus,
    Environment,
    PipelineStage,
    PipelineConfig
)


class TestCIPipelineManager(unittest.TestCase):
    """Тесты для CIPipelineManager"""
    
    def setUp(self):
        """Настройка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
        
        # Создаем тестовую конфигурацию
        self.test_config = {
            "build_timeout": 60,
            "test_timeout": 30,
            "deploy_timeout": 60,
            "max_retries": 1,
            "parallel_jobs": 2,
            "notifications": False,
            "auto_deploy": False,
            "security_scan": False,
            "code_quality_check": False
        }
        
        self.manager = CIPipelineManager("TestCIPipelineManager", self.test_config)
    
    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Тест инициализации менеджера"""
        self.assertTrue(self.manager.initialize())
        self.assertEqual(self.manager.name, "TestCIPipelineManager")
        self.assertIsNotNone(self.manager.config)
    
    def test_create_pipeline(self):
        """Тест создания пайплайна"""
        self.manager.initialize()
        
        pipeline = self.manager.create_pipeline(
            "test_pipeline",
            Environment.DEVELOPMENT
        )
        
        self.assertIsNotNone(pipeline)
        self.assertEqual(pipeline.name, "test_pipeline")
        self.assertEqual(pipeline.environment, Environment.DEVELOPMENT)
        self.assertIn("test_pipeline", self.manager.pipelines)
    
    def test_pipeline_stages(self):
        """Тест этапов пайплайна"""
        self.manager.initialize()
        
        pipeline = self.manager.create_pipeline(
            "test_pipeline",
            Environment.DEVELOPMENT
        )
        
        # Проверяем, что этапы добавлены
        self.assertGreater(len(pipeline.stages), 0)
        
        # Проверяем типы этапов
        stage_types = [stage.stage_type for stage in pipeline.stages]
        self.assertIn(PipelineStage.BUILD, stage_types)
        self.assertIn(PipelineStage.TEST, stage_types)
        self.assertIn(PipelineStage.DEPLOY, stage_types)
    
    def test_pipeline_config(self):
        """Тест конфигурации пайплайна"""
        config = PipelineConfig(self.test_config)
        
        self.assertEqual(config.config["build_timeout"], 60)
        self.assertEqual(config.config["test_timeout"], 30)
        self.assertEqual(config.config["max_retries"], 1)
        self.assertFalse(config.config["notifications"])
        self.assertFalse(config.config["security_scan"])
    
    def test_pipeline_status(self):
        """Тест статуса пайплайна"""
        self.manager.initialize()
        
        pipeline = self.manager.create_pipeline(
            "test_pipeline",
            Environment.DEVELOPMENT
        )
        
        # Проверяем начальный статус
        self.assertEqual(pipeline.status, PipelineStatus.PENDING)
        
        # Проверяем статус этапов
        for stage in pipeline.stages:
            self.assertEqual(stage.status.value, "pending")
    
    def test_metrics(self):
        """Тест метрик"""
        self.manager.initialize()
        
        metrics = self.manager.get_metrics()
        
        self.assertIn("total_pipelines", metrics)
        self.assertIn("successful_pipelines", metrics)
        self.assertIn("failed_pipelines", metrics)
        self.assertIn("average_duration", metrics)
        self.assertIn("success_rate", metrics)
        
        # Начальные значения
        self.assertEqual(metrics["total_pipelines"], 0)
        self.assertEqual(metrics["successful_pipelines"], 0)
        self.assertEqual(metrics["failed_pipelines"], 0)
    
    def test_pipeline_history(self):
        """Тест истории пайплайнов"""
        self.manager.initialize()
        
        # Проверяем начальную историю
        history = self.manager.get_pipeline_history()
        self.assertIsInstance(history, list)
    
    def test_active_pipelines(self):
        """Тест активных пайплайнов"""
        self.manager.initialize()
        
        # Проверяем начальное состояние
        active = self.manager.get_active_pipelines()
        self.assertIsInstance(active, list)
        self.assertEqual(len(active), 0)
    
    def test_pipeline_creation_different_environments(self):
        """Тест создания пайплайнов для разных окружений"""
        self.manager.initialize()
        
        # Создаем пайплайны для разных окружений
        dev_pipeline = self.manager.create_pipeline("dev", Environment.DEVELOPMENT)
        staging_pipeline = self.manager.create_pipeline("staging", Environment.STAGING)
        prod_pipeline = self.manager.create_pipeline("prod", Environment.PRODUCTION)
        
        self.assertEqual(dev_pipeline.environment, Environment.DEVELOPMENT)
        self.assertEqual(staging_pipeline.environment, Environment.STAGING)
        self.assertEqual(prod_pipeline.environment, Environment.PRODUCTION)
    
    def test_pipeline_stage_creation(self):
        """Тест создания этапа пайплайна"""
        stage = PipelineStage(
            "test_stage",
            PipelineStage.TEST,
            "echo 'test'",
            timeout=30,
            retries=1
        )
        
        self.assertEqual(stage.name, "test_stage")
        self.assertEqual(stage.stage_type, PipelineStage.TEST)
        self.assertEqual(stage.command, "echo 'test'")
        self.assertEqual(stage.timeout, 30)
        self.assertEqual(stage.retries, 1)
        self.assertEqual(stage.status.value, "pending")
    
    def test_pipeline_to_dict(self):
        """Тест преобразования пайплайна в словарь"""
        self.manager.initialize()
        
        pipeline = self.manager.create_pipeline(
            "test_pipeline",
            Environment.DEVELOPMENT
        )
        
        pipeline_dict = pipeline.to_dict()
        
        self.assertIsInstance(pipeline_dict, dict)
        self.assertIn("name", pipeline_dict)
        self.assertIn("environment", pipeline_dict)
        self.assertIn("status", pipeline_dict)
        self.assertIn("stages", pipeline_dict)
        self.assertIn("start_time", pipeline_dict)
        self.assertIn("end_time", pipeline_dict)
        self.assertIn("duration", pipeline_dict)
    
    def test_stage_to_dict(self):
        """Тест преобразования этапа в словарь"""
        stage = PipelineStage(
            "test_stage",
            PipelineStage.BUILD,
            "echo 'build'",
            timeout=60,
            retries=2
        )
        
        stage_dict = stage.to_dict()
        
        self.assertIsInstance(stage_dict, dict)
        self.assertIn("name", stage_dict)
        self.assertIn("stage_type", stage_dict)
        self.assertIn("command", stage_dict)
        self.assertIn("timeout", stage_dict)
        self.assertIn("retries", stage_dict)
        self.assertIn("status", stage_dict)
        self.assertIn("start_time", stage_dict)
        self.assertIn("end_time", stage_dict)
        self.assertIn("duration", stage_dict)


if __name__ == '__main__':
    unittest.main()