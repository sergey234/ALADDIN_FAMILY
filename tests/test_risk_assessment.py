# -*- coding: utf-8 -*-
"""
Тесты для RiskAssessment
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from security.preliminary.risk_assessment import (
    RiskAssessmentService, RiskCategory, RiskLevel, RiskStatus, ThreatSource,
    RiskFactor, RiskAssessment, RiskProfile
)
from core.security_base import IncidentSeverity


class TestRiskAssessment:
    """Тесты для RiskAssessmentService"""
    
    @pytest.fixture
    def risk_assessment(self):
        """Создание экземпляра RiskAssessmentService"""
        return RiskAssessmentService()
    
    def test_initialization(self, risk_assessment):
        """Тест инициализации"""
        assert risk_assessment.name == "RiskAssessment"
        assert len(risk_assessment.risk_factors) > 0
        assert len(risk_assessment.risk_controls) > 0
        assert len(risk_assessment.risk_thresholds) == 5
        assert len(risk_assessment.assessment_weights) == 10
    
    def test_calculate_risk_score(self, risk_assessment):
        """Тест вычисления балла риска"""
        factor = RiskFactor(
            factor_id="test_factor",
            name="Test Factor",
            description="Test description",
            category=RiskCategory.AUTHENTICATION,
            weight=0.8,
            impact_score=0.7,
            likelihood_score=0.6
        )
        
        risk_score = risk_assessment._calculate_risk_score(factor)
        expected_score = 0.7 * 0.6 * 0.8  # 0.336
        assert abs(risk_score - expected_score) < 0.001
    
    def test_determine_risk_level(self, risk_assessment):
        """Тест определения уровня риска"""
        # Тестируем разные уровни риска
        assert risk_assessment._determine_risk_level(0.95) == RiskLevel.CRITICAL
        assert risk_assessment._determine_risk_level(0.8) == RiskLevel.HIGH
        assert risk_assessment._determine_risk_level(0.6) == RiskLevel.MEDIUM
        assert risk_assessment._determine_risk_level(0.4) == RiskLevel.LOW
        assert risk_assessment._determine_risk_level(0.1) == RiskLevel.MINIMAL
    
    def test_is_factor_applicable(self, risk_assessment):
        """Тест проверки применимости фактора"""
        factor = RiskFactor(
            factor_id="test_factor",
            name="Test Factor",
            description="Test description",
            category=RiskCategory.AUTHENTICATION,
            weight=0.8,
            impact_score=0.7,
            likelihood_score=0.6
        )
        
        # Тест с данными аутентификации
        user_data_auth = {"password_strength": 0.5, "mfa_enabled": False}
        assert risk_assessment._is_factor_applicable(factor, user_data_auth) is True
        
        # Тест с данными сетевой безопасности
        factor_network = RiskFactor(
            factor_id="network_factor",
            name="Network Factor",
            description="Network description",
            category=RiskCategory.NETWORK_SECURITY,
            weight=0.7,
            impact_score=0.6,
            likelihood_score=0.7
        )
        
        user_data_network = {"wifi_usage": {"unsecured_ratio": 0.3}}
        assert risk_assessment._is_factor_applicable(factor_network, user_data_network) is True
        
        # Тест без соответствующих данных
        user_data_empty = {}
        assert risk_assessment._is_factor_applicable(factor, user_data_empty) is False
    
    def test_update_factor_scores(self, risk_assessment):
        """Тест обновления оценок фактора"""
        factor = RiskFactor(
            factor_id="weak_passwords",
            name="Слабые пароли",
            description="Test description",
            category=RiskCategory.AUTHENTICATION,
            weight=0.8,
            impact_score=0.7,
            likelihood_score=0.6
        )
        
        # Тест с слабым паролем
        user_data_weak = {"password_strength": 0.2}
        updated_factor = risk_assessment._update_factor_scores(factor, user_data_weak)
        assert updated_factor.likelihood_score > factor.likelihood_score
        
        # Тест с сильным паролем
        user_data_strong = {"password_strength": 0.9}
        updated_factor = risk_assessment._update_factor_scores(factor, user_data_strong)
        assert updated_factor.likelihood_score < factor.likelihood_score
        
        # Тест без MFA
        user_data_no_mfa = {"mfa_enabled": False}
        updated_factor = risk_assessment._update_factor_scores(factor, user_data_no_mfa)
        assert updated_factor.likelihood_score > factor.likelihood_score
    
    def test_calculate_overall_risk_score(self, risk_assessment):
        """Тест вычисления общего балла риска"""
        # Создаем тестовые факторы риска
        factors = {
            "factor1": RiskFactor(
                factor_id="factor1",
                name="Factor 1",
                description="Test factor 1",
                category=RiskCategory.AUTHENTICATION,
                weight=0.8,
                impact_score=0.7,
                likelihood_score=0.6,
                risk_score=0.336
            ),
            "factor2": RiskFactor(
                factor_id="factor2",
                name="Factor 2",
                description="Test factor 2",
                category=RiskCategory.NETWORK_SECURITY,
                weight=0.7,
                impact_score=0.8,
                likelihood_score=0.5,
                risk_score=0.28
            )
        }
        
        overall_score = risk_assessment._calculate_overall_risk_score(factors)
        assert 0.0 <= overall_score <= 1.0
        assert overall_score > 0.0  # Должен быть больше 0
    
    def test_generate_mitigation_recommendations(self, risk_assessment):
        """Тест генерации рекомендаций по снижению рисков"""
        # Создаем профиль с высокими рисками
        high_risk_factor = RiskFactor(
            factor_id="weak_passwords",
            name="Слабые пароли",
            description="Test description",
            category=RiskCategory.AUTHENTICATION,
            weight=0.8,
            impact_score=0.7,
            likelihood_score=0.6,
            risk_score=0.8  # Высокий риск
        )
        
        profile = RiskProfile(
            profile_id="test_profile",
            user_id="test_user",
            risk_factors={"weak_passwords": high_risk_factor},
            overall_risk_score=0.8,
            risk_level=RiskLevel.HIGH
        )
        
        recommendations = risk_assessment._generate_mitigation_recommendations(profile)
        assert len(recommendations) > 0
        assert any("парол" in rec.lower() for rec in recommendations)
    
    def test_assess_user_risk(self, risk_assessment):
        """Тест оценки рисков пользователя"""
        user_data = {
            "password_strength": 0.3,  # Слабый пароль
            "mfa_enabled": False,  # Нет MFA
            "wifi_usage": {"unsecured_ratio": 0.4},  # Много незащищенных сетей
            "software_updates": {"outdated_ratio": 0.2},  # Немного устаревшего ПО
            "devices": ["laptop", "phone"],
            "accounts": ["email", "social"]
        }
        
        profile = risk_assessment.assess_user_risk("test_user", user_data)
        
        assert profile.user_id == "test_user"
        assert profile.overall_risk_score > 0.0
        assert profile.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert len(profile.risk_factors) > 0
        assert len(profile.mitigation_recommendations) > 0
        assert len(profile.assessment_history) > 0
    
    def test_assess_user_risk_high_risk(self, risk_assessment):
        """Тест оценки рисков пользователя с высокими рисками"""
        user_data = {
            "password_strength": 0.1,  # Очень слабый пароль
            "mfa_enabled": False,  # Нет MFA
            "wifi_usage": {"unsecured_ratio": 0.8},  # Много незащищенных сетей
            "software_updates": {"outdated_ratio": 0.7},  # Много устаревшего ПО
            "behavior_patterns": {"anomalies_count": 10},  # Много аномалий
            "devices": ["laptop", "phone", "tablet"],
            "accounts": ["email", "social", "banking"]
        }
        
        profile = risk_assessment.assess_user_risk("high_risk_user", user_data)
        
        assert profile.user_id == "high_risk_user"
        assert profile.overall_risk_score > 0.4  # Должен быть повышенный риск
        assert profile.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert len(profile.mitigation_recommendations) > 0
    
    def test_assess_user_risk_low_risk(self, risk_assessment):
        """Тест оценки рисков пользователя с низкими рисками"""
        user_data = {
            "password_strength": 0.9,  # Сильный пароль
            "mfa_enabled": True,  # Включен MFA
            "wifi_usage": {"unsecured_ratio": 0.1},  # Мало незащищенных сетей
            "software_updates": {"outdated_ratio": 0.05},  # Мало устаревшего ПО
            "behavior_patterns": {"anomalies_count": 1},  # Мало аномалий
            "devices": ["laptop"],
            "accounts": ["email"]
        }
        
        profile = risk_assessment.assess_user_risk("low_risk_user", user_data)
        
        assert profile.user_id == "low_risk_user"
        assert profile.overall_risk_score < 0.5  # Должен быть низкий риск
        assert profile.risk_level in [RiskLevel.MINIMAL, RiskLevel.LOW]
    
    def test_get_risk_summary(self, risk_assessment):
        """Тест получения сводки рисков"""
        # Сначала создаем профиль риска
        user_data = {
            "password_strength": 0.5,
            "mfa_enabled": False,
            "devices": ["laptop", "phone"]
        }
        
        risk_assessment.assess_user_risk("test_user", user_data)
        
        # Получаем сводку
        summary = risk_assessment.get_risk_summary("test_user")
        
        assert summary["user_id"] == "test_user"
        assert "overall_risk_score" in summary
        assert "risk_level" in summary
        assert "risks_by_category" in summary
        assert "mitigation_recommendations" in summary
        assert "last_assessment" in summary
        assert "total_factors" in summary
        assert "high_risk_factors" in summary
    
    def test_get_risk_summary_nonexistent_user(self, risk_assessment):
        """Тест получения сводки рисков для несуществующего пользователя"""
        summary = risk_assessment.get_risk_summary("nonexistent_user")
        
        assert summary["user_id"] == "nonexistent_user"
        assert "message" in summary
        assert "не найден" in summary["message"]
    
    def test_get_risk_trends(self, risk_assessment):
        """Тест получения трендов рисков"""
        # Создаем несколько оценок рисков
        for i in range(5):
            user_data = {
                "password_strength": 0.3 + i * 0.1,
                "mfa_enabled": i % 2 == 0,
                "devices": ["laptop"]
            }
            risk_assessment.assess_user_risk(f"user_{i}", user_data)
        
        # Получаем тренды
        trends = risk_assessment.get_risk_trends(days=30)
        
        assert "period_days" in trends
        assert "total_assessments" in trends
        assert "average_risk_score" in trends
        assert "max_risk_score" in trends
        assert "min_risk_score" in trends
        assert "risk_level_distribution" in trends
        assert "trend" in trends
        assert "high_risk_periods" in trends
    
    def test_get_risk_trends_no_data(self, risk_assessment):
        """Тест получения трендов рисков без данных"""
        trends = risk_assessment.get_risk_trends(days=1)
        
        assert "period_days" in trends
        assert "message" in trends
        assert "Нет данных" in trends["message"]
    
    def test_calculate_average_impact(self, risk_assessment):
        """Тест вычисления среднего воздействия"""
        factors = {
            "factor1": RiskFactor(
                factor_id="factor1",
                name="Factor 1",
                description="Test factor 1",
                category=RiskCategory.AUTHENTICATION,
                weight=0.8,
                impact_score=0.7,
                likelihood_score=0.6
            ),
            "factor2": RiskFactor(
                factor_id="factor2",
                name="Factor 2",
                description="Test factor 2",
                category=RiskCategory.NETWORK_SECURITY,
                weight=0.7,
                impact_score=0.9,
                likelihood_score=0.5
            )
        }
        
        avg_impact = risk_assessment._calculate_average_impact(factors)
        expected_avg = (0.7 + 0.9) / 2  # 0.8
        assert abs(avg_impact - expected_avg) < 0.001
    
    def test_calculate_average_likelihood(self, risk_assessment):
        """Тест вычисления средней вероятности"""
        factors = {
            "factor1": RiskFactor(
                factor_id="factor1",
                name="Factor 1",
                description="Test factor 1",
                category=RiskCategory.AUTHENTICATION,
                weight=0.8,
                impact_score=0.7,
                likelihood_score=0.6
            ),
            "factor2": RiskFactor(
                factor_id="factor2",
                name="Factor 2",
                description="Test factor 2",
                category=RiskCategory.NETWORK_SECURITY,
                weight=0.7,
                impact_score=0.9,
                likelihood_score=0.4
            )
        }
        
        avg_likelihood = risk_assessment._calculate_average_likelihood(factors)
        expected_avg = (0.6 + 0.4) / 2  # 0.5
        assert abs(avg_likelihood - expected_avg) < 0.001
    
    def test_identify_affected_assets(self, risk_assessment):
        """Тест идентификации затронутых активов"""
        user_data = {
            "devices": ["laptop", "phone"],
            "accounts": ["email", "social"],
            "data_types": ["personal", "financial"]
        }
        
        assets = risk_assessment._identify_affected_assets(user_data)
        
        assert "laptop" in assets
        assert "phone" in assets
        assert "account_email" in assets
        assert "account_social" in assets
        assert "data_personal" in assets
        assert "data_financial" in assets
    
    def test_identify_affected_assets_empty(self, risk_assessment):
        """Тест идентификации активов с пустыми данными"""
        user_data = {}
        
        assets = risk_assessment._identify_affected_assets(user_data)
        
        assert len(assets) > 0
        assert "user_data" in assets
        assert "devices" in assets
        assert "accounts" in assets
    
    def test_get_status(self, risk_assessment):
        """Тест получения статуса сервиса"""
        # Создаем несколько профилей для тестирования
        for i in range(3):
            user_data = {
                "password_strength": 0.5,
                "mfa_enabled": i % 2 == 0,
                "devices": ["laptop"]
            }
            risk_assessment.assess_user_risk(f"user_{i}", user_data)
        
        status = risk_assessment.get_status()
        
        assert "status" in status
        assert status["total_risk_factors"] > 0
        assert status["total_assessments"] >= 3
        assert status["total_profiles"] >= 3
        assert "risk_factors_by_category" in status
        assert "assessments_by_level" in status
        assert "high_risk_profiles" in status
        assert "avg_risk_score" in status
        assert "risk_controls_available" in status
        assert "assessment_weights" in status


if __name__ == "__main__":
    pytest.main([__file__])