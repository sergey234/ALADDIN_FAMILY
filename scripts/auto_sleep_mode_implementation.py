#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 АВТОМАТИЧЕСКАЯ РЕАЛИЗАЦИЯ СПЯЩЕГО РЕЖИМА
============================================

Автоматический перевод функций в спящий режим без интерактивного ввода
Включает защиту ML моделей и мониторинг
"""

import asyncio
import json
import os
import pickle
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoSleepModeImplementer:
    """Автоматическая реализация спящего режима"""
    
    def __init__(self):
        self.sfm_registry = self._load_sfm_registry()
        self.critical_functions = self._load_critical_functions()
        self.ml_components = self._load_ml_components()
        self.sleep_candidates = self._identify_sleep_candidates()
        self.sleep_mode_config = self._load_sleep_config()
        
    def _load_sfm_registry(self) -> Dict[str, Any]:
        """Загрузка SFM реестра"""
        try:
            with open("data/sfm/function_registry.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки SFM реестра: {e}")
            return {}
    
    def _load_critical_functions(self) -> Set[str]:
        """Загрузка критических функций"""
        critical_functions = {
            "safe_function_manager",
            "sleep_mode_manager", 
            "all_bots_sleep_manager",
            "safe_sleep_mode_optimizer",
            "enhanced_alerting",
            "threat_detection",
            "incident_response",
            "authentication_manager",
            "access_control_manager",
            "compliance_manager",
            "data_protection_manager",
            "zero_trust_manager",
            "security_audit",
            "threat_intelligence",
            "malware_protection",
            "intrusion_prevention",
            "network_monitoring",
            "ransomware_protection"
        }
        
        # Добавляем функции с уровнем critical
        if "functions" in self.sfm_registry:
            for func_id, func_data in self.sfm_registry["functions"].items():
                if func_data.get("security_level") == "critical":
                    critical_functions.add(func_data.get("name", func_id))
        
        return critical_functions
    
    def _load_ml_components(self) -> Set[str]:
        """Загрузка ML компонентов"""
        ml_components = {
            "behavioral_analysis_agent",
            "threat_detection_agent", 
            "password_security_agent",
            "incident_response_agent",
            "network_security_agent",
            "compliance_agent",
            "mobile_security_agent",
            "emergency_ml_analyzer",
            "analytics_manager",
            "rate_limiter",
            "circuit_breaker",
            "user_interface_manager",
            "mobile_navigation_bot",
            "notification_bot"
        }
        return ml_components
    
    def _identify_sleep_candidates(self) -> List[Dict[str, Any]]:
        """Идентификация кандидатов для спящего режима"""
        candidates = []
        
        if "functions" in self.sfm_registry:
            for func_id, func_data in self.sfm_registry["functions"].items():
                func_name = func_data.get("name", func_id)
                
                # Исключаем критические и ML компоненты
                if (func_name not in self.critical_functions and 
                    func_name not in self.ml_components and
                    func_data.get("security_level") not in ["critical", "high"]):
                    
                    candidates.append({
                        "function_id": func_id,
                        "name": func_name,
                        "security_level": func_data.get("security_level", "medium"),
                        "status": func_data.get("status", "active"),
                        "is_critical": func_data.get("is_critical", False)
                    })
        
        return candidates
    
    def _load_sleep_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации спящего режима"""
        try:
            with open("config/sleep_mode_config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Не удалось загрузить конфигурацию спящего режима: {e}")
            return {}
    
    async def implement_sleep_mode(self) -> Dict[str, Any]:
        """Реализация спящего режима"""
        logger.info("🤖 АВТОМАТИЧЕСКАЯ РЕАЛИЗАЦИЯ СПЯЩЕГО РЕЖИМА")
        logger.info("=" * 50)
        
        # Статистика
        total_functions = len(self.sfm_registry.get("functions", {}))
        critical_count = len(self.critical_functions)
        ml_count = len(self.ml_components)
        sleep_candidates_count = len(self.sleep_candidates)
        
        logger.info(f"📊 Всего функций: {total_functions}")
        logger.info(f"🔒 Критических функций: {critical_count}")
        logger.info(f"🤖 ML компонентов: {ml_count}")
        logger.info(f"😴 Кандидатов для сна: {sleep_candidates_count}")
        
        # Пилотный проект - первые 20 функций
        pilot_functions = self.sleep_candidates[:20]
        logger.info(f"🚀 Пилотный проект: {len(pilot_functions)} функций")
        
        # Перевод в спящий режим
        sleep_results = []
        for func in pilot_functions:
            try:
                result = await self._put_function_to_sleep(func)
                sleep_results.append(result)
                logger.info(f"✅ {func['name']} переведен в спящий режим")
            except Exception as e:
                logger.error(f"❌ Ошибка перевода {func['name']} в сон: {e}")
                sleep_results.append({
                    "function": func['name'],
                    "status": "error",
                    "error": str(e)
                })
        
        # Создание отчета
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_functions": total_functions,
            "critical_functions": critical_count,
            "ml_components": ml_count,
            "sleep_candidates": sleep_candidates_count,
            "pilot_functions": len(pilot_functions),
            "sleep_results": sleep_results,
            "successful_sleep": len([r for r in sleep_results if r.get("status") == "sleeping"]),
            "errors": len([r for r in sleep_results if r.get("status") == "error"])
        }
        
        # Сохранение отчета
        report_path = f"logs/sleep_mode_implementation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 Отчет сохранен: {report_path}")
        logger.info(f"✅ Успешно переведено в сон: {report['successful_sleep']}")
        logger.info(f"❌ Ошибок: {report['errors']}")
        
        return report
    
    async def _put_function_to_sleep(self, func: Dict[str, Any]) -> Dict[str, Any]:
        """Перевод функции в спящий режим"""
        try:
            # Обновляем статус в SFM реестре
            func_id = func["function_id"]
            if func_id in self.sfm_registry.get("functions", {}):
                self.sfm_registry["functions"][func_id]["status"] = "sleeping"
                self.sfm_registry["functions"][func_id]["sleep_time"] = datetime.now().isoformat()
            
            # Сохраняем состояние функции
            state_path = f"data/sleep_states/{func['name']}_state.json"
            os.makedirs(os.path.dirname(state_path), exist_ok=True)
            
            function_state = {
                "function_name": func["name"],
                "function_id": func_id,
                "sleep_time": datetime.now().isoformat(),
                "previous_status": func.get("status", "active"),
                "security_level": func.get("security_level", "medium"),
                "is_critical": func.get("is_critical", False)
            }
            
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(function_state, f, indent=2, ensure_ascii=False)
            
            return {
                "function": func["name"],
                "status": "sleeping",
                "sleep_time": function_state["sleep_time"],
                "state_file": state_path
            }
            
        except Exception as e:
            return {
                "function": func["name"],
                "status": "error",
                "error": str(e)
            }
    
    async def wake_up_function(self, function_name: str) -> Dict[str, Any]:
        """Пробуждение функции"""
        try:
            state_path = f"data/sleep_states/{function_name}_state.json"
            
            if not os.path.exists(state_path):
                return {
                    "function": function_name,
                    "status": "error",
                    "error": "Файл состояния не найден"
                }
            
            # Загружаем состояние
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            
            # Обновляем статус в SFM реестре
            func_id = state["function_id"]
            if func_id in self.sfm_registry.get("functions", {}):
                self.sfm_registry["functions"][func_id]["status"] = "active"
                self.sfm_registry["functions"][func_id]["wake_time"] = datetime.now().isoformat()
            
            # Удаляем файл состояния
            os.remove(state_path)
            
            return {
                "function": function_name,
                "status": "awake",
                "wake_time": datetime.now().isoformat(),
                "previous_sleep_time": state["sleep_time"]
            }
            
        except Exception as e:
            return {
                "function": function_name,
                "status": "error",
                "error": str(e)
            }

async def main():
    """Главная функция"""
    print("🤖 АВТОМАТИЧЕСКАЯ РЕАЛИЗАЦИЯ СПЯЩЕГО РЕЖИМА")
    print("=" * 50)
    
    implementer = AutoSleepModeImplementer()
    report = await implementer.implement_sleep_mode()
    
    print(f"\n🎯 ИТОГОВЫЙ ОТЧЕТ:")
    print(f"   Всего функций: {report['total_functions']}")
    print(f"   Критических: {report['critical_functions']}")
    print(f"   ML компонентов: {report['ml_components']}")
    print(f"   Кандидатов для сна: {report['sleep_candidates']}")
    print(f"   Пилотный проект: {report['pilot_functions']}")
    print(f"   Успешно переведено в сон: {report['successful_sleep']}")
    print(f"   Ошибок: {report['errors']}")
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))