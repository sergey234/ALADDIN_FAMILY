#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ВНЕШНИЙ ИНТЕГРАТОР ПЕРСИСТЕНТНОСТИ ДЛЯ SAFEFUNCTIONMANAGER
Работает с существующим SafeFunctionManager без изменения его логики
"""

import json
import os
import threading
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class FunctionMetadata:
    """Метаданные функции для персистентного хранения"""

    function_id: str
    name: str
    description: str
    function_type: str
    security_level: str
    status: str
    created_at: str
    last_execution: Optional[str] = None
    execution_count: int = 0
    success_count: int = 0
    error_count: int = 0
    average_execution_time: float = 0.0
    dependencies: list = None
    is_critical: bool = False
    auto_enable: bool = False


class PersistenceIntegrator:
    """Внешний интегратор персистентности для SafeFunctionManager"""

    def __init__(
        self, sfm_instance, registry_file: str = "data/functions_registry.json"
    ):
        """
        Инициализация интегратора
        Args:
            sfm_instance: Экземпляр SafeFunctionManager
            registry_file: Путь к файлу реестра
        """
        self.sfm = sfm_instance
        self.registry_file = registry_file
        self.lock = threading.Lock()

        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(registry_file), exist_ok=True)

        # Загружаем существующие функции при инициализации
        self.load_functions()

    def save_functions(self) -> bool:
        """Сохранение функций в файл"""
        try:
            with self.lock:
                functions_data = {}

                # Собираем данные из SafeFunctionManager
                for func_id, function in self.sfm.functions.items():
                    functions_data[func_id] = FunctionMetadata(
                        function_id=func_id,
                        name=function.name,
                        description=function.description,
                        function_type=function.function_type,
                        security_level=function.security_level.value,
                        status=function.status.value,
                        created_at=(
                            function.created_at.isoformat()
                            if hasattr(function, "created_at")
                            else datetime.now().isoformat()
                        ),
                        last_execution=(
                            function.last_execution.isoformat()
                            if hasattr(function, "last_execution")
                            and function.last_execution
                            else None
                        ),
                        execution_count=getattr(
                            function, "execution_count", 0
                        ),
                        success_count=getattr(function, "success_count", 0),
                        error_count=getattr(function, "error_count", 0),
                        average_execution_time=getattr(
                            function, "average_execution_time", 0.0
                        ),
                        dependencies=getattr(function, "dependencies", []),
                        is_critical=getattr(function, "is_critical", False),
                        auto_enable=getattr(function, "auto_enable", False),
                    )

                # Создаем структуру данных
                registry_data = {
                    "version": "1.0",
                    "last_updated": datetime.now().isoformat(),
                    "functions": {
                        k: asdict(v) for k, v in functions_data.items()
                    },
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

            # Загружаем функции в SafeFunctionManager
            for func_id, func_data in functions_data.items():
                try:
                    # Проверяем, не зарегистрирована ли уже функция
                    if func_id not in self.sfm.functions:
                        # Регистрируем функцию БЕЗ auto_enable
                        # чтобы избежать блокировки
                        success = self.sfm.register_function(
                            function_id=func_id,
                            name=func_data["name"],
                            description=func_data["description"],
                            function_type=func_data["function_type"],
                            security_level=getattr(
                                self.sfm.SecurityLevel,
                                func_data["security_level"].upper(),
                            ),
                            is_critical=func_data.get("is_critical", False),
                            auto_enable=False,  # ВАЖНО: отключаем auto_enable
                        )

                        if success:
                            # Устанавливаем статус напрямую
                            function = self.sfm.functions[func_id]
                            function.status = getattr(
                                self.sfm.FunctionStatus,
                                func_data["status"].upper(),
                            )

                            # Восстанавливаем дополнительные свойства
                            if func_data.get("is_critical"):
                                function.is_critical = True
                            if func_data.get("auto_enable"):
                                function.auto_enable = True

                            loaded_count += 1

                except Exception as e:
                    print(f"⚠️ Ошибка загрузки функции {func_id}: {e}")
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

    def enable_function_with_persistence(self, function_id: str) -> bool:
        """Включение функции с автоматическим сохранением"""
        try:
            success = self.sfm.enable_function(function_id)

            if success:
                self.save_functions()
                print(f"✅ Функция {function_id} включена и сохранена")

            return success

        except Exception as e:
            print(f"❌ Ошибка включения функции: {e}")
            return False

    def disable_function_with_persistence(self, function_id: str) -> bool:
        """Отключение функции с автоматическим сохранением"""
        try:
            success = self.sfm.disable_function(function_id)

            if success:
                self.save_functions()
                print(f"✅ Функция {function_id} отключена и сохранена")

            return success

        except Exception as e:
            print(f"❌ Ошибка отключения функции: {e}")
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


if __name__ == "__main__":
    print("🔧 PersistenceIntegrator готов к использованию")
    print("📁 Файл реестра: data/functions_registry.json")
    print("✅ Интегратор может работать с существующим SafeFunctionManager")
