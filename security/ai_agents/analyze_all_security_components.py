#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МАССОВЫЙ АНАЛИЗ ВСЕХ КОМПОНЕНТОВ СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN
Находит и анализирует ВСЕ файлы системы безопасности:
- Менеджеры (8 классов)
- Агенты (8 классов)
- Боты (8 классов)
- SFM (Safe Function Manager)
- Архитектура безопасности
- Конфигурация безопасности
"""

import json
import os
from typing import List, Dict, Any
import sys
from datetime import datetime

# Добавляем текущую директорию в sys.path для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from security_quality_analyzer import security_quality_analyzer
except ImportError:
    print("⚠️ Модуль security_quality_analyzer не найден")
    security_quality_analyzer = None


class SecurityComponentAnalyzer:
    """Анализатор всех компонентов системы безопасности"""

    def __init__(self, base_path: str = None):
        """Инициализация анализатора компонентов"""
        self.base_path = base_path or os.path.dirname(os.path.abspath(__file__))
        self.security_components = []
        self.analysis_results = {}
        self.start_time = None

    def find_all_components(self) -> List[str]:
        """Поиск всех компонентов системы безопасности"""
        components = []

        # Поиск в директориях безопасности
        security_dirs = ['security', 'managers', 'agents', 'bots']

        for dir_name in security_dirs:
            dir_path = os.path.join(self.base_path, dir_name)
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        if file.endswith('.py') and not file.startswith('__'):
                            file_path = os.path.join(root, file)
                            components.append(file_path)

        self.security_components = components
        return components

    def analyze_components(self) -> Dict[str, Any]:
        """Анализ всех найденных компонентов"""
        self.start_time = datetime.now()

        if not self.security_components:
            self.find_all_components()

        results = {
            'total_components': len(self.security_components),
            'analyzed_components': 0,
            'analysis_time': 0,
            'components_data': {}
        }

        for component in self.security_components:
            try:
                component_data = self._analyze_single_component(component)
                results['components_data'][component] = component_data
                results['analyzed_components'] += 1
            except Exception as e:
                results['components_data'][component] = {'error': str(e)}

        results['analysis_time'] = (datetime.now() - self.start_time).total_seconds()
        return results

    def _analyze_single_component(self, component_path: str) -> Dict[str, Any]:
        """Анализ отдельного компонента"""
        try:
            with open(component_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Базовый анализ
            lines = content.split('\n')
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])

            # Проверка на классы
            has_classes = 'class ' in content
            has_init = 'def __init__' in content

            return {
                'total_lines': total_lines,
                'code_lines': code_lines,
                'has_classes': has_classes,
                'has_init': has_init,
                'file_size': os.path.getsize(component_path)
            }

        except Exception as e:
            return {'error': str(e)}


def find_security_components():
    """Находит все компоненты системы безопасности."""
    security_components = []

    # Директории системы безопасности
    security_dirs = [
        "security/",
        "security/ai_agents/",
        "security/bots/",
        "security/managers/",
        "security/agents/",
        "security/config/",
        "security/architecture/",
    ]

    for security_dir in security_dirs:
        if os.path.exists(security_dir):
            for root, dirs, files in os.walk(security_dir):
                for file in files:
                    if file.endswith(".py") and not any(
                        exclude in file.lower()
                        for exclude in [
                            "backup",
                            "script",
                            "test",
                            "temp",
                            "old",
                        ]
                    ):
                        file_path = os.path.join(root, file)
                        security_components.append(file_path)

    return security_components


def analyze_all_security_components():
    """Анализирует все компоненты системы безопасности."""
    print("🛡️ МАССОВЫЙ АНАЛИЗ ВСЕХ КОМПОНЕНТОВ СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN")
    print("=" * 80)

    # Находим все компоненты
    components = find_security_components()

    if not components:
        print("❌ Компоненты системы безопасности не найдены!")
        return

    print(f"🔍 Найдено {len(components)} компонентов системы безопасности:")
    for i, component in enumerate(components, 1):
        print(f"   {i}. {component}")
    print()

    # Анализируем каждый компонент
    results = []
    total_score = 0
    successful_analyses = 0

    for i, component in enumerate(components, 1):
        print(f"📊 Анализ {i}/{len(components)}: {component}")
        try:
            result = security_quality_analyzer(component)
            if "error" not in result:
                results.append(result)
                total_score += result.get("overall_quality_score", 0)
                successful_analyses += 1
                print(f"   ✅ Балл: {result.get('overall_quality_score', 0)}")
            else:
                print(f"   ❌ Ошибка: {result['error']}")
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
        print()

    # Сводный отчет
    if successful_analyses > 0:
        average_score = total_score / successful_analyses

        print("📊 СВОДНЫЙ ОТЧЕТ ПО СИСТЕМЕ БЕЗОПАСНОСТИ:")
        print("=" * 50)
        print(f"📁 Всего компонентов: {len(components)}")
        print(f"✅ Успешно проанализировано: {successful_analyses}")
        print(f"❌ Ошибок анализа: {len(components) - successful_analyses}")
        print(f"📊 Средний балл качества: {average_score:.1f}/100")
        print()

        # Топ-5 лучших компонентов
        if results:
            sorted_results = sorted(
                results,
                key=lambda x: x.get("overall_quality_score", 0),
                reverse=True,
            )
            print("🏆 ТОП-5 ЛУЧШИХ КОМПОНЕНТОВ:")
            for i, result in enumerate(sorted_results[:5], 1):
                score = result.get("overall_quality_score", 0)
                file_name = os.path.basename(result.get("file", ""))
                print(f"   {i}. {file_name}: {score}/100")
            print()

        # Компоненты с проблемами
        problem_components = [
            r for r in results if r.get("overall_quality_score", 0) < 80
        ]
        if problem_components:
            print("⚠️ КОМПОНЕНТЫ С ПРОБЛЕМАМИ (балл < 80):")
            for result in problem_components:
                score = result.get("overall_quality_score", 0)
                file_name = os.path.basename(result.get("file", ""))
                print(f"   - {file_name}: {score}/100")
            print()

        # Статистика по типам компонентов
        managers = [
            r for r in results if "manager" in r.get("file", "").lower()
        ]
        agents = [r for r in results if "agent" in r.get("file", "").lower()]
        bots = [r for r in results if "bot" in r.get("file", "").lower()]

        # Статистика SFM
        sfm_registered = [
            r
            for r in results
            if r.get("summary", {}).get("is_sfm_registered", False)
        ]
        sfm_total = (
            results[0].get("summary", {}).get("sfm_total_functions", 0)
            if results
            else 0
        )
        sfm_active = (
            results[0].get("summary", {}).get("sfm_active_functions", 0)
            if results
            else 0
        )
        sfm_critical = (
            results[0].get("summary", {}).get("sfm_critical_functions", 0)
            if results
            else 0
        )

        print("📈 СТАТИСТИКА ПО ТИПАМ КОМПОНЕНТОВ:")
        if managers:
            manager_avg = sum(
                r.get("overall_quality_score", 0) for r in managers
            ) / len(managers)
            print(f"   🏢 Менеджеры ({len(managers)}): {manager_avg:.1f}/100")
        if agents:
            agent_avg = sum(
                r.get("overall_quality_score", 0) for r in agents
            ) / len(agents)
            print(f"   🤖 Агенты ({len(agents)}): {agent_avg:.1f}/100")
        if bots:
            bot_avg = sum(
                r.get("overall_quality_score", 0) for r in bots
            ) / len(bots)
            print(f"   🛡️ Боты ({len(bots)}): {bot_avg:.1f}/100")

        print("\n🔧 СТАТИСТИКА SFM:")
        print(f"   📊 Всего функций в SFM: {sfm_total}")
        print(f"   ✅ Активных функций: {sfm_active}")
        print(f"   🔴 Критических функций: {sfm_critical}")
        print(f"   📝 Зарегистрированных в анализе: {len(sfm_registered)}")
        print()

        # Сохранение сводного отчета
        summary_report = {
            "timestamp": datetime.now().isoformat(),
            "total_components": len(components),
            "successful_analyses": successful_analyses,
            "failed_analyses": len(components) - successful_analyses,
            "average_score": round(average_score, 1),
            "components": results,
            "top_components": sorted_results[:5] if results else [],
            "problem_components": problem_components,
            "statistics": {
                "managers": len(managers),
                "agents": len(agents),
                "bots": len(bots),
            },
        }

        report_filename = (
            f"security_system_summary_report_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_path = os.path.join("formatting_work", report_filename)
        os.makedirs("formatting_work", exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(summary_report, f, indent=2, ensure_ascii=False)
        print(f"📄 Сводный отчет сохранен: {report_path}")

        print("🎯 АНАЛИЗ ЗАВЕРШЕН УСПЕШНО!")
        print(
            f"📊 Общее качество системы безопасности: {average_score:.1f}/100"
        )

        if average_score >= 90:
            print("🏆 ОТЛИЧНО! Система безопасности в превосходном состоянии!")
        elif average_score >= 80:
            print("✅ ХОРОШО! Система безопасности в хорошем состоянии!")
        elif average_score >= 70:
            print("⚠️ УДОВЛЕТВОРИТЕЛЬНО! Есть проблемы, требующие внимания!")
        else:
            print(
                "❌ КРИТИЧНО! Система безопасности требует "
                "срочного исправления!"
            )
    else:
        print("❌ Не удалось проанализировать ни одного компонента!")


if __name__ == "__main__":
    analyze_all_security_components()
