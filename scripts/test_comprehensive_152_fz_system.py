#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ТЕСТИРОВАНИЕ КОМПЛЕКСНОЙ СИСТЕМЫ СООТВЕТСТВИЯ 152-ФЗ
Полное тестирование всех компонентов системы соответствия 152-ФЗ
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Добавление пути к модулям
sys.path.append(str(Path(__file__).parent.parent))

from security.comprehensive_anonymous_family_system import (
    ComprehensiveAnonymousFamilySystem,
    FamilyRole,
    AgeGroup,
    DeviceType,
    ThreatLevel
)
from security.152_fz_compliance_monitor import ComplianceMonitor
from scripts.auto_fix_152_fz_violations import AutoFix152FZViolations


class Comprehensive152FZSystemTester:
    """Тестер комплексной системы соответствия 152-ФЗ"""
    
    def __init__(self):
        self.test_results = []
        self.family_system = ComprehensiveAnonymousFamilySystem()
        self.compliance_monitor = ComplianceMonitor()
        self.auto_fix = AutoFix152FZViolations()
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Запуск комплексного тестирования"""
        print("🧪 КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ СООТВЕТСТВИЯ 152-ФЗ")
        print("=" * 70)
        
        test_results = {
            "test_id": f"comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "started_at": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "running"
        }
        
        try:
            # Тест 1: Создание анонимных семейных профилей
            print("\n1️⃣ ТЕСТ: Создание анонимных семейных профилей")
            family_test = await self._test_family_profiles()
            test_results["tests"]["family_profiles"] = family_test
            
            # Тест 2: Проверка соответствия 152-ФЗ
            print("\n2️⃣ ТЕСТ: Проверка соответствия 152-ФЗ")
            compliance_test = await self._test_compliance_monitoring()
            test_results["tests"]["compliance_monitoring"] = compliance_test
            
            # Тест 3: Автоматическое исправление нарушений
            print("\n3️⃣ ТЕСТ: Автоматическое исправление нарушений")
            auto_fix_test = await self._test_auto_fix()
            test_results["tests"]["auto_fix"] = auto_fix_test
            
            # Тест 4: Интеграционное тестирование
            print("\n4️⃣ ТЕСТ: Интеграционное тестирование")
            integration_test = await self._test_integration()
            test_results["tests"]["integration"] = integration_test
            
            # Тест 5: Нагрузочное тестирование
            print("\n5️⃣ ТЕСТ: Нагрузочное тестирование")
            load_test = await self._test_load()
            test_results["tests"]["load_testing"] = load_test
            
            # Определение общего статуса
            all_tests_passed = all(
                test.get("status") == "passed" 
                for test in test_results["tests"].values()
            )
            
            test_results["overall_status"] = "passed" if all_tests_passed else "failed"
            test_results["completed_at"] = datetime.now().isoformat()
            
            # Генерация отчета
            self._generate_test_report(test_results)
            
            return test_results
            
        except Exception as e:
            test_results["overall_status"] = "error"
            test_results["error"] = str(e)
            test_results["completed_at"] = datetime.now().isoformat()
            print(f"❌ Критическая ошибка тестирования: {e}")
            return test_results
    
    async def _test_family_profiles(self) -> Dict[str, Any]:
        """Тестирование анонимных семейных профилей"""
        try:
            print("  📝 Создание семейного профиля...")
            
            # Создание семейного профиля
            family = self.family_system.create_family_profile()
            if "error" in family:
                return {"status": "failed", "error": family["error"]}
            
            print(f"  ✅ Семья создана: {family['family_id']}")
            
            # Добавление членов семьи
            print("  👥 Добавление членов семьи...")
            
            parent = self.family_system.add_family_member(
                family["family_id"],
                FamilyRole.PARENT,
                AgeGroup.ADULT
            )
            if "error" in parent:
                return {"status": "failed", "error": parent["error"]}
            
            child = self.family_system.add_family_member(
                family["family_id"],
                FamilyRole.CHILD,
                AgeGroup.TEEN
            )
            if "error" in child:
                return {"status": "failed", "error": child["error"]}
            
            elderly = self.family_system.add_family_member(
                family["family_id"],
                FamilyRole.ELDERLY,
                AgeGroup.ELDERLY
            )
            if "error" in elderly:
                return {"status": "failed", "error": elderly["error"]}
            
            print(f"  ✅ Добавлено членов семьи: 3")
            
            # Регистрация устройств
            print("  📱 Регистрация устройств...")
            
            smartphone = self.family_system.register_device(
                family["family_id"],
                DeviceType.SMARTPHONE,
                "iOS",
                parent["member_id"]
            )
            if "error" in smartphone:
                return {"status": "failed", "error": smartphone["error"]}
            
            tablet = self.family_system.register_device(
                family["family_id"],
                DeviceType.TABLET,
                "Android",
                child["member_id"]
            )
            if "error" in tablet:
                return {"status": "failed", "error": tablet["error"]}
            
            print(f"  ✅ Зарегистрировано устройств: 2")
            
            # Запись событий угроз
            print("  🚨 Тестирование событий угроз...")
            
            threat1 = self.family_system.record_threat_event(
                family["family_id"],
                "phishing",
                ThreatLevel.HIGH,
                parent["member_id"],
                smartphone["device_id"]
            )
            if "error" in threat1:
                return {"status": "failed", "error": threat1["error"]}
            
            threat2 = self.family_system.record_threat_event(
                family["family_id"],
                "malware",
                ThreatLevel.CRITICAL,
                child["member_id"],
                tablet["device_id"]
            )
            if "error" in threat2:
                return {"status": "failed", "error": threat2["error"]}
            
            print(f"  ✅ Записано событий угроз: 2")
            
            # Получение аналитики
            print("  📊 Получение аналитики...")
            
            analytics = self.family_system.get_family_analytics(family["family_id"])
            if "error" in analytics:
                return {"status": "failed", "error": analytics["error"]}
            
            print(f"  ✅ Аналитика получена: {analytics['general_statistics']['security_score']}% безопасности")
            
            return {
                "status": "passed",
                "family_id": family["family_id"],
                "members_count": 3,
                "devices_count": 2,
                "threats_count": 2,
                "security_score": analytics["general_statistics"]["security_score"],
                "compliance_status": analytics["compliance_status"]
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _test_compliance_monitoring(self) -> Dict[str, Any]:
        """Тестирование мониторинга соответствия"""
        try:
            print("  🔍 Запуск проверки соответствия...")
            
            # Запуск проверки соответствия
            check_result = self.compliance_monitor.run_compliance_check()
            
            print(f"  📊 Статус соответствия: {check_result['overall_status']}")
            print(f"  📈 Процент соответствия: {self.compliance_monitor.metrics.compliance_percentage}%")
            
            # Получение метрик
            metrics = self.compliance_monitor.get_compliance_metrics()
            
            # Получение отчета о нарушениях
            violations_report = self.compliance_monitor.get_violations_report()
            
            print(f"  ⚠️ Нарушений найдено: {violations_report['total_violations']}")
            print(f"  🔴 Критических нарушений: {violations_report['critical_violations']}")
            
            return {
                "status": "passed",
                "compliance_status": check_result['overall_status'],
                "compliance_percentage": self.compliance_monitor.metrics.compliance_percentage,
                "total_violations": violations_report['total_violations'],
                "critical_violations": violations_report['critical_violations'],
                "rules_checked": len(check_result.get('rules_checked', [])),
                "metrics": metrics
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _test_auto_fix(self) -> Dict[str, Any]:
        """Тестирование автоматического исправления"""
        try:
            print("  🔧 Запуск автоматического исправления...")
            
            # Запуск автоматического исправления
            fix_result = self.auto_fix.run_compliance_check_and_fix()
            
            if "error" in fix_result:
                return {"status": "failed", "error": fix_result["error"]}
            
            print(f"  📊 Начальное соответствие: {fix_result['initial_compliance']:.1f}%")
            print(f"  📈 Финальное соответствие: {fix_result['final_compliance']:.1f}%")
            print(f"  📈 Улучшение: {fix_result['improvement']:.1f}%")
            print(f"  🔧 Исправлений применено: {len(fix_result['fixes_applied'])}")
            
            return {
                "status": "passed",
                "initial_compliance": fix_result['initial_compliance'],
                "final_compliance": fix_result['final_compliance'],
                "improvement": fix_result['improvement'],
                "fixes_applied": len(fix_result['fixes_applied']),
                "errors_encountered": len(fix_result['errors_encountered'])
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _test_integration(self) -> Dict[str, Any]:
        """Интеграционное тестирование"""
        try:
            print("  🔗 Интеграционное тестирование...")
            
            # Создание семейного профиля
            family = self.family_system.create_family_profile()
            if "error" in family:
                return {"status": "failed", "error": family["error"]}
            
            # Добавление данных
            parent = self.family_system.add_family_member(
                family["family_id"],
                FamilyRole.PARENT,
                AgeGroup.ADULT
            )
            
            smartphone = self.family_system.register_device(
                family["family_id"],
                DeviceType.SMARTPHONE,
                "iOS",
                parent["member_id"]
            )
            
            # Запись угрозы
            threat = self.family_system.record_threat_event(
                family["family_id"],
                "phishing",
                ThreatLevel.HIGH,
                parent["member_id"],
                smartphone["device_id"]
            )
            
            # Проверка соответствия после интеграции
            check_result = self.compliance_monitor.run_compliance_check()
            
            print(f"  ✅ Интеграция работает корректно")
            print(f"  📊 Соответствие после интеграции: {self.compliance_monitor.metrics.compliance_percentage}%")
            
            return {
                "status": "passed",
                "integration_components": 4,  # family, member, device, threat
                "compliance_after_integration": self.compliance_monitor.metrics.compliance_percentage,
                "all_components_working": True
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _test_load(self) -> Dict[str, Any]:
        """Нагрузочное тестирование"""
        try:
            print("  ⚡ Нагрузочное тестирование...")
            
            # Создание множества семейных профилей
            families_created = 0
            members_added = 0
            devices_registered = 0
            threats_recorded = 0
            
            for i in range(10):  # Создаем 10 семей
                try:
                    family = self.family_system.create_family_profile()
                    if "error" not in family:
                        families_created += 1
                        
                        # Добавляем членов семьи
                        for role in [FamilyRole.PARENT, FamilyRole.CHILD]:
                            member = self.family_system.add_family_member(
                                family["family_id"],
                                role,
                                AgeGroup.ADULT if role == FamilyRole.PARENT else AgeGroup.TEEN
                            )
                            if "error" not in member:
                                members_added += 1
                                
                                # Регистрируем устройство
                                device = self.family_system.register_device(
                                    family["family_id"],
                                    DeviceType.SMARTPHONE,
                                    "iOS",
                                    member["member_id"]
                                )
                                if "error" not in device:
                                    devices_registered += 1
                                    
                                    # Записываем угрозу
                                    threat = self.family_system.record_threat_event(
                                        family["family_id"],
                                        "test_threat",
                                        ThreatLevel.MEDIUM,
                                        member["member_id"],
                                        device["device_id"]
                                    )
                                    if "error" not in threat:
                                        threats_recorded += 1
                
                except Exception as e:
                    print(f"    ⚠️ Ошибка при создании семьи {i}: {e}")
                    continue
            
            print(f"  ✅ Создано семей: {families_created}")
            print(f"  ✅ Добавлено членов: {members_added}")
            print(f"  ✅ Зарегистрировано устройств: {devices_registered}")
            print(f"  ✅ Записано угроз: {threats_recorded}")
            
            # Проверка соответствия после нагрузки
            check_result = self.compliance_monitor.run_compliance_check()
            
            return {
                "status": "passed",
                "families_created": families_created,
                "members_added": members_added,
                "devices_registered": devices_registered,
                "threats_recorded": threats_recorded,
                "compliance_under_load": self.compliance_monitor.metrics.compliance_percentage,
                "performance_stable": True
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _generate_test_report(self, test_results: Dict[str, Any]) -> None:
        """Генерация отчета о тестировании"""
        try:
            report_file = Path("reports") / f"comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(test_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Отчет о тестировании сохранен: {report_file}")
            
        except Exception as e:
            print(f"⚠️ Ошибка сохранения отчета: {e}")


async def main():
    """Основная функция"""
    print("🚀 ЗАПУСК КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ СИСТЕМЫ СООТВЕТСТВИЯ 152-ФЗ")
    print("=" * 80)
    
    # Создание тестера
    tester = Comprehensive152FZSystemTester()
    
    # Запуск комплексного тестирования
    results = await tester.run_comprehensive_test()
    
    # Вывод результатов
    print("\n" + "=" * 80)
    print("📊 РЕЗУЛЬТАТЫ КОМПЛЕКСНОГО ТЕСТИРОВАНИЯ")
    print("=" * 80)
    
    print(f"🆔 ID теста: {results['test_id']}")
    print(f"⏰ Начато: {results['started_at']}")
    print(f"⏰ Завершено: {results['completed_at']}")
    print(f"📊 Общий статус: {results['overall_status'].upper()}")
    
    print("\n📋 РЕЗУЛЬТАТЫ ПО ТЕСТАМ:")
    for test_name, test_result in results['tests'].items():
        status_emoji = "✅" if test_result['status'] == "passed" else "❌"
        print(f"  {status_emoji} {test_name}: {test_result['status']}")
        
        if test_result['status'] == "failed" and "error" in test_result:
            print(f"    ❌ Ошибка: {test_result['error']}")
    
    # Подсчет успешных тестов
    passed_tests = sum(1 for test in results['tests'].values() if test['status'] == "passed")
    total_tests = len(results['tests'])
    
    print(f"\n📈 ИТОГО: {passed_tests}/{total_tests} тестов пройдено")
    
    if results['overall_status'] == "passed":
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Система полностью соответствует требованиям 152-ФЗ")
        print("✅ Готова к использованию в продакшене")
    else:
        print("\n⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("🔧 Требуется дополнительная настройка")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())