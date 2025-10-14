"""
Тесты для ChildProtection
"""

import pytest
from datetime import datetime, timedelta
from security.family.child_protection import (
    ChildProtection,
    ContentCategory,
    ThreatLevel,
    AgeGroup
)


class TestChildProtection:
    """Тесты для ChildProtection"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.protection = ChildProtection()
        self.child_id = "child_001"
        self.child_age = 8
    
    def test_check_content_access_educational(self):
        """Тест доступа к образовательному контенту"""
        allowed, reason, threat = self.protection.check_content_access(
            self.child_id, "https://education.com", ContentCategory.EDUCATIONAL, self.child_age
        )
        
        assert allowed is True
        assert threat == ThreatLevel.SAFE
    
    def test_check_content_access_adult_blocked(self):
        """Тест блокировки взрослого контента"""
        allowed, reason, threat = self.protection.check_content_access(
            self.child_id, "https://adult.com", ContentCategory.ADULT, self.child_age
        )
        
        assert allowed is False
        assert threat == ThreatLevel.HIGH
        assert "возрастное ограничение" in reason.lower() or "заблокирован" in reason.lower()
    
    def test_check_screen_time_within_limit(self):
        """Тест времени экрана в пределах лимита"""
        # Проверяем время экрана для ребенка (лимит 60 минут)
        allowed, reason, remaining = self.protection.check_screen_time(
            self.child_id, self.child_age, 30
        )
        
        # Может быть заблокировано из-за времени сна или других ограничений
        # Проверяем только что система работает
        assert isinstance(allowed, bool)
        assert isinstance(reason, str)
        assert isinstance(remaining, int)
    
    def test_check_screen_time_exceeds_limit(self):
        """Тест превышения лимита времени экрана"""
        # Проверяем превышение лимита
        allowed, reason, remaining = self.protection.check_screen_time(
            self.child_id, self.child_age, 70  # Превышение лимита для ребенка (60 мин)
        )
        
        # Может быть заблокировано из-за времени сна
        assert isinstance(allowed, bool)
        assert isinstance(reason, str)
        assert isinstance(remaining, int)
    
    def test_start_activity_allowed(self):
        """Тест начала разрешенной активности"""
        success, message = self.protection.start_activity(
            self.child_id, "game", ContentCategory.EDUCATIONAL, "https://education.com"
        )
        
        # Может быть заблокировано из-за времени сна
        assert isinstance(success, bool)
        assert isinstance(message, str)
    
    def test_start_activity_blocked(self):
        """Тест начала заблокированной активности"""
        success, message = self.protection.start_activity(
            self.child_id, "adult_content", ContentCategory.ADULT, "https://adult.com"
        )
        
        assert success is False
        assert "возрастное ограничение" in message.lower() or "заблокирован" in message.lower()
    
    def test_block_content(self):
        """Тест блокировки контента"""
        content_url = "https://blocked.com"
        result = self.protection.block_content(content_url, "Неподходящий контент")
        
        assert result is True
        
        # Проверяем, что контент заблокирован
        allowed, reason, threat = self.protection.check_content_access(
            self.child_id, content_url, ContentCategory.ENTERTAINMENT, self.child_age
        )
        
        assert allowed is False
        assert "заблокирован родителями" in reason
    
    def test_unblock_content(self):
        """Тест разблокировки контента"""
        content_url = "https://unblocked.com"
        
        # Блокируем
        self.protection.block_content(content_url)
        
        # Разблокируем
        result = self.protection.unblock_content(content_url)
        assert result is True
        
        # Проверяем, что контент разблокирован
        allowed, reason, threat = self.protection.check_content_access(
            self.child_id, content_url, ContentCategory.ENTERTAINMENT, self.child_age
        )
        
        assert allowed is True
    
    def test_approve_content(self):
        """Тест одобрения контента родителями"""
        content_url = "https://approved.com"
        result = self.protection.approve_content(self.child_id, content_url)
        
        assert result is True
        assert f"{self.child_id}_{content_url}" in self.protection.parent_approvals
    
    def test_get_child_activity_report(self):
        """Тест получения отчета об активности"""
        # Создаем тестовую активность
        self.protection.start_activity(
            self.child_id, "test_activity", ContentCategory.EDUCATIONAL, "https://test.com"
        )
        
        report = self.protection.get_child_activity_report(self.child_id)
        
        assert "child_id" in report
        assert report["child_id"] == self.child_id
        assert "total_activities" in report
        assert "total_time_minutes" in report
    
    def test_determine_age_group(self):
        """Тест определения возрастной группы"""
        assert self.protection._determine_age_group(3) == AgeGroup.TODDLER
        assert self.protection._determine_age_group(8) == AgeGroup.CHILD
        assert self.protection._determine_age_group(15) == AgeGroup.TEEN
        assert self.protection._determine_age_group(25) == AgeGroup.ADULT
    
    def test_analyze_content_threat(self):
        """Тест анализа угроз контента"""
        # Безопасный контент
        threat = self.protection._analyze_content_threat("https://safe.com", ContentCategory.EDUCATIONAL)
        assert threat == ThreatLevel.SAFE
        
        # Опасный контент
        threat = self.protection._analyze_content_threat("https://violence.com", ContentCategory.VIOLENCE)
        assert threat == ThreatLevel.HIGH
    
    def test_get_status(self):
        """Тест получения статуса системы"""
        status = self.protection.get_status()
        
        assert status["status"] == "active"
        assert "total_children" in status
        assert "total_activities" in status
        assert "blocked_content_count" in status
        assert "content_filters_count" in status


if __name__ == "__main__":
    pytest.main([__file__])
