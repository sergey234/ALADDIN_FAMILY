#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 МИНИМАЛЬНАЯ АКТИВНАЯ СИСТЕМА
===============================

Перевод в спящий режим всех функций кроме минимально необходимых
для функционирования системы

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
from typing import Dict, List, Any, Set

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MinimalActiveSystem:
    """Минимальная активная система"""
    
    def __init__(self):
        self.minimal_active_functions = {
            # Управление системой
            "safe_function_manager",
            "sleep_mode_manager",
            "all_bots_sleep_manager",
            "safe_sleep_mode_optimizer",
            
            # Критические системы
            "enhanced_alerting",
            "threat_detection",
            "incident_response",
            
            # ML компоненты (все AI агенты)
            "behavioral_analysis_agent",
            "threat_detection_agent", 
            "password_security_agent",
            "incident_response_agent",
            "network_security_agent",
            "compliance_agent",
            "mobile_security_agent",
            "emergency_ml_analyzer",
            "analytics_manager",
            
            # Критические микросервисы
            "rate_limiter",
            "circuit_breaker",
            "user_interface_manager",
            
            # Критические боты
            "mobile_navigation_bot",
            "notification_bot",
            
            # Базовые системы
            "authentication_manager",
            "access_control_manager",
            "data_protection_manager",
            "zero_trust_manager",
            "security_audit",
            "threat_intelligence",
            "malware_protection",
            "intrusion_prevention",
            "network_monitoring",
            "ransomware_protection",
            
            # Ядро системы
            "configuration",
            "database",
            "logging_module",
            "security_base",
            "service_base"
        }
        
    async def create_minimal_system(self) -> Dict[str, Any]:
        """Создание минимальной активной системы"""
        logger.info("🎯 СОЗДАНИЕ МИНИМАЛЬНОЙ АКТИВНОЙ СИСТЕМЫ")
        logger.info("=" * 50)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "minimal_active": len(self.minimal_active_functions),
            "sleep_attempts": 0,
            "successful_sleep": 0,
            "errors": 0,
            "slept_functions": [],
            "error_functions": []
        }
        
        # 1. Загружаем SFM реестр
        sfm_registry = await self._load_sfm_registry()
        
        # 2. Переводим все функции в спящий режим кроме минимальных
        if "functions" in sfm_registry:
            for func_id, func_data in sfm_registry["functions"].items():
                func_name = func_data.get("name", func_id)
                
                # Пропускаем минимальные активные функции
                if func_name in self.minimal_active_functions:
                    logger.info(f"✅ {func_name} - остается активной")
                    continue
                
                # Переводим в спящий режим
                try:
                    result = await self._put_function_to_sleep(func_id, func_data, sfm_registry)
                    results["sleep_attempts"] += 1
                    
                    if result["success"]:
                        results["successful_sleep"] += 1
                        results["slept_functions"].append(func_name)
                        logger.info(f"😴 {func_name} - переведена в спящий режим")
                    else:
                        results["errors"] += 1
                        results["error_functions"].append({
                            "name": func_name,
                            "error": result["message"]
                        })
                        logger.error(f"❌ Ошибка перевода {func_name}: {result['message']}")
                        
                except Exception as e:
                    results["errors"] += 1
                    results["error_functions"].append({
                        "name": func_name,
                        "error": str(e)
                    })
                    logger.error(f"❌ Критическая ошибка {func_name}: {e}")
        
        # 3. Сохраняем обновленный реестр
        await self._save_sfm_registry(sfm_registry)
        
        # 4. Создаем отчет
        report_path = f"logs/minimal_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 Отчет минимальной системы: {report_path}")
        logger.info(f"✅ Минимальных активных: {results['minimal_active']}")
        logger.info(f"😴 Переведено в сон: {results['successful_sleep']}")
        logger.info(f"❌ Ошибок: {results['errors']}")
        
        return results
    
    async def _load_sfm_registry(self) -> Dict[str, Any]:
        """Загрузка SFM реестра"""
        try:
            with open("data/sfm/function_registry.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки SFM реестра: {e}")
            return {}
    
    async def _save_sfm_registry(self, sfm_registry: Dict[str, Any]) -> None:
        """Сохранение SFM реестра"""
        try:
            with open("data/sfm/function_registry.json", "w", encoding="utf-8") as f:
                json.dump(sfm_registry, f, indent=2, ensure_ascii=False)
            logger.info("✅ SFM реестр сохранен")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения SFM реестра: {e}")
    
    async def _put_function_to_sleep(self, func_id: str, func_data: Dict[str, Any], sfm_registry: Dict[str, Any]) -> Dict[str, Any]:
        """Перевод функции в спящий режим"""
        try:
            # Обновляем статус в SFM реестре
            sfm_registry["functions"][func_id]["status"] = "sleeping"
            sfm_registry["functions"][func_id]["sleep_time"] = datetime.now().isoformat()
            sfm_registry["functions"][func_id]["minimal_system_sleep"] = True
            
            # Сохраняем состояние функции
            state_path = f"data/sleep_states/{func_data.get('name', func_id)}_state.json"
            os.makedirs(os.path.dirname(state_path), exist_ok=True)
            
            function_state = {
                "function_name": func_data.get("name", func_id),
                "function_id": func_id,
                "sleep_time": datetime.now().isoformat(),
                "previous_status": func_data.get("status", "active"),
                "security_level": func_data.get("security_level", "medium"),
                "is_critical": func_data.get("is_critical", False),
                "minimal_system_sleep": True
            }
            
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(function_state, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "message": f"Функция переведена в спящий режим",
                "sleep_time": function_state["sleep_time"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Ошибка перевода в сон: {str(e)}"
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        try:
            sfm_registry = await self._load_sfm_registry()
            
            if "functions" not in sfm_registry:
                return {"error": "SFM реестр не найден"}
            
            active_count = 0
            sleeping_count = 0
            minimal_active_count = 0
            
            for func_id, func_data in sfm_registry["functions"].items():
                func_name = func_data.get("name", func_id)
                status = func_data.get("status", "unknown")
                
                if func_name in self.minimal_active_functions:
                    minimal_active_count += 1
                elif status == "active":
                    active_count += 1
                elif status == "sleeping":
                    sleeping_count += 1
            
            return {
                "total_functions": len(sfm_registry["functions"]),
                "minimal_active": minimal_active_count,
                "other_active": active_count,
                "sleeping": sleeping_count,
                "minimal_functions": list(self.minimal_active_functions)
            }
            
        except Exception as e:
            return {"error": str(e)}

async def main():
    """Главная функция"""
    print("🎯 МИНИМАЛЬНАЯ АКТИВНАЯ СИСТЕМА")
    print("=" * 40)
    
    minimal_system = MinimalActiveSystem()
    
    # Проверяем текущий статус
    print("🔍 Проверка текущего статуса...")
    status_before = await minimal_system.get_system_status()
    print(f"   Всего функций: {status_before.get('total_functions', 0)}")
    print(f"   Активных: {status_before.get('other_active', 0)}")
    print(f"   Спящих: {status_before.get('sleeping', 0)}")
    print(f"   Минимальных активных: {status_before.get('minimal_active', 0)}")
    
    # Создаем минимальную систему
    print("\n🎯 Создание минимальной активной системы...")
    results = await minimal_system.create_minimal_system()
    
    # Проверяем результат
    print("\n🔍 Проверка результата...")
    status_after = await minimal_system.get_system_status()
    print(f"   Всего функций: {status_after.get('total_functions', 0)}")
    print(f"   Активных: {status_after.get('other_active', 0)}")
    print(f"   Спящих: {status_after.get('sleeping', 0)}")
    print(f"   Минимальных активных: {status_after.get('minimal_active', 0)}")
    
    print(f"\n🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"   Минимальных активных: {results['minimal_active']}")
    print(f"   Переведено в сон: {results['successful_sleep']}")
    print(f"   Ошибок: {results['errors']}")
    
    if results['errors'] == 0:
        print("✅ МИНИМАЛЬНАЯ СИСТЕМА СОЗДАНА!")
    else:
        print("⚠️ Некоторые функции требуют внимания")
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))