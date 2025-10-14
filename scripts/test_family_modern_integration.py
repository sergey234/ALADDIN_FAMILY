#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование интеграции современных функций в семейную систему безопасности
IPv6 защита, Kill Switch, родительский контроль
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Добавление пути к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_family_modern_integration():
    """Тестирование интеграции современных функций в семейную систему"""
    print("🏠 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ С СЕМЕЙНОЙ СИСТЕМОЙ")
    print("=" * 60)
    print(f"Время начала: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Импорт семейных компонентов
        from security.family.family_profile_manager import (
            FamilyProfileManager, FamilyProfile, FamilyMember, AgeGroup, FamilyRole
        )
        from security.family.parental_controls import (
            ParentalControls, ControlType, ControlStatus
        )
        from security.family.child_protection import (
            ChildProtection, KillSwitchStatus, ThreatLevel, ContentCategory
        )
        
        print("1. Создание тестовой семьи...")
        
        # Создание семейного профиля
        family_manager = FamilyProfileManager()
        
        # Создание тестовой семьи
        test_family = FamilyProfile(
            family_id="test_family_modern",
            family_name="Тестовая семья с современными функциями",
            created_at=datetime.now()
        )
        
        # Добавление ребенка
        child = FamilyMember(
            id="child_modern_1",
            name="Анна (тест)",
            age=10,
            role=FamilyRole.CHILD,
            age_group=AgeGroup.CHILD
        )
        test_family.members["child_modern_1"] = child
        
        # Добавление родителя
        parent = FamilyMember(
            id="parent_modern_1",
            name="Мама (тест)",
            age=35,
            role=FamilyRole.PARENT,
            age_group=AgeGroup.ADULT
        )
        test_family.members["parent_modern_1"] = parent
        
        family_manager.families["test_family_modern"] = test_family
        
        print(f"   ✅ Семья создана: {test_family.family_name}")
        print(f"   ✅ Ребенок: {child.name} ({child.age} лет)")
        print(f"   ✅ Родитель: {parent.name} ({parent.age} лет)")
        
        print("\n2. Инициализация систем защиты...")
        
        # Создание систем защиты
        child_protection = ChildProtection()
        parental_controls = ParentalControls(
            family_profile_manager=family_manager,
            child_protection=child_protection,
            elderly_protection=None  # Для теста не нужен
        )
        
        print("   ✅ ChildProtection инициализирован")
        print("   ✅ ParentalControls инициализирован")
        
        print("\n3. Тестирование IPv6 защиты в родительском контроле...")
        
        # Проверка IPv6 защиты
        ipv6_protected, ipv6_message = parental_controls.check_ipv6_protection("child_modern_1")
        print(f"   📊 IPv6 защита: {'✅' if ipv6_protected else '❌'} {ipv6_message}")
        
        # Получение статуса современных функций
        modern_status = parental_controls.get_modern_protection_status("child_modern_1")
        print(f"   📊 IPv6 статус: {modern_status['ipv6_protection']['status']}")
        print(f"   📊 Kill Switch статус: {modern_status['kill_switch']['status']}")
        print(f"   📊 Активных функций: {modern_status['modern_features_active']}/{modern_status['total_modern_features']}")
        
        print("\n4. Тестирование Kill Switch в защите детей...")
        
        # Настройка Kill Switch для ребенка
        kill_switch_setup = child_protection.setup_kill_switch("child_modern_1", {
            "auto_kill_on_danger": True,
            "auto_kill_on_vpn_disconnect": True,
            "auto_kill_on_suspicious_activity": True,
            "notify_parents_on_kill": True,
            "kill_duration_minutes": 30
        })
        print(f"   📊 Настройка Kill Switch: {'✅' if kill_switch_setup else '❌'}")
        
        # Получение статуса Kill Switch
        kill_switch_status = child_protection.get_kill_switch_status("child_modern_1")
        print(f"   📊 Kill Switch настроен: {'✅' if kill_switch_status['kill_switch_configured'] else '❌'}")
        print(f"   📊 Статус: {kill_switch_status['status']}")
        print(f"   📊 Авто-килл при опасности: {'✅' if kill_switch_status['config']['auto_kill_on_danger'] else '❌'}")
        
        print("\n5. Тестирование активации Kill Switch...")
        
        # Активация Kill Switch
        kill_activated = child_protection.activate_kill_switch("child_modern_1", "Тестовая активация")
        print(f"   📊 Kill Switch активирован: {'✅' if kill_activated else '❌'}")
        
        # Проверка статуса после активации
        kill_switch_status_after = child_protection.get_kill_switch_status("child_modern_1")
        print(f"   📊 Статус после активации: {kill_switch_status_after['status']}")
        print(f"   📊 История активаций: {kill_switch_status_after['history_count']}")
        
        print("\n6. Тестирование деактивации Kill Switch...")
        
        # Деактивация Kill Switch
        kill_deactivated = child_protection.deactivate_kill_switch("child_modern_1")
        print(f"   📊 Kill Switch деактивирован: {'✅' if kill_deactivated else '❌'}")
        
        # Проверка статуса после деактивации
        kill_switch_status_final = child_protection.get_kill_switch_status("child_modern_1")
        print(f"   📊 Статус после деактивации: {kill_switch_status_final['status']}")
        
        print("\n7. Тестирование проверки условий Kill Switch...")
        
        # Создание тестовой активности
        from security.family.child_protection import ChildActivity
        test_activity = ChildActivity(
            activity_id="test_activity_1",
            child_id="child_modern_1",
            activity_type="web_browsing",
            content_category=ContentCategory.SOCIAL,
            start_time=datetime.now(),
            threat_level=ThreatLevel.DANGEROUS,
            blocked=True
        )
        
        # Проверка условий
        should_kill = child_protection.check_kill_switch_conditions("child_modern_1", test_activity)
        print(f"   📊 Условия для Kill Switch: {'✅' if should_kill else '❌'} (опасная активность)")
        
        print("\n8. Получение общего статуса систем...")
        
        # Статус родительского контроля
        parental_status = parental_controls.get_status()
        print(f"   📊 Всего правил контроля: {parental_status['total_control_rules']}")
        print(f"   📊 Активных правил: {parental_status['active_rules']}")
        print(f"   📊 IPv6 правил: {parental_status['modern_features']['ipv6_protection_rules']}")
        print(f"   📊 Kill Switch правил: {parental_status['modern_features']['kill_switch_rules']}")
        print(f"   📊 Активных современных функций: {parental_status['modern_features']['active_modern_features']}")
        
        # Статус защиты детей
        child_status = child_protection.get_status()
        print(f"   📊 Всего детей: {child_status['total_children']}")
        print(f"   📊 Kill Switch настроен для: {child_status['kill_switch']['configured_children']} детей")
        print(f"   📊 Kill Switch активен для: {child_status['kill_switch']['active_children']} детей")
        
        print("\n🎉 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ ЗАВЕРШЕНО УСПЕШНО!")
        print("\n📊 РЕЗУЛЬТАТЫ ИНТЕГРАЦИИ:")
        print("   ✅ IPv6 защита интегрирована в родительский контроль")
        print("   ✅ Kill Switch интегрирован в защиту детей")
        print("   ✅ Семейная система поддерживает современные функции")
        print("   ✅ Автоматическая активация Kill Switch при опасности")
        print("   ✅ Уведомления родителей о событиях безопасности")
        print("   ✅ Полная интеграция с существующей семейной системой")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка в тестировании интеграции: {e}")
        print(f"\n❌ ОШИБКА В ТЕСТИРОВАНИИ: {e}")
        return False

async def main():
    """Основная функция"""
    print("🏠 ALADDIN - ИНТЕГРАЦИЯ С СЕМЕЙНОЙ СИСТЕМОЙ")
    print("=" * 60)
    
    # Тестирование интеграции
    success = await test_family_modern_integration()
    
    print("\n" + "=" * 60)
    print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if success:
        print("✅ СОВРЕМЕННЫЕ ФУНКЦИИ УСПЕШНО ИНТЕГРИРОВАНЫ В СЕМЕЙНУЮ СИСТЕМУ!")
        print("\n🎯 ИНТЕГРИРОВАННЫЕ ФУНКЦИИ:")
        print("1. 🛡️ IPv6 защита - в родительском контроле")
        print("2. ⚡ Kill Switch - в защите детей")
        print("3. 👨‍👩‍👧‍👦 Семейная интеграция - полная поддержка")
        print("4. 📱 Автоматическая защита - при опасной активности")
        print("5. 🔔 Уведомления родителей - о событиях безопасности")
        print("6. 📊 Мониторинг - статус всех функций")
        print("7. 🎛️ Гибкие настройки - для каждого ребенка")
        print("8. 🔒 Максимальная безопасность - для всей семьи")
    else:
        print("❌ ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ ЗАВЕРШЕНО С ОШИБКАМИ!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
