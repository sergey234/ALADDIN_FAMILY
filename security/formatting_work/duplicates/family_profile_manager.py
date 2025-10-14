#!/usr/bin/env python3
"""
FamilyProfileManager - Менеджер семейных профилей
ОБНОВЛЕННАЯ ВЕРСИЯ с обратной совместимостью

Этот файл теперь является адаптером для FamilyProfileManagerEnhanced
Обеспечивает полную обратную совместимость с существующим API
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import SecurityBase

# Импорт enhanced версии
from .family_profile_manager_enhanced import (
    FamilyProfileManagerEnhanced,
    FamilyRole as EnhancedFamilyRole,
    AgeGroup as EnhancedAgeGroup,
    FamilyMember as EnhancedFamilyMember,
    FamilyProfile as EnhancedFamilyProfile,
    FamilyGroup as EnhancedFamilyGroup,
    FamilyGroupStatus,
    MessageType,
    MessagePriority,
    CommunicationChannel
)

# ==================== ОБРАТНАЯ СОВМЕСТИМОСТЬ ====================

# Переопределяем классы для обратной совместимости
class FamilyRole(Enum):
    """Роли в семье (обратная совместимость)"""
    CHILD = "child"
    TEEN = "teen"
    PARENT = "parent"
    ELDERLY = "elderly"


class AgeGroup(Enum):
    """Возрастные группы (обратная совместимость)"""
    TODDLER = "toddler"
    CHILD = "child"
    TEEN = "teen"
    ADULT = "adult"
    SENIOR = "senior"


@dataclass
class FamilyMember:
    """Профиль члена семьи (обратная совместимость)"""
    id: str
    name: str
    age: int
    role: FamilyRole
    age_group: AgeGroup
    devices: List[str] = field(default_factory=list)
    permissions: Dict[str, Any] = field(default_factory=dict)
    restrictions: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: Optional[datetime] = None
    is_active: bool = True


@dataclass
class FamilyProfile:
    """Профиль семьи (обратная совместимость)"""
    family_id: str
    family_name: str
    members: Dict[str, FamilyMember] = field(default_factory=dict)
    emergency_contacts: List[Dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class FamilyProfileManager(SecurityBase):
    """
    Менеджер семейных профилей (обратная совместимость)
    
    Этот класс является адаптером для FamilyProfileManagerEnhanced
    Обеспечивает полную совместимость с существующим API
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("FamilyProfileManager", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )
        
        # Создаем enhanced версию
        self.enhanced_manager = FamilyProfileManagerEnhanced(config)
        self.enhanced_manager.initialize()
        
        # Кэш для обратной совместимости
        self._legacy_families: Dict[str, FamilyProfile] = {}

    def create_family(self, family_id: str, family_name: str) -> bool:
        """Создание новой семьи (обратная совместимость)"""
        try:
            # Используем enhanced версию
            result = self.enhanced_manager.create_family(family_id, family_name)
            
            if result:
                # Создаем legacy версию для совместимости
                legacy_family = FamilyProfile(
                    family_id=family_id,
                    family_name=family_name
                )
                self._legacy_families[family_id] = legacy_family
                
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка создания семьи {family_id}: {e}")
            return False

    def add_family_member(
        self,
        family_id: str,
        member_id: str,
        name: str,
        age: int,
        role: Optional[FamilyRole] = None,
    ) -> bool:
        """Добавление члена семьи (обратная совместимость)"""
        try:
            # Конвертируем роль в enhanced формат
            enhanced_role = None
            if role:
                enhanced_role = EnhancedFamilyRole(role.value)
            
            # Используем enhanced версию
            result = self.enhanced_manager.add_family_member(
                family_id, member_id, name, age, enhanced_role
            )
            
            if result and family_id in self._legacy_families:
                # Обновляем legacy версию
                enhanced_member = self.enhanced_manager.families[family_id].members[member_id]
                
                legacy_member = FamilyMember(
                    id=enhanced_member.id,
                    name=enhanced_member.name,
                    age=enhanced_member.age,
                    role=FamilyRole(enhanced_member.role.value),
                    age_group=AgeGroup(enhanced_member.age_group.value),
                    devices=enhanced_member.devices,
                    permissions=enhanced_member.permissions,
                    restrictions=enhanced_member.restrictions,
                    preferences=enhanced_member.preferences,
                    created_at=enhanced_member.created_at,
                    last_active=enhanced_member.last_active,
                    is_active=enhanced_member.is_active
                )
                
                self._legacy_families[family_id].members[member_id] = legacy_member
                self._legacy_families[family_id].updated_at = datetime.now()
                
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка добавления члена семьи: {e}")
            return False

    def get_family_member(self, family_id: str, member_id: str) -> Optional[FamilyMember]:
        """Получение члена семьи (обратная совместимость)"""
        try:
            if family_id not in self._legacy_families:
                return None
                
            return self._legacy_families[family_id].members.get(member_id)
            
        except Exception as e:
            self.logger.error(f"Ошибка получения члена семьи: {e}")
            return None

    def get_family(self, family_id: str) -> Optional[FamilyProfile]:
        """Получение семьи (обратная совместимость)"""
        try:
            return self._legacy_families.get(family_id)
            
        except Exception as e:
            self.logger.error(f"Ошибка получения семьи: {e}")
            return None

    def get_all_families(self) -> Dict[str, FamilyProfile]:
        """Получение всех семей (обратная совместимость)"""
        return self._legacy_families.copy()

    def update_member_permissions(
        self, family_id: str, member_id: str, permissions: Dict[str, Any]
    ) -> bool:
        """Обновление разрешений члена семьи (обратная совместимость)"""
        try:
            if family_id not in self.enhanced_manager.families:
                return False
                
            if member_id not in self.enhanced_manager.families[family_id].members:
                return False
                
            # Обновляем в enhanced версии
            member = self.enhanced_manager.families[family_id].members[member_id]
            member.permissions.update(permissions)
            
            # Обновляем в legacy версии
            if family_id in self._legacy_families:
                if member_id in self._legacy_families[family_id].members:
                    self._legacy_families[family_id].members[member_id].permissions.update(permissions)
                    self._legacy_families[family_id].updated_at = datetime.now()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления разрешений: {e}")
            return False

    def update_member_restrictions(
        self, family_id: str, member_id: str, restrictions: Dict[str, Any]
    ) -> bool:
        """Обновление ограничений члена семьи (обратная совместимость)"""
        try:
            if family_id not in self.enhanced_manager.families:
                return False
                
            if member_id not in self.enhanced_manager.families[family_id].members:
                return False
                
            # Обновляем в enhanced версии
            member = self.enhanced_manager.families[family_id].members[member_id]
            member.restrictions.update(restrictions)
            
            # Обновляем в legacy версии
            if family_id in self._legacy_families:
                if member_id in self._legacy_families[family_id].members:
                    self._legacy_families[family_id].members[member_id].restrictions.update(restrictions)
                    self._legacy_families[family_id].updated_at = datetime.now()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления ограничений: {e}")
            return False

    def remove_family_member(self, family_id: str, member_id: str) -> bool:
        """Удаление члена семьи (обратная совместимость)"""
        try:
            if family_id not in self.enhanced_manager.families:
                return False
                
            if member_id not in self.enhanced_manager.families[family_id].members:
                return False
                
            # Удаляем из enhanced версии
            del self.enhanced_manager.families[family_id].members[member_id]
            self.enhanced_manager.total_members -= 1
            self.enhanced_manager.active_members -= 1
            
            # Удаляем из legacy версии
            if family_id in self._legacy_families:
                if member_id in self._legacy_families[family_id].members:
                    del self._legacy_families[family_id].members[member_id]
                    self._legacy_families[family_id].updated_at = datetime.now()
            
            self.logger.info(f"Член семьи {member_id} удален из семьи {family_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка удаления члена семьи: {e}")
            return False

    def get_family_statistics(self, family_id: str) -> Optional[Dict[str, Any]]:
        """Получение статистики семьи (обратная совместимость)"""
        try:
            # Используем enhanced версию для получения полной статистики
            enhanced_stats = self.enhanced_manager.get_family_statistics(family_id)
            
            if not enhanced_stats:
                return None
                
            # Конвертируем в legacy формат
            legacy_stats = {
                'family_id': enhanced_stats['family_id'],
                'family_name': enhanced_stats['family_name'],
                'total_members': enhanced_stats['total_members'],
                'active_members': enhanced_stats['active_members'],
                'created_at': enhanced_stats['created_at'],
                'updated_at': enhanced_stats['updated_at']
            }
            
            return legacy_stats
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return None

    def shutdown(self) -> bool:
        """Корректное завершение работы (обратная совместимость)"""
        try:
            # Завершаем enhanced версию
            self.enhanced_manager.shutdown()
            
            # Очищаем legacy кэш
            self._legacy_families.clear()
            
            self.logger.info("FamilyProfileManager остановлен")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка завершения работы: {e}")
            return False

    # ==================== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ====================
    
    def get_enhanced_manager(self) -> FamilyProfileManagerEnhanced:
        """Получение доступа к enhanced менеджеру"""
        return self.enhanced_manager
    
    def migrate_to_enhanced(self) -> bool:
        """Миграция данных в enhanced версию"""
        try:
            # Данные уже в enhanced версии, просто синхронизируем legacy
            for family_id, enhanced_family in self.enhanced_manager.families.items():
                if family_id not in self._legacy_families:
                    # Создаем legacy версию
                    legacy_family = FamilyProfile(
                        family_id=enhanced_family.family_id,
                        family_name=enhanced_family.family_name,
                        emergency_contacts=enhanced_family.emergency_contacts,
                        created_at=enhanced_family.created_at,
                        updated_at=enhanced_family.updated_at
                    )
                    
                    # Конвертируем членов семьи
                    for member_id, enhanced_member in enhanced_family.members.items():
                        legacy_member = FamilyMember(
                            id=enhanced_member.id,
                            name=enhanced_member.name,
                            age=enhanced_member.age,
                            role=FamilyRole(enhanced_member.role.value),
                            age_group=AgeGroup(enhanced_member.age_group.value),
                            devices=enhanced_member.devices,
                            permissions=enhanced_member.permissions,
                            restrictions=enhanced_member.restrictions,
                            preferences=enhanced_member.preferences,
                            created_at=enhanced_member.created_at,
                            last_active=enhanced_member.last_active,
                            is_active=enhanced_member.is_active
                        )
                        legacy_family.members[member_id] = legacy_member
                    
                    self._legacy_families[family_id] = legacy_family
            
            self.logger.info("Миграция в enhanced версию завершена")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка миграции: {e}")
            return False


# ==================== ФАБРИКА ====================

def create_family_profile_manager(config: Optional[Dict[str, Any]] = None) -> FamilyProfileManager:
    """Фабрика для создания FamilyProfileManager (обратная совместимость)"""
    manager = FamilyProfileManager(config)
    return manager


# ==================== ТЕСТИРОВАНИЕ ====================

if __name__ == "__main__":
    # Тестирование обратной совместимости
    manager = create_family_profile_manager()
    
    # Создание семьи
    family_id = "test_family_legacy"
    manager.create_family(family_id, "Тестовая семья (Legacy)")
    
    # Добавление членов
    manager.add_family_member(family_id, "parent_001", "Иван Петров", 35, FamilyRole.PARENT)
    manager.add_family_member(family_id, "child_001", "Мария Петрова", 10, FamilyRole.CHILD)
    
    # Получение данных
    family = manager.get_family(family_id)
    print(f"Legacy семья: {family.family_name if family else 'Не найдена'}")
    
    # Статистика
    stats = manager.get_family_statistics(family_id)
    print(f"Legacy статистика: {stats}")
    
    # Enhanced статистика
    enhanced_stats = manager.get_enhanced_manager().get_system_statistics()
    print(f"Enhanced статистика: {enhanced_stats}")
    
    print("FamilyProfileManager (Legacy) успешно протестирован!")