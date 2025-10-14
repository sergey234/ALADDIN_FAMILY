#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание полной карты зависимостей для системы спящего режима
Включает анализ ML компонентов, критических функций и связей
"""

import json
import os
import ast
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DependencyMapCreator:
    """Создатель карты зависимостей системы"""
    
    def __init__(self):
        self.sfm_registry = self._load_sfm_registry()
        self.dependency_map = {
            "created_at": datetime.now().isoformat(),
            "critical_functions": [],
            "ml_components": [],
            "dependencies": {},
            "ml_model_dependencies": {},
            "risks": {},
            "sleep_mode_candidates": [],
            "active_required": []
        }
        
    def _load_sfm_registry(self) -> Dict:
        """Загрузка реестра SFM"""
        try:
            with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки реестра SFM: {e}")
            return {}
    
    def analyze_critical_functions(self) -> List[str]:
        """Анализ критических функций"""
        critical_functions = []
        
        for function_id, function_data in self.sfm_registry.get('functions', {}).items():
            if function_data.get('is_critical', False):
                critical_functions.append(function_id)
        
        self.dependency_map['critical_functions'] = critical_functions
        logger.info(f"Найдено критических функций: {len(critical_functions)}")
        
        return critical_functions
    
    def analyze_ml_components(self) -> List[Dict[str, Any]]:
        """Анализ ML компонентов"""
        ml_components = []
        
        # Поиск ML компонентов в коде
        ml_patterns = [
            'sklearn', 'tensorflow', 'pytorch', 'ml_model', 'MLModel',
            'IsolationForest', 'RandomForest', 'KMeans', 'DBSCAN', 'SVM',
            'machine_learning', 'neural_network', 'classifier', 'predictor'
        ]
        
        for function_id, function_data in self.sfm_registry.get('functions', {}).items():
            file_path = function_data.get('file_path', '')
            
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Проверка на наличие ML паттернов
                    ml_indicators = sum(1 for pattern in ml_patterns if pattern.lower() in content.lower())
                    
                    if ml_indicators > 0:
                        ml_component = {
                            "function_id": function_id,
                            "name": function_data.get('name', ''),
                            "file_path": file_path,
                            "ml_indicators": ml_indicators,
                            "ml_models": self._extract_ml_models(content),
                            "is_critical": function_data.get('is_critical', False),
                            "security_level": function_data.get('security_level', 'medium')
                        }
                        ml_components.append(ml_component)
                        
                except Exception as e:
                    logger.warning(f"Ошибка анализа файла {file_path}: {e}")
        
        self.dependency_map['ml_components'] = ml_components
        logger.info(f"Найдено ML компонентов: {len(ml_components)}")
        
        return ml_components
    
    def _extract_ml_models(self, content: str) -> List[str]:
        """Извлечение типов ML моделей из кода"""
        ml_models = []
        
        # Паттерны для поиска ML моделей
        model_patterns = [
            'IsolationForest', 'RandomForest', 'KMeans', 'DBSCAN', 'SVM', 'SVC',
            'MLPClassifier', 'MLPRegressor', 'GaussianNB', 'MultinomialNB',
            'LinearRegression', 'LogisticRegression', 'Ridge', 'Lasso', 'ElasticNet',
            'DecisionTreeClassifier', 'AdaBoostClassifier', 'BaggingClassifier',
            'GradientBoostingClassifier', 'VotingClassifier', 'OneClassSVM',
            'LocalOutlierFactor', 'KNeighborsClassifier', 'GaussianMixture'
        ]
        
        for pattern in model_patterns:
            if pattern in content:
                ml_models.append(pattern)
        
        return list(set(ml_models))  # Удаление дубликатов
    
    def analyze_dependencies(self) -> Dict[str, List[str]]:
        """Анализ зависимостей между функциями"""
        dependencies = {}
        
        for function_id, function_data in self.sfm_registry.get('functions', {}).items():
            function_deps = function_data.get('dependencies', [])
            if function_deps:
                dependencies[function_id] = function_deps
        
        self.dependency_map['dependencies'] = dependencies
        logger.info(f"Найдено зависимостей: {len(dependencies)}")
        
        return dependencies
    
    def analyze_ml_model_dependencies(self) -> Dict[str, List[str]]:
        """Анализ зависимостей ML моделей"""
        ml_model_deps = {}
        
        for ml_component in self.dependency_map['ml_components']:
            ml_models = ml_component.get('ml_models', [])
            function_id = ml_component['function_id']
            
            for model in ml_models:
                if model not in ml_model_deps:
                    ml_model_deps[model] = []
                ml_model_deps[model].append(function_id)
        
        self.dependency_map['ml_model_dependencies'] = ml_model_deps
        logger.info(f"Найдено ML моделей: {len(ml_model_deps)}")
        
        return ml_model_deps
    
    def identify_risks(self) -> Dict[str, Any]:
        """Идентификация рисков"""
        risks = {
            "high_risk_components": [],
            "critical_dependencies": [],
            "ml_model_risks": [],
            "sleep_mode_risks": []
        }
        
        # Высокорисковые компоненты
        for ml_component in self.dependency_map['ml_components']:
            if ml_component.get('is_critical', False):
                risks["high_risk_components"].append({
                    "function_id": ml_component['function_id'],
                    "name": ml_component['name'],
                    "risk_level": "HIGH",
                    "reason": "Critical ML component"
                })
        
        # Критические зависимости
        for function_id, deps in self.dependency_map['dependencies'].items():
            if len(deps) > 5:  # Много зависимостей
                risks["critical_dependencies"].append({
                    "function_id": function_id,
                    "dependencies_count": len(deps),
                    "risk_level": "HIGH",
                    "reason": "High dependency count"
                })
        
        # Риски ML моделей
        for model, components in self.dependency_map['ml_model_dependencies'].items():
            if len(components) > 3:  # Модель используется многими компонентами
                risks["ml_model_risks"].append({
                    "model": model,
                    "components_count": len(components),
                    "components": components,
                    "risk_level": "HIGH",
                    "reason": "Model used by multiple components"
                })
        
        self.dependency_map['risks'] = risks
        logger.info(f"Выявлено рисков: {sum(len(v) for v in risks.values())}")
        
        return risks
    
    def identify_sleep_mode_candidates(self) -> List[Dict[str, Any]]:
        """Идентификация кандидатов для спящего режима"""
        candidates = []
        
        for function_id, function_data in self.sfm_registry.get('functions', {}).items():
            # Исключаем критические функции
            if function_data.get('is_critical', False):
                continue
            
            # Исключаем ML компоненты
            is_ml_component = any(
                ml['function_id'] == function_id 
                for ml in self.dependency_map['ml_components']
            )
            if is_ml_component:
                continue
            
            # Кандидат для спящего режима
            candidate = {
                "function_id": function_id,
                "name": function_data.get('name', ''),
                "security_level": function_data.get('security_level', 'medium'),
                "dependencies_count": len(function_data.get('dependencies', [])),
                "priority": self._calculate_sleep_priority(function_data)
            }
            candidates.append(candidate)
        
        # Сортировка по приоритету
        candidates.sort(key=lambda x: x['priority'])
        
        self.dependency_map['sleep_mode_candidates'] = candidates
        logger.info(f"Кандидатов для спящего режима: {len(candidates)}")
        
        return candidates
    
    def _calculate_sleep_priority(self, function_data: Dict) -> int:
        """Расчет приоритета для перевода в спящий режим"""
        priority = 0
        
        # Базовый приоритет
        priority += 100
        
        # Уменьшение приоритета для важных функций
        security_level = function_data.get('security_level', 'medium')
        if security_level == 'high':
            priority -= 30
        elif security_level == 'critical':
            priority -= 50
        
        # Уменьшение приоритета для функций с зависимостями
        deps_count = len(function_data.get('dependencies', []))
        priority -= deps_count * 5
        
        return priority
    
    def identify_active_required(self) -> List[Dict[str, Any]]:
        """Идентификация функций, которые должны остаться активными"""
        active_required = []
        
        # Критические функции
        for function_id in self.dependency_map['critical_functions']:
            function_data = self.sfm_registry['functions'].get(function_id, {})
            active_required.append({
                "function_id": function_id,
                "name": function_data.get('name', ''),
                "reason": "Critical function",
                "priority": "HIGH"
            })
        
        # ML компоненты
        for ml_component in self.dependency_map['ml_components']:
            active_required.append({
                "function_id": ml_component['function_id'],
                "name": ml_component['name'],
                "reason": "ML component with models",
                "priority": "HIGH",
                "ml_models": ml_component['ml_models']
            })
        
        # Функции с высоким риском
        for risk in self.dependency_map['risks']['high_risk_components']:
            active_required.append({
                "function_id": risk['function_id'],
                "name": risk.get('name', ''),
                "reason": "High risk component",
                "priority": "HIGH"
            })
        
        self.dependency_map['active_required'] = active_required
        logger.info(f"Функций для активного режима: {len(active_required)}")
        
        return active_required
    
    def generate_statistics(self) -> Dict[str, Any]:
        """Генерация статистики"""
        stats = {
            "total_functions": len(self.sfm_registry.get('functions', {})),
            "critical_functions": len(self.dependency_map['critical_functions']),
            "ml_components": len(self.dependency_map['ml_components']),
            "sleep_candidates": len(self.dependency_map['sleep_mode_candidates']),
            "active_required": len(self.dependency_map['active_required']),
            "ml_models_count": len(self.dependency_map['ml_model_dependencies']),
            "dependencies_count": len(self.dependency_map['dependencies']),
            "risks_count": sum(len(v) for v in self.dependency_map['risks'].values())
        }
        
        self.dependency_map['statistics'] = stats
        return stats
    
    def save_dependency_map(self) -> str:
        """Сохранение карты зависимостей"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"DEPENDENCY_MAP_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.dependency_map, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Карта зависимостей сохранена: {filename}")
        return filename
    
    def create_summary_report(self) -> str:
        """Создание сводного отчета"""
        report = f"""
# 🗺️ КАРТА ЗАВИСИМОСТЕЙ СИСТЕМЫ БЕЗОПАСНОСТИ ALADDIN

**Дата создания:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 СТАТИСТИКА

- **Всего функций:** {self.dependency_map['statistics']['total_functions']}
- **Критических функций:** {self.dependency_map['statistics']['critical_functions']}
- **ML компонентов:** {self.dependency_map['statistics']['ml_components']}
- **Кандидатов для спящего режима:** {self.dependency_map['statistics']['sleep_candidates']}
- **Обязательно активных:** {self.dependency_map['statistics']['active_required']}
- **ML моделей:** {self.dependency_map['statistics']['ml_models_count']}
- **Зависимостей:** {self.dependency_map['statistics']['dependencies_count']}
- **Рисков:** {self.dependency_map['statistics']['risks_count']}

## 🔒 КРИТИЧЕСКИЕ ФУНКЦИИ

{chr(10).join(f"- {func}" for func in self.dependency_map['critical_functions'][:10])}
{'...' if len(self.dependency_map['critical_functions']) > 10 else ''}

## 🤖 ML КОМПОНЕНТЫ

{chr(10).join(f"- {comp['name']} ({comp['function_id']}) - {', '.join(comp['ml_models'])}" for comp in self.dependency_map['ml_components'][:10])}
{'...' if len(self.dependency_map['ml_components']) > 10 else ''}

## ⚠️ ВЫСОКИЕ РИСКИ

{chr(10).join(f"- {risk['function_id']}: {risk['reason']}" for risk in self.dependency_map['risks']['high_risk_components'][:5])}
{'...' if len(self.dependency_map['risks']['high_risk_components']) > 5 else ''}

## 🎯 РЕКОМЕНДАЦИИ

1. **Оставить активными:** {self.dependency_map['statistics']['active_required']} функций
2. **Перевести в спящий режим:** {self.dependency_map['statistics']['sleep_candidates']} функций
3. **Особое внимание:** ML компоненты требуют сохранения весов моделей
4. **Мониторинг:** Настроить мониторинг для всех активных функций

## 📁 ФАЙЛЫ

- **Карта зависимостей:** DEPENDENCY_MAP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json
- **Отчет:** DEPENDENCY_MAP_REPORT.md
"""
        
        report_filename = "DEPENDENCY_MAP_REPORT.md"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Сводный отчет создан: {report_filename}")
        return report_filename
    
    def run_analysis(self) -> Dict[str, Any]:
        """Запуск полного анализа"""
        print("🗺️ СОЗДАНИЕ КАРТЫ ЗАВИСИМОСТЕЙ СИСТЕМЫ БЕЗОПАСНОСТИ")
        print("=" * 60)
        
        # Анализ критических функций
        print("🔒 Анализ критических функций...")
        self.analyze_critical_functions()
        
        # Анализ ML компонентов
        print("🤖 Анализ ML компонентов...")
        self.analyze_ml_components()
        
        # Анализ зависимостей
        print("🔗 Анализ зависимостей...")
        self.analyze_dependencies()
        
        # Анализ зависимостей ML моделей
        print("🧠 Анализ зависимостей ML моделей...")
        self.analyze_ml_model_dependencies()
        
        # Идентификация рисков
        print("⚠️ Идентификация рисков...")
        self.identify_risks()
        
        # Идентификация кандидатов для спящего режима
        print("😴 Идентификация кандидатов для спящего режима...")
        self.identify_sleep_mode_candidates()
        
        # Идентификация обязательно активных функций
        print("⚡ Идентификация обязательно активных функций...")
        self.identify_active_required()
        
        # Генерация статистики
        print("📊 Генерация статистики...")
        self.generate_statistics()
        
        # Сохранение карты зависимостей
        print("💾 Сохранение карты зависимостей...")
        map_file = self.save_dependency_map()
        
        # Создание сводного отчета
        print("📋 Создание сводного отчета...")
        report_file = self.create_summary_report()
        
        print(f"\n✅ АНАЛИЗ ЗАВЕРШЕН!")
        print(f"📁 Карта зависимостей: {map_file}")
        print(f"📋 Отчет: {report_file}")
        
        return self.dependency_map

def main():
    """Главная функция"""
    creator = DependencyMapCreator()
    dependency_map = creator.run_analysis()
    
    print(f"\n🎯 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"   Всего функций: {dependency_map['statistics']['total_functions']}")
    print(f"   Критических: {dependency_map['statistics']['critical_functions']}")
    print(f"   ML компонентов: {dependency_map['statistics']['ml_components']}")
    print(f"   Кандидатов для сна: {dependency_map['statistics']['sleep_candidates']}")
    print(f"   Обязательно активных: {dependency_map['statistics']['active_required']}")
    
    return 0

if __name__ == "__main__":
    exit(main())