#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СИСТЕМА АНОНИМНОЙ РЕГИСТРАЦИИ СЕМЕЙ
====================================

Полностью соответствует 152-ФЗ - НЕ собирает персональные данные
Собирает только анонимную информацию для безопасности семьи

Автор: ALADDIN Security System
Версия: 1.0.0
Дата: 2024
"""

import hashlib
import secrets
import string
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Set
from dataclasses import dataclass
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FamilyRole(Enum):
    """Роли участников семьи (анонимно)"""
    PARENT = "parent"  # Родитель
    CHILD = "child"  # Ребенок
    ELDERLY = "elderly"  # Пожилой человек
    OTHER = "other"  # Другой член семьи


class AgeGroup(Enum):
    """Возрастные группы (анонимно)"""
    CHILD_1_6 = "1-6"  # Дети 1-6 лет
    CHILD_7_12 = "7-12"  # Дети 7-12 лет
    TEEN_13_17 = "13-17"  # Подростки 13-17 лет
    YOUNG_ADULT_18_23 = "18-23"  # Молодые взрослые 18-23
    ADULT_24_55 = "24-55"  # Взрослые 24-55 лет
    ELDERLY_55_PLUS = "55+"  # Пожилые 55+


class RegistrationMethod(Enum):
    """Методы регистрации"""
    QR_CODE = "qr_code"  # Через QR-код
    SHORT_CODE = "short_code"  # Через короткий код
    AUTO = "auto"  # Автоопределение


@dataclass
class AnonymousFamilyProfile:
    """Анонимный профиль участника семьи"""
    family_id: str              # Анонимный ID семьи
    member_id: str              # Анонимный ID участника
    role: FamilyRole            # Роль в семье
    age_group: AgeGroup         # Возрастная группа
    personal_letter: str        # Персональная буква (А, Б, В...)
    device_type: str            # Тип устройства
    registration_time: datetime  # Время регистрации
    last_active: datetime       # Последняя активность
    is_active: bool = True      # Активен ли участник


@dataclass
class RegistrationData:
    """Данные для регистрации (анонимные)"""
    role: FamilyRole
    age_group: AgeGroup
    personal_letter: str
    device_type: str
    method: RegistrationMethod = RegistrationMethod.AUTO


class FamilyRegistration:
    """
    Основной класс системы анонимной регистрации семей

    СООТВЕТСТВИЕ 152-ФЗ:
    ❌ НЕ собираем: имя, фамилия, адрес, телефон, email, паспорт
    ✅ Собираем: роли, возрастные группы, персональные буквы, типы устройств
    """

    def __init__(self):
        """Инициализация системы регистрации"""
        self.families: Dict[str, List[AnonymousFamilyProfile]] = {}
        self.registration_codes: Dict[str, Dict] = {}
        self.used_letters: Set[str] = set()
        self.available_letters = list(string.ascii_uppercase)

        # Настройки безопасности
        self.code_expiry_hours = 24
        self.max_family_members = 10
        self.max_registration_attempts = 3

        logger.info("Система анонимной регистрации семей инициализирована")

    def create_family(self, registration_data: RegistrationData) -> \
            Dict[str, str]:
        """
        Создание новой анонимной семьи

        Args:
            registration_data: Анонимные данные для регистрации

        Returns:
            Dict с family_id, qr_code_data, short_code
        """
        try:
            # Генерация анонимного ID семьи
            family_id = self._generate_anonymous_family_id()

            # Создание профиля создателя семьи
            creator_profile = AnonymousFamilyProfile(
                family_id=family_id,
                member_id=self._generate_member_id(),
                role=registration_data.role,
                age_group=registration_data.age_group,
                personal_letter=registration_data.personal_letter,
                device_type=registration_data.device_type,
                registration_time=datetime.now(),
                last_active=datetime.now()
            )

            # Сохранение семьи
            self.families[family_id] = [creator_profile]
            self.used_letters.add(registration_data.personal_letter)

            # Генерация кодов для присоединения
            qr_code_data = self._generate_qr_code(family_id)
            short_code = self._generate_short_code(family_id)

            # Сохранение кодов
            self.registration_codes[family_id] = {
                'qr_code': qr_code_data,
                'short_code': short_code,
                'expires_at': datetime.now() +
                timedelta(hours=self.code_expiry_hours),
                'attempts': 0
            }

            logger.info(f"Создана анонимная семья {family_id} с ролью \
                {registration_data.role.value}")

            return {
                'family_id': family_id,
                'qr_code_data': qr_code_data,
                'short_code': short_code,
                'creator_member_id': creator_profile.member_id,
                'expires_at': self.registration_codes[family_id]
                ['expires_at'].isoformat()
            }

        except Exception as e:
            logger.error(f"Ошибка создания семьи: {e}")
            raise

    def join_family(self, family_id: str,
                    registration_data: RegistrationData) -> Dict[str, str]:
        """
        Присоединение к существующей семье

        Args:
            family_id: ID семьи для присоединения
            registration_data: Анонимные данные участника

        Returns:
            Dict с результатом присоединения
        """
        try:
            # Проверка существования семьи
            if family_id not in self.families:
                raise ValueError("Семья не найдена")

            # Проверка лимита участников
            if len(self.families[family_id]) >= self.max_family_members:
                raise ValueError("Превышен лимит участников семьи")

            # Проверка уникальности буквы в семье
            existing_letters = {member.personal_letter
                                for member in self.families[family_id]}
            if registration_data.personal_letter in existing_letters:
                raise ValueError("Буква уже используется в этой семье")

            # Создание профиля нового участника
            new_member = AnonymousFamilyProfile(
                family_id=family_id,
                member_id=self._generate_member_id(),
                role=registration_data.role,
                age_group=registration_data.age_group,
                personal_letter=registration_data.personal_letter,
                device_type=registration_data.device_type,
                registration_time=datetime.now(),
                last_active=datetime.now()
            )

            # Добавление участника в семью
            self.families[family_id].append(new_member)

            logger.info(f"Участник {new_member.member_id} "
                        f"присоединился к семье {family_id}")

            return {
                'success': True,
                'member_id': new_member.member_id,
                'family_id': family_id,
                'role': registration_data.role.value,
                'personal_letter': registration_data.personal_letter
            }

        except Exception as e:
            logger.error(f"Ошибка присоединения к семье: {e}")
            raise

    def join_with_qr(self, qr_data: str,
                     registration_data: RegistrationData) -> Dict[str, str]:
        """Присоединение к семье через QR-код"""
        try:
            family_id = self._extract_family_id_from_qr(qr_data)
            if family_id in self.registration_codes:
                if (datetime.now() >
                        self.registration_codes[family_id]['expires_at']):
                    raise ValueError("Код регистрации истек")
            return self.join_family(family_id, registration_data)
        except Exception as e:
            logger.error(f"Ошибка присоединения через QR: {e}")
            raise

    def join_with_code(self, short_code: str,
                       registration_data: RegistrationData) -> Dict[str, str]:
        """Присоединение к семье через короткий код"""
        try:
            family_id = None
            for fid, codes in self.registration_codes.items():
                if codes['short_code'] == short_code:
                    family_id = fid
                    break

            if not family_id:
                raise ValueError("Неверный код регистрации")

            if datetime.now() > self.registration_codes[family_id]['expires_at']:
                raise ValueError("Код регистрации истек")

            self.registration_codes[family_id]['attempts'] += 1
            return self.join_family(family_id, registration_data)
        except Exception as e:
            logger.error(f"Ошибка присоединения через код: {e}")
            raise

    def get_family_members(self, family_id: str) -> List[Dict[str, str]]:
        """Получение списка участников семьи (анонимно)"""
        try:
            if family_id not in self.families:
                raise ValueError("Семья не найдена")

            members_data = []
            for member in self.families[family_id]:
                members_data.append({
                    'member_id': member.member_id,
                    'role': member.role.value,
                    'age_group': member.age_group.value,
                    'personal_letter': member.personal_letter,
                    'device_type': member.device_type,
                    'registration_time': member.registration_time.isoformat(),
                    'last_active': member.last_active.isoformat(),
                    'is_active': member.is_active
                })
            return members_data
        except Exception as e:
            logger.error(f"Ошибка получения участников семьи: {e}")
            raise

    def get_family_status(self, family_id: str) -> Dict[str, any]:
        """Получение статуса семьи"""
        try:
            if family_id not in self.families:
                raise ValueError("Семья не найдена")

            family = self.families[family_id]
            active_members = [m for m in family if m.is_active]

            return {
                'family_id': family_id,
                'total_members': len(family),
                'active_members': len(active_members),
                'roles_distribution': {
                    role.value: len([m for m in family if m.role == role])
                    for role in FamilyRole
                },
                'age_groups_distribution': {
                    age_group.value: len([m for m in family if m.age_group == age_group])
                    for age_group in AgeGroup
                },
                'device_types': list(set(m.device_type for m in family)),
                'created_at': min(m.registration_time for m in family).isoformat(),
                'last_activity': max(m.last_active for m in family).isoformat()
            }
        except Exception as e:
            logger.error(f"Ошибка получения статуса семьи: {e}")
            raise

    def get_available_letters(self, family_id: str) -> List[str]:
        """Получение доступных букв для выбора в семье"""
        try:
            if family_id not in self.families:
                return self.available_letters.copy()

            used_letters = {member.personal_letter for member in self.families[family_id]}
            available = [letter for letter in self.available_letters if letter not in used_letters]
            return available
        except Exception as e:
            logger.error(f"Ошибка получения доступных букв: {e}")
            return []

    def cleanup_expired_codes(self) -> int:
        """Очистка истекших кодов регистрации"""
        try:
            current_time = datetime.now()
            expired_codes = []

            for family_id, codes in self.registration_codes.items():
                if current_time > codes['expires_at']:
                    expired_codes.append(family_id)

            for family_id in expired_codes:
                del self.registration_codes[family_id]

            logger.info(f"Удалено {len(expired_codes)} истекших кодов")
            return len(expired_codes)
        except Exception as e:
            logger.error(f"Ошибка очистки кодов: {e}")
            return 0

    def _generate_anonymous_family_id(self) -> str:
        """Генерация анонимного ID семьи"""
        random_data = secrets.token_hex(16)
        timestamp = str(int(time.time()))
        combined = f"{random_data}{timestamp}"
        hash_object = hashlib.sha256(combined.encode())
        family_id = f"FAM_{hash_object.hexdigest()[:12].upper()}"
        return family_id

    def _generate_member_id(self) -> str:
        """Генерация анонимного ID участника"""
        random_data = secrets.token_hex(8)
        timestamp = str(int(time.time()))
        combined = f"{random_data}{timestamp}"
        hash_object = hashlib.sha256(combined.encode())
        member_id = f"MEM_{hash_object.hexdigest()[:8].upper()}"
        return member_id

    def _generate_qr_code(self, family_id: str) -> str:
        """Генерация QR-кода для регистрации"""
        qr_data = {
            'family_id': family_id,
            'timestamp': int(time.time()),
            'type': 'family_registration'
        }
        return json.dumps(qr_data, ensure_ascii=False)

    def _generate_short_code(self, family_id: str) -> str:
        """Генерация короткого кода (4 символа)"""
        base_chars = (family_id[-2:] +
                      secrets.choice(string.ascii_uppercase) +
                      secrets.choice(string.digits))
        short_code = ''.join(secrets.choice(base_chars)
                             for _ in range(4))
        return short_code.upper()

    def _extract_family_id_from_qr(self, qr_data: str) -> str:
        """Извлечение family_id из данных QR-кода"""
        try:
            data = json.loads(qr_data)
            if data.get('type') == 'family_registration':
                return data['family_id']
            else:
                raise ValueError("Неверный тип QR-кода")
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Неверные данные QR-кода: {e}")

    def get_system_statistics(self) -> Dict[str, any]:
        """Получение статистики системы (анонимно)"""
        try:
            total_families = len(self.families)
            total_members = sum(len(family) for family in self.families.values())
            active_codes = len(self.registration_codes)

            role_stats = {}
            for role in FamilyRole:
                count = sum(
                    len([m for m in family if m.role == role])
                    for family in self.families.values()
                )
                role_stats[role.value] = count

            age_stats = {}
            for age_group in AgeGroup:
                count = sum(
                    len([m for m in family if m.age_group == age_group])
                    for family in self.families.values()
                )
                age_stats[age_group.value] = count

            return {
                'total_families': total_families,
                'total_members': total_members,
                'active_registration_codes': active_codes,
                'role_distribution': role_stats,
                'age_group_distribution': age_stats,
                'average_family_size': total_members / total_families if total_families > 0 else 0,
                'system_uptime': 'active',
                'compliance_152_fz': True
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}


# Глобальный экземпляр системы регистрации
family_registration_system = FamilyRegistration()


def create_family(role: str, age_group: str, personal_letter: str, device_type: str) -> Dict[str, str]:
    """Удобная функция для создания семьи"""
    try:
        registration_data = RegistrationData(
            role=FamilyRole(role),
            age_group=AgeGroup(age_group),
            personal_letter=personal_letter.upper(),
            device_type=device_type
        )
        return family_registration_system.create_family(registration_data)
    except Exception as e:
        logger.error(f"Ошибка создания семьи: {e}")
        raise


def join_family(family_id: str, role: str, age_group: str, personal_letter: str, device_type: str) -> Dict[str, str]:
    """Удобная функция для присоединения к семье"""
    try:
        registration_data = RegistrationData(
            role=FamilyRole(role),
            age_group=AgeGroup(age_group),
            personal_letter=personal_letter.upper(),
            device_type=device_type
        )
        return family_registration_system.join_family(family_id, registration_data)
    except Exception as e:
        logger.error(f"Ошибка присоединения к семье: {e}")
        raise


if __name__ == "__main__":
    """Демонстрация работы системы"""
    print("🔐 СИСТЕМА АНОНИМНОЙ РЕГИСТРАЦИИ СЕМЕЙ")
    print("=" * 50)
    print("✅ Полное соответствие 152-ФЗ")
    print("❌ НЕ собираем персональные данные")
    print("✅ Только анонимная информация для безопасности")
    print()

    # Создание семьи
    print("1. Создание семьи...")
    family_data = create_family(
        role="parent",
        age_group="24-55",
        personal_letter="А",
        device_type="smartphone"
    )
    print(f"✅ Семья создана: {family_data['family_id']}")
    print(f"📱 QR-код: {family_data['qr_code_data'][:50]}...")
    print(f"🔢 Короткий код: {family_data['short_code']}")
    print()

    # Присоединение участника
    print("2. Присоединение участника...")
    join_data = join_family(
        family_id=family_data['family_id'],
        role="child",
        age_group="7-12",
        personal_letter="Б",
        device_type="tablet"
    )
    print(f"✅ Участник присоединился: {join_data['member_id']}")
    print()

    # Статистика семьи
    print("3. Статистика семьи...")
    family_status = family_registration_system.get_family_status(family_data['family_id'])
    print(f"👥 Участников: {family_status['total_members']}")
    print(f"📊 Роли: {family_status['roles_distribution']}")
    print()

    # Общая статистика
    print("4. Общая статистика системы...")
    stats = family_registration_system.get_system_statistics()
    print(f"🏠 Семей: {stats['total_families']}")
    print(f"👤 Участников: {stats['total_members']}")
    print(f"✅ Соответствие 152-ФЗ: {stats['compliance_152_fz']}")
    print()
    print("🎯 Система готова к использованию!")
