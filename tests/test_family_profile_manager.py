"""
Тесты для FamilyProfileManager
"""

import pytest
from datetime import datetime
from security.family.family_profile_manager import (
    FamilyProfileManager,
    FamilyRole,
    AgeGroup,
    FamilyMember,
    FamilyProfile
)


class TestFamilyProfileManager:
    """Тесты для FamilyProfileManager"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.manager = FamilyProfileManager()
        self.family_id = "test_family_001"
        self.family_name = "Тестовая семья"
    
    def test_create_family(self):
        """Тест создания семьи"""
        result = self.manager.create_family(self.family_id, self.family_name)
        assert result is True
        assert self.family_id in self.manager.families
        assert self.manager.families[self.family_id].family_name == self.family_name
    
    def test_add_family_member(self):
        """Тест добавления члена семьи"""
        self.manager.create_family(self.family_id, self.family_name)
        
        result = self.manager.add_family_member(
            self.family_id, "member_001", "Иван", 35
        )
        
        assert result is True
        member = self.manager.get_family_member(self.family_id, "member_001")
        assert member is not None
        assert member.name == "Иван"
        assert member.age == 35
        assert member.role == FamilyRole.PARENT
        assert member.age_group == AgeGroup.ADULT
    
    def test_add_child_member(self):
        """Тест добавления ребенка"""
        self.manager.create_family(self.family_id, self.family_name)
        
        result = self.manager.add_family_member(
            self.family_id, "child_001", "Маша", 8
        )
        
        assert result is True
        member = self.manager.get_family_member(self.family_id, "child_001")
        assert member is not None
        assert member.role == FamilyRole.CHILD
        assert member.age_group == AgeGroup.CHILD
    
    def test_determine_role_by_age(self):
        """Тест определения роли по возрасту"""
        assert self.manager._determine_role_by_age(5) == FamilyRole.CHILD
        assert self.manager._determine_role_by_age(15) == FamilyRole.TEEN
        assert self.manager._determine_role_by_age(30) == FamilyRole.PARENT
        assert self.manager._determine_role_by_age(70) == FamilyRole.ELDERLY
    
    def test_determine_age_group(self):
        """Тест определения возрастной группы"""
        assert self.manager._determine_age_group(3) == AgeGroup.TODDLER
        assert self.manager._determine_age_group(8) == AgeGroup.CHILD
        assert self.manager._determine_age_group(15) == AgeGroup.TEEN
        assert self.manager._determine_age_group(30) == AgeGroup.ADULT
        assert self.manager._determine_age_group(70) == AgeGroup.SENIOR
    
    def test_get_family_summary(self):
        """Тест получения сводки по семье"""
        self.manager.create_family(self.family_id, self.family_name)
        self.manager.add_family_member(self.family_id, "parent_001", "Папа", 35)
        self.manager.add_family_member(self.family_id, "child_001", "Ребенок", 8)
        
        summary = self.manager.get_family_summary(self.family_id)
        
        assert summary is not None
        assert summary["family_id"] == self.family_id
        assert summary["family_name"] == self.family_name
        assert summary["total_members"] == 2
    
    def test_get_status(self):
        """Тест получения статуса менеджера"""
        self.manager.create_family(self.family_id, self.family_name)
        self.manager.add_family_member(self.family_id, "member_001", "Тест", 30)
        
        status = self.manager.get_status()
        
        assert status["status"] == "active"
        assert status["total_families"] == 1
        assert status["total_members"] == 1
        assert self.family_id in status["families"]


if __name__ == "__main__":
    pytest.main([__file__])
