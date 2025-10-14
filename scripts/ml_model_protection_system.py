#!/usr/bin/env python3
"""
🛡️ СИСТЕМА ЗАЩИТЫ ML МОДЕЛЕЙ В СПЯЩЕМ РЕЖИМЕ
==============================================

Система для безопасного сохранения и восстановления ML моделей
при переводе функций в спящий режим.

Автор: ALADDIN Security System
Дата: 2025-09-15
Версия: 1.0.0
"""

import os
import json
import pickle
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import numpy as np

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLModelProtectionSystem:
    """Система защиты ML моделей в спящем режиме"""
    
    def __init__(self, backup_dir: str = "data/ml_models_backup"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.protected_models = {}
        self.model_metadata = {}
        
    async def protect_ml_models(self, function_name: str, models: Dict[str, Any]) -> bool:
        """
        Защита ML моделей функции перед переводом в спящий режим
        
        Args:
            function_name: Имя функции
            models: Словарь с ML моделями
            
        Returns:
            bool: Успешность защиты
        """
        try:
            logger.info(f"🛡️ Защита ML моделей для функции: {function_name}")
            
            # Создаем директорию для функции
            function_dir = self.backup_dir / function_name
            function_dir.mkdir(exist_ok=True)
            
            protected_models = {}
            metadata = {
                "function_name": function_name,
                "protection_time": datetime.now().isoformat(),
                "models_count": len(models),
                "models_info": {}
            }
            
            for model_name, model in models.items():
                try:
                    # Сохраняем модель
                    model_path = function_dir / f"{model_name}.pkl"
                    with open(model_path, 'wb') as f:
                        pickle.dump(model, f)
                    
                    # Сохраняем метаданные модели
                    model_metadata = {
                        "model_name": model_name,
                        "model_type": type(model).__name__,
                        "file_path": str(model_path),
                        "size_bytes": model_path.stat().st_size,
                        "has_weights": hasattr(model, 'coef_') or hasattr(model, 'weights_'),
                        "is_fitted": hasattr(model, 'predict') and callable(getattr(model, 'predict'))
                    }
                    
                    metadata["models_info"][model_name] = model_metadata
                    protected_models[model_name] = str(model_path)
                    
                    logger.info(f"✅ Модель {model_name} защищена: {model_path}")
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка защиты модели {model_name}: {e}")
                    return False
            
            # Сохраняем метаданные
            metadata_path = function_dir / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Обновляем реестр защищенных моделей
            self.protected_models[function_name] = protected_models
            self.model_metadata[function_name] = metadata
            
            logger.info(f"✅ ML модели функции {function_name} успешно защищены")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка защиты ML моделей для {function_name}: {e}")
            return False
    
    async def restore_ml_models(self, function_name: str) -> Optional[Dict[str, Any]]:
        """
        Восстановление ML моделей функции при пробуждении
        
        Args:
            function_name: Имя функции
            
        Returns:
            Dict[str, Any]: Восстановленные модели или None
        """
        try:
            logger.info(f"🔄 Восстановление ML моделей для функции: {function_name}")
            
            if function_name not in self.protected_models:
                logger.warning(f"⚠️ Нет защищенных моделей для функции: {function_name}")
                return None
            
            function_dir = self.backup_dir / function_name
            if not function_dir.exists():
                logger.error(f"❌ Директория модели не найдена: {function_dir}")
                return None
            
            restored_models = {}
            
            for model_name, model_path in self.protected_models[function_name].items():
                try:
                    # Загружаем модель
                    with open(model_path, 'rb') as f:
                        model = pickle.load(f)
                    
                    restored_models[model_name] = model
                    logger.info(f"✅ Модель {model_name} восстановлена")
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка восстановления модели {model_name}: {e}")
                    return None
            
            logger.info(f"✅ ML модели функции {function_name} успешно восстановлены")
            return restored_models
            
        except Exception as e:
            logger.error(f"❌ Ошибка восстановления ML моделей для {function_name}: {e}")
            return None
    
    async def get_protected_models_info(self) -> Dict[str, Any]:
        """Получение информации о защищенных моделях"""
        return {
            "protected_functions": list(self.protected_models.keys()),
            "total_models": sum(len(models) for models in self.protected_models.values()),
            "backup_directory": str(self.backup_dir),
            "metadata": self.model_metadata
        }
    
    async def cleanup_old_models(self, days_old: int = 30) -> int:
        """
        Очистка старых моделей
        
        Args:
            days_old: Возраст моделей в днях
            
        Returns:
            int: Количество удаленных файлов
        """
        try:
            logger.info(f"🧹 Очистка моделей старше {days_old} дней")
            
            deleted_count = 0
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
            
            for function_dir in self.backup_dir.iterdir():
                if function_dir.is_dir():
                    for model_file in function_dir.glob("*.pkl"):
                        if model_file.stat().st_mtime < cutoff_time:
                            model_file.unlink()
                            deleted_count += 1
                            logger.info(f"🗑️ Удален старый файл: {model_file}")
            
            logger.info(f"✅ Очищено {deleted_count} старых файлов")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки старых моделей: {e}")
            return 0

# Глобальный экземпляр системы защиты
ml_protection = MLModelProtectionSystem()

async def main():
    """Тестирование системы защиты ML моделей"""
    print("🛡️ ТЕСТИРОВАНИЕ СИСТЕМЫ ЗАЩИТЫ ML МОДЕЛЕЙ")
    print("=" * 50)
    
    # Тестовые модели
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    
    test_models = {
        "anomaly_detector": IsolationForest(contamination=0.1),
        "scaler": StandardScaler()
    }
    
    # Тест защиты
    success = await ml_protection.protect_ml_models("test_function", test_models)
    print(f"Защита моделей: {'✅ Успешно' if success else '❌ Ошибка'}")
    
    # Тест восстановления
    restored = await ml_protection.restore_ml_models("test_function")
    print(f"Восстановление моделей: {'✅ Успешно' if restored else '❌ Ошибка'}")
    
    # Информация о защищенных моделях
    info = await ml_protection.get_protected_models_info()
    print(f"Защищенных функций: {len(info['protected_functions'])}")
    print(f"Всего моделей: {info['total_models']}")

if __name__ == "__main__":
    asyncio.run(main())