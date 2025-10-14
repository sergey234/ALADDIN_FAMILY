#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПАТЧ для SafeFunctionManager - исправляет блокировку и добавляет персистентность
"""

import re


def apply_patch():
    """Применить патч к safe_function_manager.py"""

    # Читаем файл
    with open("security/safe_function_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Добавляем персистентное хранение в конструктор
    content = re.sub(
        r"(self\.enable_auto_management = config\.get\(\'enable_auto_management\', True\) "
        r"if config else True)",
        r'\1\n        \n        # НОВОЕ: Персистентное хранение функций\n        '
        r'self.registry_file = config.get("registry_file", "data/functions_registry.json") '
        r'if config else "data/functions_registry.json"\n        '
        r'self.enable_persistence = config.get("enable_persistence", True) '
        r'if config else True',
        content,
    )

    # 2. Добавляем загрузку функций
    content = re.sub(
        r"(self\._init_vpn_antivirus\(\))",
        r"\1\n        \n        # НОВОЕ: Загрузить функции при инициализации\n        "
        r"if self.enable_persistence:\n            self.load_functions()",
        content,
    )

    # 3. Исправляем блокировку в register_function
    content = re.sub(
        r"(\s+# Автоматическое включение если требуется\s+if auto_enable:\s+self\.enable_function\(function_id\))",
        r"""\1
                # Автоматическое включение если требуется (без блокировки)
                if auto_enable:
                    function.status = FunctionStatus.ENABLED
                    self.functions_enabled += 1
                    self.log_activity(f"Функция {function_id} автоматически включена")
                # НОВОЕ: Автоматически сохранить после регистрации
                if self.enable_persistence:
                    self.save_functions()""",
        content,
    )

    # 4. Исправляем блокировку в _initialize_critical_functions
    content = re.sub(
        r"(\s+for function in self\.functions\.values\(\):\s+"
        r"if function\.is_critical and function\.auto_enable:\s+"
        r"self\.enable_function\(function\.function_id\))",
        r"""\1
        for function in self.functions.values():
            if function.is_critical and function.auto_enable:
                function.status = FunctionStatus.ENABLED
                self.functions_enabled += 1
                self.functions_disabled = max(0, self.functions_disabled - 1)""",
        content,
    )

    # Записываем исправленный файл
    with open("security/safe_function_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ ПАТЧ ПРИМЕНЕН УСПЕШНО!")
    print("✅ Исправлена блокировка в register_function")
    print("✅ Исправлена блокировка в _initialize_critical_functions")
    print("✅ Добавлено персистентное хранение")
    print("✅ Добавлена загрузка функций при инициализации")


if __name__ == "__main__":
    apply_patch()
