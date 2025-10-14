# -*- coding: utf-8 -*-
"""
Тесты для ContextAwareAccess
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from security.preliminary.context_aware_access import (
    ContextAwareAccess, AccessContext, AccessLevel, ContextFactor, AccessDecisionType,
    ContextData, AccessRule, AccessDecision
)
from core.security_base import IncidentSeverity


class TestContextAwareAccess:
    """Тесты для ContextAwareAccess"""
    
    @pytest.fixture
    def context_aware_access(self):
        """Создание экземпляра ContextAwareAccess"""
        return ContextAwareAccess()
    
    @pytest.fixture
    def sample_context_data(self):
        """Создание примера данных контекста"""
        return ContextData(
            user_id="test_user",
            device_id="trusted_device_001",
            location="home",
            network_type="home",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            risk_score=0.2,
            trust_score=0.8,
            authentication_level=2,
            activity_type="browsing"
        )
    
    def test_initialization(self, context_aware_access):
        """Тест инициализации"""
        assert context_aware_access.name == "ContextAwareAccess"
        assert len(context_aware_access.access_rules) > 0
        assert len(context_aware_access.context_weights) == 10
        assert len(context_aware_access.context_access_levels) == 5
        assert len(context_aware_access.time_restrictions) == 3
    
    def test_evaluate_location(self, context_aware_access):
        """Тест оценки местоположения"""
        assert context_aware_access._evaluate_location("home") == 1.0
        assert context_aware_access._evaluate_location("work") == 0.8
        assert context_aware_access._evaluate_location("public") == 0.3
        assert context_aware_access._evaluate_location("unknown") == 0.5
    
    def test_evaluate_time(self, context_aware_access):
        """Тест оценки времени"""
        # Ночные часы
        night_time = datetime(2025, 1, 1, 23, 0)
        assert context_aware_access._evaluate_time(night_time) == 0.3
        
        # Рабочие часы
        work_time = datetime(2025, 1, 1, 12, 0)
        assert context_aware_access._evaluate_time(work_time) == 0.7
        
        # Вечерние часы
        evening_time = datetime(2025, 1, 1, 19, 0)
        assert context_aware_access._evaluate_time(evening_time) == 0.9
        
        # Утренние часы
        morning_time = datetime(2025, 1, 1, 7, 0)
        assert context_aware_access._evaluate_time(morning_time) == 0.6
    
    def test_evaluate_device(self, context_aware_access):
        """Тест оценки устройства"""
        assert context_aware_access._evaluate_device("trusted_device") == 1.0
        assert context_aware_access._evaluate_device("mobile_device") == 0.7
        assert context_aware_access._evaluate_device("unknown_device") == 0.2
        assert context_aware_access._evaluate_device("regular_device") == 0.5
    
    def test_evaluate_network(self, context_aware_access):
        """Тест оценки сети"""
        assert context_aware_access._evaluate_network("home") == 1.0
        assert context_aware_access._evaluate_network("work") == 0.8
        assert context_aware_access._evaluate_network("mobile") == 0.6
        assert context_aware_access._evaluate_network("public") == 0.2
        assert context_aware_access._evaluate_network("unknown") == 0.3
    
    def test_evaluate_user_behavior(self, context_aware_access):
        """Тест оценки поведения пользователя"""
        assert context_aware_access._evaluate_user_behavior("admin") == 1.0
        assert context_aware_access._evaluate_user_behavior("parent") == 0.9
        assert context_aware_access._evaluate_user_behavior("child") == 0.6
        assert context_aware_access._evaluate_user_behavior("elderly") == 0.7
        assert context_aware_access._evaluate_user_behavior("regular") == 0.5
    
    def test_check_time_condition(self, context_aware_access):
        """Тест проверки временного условия"""
        # Ночные часы
        night_time = datetime(2025, 1, 1, 23, 0)
        assert context_aware_access._check_time_condition("night_hours", night_time) is True
        
        # Школьные часы
        school_time = datetime(2025, 1, 1, 10, 0)
        assert context_aware_access._check_time_condition("school_hours", school_time) is True
        
        # Рабочие часы
        work_time = datetime(2025, 1, 1, 12, 0)
        assert context_aware_access._check_time_condition("work_hours", work_time) is True
        
        # Вне рабочих часов
        evening_time = datetime(2025, 1, 1, 19, 0)
        assert context_aware_access._check_time_condition("work_hours", evening_time) is False
    
    def test_analyze_context(self, context_aware_access, sample_context_data):
        """Тест анализа контекста"""
        context_score = context_aware_access._analyze_context(sample_context_data)
        assert 0.0 <= context_score <= 1.0
        assert context_score > 0.5  # Должен быть выше среднего для хорошего контекста
    
    def test_find_applicable_rules(self, context_aware_access, sample_context_data):
        """Тест поиска применимых правил"""
        applicable_rules = context_aware_access._find_applicable_rules(sample_context_data)
        assert isinstance(applicable_rules, list)
        # Должно найти хотя бы одно правило для домашней сети
        assert len(applicable_rules) > 0
    
    def test_rule_matches_context(self, context_aware_access, sample_context_data):
        """Тест соответствия правила контексту"""
        # Создаем тестовое правило
        rule = AccessRule(
            rule_id="test_rule",
            name="Test Rule",
            description="Test rule for home network",
            context_conditions={
                ContextFactor.NETWORK: "home"
            },
            access_level=AccessLevel.FULL
        )
        
        # Проверяем соответствие
        assert context_aware_access._rule_matches_context(rule, sample_context_data) is True
        
        # Проверяем несоответствие
        rule.context_conditions[ContextFactor.NETWORK] = "public"
        assert context_aware_access._rule_matches_context(rule, sample_context_data) is False
    
    def test_make_access_decision(self, context_aware_access, sample_context_data):
        """Тест принятия решения о доступе"""
        applicable_rules = context_aware_access._find_applicable_rules(sample_context_data)
        context_score = context_aware_access._analyze_context(sample_context_data)
        
        decision, access_level, confidence = context_aware_access._make_access_decision(
            sample_context_data, applicable_rules, context_score
        )
        
        assert decision in [AccessDecisionType.ALLOW, AccessDecisionType.DENY, AccessDecisionType.CHALLENGE, AccessDecisionType.MONITOR, AccessDecisionType.ESCALATE]
        assert access_level in [AccessLevel.DENIED, AccessLevel.RESTRICTED, AccessLevel.LIMITED, AccessLevel.STANDARD, AccessLevel.FULL]
        assert 0.0 <= confidence <= 1.0
    
    def test_generate_reasoning(self, context_aware_access, sample_context_data):
        """Тест генерации обоснования"""
        applicable_rules = context_aware_access._find_applicable_rules(sample_context_data)
        context_score = context_aware_access._analyze_context(sample_context_data)
        
        reasoning = context_aware_access._generate_reasoning(applicable_rules, context_score)
        assert isinstance(reasoning, str)
        assert len(reasoning) > 0
    
    def test_evaluate_access_request(self, context_aware_access, sample_context_data):
        """Тест оценки запроса на доступ"""
        decision = context_aware_access.evaluate_access_request(
            user_id="test_user",
            resource="test_resource",
            context_data=sample_context_data
        )
        
        assert decision.user_id == "test_user"
        assert decision.resource == "test_resource"
        assert decision.decision in [AccessDecisionType.ALLOW, AccessDecisionType.DENY, AccessDecisionType.CHALLENGE, AccessDecisionType.MONITOR, AccessDecisionType.ESCALATE]
        assert decision.access_level in [AccessLevel.DENIED, AccessLevel.RESTRICTED, AccessLevel.LIMITED, AccessLevel.STANDARD, AccessLevel.FULL]
        assert 0.0 <= decision.confidence_score <= 1.0
        assert len(decision.reasoning) > 0
        assert decision.expires_at is not None
    
    def test_evaluate_access_request_high_risk(self, context_aware_access):
        """Тест оценки запроса с высоким риском"""
        high_risk_context = ContextData(
            user_id="test_user",
            device_id="unknown_device",
            location="public",
            network_type="public",
            risk_score=0.9,
            trust_score=0.2,
            authentication_level=0
        )
        
        decision = context_aware_access.evaluate_access_request(
            user_id="test_user",
            resource="test_resource",
            context_data=high_risk_context
        )
        
        # При высоком риске должно быть ограничение или запрет
        assert decision.decision in [AccessDecisionType.DENY, AccessDecisionType.CHALLENGE]
        assert decision.access_level in [AccessLevel.DENIED, AccessLevel.RESTRICTED]
    
    def test_evaluate_access_request_night_time(self, context_aware_access):
        """Тест оценки запроса в ночное время"""
        night_context = ContextData(
            user_id="child_user",
            device_id="child_device",
            location="home",
            network_type="home",
            timestamp=datetime(2025, 1, 1, 23, 0),
            risk_score=0.1,
            trust_score=0.6,
            authentication_level=1,
            activity_type="child"
        )
        
        decision = context_aware_access.evaluate_access_request(
            user_id="child_user",
            resource="entertainment",
            context_data=night_context
        )
        
        # В ночное время для детей должно быть ограничение
        assert decision.decision in [AccessDecisionType.DENY, AccessDecisionType.CHALLENGE]
        assert decision.access_level in [AccessLevel.DENIED, AccessLevel.RESTRICTED]
    
    def test_create_access_rule(self, context_aware_access):
        """Тест создания правила доступа"""
        success = context_aware_access.create_access_rule(
            rule_id="test_rule_001",
            name="Test Rule",
            description="Test rule for testing",
            context_conditions={
                ContextFactor.NETWORK: "test"
            },
            access_level=AccessLevel.STANDARD,
            priority=50
        )
        
        assert success is True
        assert "test_rule_001" in context_aware_access.access_rules
        
        rule = context_aware_access.access_rules["test_rule_001"]
        assert rule.name == "Test Rule"
        assert rule.access_level == AccessLevel.STANDARD
        assert rule.priority == 50
    
    def test_create_access_rule_duplicate(self, context_aware_access):
        """Тест создания дублирующего правила"""
        # Создаем первое правило
        success1 = context_aware_access.create_access_rule(
            rule_id="duplicate_rule",
            name="First Rule",
            description="First rule",
            context_conditions={},
            access_level=AccessLevel.STANDARD
        )
        assert success1 is True
        
        # Пытаемся создать дублирующее правило
        success2 = context_aware_access.create_access_rule(
            rule_id="duplicate_rule",
            name="Second Rule",
            description="Second rule",
            context_conditions={},
            access_level=AccessLevel.FULL
        )
        assert success2 is False
    
    def test_update_access_rule(self, context_aware_access):
        """Тест обновления правила доступа"""
        # Создаем правило
        context_aware_access.create_access_rule(
            rule_id="update_test_rule",
            name="Original Name",
            description="Original description",
            context_conditions={},
            access_level=AccessLevel.STANDARD
        )
        
        # Обновляем правило
        success = context_aware_access.update_access_rule(
            "update_test_rule",
            name="Updated Name",
            access_level=AccessLevel.FULL
        )
        
        assert success is True
        rule = context_aware_access.access_rules["update_test_rule"]
        assert rule.name == "Updated Name"
        assert rule.access_level == AccessLevel.FULL
    
    def test_update_access_rule_nonexistent(self, context_aware_access):
        """Тест обновления несуществующего правила"""
        success = context_aware_access.update_access_rule(
            "nonexistent_rule",
            name="New Name"
        )
        assert success is False
    
    def test_delete_access_rule(self, context_aware_access):
        """Тест удаления правила доступа"""
        # Создаем правило
        context_aware_access.create_access_rule(
            rule_id="delete_test_rule",
            name="Rule to Delete",
            description="This rule will be deleted",
            context_conditions={},
            access_level=AccessLevel.STANDARD
        )
        
        assert "delete_test_rule" in context_aware_access.access_rules
        
        # Удаляем правило
        success = context_aware_access.delete_access_rule("delete_test_rule")
        
        assert success is True
        assert "delete_test_rule" not in context_aware_access.access_rules
    
    def test_delete_access_rule_nonexistent(self, context_aware_access):
        """Тест удаления несуществующего правила"""
        success = context_aware_access.delete_access_rule("nonexistent_rule")
        assert success is False
    
    def test_get_access_summary(self, context_aware_access, sample_context_data):
        """Тест получения сводки доступа"""
        # Создаем несколько решений
        for i in range(3):
            context_aware_access.evaluate_access_request(
                user_id="test_user",
                resource=f"resource_{i}",
                context_data=sample_context_data
            )
        
        summary = context_aware_access.get_access_summary("test_user", hours=24)
        
        assert summary["user_id"] == "test_user"
        assert summary["period_hours"] == 24
        assert summary["total_requests"] == 3
        assert "decision_counts" in summary
        assert "access_level_counts" in summary
        assert "average_confidence" in summary
        assert "recent_decisions" in summary
    
    def test_get_access_summary_no_data(self, context_aware_access):
        """Тест получения сводки доступа без данных"""
        summary = context_aware_access.get_access_summary("nonexistent_user", hours=1)
        
        assert summary["user_id"] == "nonexistent_user"
        assert summary["total_requests"] == 0
        assert "message" in summary
    
    def test_get_status(self, context_aware_access):
        """Тест получения статуса сервиса"""
        status = context_aware_access.get_status()
        
        assert "status" in status
        assert "total_rules" in status
        assert "total_decisions" in status
        assert "cache_size" in status
        assert "rules_by_priority" in status
        assert "decisions_by_type" in status
        assert "context_weights" in status
        assert "context_access_levels" in status
        assert "time_restrictions" in status
        
        # Проверяем, что статистика соответствует реальным данным
        assert status["total_rules"] == len(context_aware_access.access_rules)
        assert status["total_decisions"] == len(context_aware_access.access_decisions)
        assert status["cache_size"] == len(context_aware_access.context_cache)
    
    def test_context_cache(self, context_aware_access, sample_context_data):
        """Тест кэширования контекста"""
        # Оцениваем запрос на доступ
        decision = context_aware_access.evaluate_access_request(
            user_id="test_user",
            resource="test_resource",
            context_data=sample_context_data
        )
        
        # Проверяем, что контекст закэширован
        cache_key = "test_user_test_resource"
        assert cache_key in context_aware_access.context_cache
        
        cached_context = context_aware_access.context_cache[cache_key]
        assert cached_context.user_id == sample_context_data.user_id
        assert cached_context.device_id == sample_context_data.device_id
    
    def test_decision_expiration(self, context_aware_access, sample_context_data):
        """Тест истечения срока действия решения"""
        decision = context_aware_access.evaluate_access_request(
            user_id="test_user",
            resource="test_resource",
            context_data=sample_context_data
        )
        
        assert decision.expires_at is not None
        assert decision.expires_at > decision.timestamp
        
        # Проверяем, что срок действия составляет примерно 1 час
        time_diff = decision.expires_at - decision.timestamp
        assert timedelta(hours=0.9) < time_diff < timedelta(hours=1.1)
    
    def test_multiple_rules_priority(self, context_aware_access):
        """Тест приоритета правил"""
        # Создаем правила с разными приоритетами
        context_aware_access.create_access_rule(
            rule_id="low_priority_rule",
            name="Low Priority Rule",
            description="Rule with low priority",
            context_conditions={ContextFactor.NETWORK: "home"},
            access_level=AccessLevel.FULL,
            priority=100
        )
        
        context_aware_access.create_access_rule(
            rule_id="high_priority_rule",
            name="High Priority Rule",
            description="Rule with high priority",
            context_conditions={ContextFactor.NETWORK: "home"},
            access_level=AccessLevel.DENIED,
            priority=10
        )
        
        # Создаем контекст для домашней сети
        home_context = ContextData(
            user_id="test_user",
            device_id="test_device",
            network_type="home"
        )
        
        # Оцениваем запрос
        decision = context_aware_access.evaluate_access_request(
            user_id="test_user",
            resource="test_resource",
            context_data=home_context
        )
        
        # Должно примениться правило с высоким приоритетом (запрет)
        assert decision.decision == AccessDecisionType.DENY
        assert decision.access_level == AccessLevel.DENIED


if __name__ == "__main__":
    pytest.main([__file__])