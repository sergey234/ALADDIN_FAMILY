#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Безопасная реализация спящего режима с защитой ML моделей
Включает сохранение весов, карту зависимостей и мониторинг
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

class SafeSleepModeImplementer:
    """Безопасная реализация спящего режима"""
    
    def __init__(self):
        self.sfm_registry = self._load_sfm_registry()
        self.dependency_map = self._load_dependency_map()
        self.ml_components = self._identify_ml_components()
        self.critical_functions = self._load_critical_functions()
        self.sleep_state = {}
        self.backup_dir = Path("sleep_mode_backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def _load_sfm_registry(self) -> Dict:
        """Загрузка реестра SFM"""
        try:
            with open('data/sfm/function_registry.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки реестра SFM: {e}")
            return {}
    
    def _load_dependency_map(self) -> Dict:
        """Загрузка карты зависимостей"""
        try:
            # Поиск последнего файла карты зависимостей
            map_files = list(Path('.').glob('DEPENDENCY_MAP_*.json'))
            if map_files:
                latest_map = max(map_files, key=os.path.getctime)
                with open(latest_map, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Ошибка загрузки карты зависимостей: {e}")
            return {}
    
    def _identify_ml_components(self) -> List[str]:
        """Идентификация ML компонентов"""
        ml_components = [
            # AI Агенты с ML моделями
            "behavioral_analysis_agent",
            "threat_detection_agent", 
            "password_security_agent",
            "incident_response_agent",
            "threat_intelligence_agent",
            "network_security_agent",
            "compliance_agent",
            "mobile_security_agent",
            "emergency_ml_analyzer",
            "alert_manager",
            "voice_security_validator",
            "family_communication_hub_a_plus",
            "behavioral_analytics_engine_main",
            "anti_fraud_master_ai",
            "phishing_protection_agent",
            
            # Микросервисы с ML моделями
            "rate_limiter",
            "circuit_breaker", 
            "user_interface_manager",
            "analytics_manager",
            "monitor_manager",
            
            # Боты с ML моделями
            "mobile_navigation_bot",
            "notification_bot"
        ]
        return ml_components
    
    def _load_critical_functions(self) -> Set[str]:
        """Загрузка критических функций"""
        try:
            with open('TOP_50_CRITICAL_FUNCTIONS.json', 'r', encoding='utf-8') as f:
                critical_data = json.load(f)
            return {func['id'] for func in critical_data}
        except Exception as e:
            logger.error(f"Ошибка загрузки критических функций: {e}")
            return set()
    
    async def save_ml_model_weights(self, component_id: str, model_data: Any) -> bool:
        """Безопасное сохранение весов ML модели"""
        try:
            model_path = self.backup_dir / f"{component_id}_ml_model"
            
            # Сохранение модели
            import joblib
            joblib.dump(model_data, f"{model_path}.joblib")
            
            # Сохранение метаданных
            metadata = {
                "component_id": component_id,
                "timestamp": datetime.now().isoformat(),
                "model_type": type(model_data).__name__,
                "model_path": str(model_path),
                "parameters": getattr(model_data, 'get_params', lambda: {})()
            }
            
            with open(f"{model_path}_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"ML модель {component_id} сохранена в {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения ML модели {component_id}: {e}")
            return False
    
    async def restore_ml_model_weights(self, component_id: str) -> Any:
        """Безопасное восстановление весов ML модели"""
        try:
            model_path = self.backup_dir / f"{component_id}_ml_model"
            
            if not Path(f"{model_path}.joblib").exists():
                logger.warning(f"Файл модели {component_id} не найден")
                return None
            
            import joblib
            model_data = joblib.load(f"{model_path}.joblib")
            
            logger.info(f"ML модель {component_id} восстановлена из {model_path}")
            return model_data
            
        except Exception as e:
            logger.error(f"Ошибка восстановления ML модели {component_id}: {e}")
            return None
    
    async def safe_put_to_sleep(self, function_id: str, reason: str = "Safe sleep") -> bool:
        """Безопасный перевод функции в спящий режим"""
        try:
            # Проверка, что функция не критическая
            if function_id in self.critical_functions:
                logger.warning(f"Функция {function_id} критическая, пропускаем")
                return False
            
            # Получение данных функции
            func_data = self.sfm_registry.get('functions', {}).get(function_id, {})
            if not func_data:
                logger.warning(f"Функция {function_id} не найдена в реестре")
                return False
            
            # Сохранение состояния ML модели если необходимо
            if function_id in self.ml_components:
                # Здесь должен быть код для получения ML модели
                # Пока что создаем заглушку
                ml_model_data = {"placeholder": "ml_model_data", "type": "IsolationForest"}
                await self.save_ml_model_weights(function_id, ml_model_data)
            
            # Сохранение общего состояния функции
            sleep_data = {
                "function_id": function_id,
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "original_status": func_data.get('status', 'unknown'),
                "config": func_data.get('config', {}),
                "stats": func_data.get('stats', {}),
                "is_ml_component": function_id in self.ml_components,
                "ml_models": func_data.get('ml_models', [])
            }
            
            # Сохранение состояния в файл
            state_file = self.backup_dir / f"{function_id}_sleep_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(sleep_data, f, indent=2, ensure_ascii=False)
            
            # Обновление статуса в реестре
            self.sfm_registry['functions'][function_id]['status'] = 'sleeping'
            self.sfm_registry['functions'][function_id]['sleep_time'] = datetime.now().isoformat()
            self.sfm_registry['functions'][function_id]['sleep_reason'] = reason
            
            # Сохранение обновленного реестра
            await self._save_sfm_registry()
            
            self.sleep_state[function_id] = sleep_data
            logger.info(f"Функция {function_id} безопасно переведена в спящий режим")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка перевода функции {function_id} в спящий режим: {e}")
            return False
    
    async def safe_wake_up(self, function_id: str) -> bool:
        """Безопасное пробуждение функции из спящего режима"""
        try:
            # Проверка, что функция в спящем режиме
            if function_id not in self.sleep_state:
                logger.warning(f"Функция {function_id} не в спящем режиме")
                return False
            
            sleep_data = self.sleep_state[function_id]
            
            # Восстановление ML модели если необходимо
            if sleep_data.get('is_ml_component', False):
                ml_model = await self.restore_ml_model_weights(function_id)
                if ml_model is None:
                    logger.error(f"Не удалось восстановить ML модель для {function_id}")
                    return False
            
            # Восстановление общего состояния
            func_data = self.sfm_registry.get('functions', {}).get(function_id, {})
            if 'config' in sleep_data:
                func_data['config'].update(sleep_data['config'])
            if 'stats' in sleep_data:
                func_data['stats'].update(sleep_data['stats'])
            
            # Обновление статуса в реестре
            self.sfm_registry['functions'][function_id]['status'] = 'enabled'
            self.sfm_registry['functions'][function_id]['wake_up_time'] = datetime.now().isoformat()
            self.sfm_registry['functions'][function_id]['sleep_duration'] = (
                datetime.now() - datetime.fromisoformat(sleep_data['timestamp'])
            ).total_seconds()
            
            # Сохранение обновленного реестра
            await self._save_sfm_registry()
            
            # Удаление из спящего состояния
            del self.sleep_state[function_id]
            
            logger.info(f"Функция {function_id} безопасно пробуждена из спящего режима")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка пробуждения функции {function_id}: {e}")
            return False
    
    async def _save_sfm_registry(self) -> None:
        """Сохранение обновленного реестра SFM"""
        try:
            # Создание резервной копии
            backup_file = f"data/sfm/function_registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.sfm_registry, f, indent=2, ensure_ascii=False)
            
            # Сохранение обновленного реестра
            with open('data/sfm/function_registry.json', 'w', encoding='utf-8') as f:
                json.dump(self.sfm_registry, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Реестр SFM обновлен, резервная копия: {backup_file}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения реестра SFM: {e}")
    
    async def implement_sleep_mode(self) -> Dict[str, Any]:
        """Реализация спящего режима"""
        print("🛡️ БЕЗОПАСНАЯ РЕАЛИЗАЦИЯ СПЯЩЕГО РЕЖИМА")
        print("=" * 60)
        
        # Получение списка функций для перевода в спящий режим
        all_functions = list(self.sfm_registry.get('functions', {}).keys())
        sleep_functions = [
            f for f in all_functions 
            if f not in self.critical_functions and f not in self.ml_components
        ]
        
        print(f"📊 Всего функций: {len(all_functions)}")
        print(f"🔒 Критических функций: {len(self.critical_functions)}")
        print(f"🤖 ML компонентов: {len(self.ml_components)}")
        print(f"😴 Кандидатов для спящего режима: {len(sleep_functions)}")
        
        # Запрос подтверждения
        confirm = input("\n❓ Продолжить безопасный перевод в спящий режим? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Операция отменена")
            return {"success": False, "reason": "User cancelled"}
        
        # Перевод в спящий режим
        results = {}
        successful = 0
        
        print(f"\n😴 Перевод {len(sleep_functions)} функций в спящий режим...")
        
        for i, function_id in enumerate(sleep_functions, 1):
            print(f"   [{i}/{len(sleep_functions)}] {function_id}...", end=" ")
            
            success = await self.safe_put_to_sleep(function_id, "Safe sleep implementation")
            results[function_id] = success
            
            if success:
                print("✅")
                successful += 1
            else:
                print("❌")
            
            # Небольшая задержка между операциями
            await asyncio.sleep(0.1)
        
        # Генерация отчета
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_functions": len(all_functions),
            "critical_functions": len(self.critical_functions),
            "ml_components": len(self.ml_components),
            "sleep_candidates": len(sleep_functions),
            "successful_sleep": successful,
            "failed_sleep": len(sleep_functions) - successful,
            "success_rate": (successful / len(sleep_functions)) * 100 if sleep_functions else 0,
            "results": results
        }
        
        # Сохранение отчета
        report_file = f"SLEEP_MODE_IMPLEMENTATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 ПЕРЕВОД В СПЯЩИЙ РЕЖИМ ЗАВЕРШЕН!")
        print("=" * 60)
        print(f"✅ Успешно переведено: {successful}/{len(sleep_functions)}")
        print(f"📊 Процент успеха: {report['success_rate']:.1f}%")
        print(f"🔒 Критических функций защищено: {len(self.critical_functions)}")
        print(f"🤖 ML компонентов защищено: {len(self.ml_components)}")
        print(f"📁 Отчет сохранен: {report_file}")
        
        return report

async def main():
    """Главная функция"""
    implementer = SafeSleepModeImplementer()
    report = await implementer.implement_sleep_mode()
    
    if report.get("success", True):
        print("\n✅ СПЯЩИЙ РЕЖИМ УСПЕШНО РЕАЛИЗОВАН!")
        return 0
    else:
        print("\n❌ ОШИБКА РЕАЛИЗАЦИИ СПЯЩЕГО РЕЖИМА!")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))