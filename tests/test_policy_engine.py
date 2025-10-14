# -*- coding: utf-8 -*-
"""
Тесты для PolicyEngine
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from security.preliminary.policy_engine import (
    PolicyEngine, PolicyType, PolicyStatus, PolicyPriority, ActionType,
    ConditionOperator, PolicyCondition, PolicyAction, SecurityPolicy, PolicyEvaluation
)
from core.security_base import IncidentSeverity


class TestPolicyEngine:
    """Тесты для PolicyEngine"""
    
    @pytest.fixture
    def policy_engine(self):
        """Создание экземпляра PolicyEngine"""
        return PolicyEngine()
    
    def test_initialization(self, policy_engine):
        """Тест инициализации"""
        assert policy_engine.name == "PolicyEngine"
        assert len(policy_engine.policies) > 0
        assert policy_engine.evaluation_timeout == 5.0
        assert policy_engine.max_evaluations_per_request == 100
        assert policy_engine.enable_caching is True
    
    def test_create_policy(self, policy_engine):
        """Тест создания политики"""
        policy_data = {
            "policy_id": "test_policy",
            "name": "Тестовая политика",
            "description": "Описание тестовой политики",
            "policy_type": "access_control",
            "priority": "high",
            "conditions": [
                {
                    "field": "user_role",
                    "operator": "equals",
                    "value": "admin",
                    "description": "Роль администратора"
                }
            ],
            "actions": [
                {
                    "action_type": "allow",
                    "parameters": {"reason": "Администратор"},
                    "description": "Разрешить доступ"
                }
            ],
            "target_users": ["admin"]
        }
        
        result = policy_engine.create_policy(policy_data)
        assert result is True
        assert "test_policy" in policy_engine.policies
        
        policy = policy_engine.policies["test_policy"]
        assert policy.name == "Тестовая политика"
        assert policy.policy_type == PolicyType.ACCESS_CONTROL
        assert policy.priority == PolicyPriority.HIGH
        assert len(policy.conditions) == 1
        assert len(policy.actions) == 1
    
    def test_create_policy_duplicate(self, policy_engine):
        """Тест создания дублирующейся политики"""
        policy_data = {
            "policy_id": "child_content_filter",  # Уже существует
            "name": "Дублирующая политика",
            "description": "Описание",
            "policy_type": "content_filtering",
            "priority": "medium"
        }
        
        result = policy_engine.create_policy(policy_data)
        assert result is False
    
    def test_evaluate_condition_equals(self, policy_engine):
        """Тест оценки условия EQUALS"""
        condition = PolicyCondition(
            field="user_role",
            operator=ConditionOperator.EQUALS,
            value="admin"
        )
        
        context = {"user_role": "admin"}
        assert policy_engine._evaluate_condition(condition, context) is True
        
        context = {"user_role": "user"}
        assert policy_engine._evaluate_condition(condition, context) is False
    
    def test_evaluate_condition_not_equals(self, policy_engine):
        """Тест оценки условия NOT_EQUALS"""
        condition = PolicyCondition(
            field="user_role",
            operator=ConditionOperator.NOT_EQUALS,
            value="guest"
        )
        
        context = {"user_role": "admin"}
        assert policy_engine._evaluate_condition(condition, context) is True
        
        context = {"user_role": "guest"}
        assert policy_engine._evaluate_condition(condition, context) is False
    
    def test_evaluate_condition_contains(self, policy_engine):
        """Тест оценки условия CONTAINS"""
        condition = PolicyCondition(
            field="content",
            operator=ConditionOperator.CONTAINS,
            value="spam"
        )
        
        context = {"content": "This is spam content"}
        assert policy_engine._evaluate_condition(condition, context) is True
        
        context = {"content": "This is normal content"}
        assert policy_engine._evaluate_condition(condition, context) is False
    
    def test_evaluate_condition_greater_than(self, policy_engine):
        """Тест оценки условия GREATER_THAN"""
        condition = PolicyCondition(
            field="user_age",
            operator=ConditionOperator.GREATER_THAN,
            value=18
        )
        
        context = {"user_age": 25}
        assert policy_engine._evaluate_condition(condition, context) is True
        
        context = {"user_age": 16}
        assert policy_engine._evaluate_condition(condition, context) is False
    
    def test_evaluate_condition_less_than(self, policy_engine):
        """Тест оценки условия LESS_THAN"""
        condition = PolicyCondition(
            field="user_age",
            operator=ConditionOperator.LESS_THAN,
            value=18
        )
        
        context = {"user_age": 16}
        assert policy_engine._evaluate_condition(condition, context) is True
        
        context = {"user_age": 25}
        assert policy_engine._evaluate_condition(condition, context) is False
    
    def test_evaluate_condition_in(self, policy_engine):
        """Тест оценки условия IN"""
        condition = PolicyCondition(
            field="content_category",
            operator=ConditionOperator.IN,
            value=["adult", "violence", "gambling"]
        )
        
        context = {"content_category": "adult"}
        assert policy_engine._evaluate_condition(condition, context) is True
        
        context = {"content_category": "education"}
        assert policy_engine._evaluate_condition(condition, context) is False
    
    def test_evaluate_condition_not_in(self, policy_engine):
        """Тест оценки условия NOT_IN"""
        condition = PolicyCondition(
            field="content_category",
            operator=ConditionOperator.NOT_IN,
            value=["adult", "violence", "gambling"]
        )
        
        context = {"content_category": "education"}
        assert policy_engine._evaluate_condition(condition, context) is True
        
        context = {"content_category": "adult"}
        assert policy_engine._evaluate_condition(condition, context) is False
    
    def test_evaluate_time_range(self, policy_engine):
        """Тест оценки временного диапазона"""
        time_range = {"start": "22:00", "end": "07:00"}
        
        # Ночное время
        current_time = datetime.now().replace(hour=23, minute=30).time()
        assert policy_engine._evaluate_time_range(current_time, time_range) is True
        
        # Дневное время
        current_time = datetime.now().replace(hour=14, minute=30).time()
        assert policy_engine._evaluate_time_range(current_time, time_range) is False
        
        # Раннее утро
        current_time = datetime.now().replace(hour=6, minute=30).time()
        assert policy_engine._evaluate_time_range(current_time, time_range) is True
    
    def test_evaluate_time_range_string(self, policy_engine):
        """Тест оценки временного диапазона со строкой"""
        time_range = {"start": "22:00", "end": "07:00"}
        
        # Ночное время
        current_time = "23:30"
        assert policy_engine._evaluate_time_range(current_time, time_range) is True
        
        # Дневное время
        current_time = "14:30"
        assert policy_engine._evaluate_time_range(current_time, time_range) is False
    
    def test_evaluate_policy_success(self, policy_engine):
        """Тест успешной оценки политики"""
        # Используем существующую политику child_content_filter
        policy_id = "child_content_filter"
        user_id = "children"  # Используем ID из целевой группы
        request_context = {
            "user_age": 15,
            "content_category": "adult"
        }
        
        evaluation = policy_engine.evaluate_policy(policy_id, user_id, request_context)
        
        assert evaluation.policy_id == policy_id
        assert evaluation.user_id == user_id
        assert evaluation.matched is True
        assert len(evaluation.matched_conditions) > 0
        assert len(evaluation.executed_actions) > 0
        assert evaluation.evaluation_time > 0
        assert evaluation.error_message is None
    
    def test_evaluate_policy_no_match(self, policy_engine):
        """Тест оценки политики без совпадения"""
        policy_id = "child_content_filter"
        user_id = "adult_user"
        request_context = {
            "user_age": 25,
            "content_category": "adult"
        }
        
        evaluation = policy_engine.evaluate_policy(policy_id, user_id, request_context)
        
        assert evaluation.policy_id == policy_id
        assert evaluation.user_id == user_id
        assert evaluation.matched is False
        assert len(evaluation.executed_actions) == 0
    
    def test_evaluate_policy_nonexistent(self, policy_engine):
        """Тест оценки несуществующей политики"""
        policy_id = "nonexistent_policy"
        user_id = "test_user"
        request_context = {}
        
        evaluation = policy_engine.evaluate_policy(policy_id, user_id, request_context)
        
        assert evaluation.policy_id == policy_id
        assert evaluation.user_id == user_id
        assert evaluation.matched is False
        assert evaluation.error_message == "Политика не найдена"
    
    def test_evaluate_policies(self, policy_engine):
        """Тест оценки множественных политик"""
        user_id = "children"  # Используем ID из целевой группы
        request_context = {
            "user_age": 15,
            "content_category": "adult",
            "current_time": "23:30"
        }
        
        evaluations = policy_engine.evaluate_policies(user_id, request_context)
        
        assert len(evaluations) > 0
        assert all(isinstance(eval, PolicyEvaluation) for eval in evaluations)
        
        # Проверяем, что хотя бы одна политика сработала
        matched_evaluations = [eval for eval in evaluations if eval.matched]
        assert len(matched_evaluations) > 0
    
    def test_evaluate_policies_by_type(self, policy_engine):
        """Тест оценки политик по типу"""
        user_id = "test_user"
        request_context = {
            "user_age": 15,
            "content_category": "adult"
        }
        policy_types = [PolicyType.CONTENT_FILTERING]
        
        evaluations = policy_engine.evaluate_policies(user_id, request_context, policy_types)
        
        assert len(evaluations) > 0
        # Проверяем, что все политики относятся к указанному типу
        for evaluation in evaluations:
            if evaluation.policy_id in policy_engine.policies:
                policy = policy_engine.policies[evaluation.policy_id]
                assert policy.policy_type in policy_types
    
    def test_execute_action_allow(self, policy_engine):
        """Тест выполнения действия ALLOW"""
        action = PolicyAction(
            action_type=ActionType.ALLOW,
            parameters={"reason": "Test allow"},
            description="Test allow action"
        )
        
        result = policy_engine._execute_action(action, "test_user", {})
        assert result is True
    
    def test_execute_action_deny(self, policy_engine):
        """Тест выполнения действия DENY"""
        action = PolicyAction(
            action_type=ActionType.DENY,
            parameters={"reason": "Test deny"},
            description="Test deny action"
        )
        
        result = policy_engine._execute_action(action, "test_user", {})
        assert result is True
    
    def test_execute_action_block(self, policy_engine):
        """Тест выполнения действия BLOCK"""
        action = PolicyAction(
            action_type=ActionType.BLOCK,
            parameters={"reason": "Test block"},
            description="Test block action"
        )
        
        result = policy_engine._execute_action(action, "test_user", {})
        assert result is True
    
    def test_execute_action_notify(self, policy_engine):
        """Тест выполнения действия NOTIFY"""
        action = PolicyAction(
            action_type=ActionType.NOTIFY,
            parameters={"recipients": ["admin", "parents"]},
            description="Test notify action"
        )
        
        result = policy_engine._execute_action(action, "test_user", {})
        assert result is True
    
    def test_get_policy_summary(self, policy_engine):
        """Тест получения сводки по политике"""
        policy_id = "child_content_filter"
        
        summary = policy_engine.get_policy_summary(policy_id)
        
        assert "policy_id" in summary
        assert summary["policy_id"] == policy_id
        assert "name" in summary
        assert "description" in summary
        assert "type" in summary
        assert "status" in summary
        assert "priority" in summary
        assert "conditions_count" in summary
        assert "actions_count" in summary
        assert "evaluation_stats" in summary
    
    def test_get_policy_summary_nonexistent(self, policy_engine):
        """Тест получения сводки по несуществующей политике"""
        policy_id = "nonexistent_policy"
        
        summary = policy_engine.get_policy_summary(policy_id)
        
        assert "error" in summary
        assert summary["error"] == "Политика не найдена"
    
    def test_get_policies_by_type(self, policy_engine):
        """Тест получения политик по типу"""
        policy_type = PolicyType.CONTENT_FILTERING
        
        policies = policy_engine.get_policies_by_type(policy_type)
        
        assert len(policies) > 0
        assert all(policy["policy_id"] in policy_engine.policies for policy in policies)
        
        # Проверяем, что все политики имеют правильный тип
        for policy_data in policies:
            policy = policy_engine.policies[policy_data["policy_id"]]
            assert policy.policy_type == policy_type
    
    def test_get_policies_by_type_empty(self, policy_engine):
        """Тест получения политик по несуществующему типу"""
        # Создаем несуществующий тип политики
        policy_type = PolicyType.ACCESS_CONTROL
        
        policies = policy_engine.get_policies_by_type(policy_type)
        
        # Может быть пустой список, если нет политик этого типа
        assert isinstance(policies, list)
    
    def test_get_priority_order(self, policy_engine):
        """Тест получения порядка приоритета"""
        assert policy_engine._get_priority_order(PolicyPriority.CRITICAL) == 0
        assert policy_engine._get_priority_order(PolicyPriority.HIGH) == 1
        assert policy_engine._get_priority_order(PolicyPriority.MEDIUM) == 2
        assert policy_engine._get_priority_order(PolicyPriority.LOW) == 3
        assert policy_engine._get_priority_order(PolicyPriority.INFO) == 4
    
    def test_update_policy_cache(self, policy_engine):
        """Тест обновления кэша политик"""
        initial_cache_size = len(policy_engine.policy_cache)
        
        policy_engine._update_policy_cache()
        
        # Кэш должен содержать активные политики
        assert len(policy_engine.policy_cache) > 0
        
        # Проверяем, что все политики в кэше активны
        for policy_type, policies in policy_engine.policy_cache.items():
            for policy in policies:
                assert policy.status == PolicyStatus.ACTIVE
    
    def test_get_status(self, policy_engine):
        """Тест получения статуса сервиса"""
        status = policy_engine.get_status()
        
        assert "status" in status
        assert "total_policies" in status
        assert "active_policies" in status
        assert "policies_by_type" in status
        assert "policies_by_priority" in status
        assert "policies_by_status" in status
        assert "evaluation_stats" in status
        assert "cache_stats" in status
        assert "engine_settings" in status
        
        # Проверяем, что статистика соответствует реальным данным
        assert status["total_policies"] == len(policy_engine.policies)
        assert status["active_policies"] == len([p for p in policy_engine.policies.values() if p.status == PolicyStatus.ACTIVE])
    
    def test_evaluation_stats(self, policy_engine):
        """Тест статистики оценок"""
        initial_stats = policy_engine.evaluation_stats.copy()
        
        # Выполняем несколько оценок
        user_id = "test_user"
        request_context = {"user_age": 15, "content_category": "adult"}
        
        policy_engine.evaluate_policies(user_id, request_context)
        
        # Проверяем, что статистика обновилась
        assert policy_engine.evaluation_stats["total_evaluations"] > initial_stats["total_evaluations"]
    
    def test_condition_missing_field(self, policy_engine):
        """Тест условия с отсутствующим полем"""
        condition = PolicyCondition(
            field="nonexistent_field",
            operator=ConditionOperator.EQUALS,
            value="test"
        )
        
        context = {"other_field": "test"}
        assert policy_engine._evaluate_condition(condition, context) is False
    
    def test_condition_none_value(self, policy_engine):
        """Тест условия с None значением"""
        condition = PolicyCondition(
            field="test_field",
            operator=ConditionOperator.EQUALS,
            value="test"
        )
        
        context = {"test_field": None}
        assert policy_engine._evaluate_condition(condition, context) is False


if __name__ == "__main__":
    pytest.main([__file__])