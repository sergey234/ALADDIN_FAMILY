#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRODUCTION МЕНЕДЖЕР ПЕРСИСТЕНТНОСТИ ДЛЯ SAFEFUNCTIONMANAGER
Упрощенная версия для production использования
"""

import json
import os
import threading
from datetime import datetime
from typing import Any, Dict


class ProductionPersistenceManager:
    """Production менеджер персистентности для SafeFunctionManager"""

    def __init__(
        self, sfm_instance, registry_file: str = "data/functions_registry.json"
    ):
        """
        Инициализация менеджера
        Args:
            sfm_instance: Экземпляр SafeFunctionManager
            registry_file: Путь к файлу реестра
        """
        self.sfm = sfm_instance
        self.registry_file = registry_file
        self.lock = threading.Lock()

        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(registry_file), exist_ok=True)

        print("🔧 ProductionPersistenceManager инициализирован")
        print(f"📁 Файл реестра: {registry_file}")

    def save_functions(self) -> bool:
        """Сохранение функций в файл"""
        try:
            with self.lock:
                functions_data = {}

                # Собираем данные из SafeFunctionManager
                for func_id, function in self.sfm.functions.items():
                    functions_data[func_id] = {
                        "function_id": func_id,
                        "name": function.name,
                        "description": function.description,
                        "function_type": function.function_type,
                        "security_level": (
                            function.security_level.value
                            if hasattr(function.security_level, "value")
                            else str(function.security_level)
                        ),
                        "status": (
                            function.status.value
                            if hasattr(function.status, "value")
                            else str(function.status)
                        ),
                        "created_at": (
                            function.created_at.isoformat()
                            if hasattr(function, "created_at")
                            else datetime.now().isoformat()
                        ),
                        "is_critical": getattr(function, "is_critical", False),
                        "auto_enable": getattr(function, "auto_enable", False),
                    }

                # Создаем структуру данных
                registry_data = {
                    "version": "1.0",
                    "last_updated": datetime.now().isoformat(),
                    "functions": functions_data,
                }

                # Сохраняем в файл
                with open(self.registry_file, "w", encoding="utf-8") as f:
                    json.dump(registry_data, f, indent=2, ensure_ascii=False)

                print(f"✅ Функции сохранены: {len(functions_data)} функций")
                return True

        except Exception as e:
            print(f"❌ Ошибка сохранения функций: {e}")
            return False

    def load_functions(self) -> bool:
        """Загрузка функций из файла"""
        try:
            if not os.path.exists(self.registry_file):
                print(f"📁 Файл реестра не найден: {self.registry_file}")
                return False

            with open(self.registry_file, "r", encoding="utf-8") as f:
                registry_data = json.load(f)

            functions_data = registry_data.get("functions", {})
            loaded_count = 0

            print(f"📥 Загружаем {len(functions_data)} функций...")

            # Загружаем функции в SafeFunctionManager
            for func_id, func_data in functions_data.items():
                try:
                    # Проверяем, не зарегистрирована ли уже функция
                    if func_id not in self.sfm.functions:
                        # Импортируем SecurityLevel
                        from security.core.security_base import SecurityLevel

                        # Регистрируем функцию БЕЗ auto_enable
                        success = self.sfm.register_function(
                            function_id=func_id,
                            name=func_data["name"],
                            description=func_data["description"],
                            function_type=func_data["function_type"],
                            security_level=SecurityLevel[
                                func_data["security_level"].upper()
                            ],
                            is_critical=func_data.get("is_critical", False),
                            auto_enable=False,  # ВАЖНО: отключаем auto_enable
                        )

                        if success:
                            loaded_count += 1
                            print(f"   ✅ {func_data['name']} загружена")
                        else:
                            print(f"   ⚠️ Ошибка загрузки {func_data['name']}")
                    else:
                        print(
                            f"   ℹ️ {func_data['name']} уже зарегистрирована"
                        )

                except Exception as e:
                    print(f"   ❌ Ошибка загрузки функции {func_id}: {e}")
                    continue

            print(f"✅ Загружено функций: {loaded_count}")
            return loaded_count > 0

        except Exception as e:
            print(f"❌ Ошибка загрузки функций: {e}")
            return False

    def register_function_with_persistence(self, **kwargs) -> bool:
        """Регистрация функции с автоматическим сохранением"""
        try:
            # Регистрируем функцию
            success = self.sfm.register_function(**kwargs)

            if success:
                # Сохраняем в файл
                self.save_functions()
                print(
                    f"✅ Функция {kwargs.get('function_id')} "
                    f"зарегистрирована и сохранена"
                )

            return success

        except Exception as e:
            print(f"❌ Ошибка регистрации функции: {e}")
            return False

    def get_functions_status(self) -> Dict[str, Any]:
        """Получение статуса всех функций"""
        try:
            status = {
                "total_functions": len(self.sfm.functions),
                "enabled_functions": len(
                    [
                        f
                        for f in self.sfm.functions.values()
                        if f.status.value == "enabled"
                    ]
                ),
                "disabled_functions": len(
                    [
                        f
                        for f in self.sfm.functions.values()
                        if f.status.value == "disabled"
                    ]
                ),
                "critical_functions": len(
                    [
                        f
                        for f in self.sfm.functions.values()
                        if getattr(f, "is_critical", False)
                    ]
                ),
                "registry_file": self.registry_file,
                "registry_exists": os.path.exists(self.registry_file),
            }
            return status
        except Exception as e:
            print(f"❌ Ошибка получения статуса: {e}")
            return {}

    def initialize_security_functions(self) -> bool:
        """Инициализация критических функций безопасности"""
        try:
            print("🚀 Инициализация критических функций безопасности...")

            # Список критических функций
            critical_functions = [
                {
                    "function_id": "anti_fraud_master_ai",
                    "name": "AntiFraudMasterAI",
                    "description": "Главный агент защиты от мошенничества",
                    "function_type": "ai_agent",
                    "security_level": "critical",
                    "is_critical": True,
                    "auto_enable": False,
                },
                {
                    "function_id": "threat_detection_agent",
                    "name": "ThreatDetectionAgent",
                    "description": "Агент обнаружения угроз",
                    "function_type": "ai_agent",
                    "security_level": "high",
                    "is_critical": True,
                    "auto_enable": False,
                },
                {
                    "function_id": "security_monitoring",
                    "name": "SecurityMonitoring",
                    "description": "Мониторинг безопасности",
                    "function_type": "security",
                    "security_level": "high",
                    "is_critical": True,
                    "auto_enable": False,
                },
            ]

            registered_count = 0
            for func_data in critical_functions:
                if func_data["function_id"] not in self.sfm.functions:
                    success = self.register_function_with_persistence(
                        **func_data
                    )
                    if success:
                        registered_count += 1

            print(
                f"✅ Инициализировано критических функций: {registered_count}"
            )
            return registered_count > 0

        except Exception as e:
            print(f"❌ Ошибка инициализации функций: {e}")
            return False


if __name__ == "__main__":
    print("🔧 ProductionPersistenceManager готов к использованию")
    print("📁 Файл реестра: data/functions_registry.json")
    print("✅ Готов к production использованию")
