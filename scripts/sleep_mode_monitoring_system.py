#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 СИСТЕМА МОНИТОРИНГА СПЯЩЕГО РЕЖИМА
=====================================

Система мониторинга, алертов и контроля спящего режима
Включает проверку состояния, производительности и автоматические уведомления

Автор: ALADDIN Security System
Дата: 2025-09-15
Версия: 1.0.0
"""

import asyncio
import json
import os
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import psutil

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SleepModeMonitoringSystem:
    """Система мониторинга спящего режима"""
    
    def __init__(self):
        self.monitoring_active = False
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "sleep_functions_count": 50,
            "error_rate": 5.0,
            "response_time": 2.0
        }
        self.alerts = []
        self.metrics = {}
        self.sleep_functions = self._load_sleep_functions()
        
    def _load_sleep_functions(self) -> List[Dict[str, Any]]:
        """Загрузка списка спящих функций"""
        sleep_functions = []
        
        # Загружаем из SFM реестра
        try:
            with open("data/sfm/function_registry.json", "r", encoding="utf-8") as f:
                sfm_registry = json.load(f)
                
            if "functions" in sfm_registry:
                for func_id, func_data in sfm_registry["functions"].items():
                    if func_data.get("status") == "sleeping":
                        sleep_functions.append({
                            "function_id": func_id,
                            "name": func_data.get("name", func_id),
                            "sleep_time": func_data.get("sleep_time"),
                            "security_level": func_data.get("security_level", "medium"),
                            "is_critical": func_data.get("is_critical", False)
                        })
        except Exception as e:
            logger.error(f"Ошибка загрузки спящих функций: {e}")
        
        # Загружаем из файлов состояния
        state_dir = Path("data/sleep_states")
        if state_dir.exists():
            for state_file in state_dir.glob("*_state.json"):
                try:
                    with open(state_file, "r", encoding="utf-8") as f:
                        state = json.load(f)
                    sleep_functions.append({
                        "function_id": state.get("function_id", "unknown"),
                        "name": state.get("function_name", "unknown"),
                        "sleep_time": state.get("sleep_time"),
                        "security_level": state.get("security_level", "medium"),
                        "is_critical": state.get("is_critical", False),
                        "state_file": str(state_file)
                    })
                except Exception as e:
                    logger.error(f"Ошибка загрузки состояния {state_file}: {e}")
        
        return sleep_functions
    
    async def start_monitoring(self) -> None:
        """Запуск мониторинга"""
        logger.info("📊 ЗАПУСК СИСТЕМЫ МОНИТОРИНГА СПЯЩЕГО РЕЖИМА")
        logger.info("=" * 50)
        
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # Сбор метрик
                await self._collect_metrics()
                
                # Проверка алертов
                await self._check_alerts()
                
                # Обновление состояния спящих функций
                self.sleep_functions = self._load_sleep_functions()
                
                # Логирование статуса
                logger.info(f"📊 Мониторинг активен: {len(self.sleep_functions)} функций в спящем режиме")
                
                # Ожидание перед следующей проверкой
                await asyncio.sleep(30)  # Проверка каждые 30 секунд
                
            except Exception as e:
                logger.error(f"Ошибка в мониторинге: {e}")
                await asyncio.sleep(10)
    
    async def stop_monitoring(self) -> None:
        """Остановка мониторинга"""
        logger.info("⏹️ ОСТАНОВКА СИСТЕМЫ МОНИТОРИНГА")
        self.monitoring_active = False
    
    async def _collect_metrics(self) -> None:
        """Сбор метрик системы"""
        try:
            # Системные метрики
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Метрики спящего режима
            sleep_count = len(self.sleep_functions)
            critical_sleep = len([f for f in self.sleep_functions if f.get("is_critical", False)])
            
            self.metrics = {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "memory_available": memory.available,
                    "disk_usage": disk.percent,
                    "disk_free": disk.free
                },
                "sleep_mode": {
                    "sleep_functions_count": sleep_count,
                    "critical_sleep_count": critical_sleep,
                    "sleep_functions": self.sleep_functions
                }
            }
            
        except Exception as e:
            logger.error(f"Ошибка сбора метрик: {e}")
    
    async def _check_alerts(self) -> None:
        """Проверка алертов"""
        try:
            current_time = datetime.now()
            
            # Проверка CPU
            if self.metrics.get("system", {}).get("cpu_usage", 0) > self.alert_thresholds["cpu_usage"]:
                await self._create_alert(
                    "HIGH_CPU_USAGE",
                    f"Высокое использование CPU: {self.metrics['system']['cpu_usage']:.1f}%",
                    "warning"
                )
            
            # Проверка памяти
            if self.metrics.get("system", {}).get("memory_usage", 0) > self.alert_thresholds["memory_usage"]:
                await self._create_alert(
                    "HIGH_MEMORY_USAGE",
                    f"Высокое использование памяти: {self.metrics['system']['memory_usage']:.1f}%",
                    "warning"
                )
            
            # Проверка количества спящих функций
            sleep_count = self.metrics.get("sleep_mode", {}).get("sleep_functions_count", 0)
            if sleep_count > self.alert_thresholds["sleep_functions_count"]:
                await self._create_alert(
                    "TOO_MANY_SLEEP_FUNCTIONS",
                    f"Слишком много спящих функций: {sleep_count}",
                    "info"
                )
            
            # Проверка критических функций в спящем режиме
            critical_sleep = self.metrics.get("sleep_mode", {}).get("critical_sleep_count", 0)
            if critical_sleep > 0:
                await self._create_alert(
                    "CRITICAL_FUNCTIONS_SLEEPING",
                    f"Критические функции в спящем режиме: {critical_sleep}",
                    "critical"
                )
            
        except Exception as e:
            logger.error(f"Ошибка проверки алертов: {e}")
    
    async def _create_alert(self, alert_type: str, message: str, severity: str) -> None:
        """Создание алерта"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "message": message,
            "severity": severity,
            "acknowledged": False
        }
        
        self.alerts.append(alert)
        
        # Логирование алерта
        if severity == "critical":
            logger.critical(f"🚨 КРИТИЧЕСКИЙ АЛЕРТ: {message}")
        elif severity == "warning":
            logger.warning(f"⚠️ ПРЕДУПРЕЖДЕНИЕ: {message}")
        else:
            logger.info(f"ℹ️ ИНФОРМАЦИЯ: {message}")
        
        # Сохранение алерта
        await self._save_alert(alert)
    
    async def _save_alert(self, alert: Dict[str, Any]) -> None:
        """Сохранение алерта"""
        try:
            alerts_dir = Path("logs/sleep_mode_alerts")
            alerts_dir.mkdir(parents=True, exist_ok=True)
            
            alert_file = alerts_dir / f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(alert_file, "w", encoding="utf-8") as f:
                json.dump(alert, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Ошибка сохранения алерта: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Получение статуса системы"""
        return {
            "monitoring_active": self.monitoring_active,
            "sleep_functions_count": len(self.sleep_functions),
            "alerts_count": len(self.alerts),
            "unacknowledged_alerts": len([a for a in self.alerts if not a.get("acknowledged", False)]),
            "metrics": self.metrics,
            "sleep_functions": self.sleep_functions
        }
    
    async def wake_up_function(self, function_name: str) -> Dict[str, Any]:
        """Пробуждение функции"""
        try:
            # Находим функцию в списке спящих
            sleep_function = None
            for func in self.sleep_functions:
                if func.get("name") == function_name:
                    sleep_function = func
                    break
            
            if not sleep_function:
                return {
                    "success": False,
                    "message": f"Функция {function_name} не найдена в спящих"
                }
            
            # Обновляем статус в SFM реестре
            try:
                with open("data/sfm/function_registry.json", "r", encoding="utf-8") as f:
                    sfm_registry = json.load(f)
                
                func_id = sleep_function.get("function_id")
                if func_id in sfm_registry.get("functions", {}):
                    sfm_registry["functions"][func_id]["status"] = "active"
                    sfm_registry["functions"][func_id]["wake_time"] = datetime.now().isoformat()
                
                with open("data/sfm/function_registry.json", "w", encoding="utf-8") as f:
                    json.dump(sfm_registry, f, indent=2, ensure_ascii=False)
                
            except Exception as e:
                logger.error(f"Ошибка обновления SFM реестра: {e}")
            
            # Удаляем файл состояния
            state_file = sleep_function.get("state_file")
            if state_file and os.path.exists(state_file):
                os.remove(state_file)
            
            # Создаем алерт о пробуждении
            await self._create_alert(
                "FUNCTION_WOKE_UP",
                f"Функция {function_name} пробуждена",
                "info"
            )
            
            return {
                "success": True,
                "message": f"Функция {function_name} успешно пробуждена",
                "wake_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка пробуждения функции {function_name}: {e}")
            return {
                "success": False,
                "message": f"Ошибка пробуждения: {str(e)}"
            }

async def main():
    """Главная функция"""
    print("📊 СИСТЕМА МОНИТОРИНГА СПЯЩЕГО РЕЖИМА")
    print("=" * 50)
    
    monitoring = SleepModeMonitoringSystem()
    
    # Получаем текущий статус
    status = await monitoring.get_system_status()
    print(f"📊 Спящих функций: {status['sleep_functions_count']}")
    print(f"🚨 Алертов: {status['alerts_count']}")
    print(f"⚠️ Неподтвержденных алертов: {status['unacknowledged_alerts']}")
    
    # Запускаем мониторинг на 2 минуты для демонстрации
    print("\n🔄 Запуск мониторинга на 2 минуты...")
    monitoring_task = asyncio.create_task(monitoring.start_monitoring())
    
    try:
        await asyncio.wait_for(monitoring_task, timeout=120)  # 2 минуты
    except asyncio.TimeoutError:
        print("⏰ Время мониторинга истекло")
    
    await monitoring.stop_monitoring()
    
    # Финальный статус
    final_status = await monitoring.get_system_status()
    print(f"\n📊 ФИНАЛЬНЫЙ СТАТУС:")
    print(f"   Спящих функций: {final_status['sleep_functions_count']}")
    print(f"   Алертов создано: {final_status['alerts_count']}")
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))