# -*- coding: utf-8 -*-
"""
Тесты для ParentalControls
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock

from security.family.parental_controls import (
    ParentalControls, ControlType, ControlStatus, NotificationType,
    ControlRule, ParentalNotification, ChildActivitySummary
)
from security.family.family_profile_manager import FamilyProfileManager, FamilyProfile, FamilyMember, AgeGroup, FamilyRole
from security.family.child_protection import ChildProtection, ThreatLevel
from security.family.elderly_protection import ElderlyProtection
from core.security_base import IncidentSeverity


class TestParentalControls:
    """Тесты для ParentalControls"""
    
    @pytest.fixture
    def mock_family_manager(self):
        """Мок FamilyProfileManager"""
        manager = Mock(spec=FamilyProfileManager)
        
        # Создаем тестовую семью
        family = FamilyProfile(
            family_id="test_family",
            family_name="Тестовая семья",
            created_at=datetime.now()
        )
        
        # Добавляем члена семьи
        child = FamilyMember(
            id="child_1",
            name="Тестовый ребенок",
            age=10,
            role=FamilyRole.CHILD,
            age_group=AgeGroup.CHILD
        )
        family.members["child_1"] = child
        
        parent = FamilyMember(
            id="parent_1",
            name="Тестовый родитель",
            age=35,
            role=FamilyRole.PARENT,
            age_group=AgeGroup.ADULT
        )
        family.members["parent_1"] = parent
        
        manager.families = {"test_family": family}
        
        return manager
    
    @pytest.fixture
    def mock_child_protection(self):
        """Мок ChildProtection"""
        protection = Mock(spec=ChildProtection)
        protection.get_child_activity_report.return_value = []
        protection.check_content_access.return_value = (True, "Доступ разрешен", ThreatLevel.LOW)
        return protection
    
    @pytest.fixture
    def mock_elderly_protection(self):
        """Мок ElderlyProtection"""
        return Mock(spec=ElderlyProtection)
    
    @pytest.fixture
    def parental_controls(self, mock_family_manager, mock_child_protection, mock_elderly_protection):
        """Создание экземпляра ParentalControls"""
        return ParentalControls(
            family_profile_manager=mock_family_manager,
            child_protection=mock_child_protection,
            elderly_protection=mock_elderly_protection
        )
    
    def test_create_control_rule(self, parental_controls):
        """Тест создания правила контроля"""
        settings = {"daily_limit": 3600, "bedtime": "21:00"}
        
        result = parental_controls.create_control_rule(
            child_id="child_1",
            control_type=ControlType.TIME_LIMIT,
            settings=settings
        )
        
        assert result is True
        assert len(parental_controls.control_rules) > 0
        
        # Проверяем, что правило создано
        rule_found = False
        for rule in parental_controls.control_rules.values():
            if rule.child_id == "child_1" and rule.control_type == ControlType.TIME_LIMIT:
                rule_found = True
                # Проверяем, что настройки установлены (может быть правило по умолчанию или новое)
                assert "daily_limit" in rule.settings
                assert "bedtime" in rule.settings
                break
        
        assert rule_found
    
    def test_update_control_rule(self, parental_controls):
        """Тест обновления правила контроля"""
        # Создаем правило
        rule_id = parental_controls.create_control_rule(
            child_id="child_1",
            control_type=ControlType.TIME_LIMIT,
            settings={"daily_limit": 3600}
        )
        
        # Находим созданное правило
        rule_id_found = None
        for rid, rule in parental_controls.control_rules.items():
            if rule.child_id == "child_1" and rule.control_type == ControlType.TIME_LIMIT:
                rule_id_found = rid
                break
        
        assert rule_id_found is not None
        
        # Обновляем правило
        new_settings = {"daily_limit": 7200, "bedtime": "22:00"}
        result = parental_controls.update_control_rule(rule_id_found, new_settings)
        
        assert result is True
        rule = parental_controls.control_rules[rule_id_found]
        assert rule.settings["daily_limit"] == 7200
        assert rule.settings["bedtime"] == "22:00"
    
    def test_activate_control_rule(self, parental_controls):
        """Тест активации правила контроля"""
        # Создаем правило
        parental_controls.create_control_rule(
            child_id="child_1",
            control_type=ControlType.TIME_LIMIT,
            settings={"daily_limit": 3600}
        )
        
        # Находим созданное правило
        rule_id = None
        for rid, rule in parental_controls.control_rules.items():
            if rule.child_id == "child_1" and rule.control_type == ControlType.TIME_LIMIT:
                rule_id = rid
                break
        
        assert rule_id is not None
        
        # Активируем правило
        result = parental_controls.activate_control_rule(rule_id)
        
        assert result is True
        rule = parental_controls.control_rules[rule_id]
        assert rule.status == ControlStatus.ACTIVE
        assert rule.is_active is True
    
    def test_deactivate_control_rule(self, parental_controls):
        """Тест деактивации правила контроля"""
        # Создаем правило
        parental_controls.create_control_rule(
            child_id="child_1",
            control_type=ControlType.TIME_LIMIT,
            settings={"daily_limit": 3600}
        )
        
        # Находим созданное правило
        rule_id = None
        for rid, rule in parental_controls.control_rules.items():
            if rule.child_id == "child_1" and rule.control_type == ControlType.TIME_LIMIT:
                rule_id = rid
                break
        
        assert rule_id is not None
        
        # Деактивируем правило
        result = parental_controls.deactivate_control_rule(rule_id)
        
        assert result is True
        rule = parental_controls.control_rules[rule_id]
        assert rule.status == ControlStatus.INACTIVE
        assert rule.is_active is False
    
    def test_get_child_control_rules(self, parental_controls):
        """Тест получения правил контроля для ребенка"""
        # Создаем несколько правил для ребенка
        parental_controls.create_control_rule(
            child_id="child_1",
            control_type=ControlType.TIME_LIMIT,
            settings={"daily_limit": 3600}
        )
        
        parental_controls.create_control_rule(
            child_id="child_1",
            control_type=ControlType.CONTENT_FILTER,
            settings={"allowed_categories": ["educational"]}
        )
        
        # Получаем правила
        rules = parental_controls.get_child_control_rules("child_1")
        
        assert len(rules) >= 2
        assert all(rule.child_id == "child_1" for rule in rules)
    
    def test_check_time_limit_no_rules(self, parental_controls):
        """Тест проверки ограничения времени без правил"""
        exceeded, message = parental_controls.check_time_limit("child_1")
        
        assert exceeded is False
        # Система создает правила по умолчанию, поэтому проверяем сообщение о времени
        assert "времени" in message
    
    def test_check_content_access(self, parental_controls):
        """Тест проверки доступа к контенту"""
        allowed, message = parental_controls.check_content_access(
            child_id="child_1",
            content_url="https://example.com",
            content_type="website"
        )
        
        assert allowed is True
        assert "разрешен" in message
    
    def test_emergency_lock_child_device(self, parental_controls):
        """Тест экстренной блокировки устройства"""
        result = parental_controls.emergency_lock_child_device(
            child_id="child_1",
            reason="Подозрительная активность"
        )
        
        assert result is True
        
        # Проверяем, что создано уведомление
        assert len(parental_controls.notifications) > 0
        
        # Проверяем, что правила переведены в экстренный режим
        child_rules = parental_controls.get_child_control_rules("child_1")
        for rule in child_rules:
            if rule.control_type == ControlType.TIME_LIMIT:  # Проверяем одно из правил
                assert rule.status == ControlStatus.EMERGENCY
    
    def test_get_daily_activity_summary(self, parental_controls):
        """Тест получения сводки активности за день"""
        summary = parental_controls.get_daily_activity_summary("child_1")
        
        assert summary is not None
        assert summary.child_id == "child_1"
        assert summary.total_screen_time == timedelta()
        assert summary.blocked_attempts == 0
        assert summary.suspicious_activities == 0
        assert summary.emergency_alerts == 0
    
    def test_get_parent_notifications(self, parental_controls):
        """Тест получения уведомлений для родителя"""
        # Создаем тестовое уведомление
        notification = ParentalNotification(
            notification_id="test_notification",
            parent_id="parent_1",
            child_id="child_1",
            notification_type=NotificationType.TIME_LIMIT_REACHED,
            title="Тестовое уведомление",
            message="Тестовое сообщение",
            severity=IncidentSeverity.MEDIUM
        )
        parental_controls.notifications["test_notification"] = notification
        
        # Получаем уведомления
        notifications = parental_controls.get_parent_notifications("parent_1")
        
        assert len(notifications) >= 1
        assert any(n.notification_id == "test_notification" for n in notifications)
    
    def test_mark_notification_read(self, parental_controls):
        """Тест отметки уведомления как прочитанного"""
        # Создаем тестовое уведомление
        notification = ParentalNotification(
            notification_id="test_notification",
            parent_id="parent_1",
            child_id="child_1",
            notification_type=NotificationType.TIME_LIMIT_REACHED,
            title="Тестовое уведомление",
            message="Тестовое сообщение",
            severity=IncidentSeverity.MEDIUM
        )
        parental_controls.notifications["test_notification"] = notification
        
        # Отмечаем как прочитанное
        result = parental_controls.mark_notification_read("test_notification")
        
        assert result is True
        assert parental_controls.notifications["test_notification"].is_read is True
    
    def test_get_status(self, parental_controls):
        """Тест получения статуса системы"""
        status = parental_controls.get_status()
        
        assert "status" in status
        assert "total_control_rules" in status
        assert "active_rules" in status
        assert "total_notifications" in status
        assert "unread_notifications" in status
        assert "activity_summaries" in status
        assert "emergency_contacts" in status
        assert "control_types_active" in status
        
        assert isinstance(status["total_control_rules"], int)
        assert isinstance(status["active_rules"], int)
        assert isinstance(status["total_notifications"], int)
        assert isinstance(status["unread_notifications"], int)


if __name__ == "__main__":
    pytest.main([__file__])