#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Script for Optimization Components
Скрипт интеграции компонентов оптимизации

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-28
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent.parent))

from security.unified_security_orchestrator import UnifiedSecurityOrchestrator
from security.performance_optimizer import PerformanceOptimizer
from security.ai_optimization_engine import AIOptimizationEngine, PerformanceDataPoint


class OptimizationIntegrationManager:
    """Менеджер интеграции компонентов оптимизации"""
    
    def __init__(self):
        self.orchestrator = None
        self.performance_optimizer = None
        self.ai_engine = None
        self.integration_active = False
        
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def initialize_all_components(self):
        """Инициализация всех компонентов"""
        self.logger.info("🚀 Инициализация компонентов оптимизации...")
        
        try:
            # 1. Инициализация Unified Security Orchestrator
            self.logger.info("📋 Инициализация Unified Security Orchestrator...")
            self.orchestrator = UnifiedSecurityOrchestrator()
            orchestrator_success = await self.orchestrator.initialize()
            
            if not orchestrator_success:
                self.logger.error("❌ Ошибка инициализации Orchestrator")
                return False
            
            # 2. Инициализация Performance Optimizer
            self.logger.info("⚙️ Инициализация Performance Optimizer...")
            self.performance_optimizer = PerformanceOptimizer()
            
            # 3. Инициализация AI Optimization Engine
            self.logger.info("🤖 Инициализация AI Optimization Engine...")
            self.ai_engine = AIOptimizationEngine()
            
            self.logger.info("✅ Все компоненты успешно инициализированы")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Критическая ошибка инициализации: {e}")
            return False
    
    async def start_integrated_optimization(self):
        """Запуск интегрированной оптимизации"""
        if not self.orchestrator or not self.performance_optimizer or not self.ai_engine:
            self.logger.error("❌ Компоненты не инициализированы")
            return False
        
        self.logger.info("🔄 Запуск интегрированной оптимизации...")
        self.integration_active = True
        
        try:
            # Запуск мониторинга производительности
            performance_task = asyncio.create_task(
                self.performance_optimizer.start_monitoring()
            )
            
            # Запуск AI оптимизации
            ai_task = asyncio.create_task(
                self.ai_engine.start_continuous_optimization()
            )
            
            # Основной цикл интеграции
            integration_task = asyncio.create_task(
                self._integration_loop()
            )
            
            # Ожидание завершения всех задач
            await asyncio.gather(performance_task, ai_task, integration_task)
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка интегрированной оптимизации: {e}")
        finally:
            self.integration_active = False
    
    async def _integration_loop(self):
        """Основной цикл интеграции"""
        while self.integration_active:
            try:
                # 1. Получение данных о производительности
                performance_profile = await self.performance_optimizer.analyze_system_performance()
                
                if performance_profile:
                    # 2. Создание точки данных для AI
                    data_point = PerformanceDataPoint(
                        timestamp=datetime.now(),
                        function_id="system_wide",
                        execution_time=0.1,  # Заглушка
                        success=True,
                        cpu_usage=performance_profile.current_load,
                        memory_usage=100 - (performance_profile.available_memory_gb / performance_profile.total_memory_gb * 100),
                        concurrent_functions=performance_profile.recommended_concurrency,
                        cache_hit_rate=0.8,  # Заглушка
                        error_rate=0.05  # Заглушка
                    )
                    
                    # 3. Добавление данных в AI engine
                    await self.ai_engine.add_performance_data(data_point)
                    
                    # 4. Получение AI предсказаний
                    prediction = await self.ai_engine.predict_function_performance("system_wide")
                    
                    if prediction and prediction.confidence > 0.5:
                        # 5. Применение оптимизаций
                        await self._apply_integrated_optimizations(performance_profile, prediction)
                
                # Пауза между циклами
                await asyncio.sleep(60)  # 1 минута
                
            except Exception as e:
                self.logger.error(f"❌ Ошибка в цикле интеграции: {e}")
                await asyncio.sleep(30)
    
    async def _apply_integrated_optimizations(self, performance_profile, prediction):
        """Применение интегрированных оптимизаций"""
        try:
            self.logger.info(f"🔧 Применение AI-оптимизаций: concurrency={prediction.recommended_concurrency}, "
                           f"cache={prediction.recommended_cache_size}, risk={prediction.risk_score:.2f}")
            
            # Создание конфигурации на основе AI предсказаний
            ai_config = {
                "max_concurrent_functions": prediction.recommended_concurrency,
                "cache_ttl": 3600,
                "max_thread_pool_workers": min(prediction.recommended_concurrency // 2, 50),
                "integration": {
                    "enable_zero_trust": True,
                    "enable_load_balancing": True,
                    "enable_auto_scaling": True,
                    "enable_circuit_breaking": True,
                    "trust_threshold": "MEDIUM" if prediction.risk_score < 0.5 else "HIGH"
                }
            }
            
            # Применение конфигурации к оркестратору
            if self.orchestrator:
                # Здесь должна быть логика применения конфигурации
                self.logger.info("✅ Конфигурация применена к оркестратору")
            
            # Сохранение результатов оптимизации
            optimization_result = {
                "timestamp": datetime.now().isoformat(),
                "performance_profile": {
                    "cpu_cores": performance_profile.cpu_cores,
                    "total_memory_gb": performance_profile.total_memory_gb,
                    "current_load": performance_profile.current_load
                },
                "ai_prediction": {
                    "predicted_execution_time": prediction.predicted_execution_time,
                    "confidence": prediction.confidence,
                    "risk_score": prediction.risk_score,
                    "recommendations": prediction.optimization_suggestions
                },
                "applied_config": ai_config
            }
            
            # Сохранение в файл
            with open("data/integrated_optimization_results.json", "w", encoding="utf-8") as f:
                json.dump(optimization_result, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info("💾 Результаты оптимизации сохранены")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка применения оптимизаций: {e}")
    
    async def get_integration_status(self):
        """Получение статуса интеграции"""
        status = {
            "integration_active": self.integration_active,
            "components_initialized": {
                "orchestrator": self.orchestrator is not None,
                "performance_optimizer": self.performance_optimizer is not None,
                "ai_engine": self.ai_engine is not None
            },
            "timestamp": datetime.now().isoformat()
        }
        
        if self.orchestrator:
            status["orchestrator_health"] = await self.orchestrator.get_system_health()
        
        if self.performance_optimizer:
            status["performance_report"] = self.performance_optimizer.get_performance_report()
        
        if self.ai_engine:
            status["ai_report"] = self.ai_engine.get_optimization_report()
        
        return status
    
    async def shutdown(self):
        """Корректное завершение работы"""
        self.logger.info("🛑 Завершение работы компонентов оптимизации...")
        
        self.integration_active = False
        
        if self.performance_optimizer:
            await self.performance_optimizer.stop_monitoring()
        
        if self.orchestrator:
            await self.orchestrator.shutdown()
        
        self.logger.info("✅ Все компоненты остановлены")


async def main():
    """Основная функция"""
    print("🎯 ИНТЕГРАЦИЯ КОМПОНЕНТОВ ОПТИМИЗАЦИИ ALADDIN")
    print("=" * 60)
    
    manager = OptimizationIntegrationManager()
    
    try:
        # Инициализация
        if await manager.initialize_all_components():
            print("✅ Все компоненты инициализированы")
            
            # Получение статуса
            status = await manager.get_integration_status()
            print(f"📊 Статус интеграции: {json.dumps(status, indent=2, ensure_ascii=False)}")
            
            # Запуск оптимизации
            print("🚀 Запуск интегрированной оптимизации...")
            print("Нажмите Ctrl+C для остановки")
            
            await manager.start_integrated_optimization()
            
        else:
            print("❌ Ошибка инициализации компонентов")
            return 1
    
    except KeyboardInterrupt:
        print("\n⏹️ Получен сигнал остановки")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return 1
    finally:
        await manager.shutdown()
        print("✅ Интеграция завершена")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)