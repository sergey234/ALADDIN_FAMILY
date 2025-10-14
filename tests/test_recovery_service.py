"""
Тесты для сервиса автоматического восстановления после атак

Этот модуль содержит тесты для function_34: RecoveryService
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from security.reactive.recovery_service import (
    RecoveryService,
    RecoveryType,
    RecoveryStatus,
    RecoveryPriority,
    RecoveryMethod,
    RecoveryTask,
    RecoveryPlan,
    RecoveryReport
)


class TestRecoveryService:
    """Тесты для RecoveryService"""

    @pytest.fixture
    def recovery_service(self):
        """Фикстура для создания экземпляра RecoveryService"""
        return RecoveryService()

    def test_initialization(self, recovery_service):
        """Тест инициализации сервиса"""
        assert recovery_service.name == "RecoveryService"
        assert recovery_service.automatic_recovery_enabled is True
        assert recovery_service.family_notifications_enabled is True
        assert recovery_service.recovery_monitoring_enabled is True
        assert len(recovery_service.recovery_rules) > 0
        assert len(recovery_service.backup_locations) > 0
        assert recovery_service.family_recovery_settings is not None

    def test_create_recovery_plan_malware_incident(self, recovery_service):
        """Тест создания плана восстановления для инцидента с вредоносным ПО"""
        incident_data = {
            "threat_type": "malware",
            "severity": "high",
            "target_entity": "system",
            "affected_entities": ["system", "data"]
        }
        
        plan = recovery_service.create_recovery_plan(
            incident_id="test_incident_1",
            incident_data=incident_data,
            user_id="test_user",
            family_role="parent"
        )
        
        assert plan is not None
        assert plan.incident_id == "test_incident_1"
        assert len(plan.recovery_tasks) > 0
        assert plan.status == RecoveryStatus.PENDING
        assert plan.estimated_duration > 0
        assert "affected_family_members" in plan.family_impact

    def test_create_recovery_plan_data_breach(self, recovery_service):
        """Тест создания плана восстановления для утечки данных"""
        incident_data = {
            "threat_type": "data_breach",
            "severity": "critical",
            "target_entity": "database",
            "affected_entities": ["data", "user_profiles"]
        }
        
        plan = recovery_service.create_recovery_plan(
            incident_id="test_incident_2",
            incident_data=incident_data,
            user_id="test_user",
            family_role="child"
        )
        
        assert plan is not None
        assert plan.incident_id == "test_incident_2"
        assert len(plan.recovery_tasks) > 0
        assert plan.family_impact["impact_level"] == "high"
        assert plan.family_impact["family_support_needed"] is True

    def test_create_recovery_plan_elderly_user(self, recovery_service):
        """Тест создания плана восстановления для пожилого пользователя"""
        incident_data = {
            "threat_type": "profile_corruption",
            "severity": "medium",
            "target_entity": "user_profile",
            "affected_entities": ["profile"]
        }
        
        plan = recovery_service.create_recovery_plan(
            incident_id="test_incident_3",
            incident_data=incident_data,
            user_id="elderly_user",
            family_role="elderly"
        )
        
        assert plan is not None
        assert plan.incident_id == "test_incident_3"
        assert len(plan.recovery_tasks) > 0
        assert plan.family_impact["family_support_needed"] is True

    def test_execute_recovery_plan(self, recovery_service):
        """Тест выполнения плана восстановления"""
        # Создаем план восстановления
        incident_data = {
            "threat_type": "malware",
            "severity": "high",
            "target_entity": "system"
        }
        
        plan = recovery_service.create_recovery_plan(
            incident_id="test_incident_4",
            incident_data=incident_data,
            user_id="test_user",
            family_role="parent"
        )
        
        assert plan is not None
        
        # Выполняем план
        success = recovery_service.execute_recovery_plan(plan.plan_id)
        
        assert success is True
        assert plan.status in [RecoveryStatus.COMPLETED, RecoveryStatus.FAILED]
        assert len(recovery_service.recovery_reports) > 0

    def test_recovery_task_execution(self, recovery_service):
        """Тест выполнения задачи восстановления"""
        task = RecoveryTask(
            task_id="test_task_1",
            recovery_type=RecoveryType.DATA_RECOVERY,
            priority=RecoveryPriority.HIGH,
            method=RecoveryMethod.BACKUP_RESTORE,
            target_entity="test_data",
            user_id="test_user",
            family_role="parent"
        )
        
        success = recovery_service._execute_recovery_task(task)
        
        assert success is True
        assert task.status == RecoveryStatus.COMPLETED
        assert task.progress_percentage == 100.0
        assert task.completed_time is not None

    def test_family_recovery_tasks_creation(self, recovery_service):
        """Тест создания семейных задач восстановления"""
        incident_data = {
            "threat_type": "account_compromise",
            "severity": "high",
            "target_entity": "user_account"
        }
        
        tasks = recovery_service._create_family_recovery_tasks(
            incident_data=incident_data,
            user_id="child_user",
            family_role="child"
        )
        
        assert len(tasks) > 0
        
        # Проверяем, что есть задача восстановления семейного профиля
        family_profile_tasks = [task for task in tasks 
                              if task.recovery_type == RecoveryType.FAMILY_PROFILE_RECOVERY]
        assert len(family_profile_tasks) > 0
        assert family_profile_tasks[0].family_role == "child"

    def test_parental_controls_recovery(self, recovery_service):
        """Тест восстановления родительского контроля"""
        incident_data = {
            "threat_type": "settings_corruption",
            "severity": "medium",
            "target_entity": "parental_controls"
        }
        
        tasks = recovery_service._create_family_recovery_tasks(
            incident_data=incident_data,
            user_id="parent_user",
            family_role="parent"
        )
        
        # Проверяем, что есть задача восстановления настроек безопасности
        security_tasks = [task for task in tasks 
                         if task.recovery_type == RecoveryType.SECURITY_SETTINGS_RECOVERY]
        assert len(security_tasks) > 0
        assert security_tasks[0].family_role == "parent"

    def test_recovery_rule_evaluation(self, recovery_service):
        """Тест оценки правил восстановления"""
        incident_data = {
            "threat_type": "malware",
            "severity": "high"
        }
        
        rule = recovery_service.recovery_rules["malware_recovery"]
        
        result = recovery_service._evaluate_recovery_rule(
            incident_data=incident_data,
            rule=rule,
            user_id="test_user",
            family_role="parent"
        )
        
        assert result is True

    def test_family_impact_assessment(self, recovery_service):
        """Тест оценки семейного воздействия"""
        incident_data = {
            "threat_type": "data_breach",
            "severity": "critical"
        }
        
        impact = recovery_service._assess_family_impact(
            incident_data=incident_data,
            user_id="child_user",
            family_role="child"
        )
        
        assert "affected_family_members" in impact
        assert "impact_level" in impact
        assert "recovery_priority" in impact
        assert impact["impact_level"] == "high"
        assert impact["family_support_needed"] is True

    def test_recovery_duration_calculation(self, recovery_service):
        """Тест расчета времени восстановления"""
        tasks = [
            RecoveryTask(
                task_id="task1",
                recovery_type=RecoveryType.DATA_RECOVERY,
                priority=RecoveryPriority.HIGH,
                method=RecoveryMethod.BACKUP_RESTORE,
                target_entity="data"
            ),
            RecoveryTask(
                task_id="task2",
                recovery_type=RecoveryType.SYSTEM_RECOVERY,
                priority=RecoveryPriority.MEDIUM,
                method=RecoveryMethod.SYSTEM_RESET,
                target_entity="system"
            )
        ]
        
        duration = recovery_service._calculate_recovery_duration(tasks)
        
        assert duration > 0
        assert duration == 45  # 15 + 30 минут

    def test_get_recovery_summary_user_specific(self, recovery_service):
        """Тест получения сводки восстановления для конкретного пользователя"""
        # Создаем несколько планов восстановления
        incident_data = {
            "threat_type": "malware",
            "severity": "high",
            "target_entity": "system"
        }
        
        plan1 = recovery_service.create_recovery_plan(
            incident_id="incident_1",
            incident_data=incident_data,
            user_id="user1",
            family_role="parent"
        )
        
        plan2 = recovery_service.create_recovery_plan(
            incident_id="incident_2",
            incident_data=incident_data,
            user_id="user1",
            family_role="parent"
        )
        
        # Выполняем планы
        recovery_service.execute_recovery_plan(plan1.plan_id)
        recovery_service.execute_recovery_plan(plan2.plan_id)
        
        # Получаем сводку
        summary = recovery_service.get_recovery_summary(user_id="user1")
        
        assert summary is not None
        assert summary["total_plans"] >= 2
        assert summary["total_tasks"] > 0
        assert "success_rate" in summary
        assert "average_recovery_time" in summary
        assert "family_impact_summary" in summary

    def test_get_recovery_summary_all_users(self, recovery_service):
        """Тест получения общей сводки восстановления"""
        # Создаем планы для разных пользователей
        users = ["user1", "user2", "user3"]
        for i, user in enumerate(users):
            incident_data = {
                "threat_type": "malware",
                "severity": "high",
                "target_entity": "system"
            }
            
            plan = recovery_service.create_recovery_plan(
                incident_id=f"incident_{i}",
                incident_data=incident_data,
                user_id=user,
                family_role="parent"
            )
            
            recovery_service.execute_recovery_plan(plan.plan_id)
        
        # Получаем общую сводку
        summary = recovery_service.get_recovery_summary()
        
        assert summary is not None
        assert summary["total_plans"] >= 3
        assert summary["total_tasks"] > 0
        assert "family_impact_summary" in summary

    def test_get_family_recovery_status(self, recovery_service):
        """Тест получения статуса семейного восстановления"""
        status = recovery_service.get_family_recovery_status()
        
        assert status is not None
        assert "automatic_recovery_enabled" in status
        assert "family_notifications_enabled" in status
        assert "recovery_monitoring_enabled" in status
        assert "total_recoveries" in status
        assert "successful_recoveries" in status
        assert "failed_recoveries" in status
        assert "success_rate" in status
        assert "family_recovery_settings" in status
        assert "backup_locations" in status
        assert "recovery_rules" in status

    def test_get_status(self, recovery_service):
        """Тест получения статуса сервиса"""
        status = recovery_service.get_status()
        
        assert status is not None
        assert status["service_name"] == "RecoveryService"
        assert "status" in status
        assert "recovery_plans" in status
        assert "recovery_tasks" in status
        assert "recovery_reports" in status
        assert "backup_locations" in status
        assert "recovery_rules" in status
        assert "family_protection_enabled" in status
        assert "automatic_recovery_enabled" in status
        assert "total_recoveries" in status
        assert "uptime" in status

    def test_recovery_recommendations_generation(self, recovery_service):
        """Тест генерации рекомендаций по восстановлению"""
        # Создаем план с различными типами восстановления
        incident_data = {
            "threat_type": "malware",
            "severity": "high",
            "target_entity": "system"
        }
        
        plan = recovery_service.create_recovery_plan(
            incident_id="test_incident_5",
            incident_data=incident_data,
            user_id="test_user",
            family_role="child"
        )
        
        recommendations = recovery_service._generate_recovery_recommendations(plan)
        
        assert len(recommendations) > 0
        assert any("резервные копии" in rec.lower() for rec in recommendations)
        assert any("безопасность" in rec.lower() for rec in recommendations)

    def test_security_event_creation(self, recovery_service):
        """Тест создания событий безопасности"""
        # Создаем план восстановления
        incident_data = {
            "threat_type": "malware",
            "severity": "high",
            "target_entity": "system"
        }
        
        plan = recovery_service.create_recovery_plan(
            incident_id="test_incident_6",
            incident_data=incident_data,
            user_id="test_user",
            family_role="parent"
        )
        
        # Проверяем, что событие было создано
        events = recovery_service.get_security_events()
        assert len(events) > 0
        
        # Проверяем, что есть событие создания плана
        plan_events = [event for event in events 
                      if event.get("event_type") == "recovery_plan_created"]
        assert len(plan_events) > 0

    def test_recovery_task_progress_tracking(self, recovery_service):
        """Тест отслеживания прогресса задач восстановления"""
        task = RecoveryTask(
            task_id="test_task_2",
            recovery_type=RecoveryType.SYSTEM_RECOVERY,
            priority=RecoveryPriority.HIGH,
            method=RecoveryMethod.SYSTEM_RESET,
            target_entity="test_system",
            user_id="test_user",
            family_role="parent"
        )
        
        # Выполняем задачу
        success = recovery_service._execute_recovery_task(task)
        
        assert success is True
        assert task.status == RecoveryStatus.COMPLETED
        assert task.progress_percentage == 100.0
        assert task.started_time is not None
        assert task.completed_time is not None
        assert task.completed_time > task.started_time

    def test_family_recovery_history_tracking(self, recovery_service):
        """Тест отслеживания истории семейного восстановления"""
        # Создаем несколько планов для одного пользователя
        incident_data = {
            "threat_type": "malware",
            "severity": "high",
            "target_entity": "system"
        }
        
        for i in range(3):
            plan = recovery_service.create_recovery_plan(
                incident_id=f"incident_{i}",
                incident_data=incident_data,
                user_id="family_user",
                family_role="parent"
            )
            
            recovery_service.execute_recovery_plan(plan.plan_id)
        
        # Проверяем историю
        status = recovery_service.get_family_recovery_status()
        assert "family_recovery_history" in status
        assert "family_user" in status["family_recovery_history"]
        assert status["family_recovery_history"]["family_user"] >= 3
