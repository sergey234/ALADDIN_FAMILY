"""
FamilyProfileManager - Менеджер семейных профилей
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from core.base import SecurityBase


class FamilyRole(Enum):
    """Роли в семье"""

    CHILD = "child"
    TEEN = "teen"
    PARENT = "parent"
    ELDERLY = "elderly"


class AgeGroup(Enum):
    """Возрастные группы"""

    TODDLER = "toddler"
    CHILD = "child"
    TEEN = "teen"
    ADULT = "adult"
    SENIOR = "senior"


@dataclass
class FamilyMember:
    """Профиль члена семьи"""

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
    """Профиль семьи"""

    family_id: str
    family_name: str
    members: Dict[str, FamilyMember] = field(default_factory=dict)
    emergency_contacts: List[Dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class FamilyProfileManager(SecurityBase):
    """Менеджер семейных профилей"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("FamilyProfileManager", config)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )
        self.families: Dict[str, FamilyProfile] = {}

    def create_family(self, family_id: str, family_name: str) -> bool:
        """Создание новой семьи"""
        try:
            if family_id in self.families:
                self.logger.warning(f"Семья {family_id} уже существует")
                return False

            family = FamilyProfile(
                family_id=family_id, family_name=family_name
            )

            self.families[family_id] = family
            self.logger.info(f"Семья {family_name} создана с ID: {family_id}")
            return True

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
        """Добавление члена семьи"""
        try:
            if family_id not in self.families:
                self.logger.error(f"Семья {family_id} не найдена")
                return False

            if member_id in self.families[family_id].members:
                self.logger.warning(f"Член семьи {member_id} уже существует")
                return False

            # Определяем роль и возрастную группу
            if role is None:
                role = self._determine_role_by_age(age)
            age_group = self._determine_age_group(age)

            # Создаем профиль члена семьи
            member = FamilyMember(
                id=member_id,
                name=name,
                age=age,
                role=role,
                age_group=age_group,
            )

            # Добавляем в семью
            self.families[family_id].members[member_id] = member
            self.families[family_id].updated_at = datetime.now()

            self.logger.info(
                f"Добавлен член семьи: {name} "
                f"(возраст: {age}, роль: {role.value})"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Ошибка добавления члена семьи {member_id}: {e}"
            )
            return False

    def _determine_role_by_age(self, age: int) -> FamilyRole:
        """Определение роли по возрасту

        Args:
            age: Возраст члена семьи

        Returns:
            FamilyRole: Роль в семье на основе возраста

        Raises:
            ValueError: Если возраст отрицательный
        """
        try:
            if age < 0:
                raise ValueError(f"Возраст не может быть отрицательным: {age}")

            if age < 13:
                return FamilyRole.CHILD
            elif age < 18:
                return FamilyRole.TEEN
            elif age < 65:
                return FamilyRole.PARENT
            else:
                return FamilyRole.ELDERLY
        except Exception as e:
            self.logger.error(
                f"Ошибка определения роли по возрасту {age}: {e}"
            )
            return (
                FamilyRole.CHILD
            )  # Возвращаем безопасное значение по умолчанию

    def _determine_age_group(self, age: int) -> AgeGroup:
        """Определение возрастной группы

        Args:
            age: Возраст члена семьи

        Returns:
            AgeGroup: Возрастная группа на основе возраста

        Raises:
            ValueError: Если возраст отрицательный
        """
        try:
            if age < 0:
                raise ValueError(f"Возраст не может быть отрицательным: {age}")

            if age <= 5:
                return AgeGroup.TODDLER
            elif age <= 12:
                return AgeGroup.CHILD
            elif age <= 17:
                return AgeGroup.TEEN
            elif age < 65:
                return AgeGroup.ADULT
            else:
                return AgeGroup.SENIOR
        except Exception as e:
            self.logger.error(
                f"Ошибка определения возрастной группы {age}: {e}"
            )
            return (
                AgeGroup.CHILD
            )  # Возвращаем безопасное значение по умолчанию

    def get_family_member(
        self, family_id: str, member_id: str
    ) -> Optional[FamilyMember]:
        """Получение профиля члена семьи"""
        try:
            if family_id not in self.families:
                return None
            return self.families[family_id].members.get(member_id)
        except Exception as e:
            self.logger.error(f"Ошибка получения члена семьи {member_id}: {e}")
            return None

    def get_family_summary(self, family_id: str) -> Optional[Dict[str, Any]]:
        """Получение сводки по семье"""
        try:
            if family_id not in self.families:
                return None

            family = self.families[family_id]
            summary = {
                "family_id": family_id,
                "family_name": family.family_name,
                "total_members": len(family.members),
                "created_at": family.created_at.isoformat(),
                "updated_at": family.updated_at.isoformat(),
                "emergency_contacts_count": len(family.emergency_contacts),
            }

            return summary

        except Exception as e:
            self.logger.error(f"Ошибка получения сводки семьи: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса менеджера семейных профилей"""
        try:
            total_families = len(self.families)
            total_members = sum(
                len(family.members) for family in self.families.values()
            )

            return {
                "status": "active",
                "total_families": total_families,
                "total_members": total_members,
                "families": list(self.families.keys()),
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Ошибка получения статуса: {e}")
            return {"status": "error", "error": str(e)}

    # Enhanced version with improvements
    def __str__(self) -> str:
        """Строковое представление менеджера семейных профилей"""
        return f"FamilyProfileManager(families={len(self.families)})"

    def __repr__(self) -> str:
        """Детальное представление менеджера семейных профилей"""
        total_members = sum(len(f.members) for f in self.families.values())
        return (
            f"FamilyProfileManager("
            f"families={len(self.families)}, "
            f"total_members={total_members}"
            f")"
        )

    def __len__(self) -> int:
        """Возвращает количество семей"""
        return len(self.families)

    def __contains__(self, family_id: str) -> bool:
        """Проверяет, существует ли семья с указанным ID"""
        return family_id in self.families

    def __iter__(self):
        """Итератор по семьям"""
        return iter(self.families.values())

    def __getitem__(self, family_id: str) -> FamilyProfile:
        """Получение семьи по ID"""
        if family_id not in self.families:
            raise KeyError(f"Семья с ID {family_id} не найдена")
        return self.families[family_id]

    def __setitem__(self, family_id: str, family: FamilyProfile) -> None:
        """Установка семьи по ID"""
        if not isinstance(family, FamilyProfile):
            raise TypeError("Значение должно быть экземпляром FamilyProfile")
        self.families[family_id] = family

    def __delitem__(self, family_id: str) -> None:
        """Удаление семьи по ID"""
        if family_id not in self.families:
            raise KeyError(f"Семья с ID {family_id} не найдена")
        del self.families[family_id]

    def keys(self):
        """Возвращает ключи (ID семей)"""
        return self.families.keys()

    def values(self):
        """Возвращает значения (семьи)"""
        return self.families.values()

    def items(self):
        """Возвращает пары ключ-значение"""
        return self.families.items()

    def clear(self) -> None:
        """Очищает все семьи"""
        self.families.clear()
        self.logger.info("Все семьи очищены")

    def get(self, family_id: str, default=None):
        """Безопасное получение семьи по ID"""
        return self.families.get(family_id, default)

    def pop(self, family_id: str, default=None):
        """Удаляет и возвращает семью по ID"""
        return self.families.pop(family_id, default)

    def update(self, other) -> None:
        """Обновляет семьи из другого словаря"""
        if not isinstance(other, dict):
            raise TypeError("Аргумент должен быть словарем")
        self.families.update(other)
        self.logger.info(f"Обновлено {len(other)} семей")

    def copy(self) -> "FamilyProfileManager":
        """Создает копию менеджера"""
        new_manager = FamilyProfileManager()
        new_manager.families = self.families.copy()
        return new_manager

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует менеджер в словарь"""
        return {
            "families": {
                family_id: {
                    "family_id": family.family_id,
                    "family_name": family.family_name,
                    "members": {
                        member_id: {
                            "id": member.id,
                            "name": member.name,
                            "age": member.age,
                            "role": member.role.value,
                            "age_group": member.age_group.value,
                            "devices": member.devices,
                            "permissions": member.permissions,
                            "restrictions": member.restrictions,
                            "preferences": member.preferences,
                            "created_at": member.created_at.isoformat(),
                            "last_active": (
                                member.last_active.isoformat()
                                if member.last_active
                                else None
                            ),
                            "is_active": member.is_active,
                        }
                        for member_id, member in family.members.items()
                    },
                    "emergency_contacts": family.emergency_contacts,
                    "created_at": family.created_at.isoformat(),
                    "updated_at": family.updated_at.isoformat(),
                }
                for family_id, family in self.families.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FamilyProfileManager":
        """Создает менеджер из словаря"""
        manager = cls()
        for family_id, family_data in data.get("families", {}).items():
            family = FamilyProfile(
                family_id=family_data["family_id"],
                family_name=family_data["family_name"],
                emergency_contacts=family_data["emergency_contacts"],
                created_at=datetime.fromisoformat(family_data["created_at"]),
                updated_at=datetime.fromisoformat(family_data["updated_at"]),
            )

            for member_id, member_data in family_data["members"].items():
                member = FamilyMember(
                    id=member_data["id"],
                    name=member_data["name"],
                    age=member_data["age"],
                    role=FamilyRole(member_data["role"]),
                    age_group=AgeGroup(member_data["age_group"]),
                    devices=member_data["devices"],
                    permissions=member_data["permissions"],
                    restrictions=member_data["restrictions"],
                    preferences=member_data["preferences"],
                    created_at=datetime.fromisoformat(
                        member_data["created_at"]
                    ),
                    last_active=(
                        datetime.fromisoformat(member_data["last_active"])
                        if member_data["last_active"]
                        else None
                    ),
                    is_active=member_data["is_active"],
                )
                family.members[member_id] = member

            manager.families[family_id] = family

        return manager

    def validate_family(self, family_id: str) -> bool:
        """Валидация семьи"""
        try:
            if family_id not in self.families:
                return False

            family = self.families[family_id]

            # Проверяем обязательные поля
            if not family.family_id or not family.family_name:
                return False

            # Проверяем членов семьи
            for member_id, member in family.members.items():
                if not member.id or not member.name or member.age < 0:
                    return False

            return True
        except Exception as e:
            self.logger.error(f"Ошибка валидации семьи {family_id}: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики"""
        try:
            total_families = len(self.families)
            total_members = sum(
                len(family.members) for family in self.families.values()
            )

            # Статистика по ролям
            role_stats = {}
            age_group_stats = {}

            for family in self.families.values():
                for member in family.members.values():
                    role = member.role.value
                    age_group = member.age_group.value

                    role_stats[role] = role_stats.get(role, 0) + 1
                    age_group_stats[age_group] = (
                        age_group_stats.get(age_group, 0) + 1
                    )

            return {
                "total_families": total_families,
                "total_members": total_members,
                "role_distribution": role_stats,
                "age_group_distribution": age_group_stats,
                "average_members_per_family": (
                    total_members / total_families if total_families > 0 else 0
                ),
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return {}

    def export_to_json(self, filepath: str) -> bool:
        """Экспорт в JSON файл"""
        try:
            import json

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            self.logger.info(f"Данные экспортированы в {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка экспорта в JSON: {e}")
            return False

    def import_from_json(self, filepath: str) -> bool:
        """Импорт из JSON файла"""
        try:
            import json

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            new_manager = self.from_dict(data)
            self.families = new_manager.families
            self.logger.info(f"Данные импортированы из {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка импорта из JSON: {e}")
            return False


# Enhanced version with improvements
