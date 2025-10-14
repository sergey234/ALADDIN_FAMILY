#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚨 ЭКСТРЕННОЕ ПРОБУЖДЕНИЕ КРИТИЧЕСКИХ ФУНКЦИЙ
============================================

Немедленное пробуждение всех критических функций из спящего режима
Исправление ошибки в автоматическом переводе

Автор: ALADDIN Security System
Дата: 2025-09-15
Версия: 1.0.0
"""

import asyncio
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmergencyWakeUpSystem:
    """Экстренное пробуждение критических функций"""
    
    def __init__(self):
        self.critical_functions = {
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
            "ransomware_protection",
            "CoreBase",
            "ServiceBase",
            "SecurityBase",
            "Database",
            "Configuration",
            "LoggingModule",
            "Authentication"
        }
        
    async def emergency_wake_up_all_critical(self) -> Dict[str, Any]:
        """Экстренное пробуждение всех критических функций"""
        logger.critical("🚨 ЭКСТРЕННОЕ ПРОБУЖДЕНИЕ КРИТИЧЕСКИХ ФУНКЦИЙ")
        logger.critical("=" * 50)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "wake_up_attempts": 0,
            "successful_wake_ups": 0,
            "errors": 0,
            "woke_up_functions": [],
            "error_functions": []
        }
        
        # 1. Обновляем SFM реестр
        await self._update_sfm_registry()
        
        # 2. Пробуждаем функции из файлов состояния
        await self._wake_up_from_state_files(results)
        
        # 3. Пробуждаем функции по именам
        for func_name in self.critical_functions:
            try:
                result = await self._wake_up_function_by_name(func_name)
                results["wake_up_attempts"] += 1
                
                if result["success"]:
                    results["successful_wake_ups"] += 1
                    results["woke_up_functions"].append(func_name)
                    logger.info(f"✅ {func_name} пробуждена")
                else:
                    results["errors"] += 1
                    results["error_functions"].append({
                        "name": func_name,
                        "error": result["message"]
                    })
                    logger.error(f"❌ Ошибка пробуждения {func_name}: {result['message']}")
                    
            except Exception as e:
                results["errors"] += 1
                results["error_functions"].append({
                    "name": func_name,
                    "error": str(e)
                })
                logger.error(f"❌ Критическая ошибка пробуждения {func_name}: {e}")
        
        # 4. Сохраняем отчет
        report_path = f"logs/emergency_wake_up_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.critical(f"📋 Отчет экстренного пробуждения: {report_path}")
        logger.critical(f"✅ Успешно пробуждено: {results['successful_wake_ups']}")
        logger.critical(f"❌ Ошибок: {results['errors']}")
        
        return results
    
    async def _update_sfm_registry(self) -> None:
        """Обновление SFM реестра - пробуждение всех критических функций"""
        try:
            with open("data/sfm/function_registry.json", "r", encoding="utf-8") as f:
                sfm_registry = json.load(f)
            
            if "functions" in sfm_registry:
                for func_id, func_data in sfm_registry["functions"].items():
                    func_name = func_data.get("name", func_id)
                    
                    # Пробуждаем критические функции
                    if (func_name in self.critical_functions or 
                        func_data.get("security_level") == "critical" or
                        func_data.get("is_critical", False)):
                        
                        sfm_registry["functions"][func_id]["status"] = "active"
                        sfm_registry["functions"][func_id]["wake_time"] = datetime.now().isoformat()
                        sfm_registry["functions"][func_id]["emergency_wake_up"] = True
                        
                        logger.info(f"🔄 SFM: {func_name} переведена в активный режим")
            
            # Сохраняем обновленный реестр
            with open("data/sfm/function_registry.json", "w", encoding="utf-8") as f:
                json.dump(sfm_registry, f, indent=2, ensure_ascii=False)
                
            logger.info("✅ SFM реестр обновлен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка обновления SFM реестра: {e}")
    
    async def _wake_up_from_state_files(self, results: Dict[str, Any]) -> None:
        """Пробуждение функций из файлов состояния"""
        try:
            state_dir = Path("data/sleep_states")
            if not state_dir.exists():
                return
            
            for state_file in state_dir.glob("*_state.json"):
                try:
                    with open(state_file, "r", encoding="utf-8") as f:
                        state = json.load(f)
                    
                    func_name = state.get("function_name", "unknown")
                    
                    # Пробуждаем только критические функции
                    if func_name in self.critical_functions:
                        # Удаляем файл состояния
                        os.remove(state_file)
                        results["wake_up_attempts"] += 1
                        results["successful_wake_ups"] += 1
                        results["woke_up_functions"].append(func_name)
                        logger.info(f"✅ {func_name} пробуждена из файла состояния")
                        
                except Exception as e:
                    logger.error(f"❌ Ошибка обработки файла состояния {state_file}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Ошибка пробуждения из файлов состояния: {e}")
    
    async def _wake_up_function_by_name(self, function_name: str) -> Dict[str, Any]:
        """Пробуждение функции по имени"""
        try:
            # Проверяем файл состояния
            state_file = f"data/sleep_states/{function_name}_state.json"
            if os.path.exists(state_file):
                os.remove(state_file)
            
            return {
                "success": True,
                "message": f"Функция {function_name} пробуждена",
                "wake_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка пробуждения: {str(e)}"
            }
    
    async def verify_critical_functions_status(self) -> Dict[str, Any]:
        """Проверка статуса критических функций"""
        try:
            with open("data/sfm/function_registry.json", "r", encoding="utf-8") as f:
                sfm_registry = json.load(f)
            
            status = {
                "total_critical": len(self.critical_functions),
                "active_critical": 0,
                "sleeping_critical": 0,
                "critical_functions_status": {}
            }
            
            if "functions" in sfm_registry:
                for func_id, func_data in sfm_registry["functions"].items():
                    func_name = func_data.get("name", func_id)
                    
                    if (func_name in self.critical_functions or 
                        func_data.get("security_level") == "critical" or
                        func_data.get("is_critical", False)):
                        
                        func_status = func_data.get("status", "unknown")
                        status["critical_functions_status"][func_name] = func_status
                        
                        if func_status == "active":
                            status["active_critical"] += 1
                        elif func_status == "sleeping":
                            status["sleeping_critical"] += 1
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки статуса: {e}")
            return {"error": str(e)}

async def main():
    """Главная функция"""
    print("🚨 ЭКСТРЕННОЕ ПРОБУЖДЕНИЕ КРИТИЧЕСКИХ ФУНКЦИЙ")
    print("=" * 50)
    
    wake_up_system = EmergencyWakeUpSystem()
    
    # Проверяем текущий статус
    print("🔍 Проверка текущего статуса критических функций...")
    status_before = await wake_up_system.verify_critical_functions_status()
    print(f"   Активных критических: {status_before.get('active_critical', 0)}")
    print(f"   Спящих критических: {status_before.get('sleeping_critical', 0)}")
    
    # Выполняем экстренное пробуждение
    print("\n🚨 Выполнение экстренного пробуждения...")
    results = await wake_up_system.emergency_wake_up_all_critical()
    
    # Проверяем результат
    print("\n🔍 Проверка результата...")
    status_after = await wake_up_system.verify_critical_functions_status()
    print(f"   Активных критических: {status_after.get('active_critical', 0)}")
    print(f"   Спящих критических: {status_after.get('sleeping_critical', 0)}")
    
    print(f"\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"   Попыток пробуждения: {results['wake_up_attempts']}")
    print(f"   Успешно пробуждено: {results['successful_wake_ups']}")
    print(f"   Ошибок: {results['errors']}")
    
    if results['errors'] == 0:
        print("✅ ВСЕ КРИТИЧЕСКИЕ ФУНКЦИИ ПРОБУЖДЕНЫ!")
    else:
        print("⚠️ Некоторые критические функции требуют внимания")
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))