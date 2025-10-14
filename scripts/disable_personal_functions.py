#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ОТКЛЮЧЕНИЕ ПЕРСОНАЛЬНЫХ ФУНКЦИЙ ДЛЯ АНОНИМНОГО РЕЖИМА
Автоматическое отключение функций, требующих персональных данных
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set


class PersonalFunctionsDisabler:
    """Отключение персональных функций для анонимного режима"""
    
    def __init__(self, project_root: str = "/Users/sergejhlystov/ALADDIN_NEW"):
        self.project_root = Path(project_root)
        self.config_file = self.project_root / "config" / "anonymous_mode_config.json"
        self.disabled_functions = set()
        self.replacement_functions = {}
        self.backup_dir = self.project_root / "backups" / "personal_functions_backup"
        
    def load_config(self) -> Dict:
        """Загрузка конфигурации анонимного режима"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            return {}
    
    def create_backup(self) -> bool:
        """Создание резервной копии перед изменениями"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Резервная копия создана: {self.backup_dir}")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания резервной копии: {e}")
            return False
    
    def find_personal_functions(self) -> List[str]:
        """Поиск функций, требующих персональных данных"""
        personal_patterns = [
            r'def.*family.*\(',  # семейные функции
            r'def.*personal.*\(',  # персональные функции
            r'def.*child.*\(',  # детские функции
            r'def.*elderly.*\(',  # функции для пожилых
            r'def.*notify.*family',  # уведомления семьи
            r'def.*get.*family',  # получение семейных данных
            r'def.*create.*family',  # создание семейных профилей
            r'def.*add.*family',  # добавление в семью
            r'def.*family.*contact',  # семейные контакты
            r'def.*family.*profile',  # семейные профили
            r'def.*family.*dashboard',  # семейные дашборды
            r'def.*family.*security',  # семейная безопасность
            r'def.*family.*analytics',  # семейная аналитика
            r'def.*family.*monitoring',  # семейный мониторинг
            r'def.*family.*tracking',  # семейное отслеживание
        ]
        
        personal_functions = []
        
        for py_file in self.project_root.rglob("*.py"):
            if "backup" in str(py_file) or "test" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in personal_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        personal_functions.append({
                            "file": str(py_file.relative_to(self.project_root)),
                            "function": match,
                            "pattern": pattern
                        })
                        
            except Exception as e:
                print(f"Ошибка чтения файла {py_file}: {e}")
        
        return personal_functions
    
    def disable_family_functions(self, file_path: str) -> bool:
        """Отключение семейных функций в файле"""
        try:
            file_full_path = self.project_root / file_path
            
            # Создание резервной копии
            backup_path = self.backup_dir / file_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_full_path, 'r', encoding='utf-8') as original:
                content = original.read()
            
            with open(backup_path, 'w', encoding='utf-8') as backup:
                backup.write(content)
            
            # Отключение функций
            disabled_content = self._disable_functions_in_content(content)
            
            with open(file_full_path, 'w', encoding='utf-8') as modified:
                modified.write(disabled_content)
            
            print(f"✅ Отключены семейные функции в: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отключения функций в {file_path}: {e}")
            return False
    
    def _disable_functions_in_content(self, content: str) -> str:
        """Отключение функций в содержимом файла"""
        # Паттерны для отключения
        disable_patterns = [
            (r'def (.*family.*)\(', r'def \1_disabled_anonymous_mode('),
            (r'def (.*personal.*)\(', r'def \1_disabled_anonymous_mode('),
            (r'def (.*child.*)\(', r'def \1_disabled_anonymous_mode('),
            (r'def (.*elderly.*)\(', r'def \1_disabled_anonymous_mode('),
            (r'def (.*notify.*family)', r'def \1_disabled_anonymous_mode'),
            (r'def (.*get.*family)', r'def \1_disabled_anonymous_mode'),
            (r'def (.*create.*family)', r'def \1_disabled_anonymous_mode'),
            (r'def (.*add.*family)', r'def \1_disabled_anonymous_mode'),
        ]
        
        modified_content = content
        
        for pattern, replacement in disable_patterns:
            modified_content = re.sub(
                pattern, 
                replacement, 
                modified_content, 
                flags=re.IGNORECASE
            )
        
        # Добавление комментария об отключении
        if "disabled_anonymous_mode" in modified_content:
            header_comment = '''"""
ВНИМАНИЕ: Этот файл был модифицирован для анонимного режима.
Семейные и персональные функции отключены для соответствия 152-ФЗ.
Для восстановления используйте резервную копию.
"""

'''
            modified_content = header_comment + modified_content
        
        return modified_content
    
    def create_anonymous_wrappers(self) -> bool:
        """Создание анонимных оберток для отключенных функций"""
        try:
            wrapper_file = self.project_root / "security" / "anonymous_function_wrappers.py"
            
            wrapper_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АНОНИМНЫЕ ОБЕРТКИ ДЛЯ ОТКЛЮЧЕННЫХ ФУНКЦИЙ
Заглушки для функций, отключенных в анонимном режиме
"""

from typing import Any, Dict, List, Optional
from core.base import SecurityBase


class AnonymousFunctionWrapper(SecurityBase):
    """Обертка для отключенных персональных функций"""
    
    def __init__(self, name: str = "AnonymousFunctionWrapper"):
        super().__init__(name)
        self.disabled_message = "Функция отключена в анонимном режиме для соответствия 152-ФЗ"
    
    def family_function_disabled(self, *args, **kwargs) -> Dict[str, Any]:
        """Заглушка для семейных функций"""
        return {
            "error": "disabled_anonymous_mode",
            "message": self.disabled_message,
            "suggestion": "Используйте анонимные образовательные функции",
            "alternative": "anonymous_family_adaptations.AnonymousFamilyManager"
        }
    
    def personal_function_disabled(self, *args, **kwargs) -> Dict[str, Any]:
        """Заглушка для персональных функций"""
        return {
            "error": "disabled_anonymous_mode", 
            "message": self.disabled_message,
            "suggestion": "Используйте общие рекомендации по безопасности",
            "alternative": "anonymous_family_adaptations.AnonymousThreatIntelligence"
        }
    
    def child_function_disabled(self, *args, **kwargs) -> Dict[str, Any]:
        """Заглушка для детских функций"""
        return {
            "error": "disabled_anonymous_mode",
            "message": self.disabled_message,
            "suggestion": "Используйте образовательный контент для детей",
            "alternative": "anonymous_family_adaptations.AnonymousFamilyManager"
        }
    
    def elderly_function_disabled(self, *args, **kwargs) -> Dict[str, Any]:
        """Заглушка для функций для пожилых"""
        return {
            "error": "disabled_anonymous_mode",
            "message": self.disabled_message,
            "suggestion": "Используйте образовательный контент для пожилых",
            "alternative": "anonymous_family_adaptations.AnonymousFamilyManager"
        }


# Глобальные заглушки для импорта
def family_function_disabled(*args, **kwargs):
    wrapper = AnonymousFunctionWrapper()
    return wrapper.family_function_disabled(*args, **kwargs)

def personal_function_disabled(*args, **kwargs):
    wrapper = AnonymousFunctionWrapper()
    return wrapper.personal_function_disabled(*args, **kwargs)

def child_function_disabled(*args, **kwargs):
    wrapper = AnonymousFunctionWrapper()
    return wrapper.child_function_disabled(*args, **kwargs)

def elderly_function_disabled(*args, **kwargs):
    wrapper = AnonymousFunctionWrapper()
    return wrapper.elderly_function_disabled(*args, **kwargs)
'''
            
            with open(wrapper_file, 'w', encoding='utf-8') as f:
                f.write(wrapper_content)
            
            print(f"✅ Создан файл анонимных оберток: {wrapper_file}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания анонимных оберток: {e}")
            return False
    
    def update_imports(self) -> bool:
        """Обновление импортов для использования анонимных функций"""
        try:
            # Файлы, которые нужно обновить
            files_to_update = [
                "security/safe_function_manager.py",
                "core/dashboard_manager.py",
                "scripts/quality_check_all.py"
            ]
            
            for file_path in files_to_update:
                full_path = self.project_root / file_path
                if full_path.exists():
                    self._update_file_imports(full_path)
            
            print("✅ Импорты обновлены для анонимного режима")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка обновления импортов: {e}")
            return False
    
    def _update_file_imports(self, file_path: Path) -> bool:
        """Обновление импортов в конкретном файле"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Замена импортов семейных функций на анонимные
            import_replacements = [
                (r'from security\.family\.family_profile_manager import', 
                 'from security.anonymous_family_adaptations import AnonymousFamilyManager as'),
                (r'from security\.family\.family_dashboard_manager import', 
                 'from security.anonymous_family_adaptations import AnonymousFamilyManager as'),
                (r'from security\.reactive\.threat_intelligence import', 
                 'from security.anonymous_family_adaptations import AnonymousThreatIntelligence as'),
            ]
            
            modified_content = content
            for pattern, replacement in import_replacements:
                modified_content = re.sub(pattern, replacement, modified_content)
            
            if modified_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                print(f"✅ Обновлены импорты в: {file_path.relative_to(self.project_root)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка обновления импортов в {file_path}: {e}")
            return False
    
    def run_disabling_process(self) -> bool:
        """Запуск процесса отключения персональных функций"""
        print("🔒 НАЧАЛО ОТКЛЮЧЕНИЯ ПЕРСОНАЛЬНЫХ ФУНКЦИЙ")
        print("=" * 50)
        
        # 1. Создание резервной копии
        if not self.create_backup():
            return False
        
        # 2. Поиск персональных функций
        print("\n🔍 Поиск персональных функций...")
        personal_functions = self.find_personal_functions()
        print(f"Найдено {len(personal_functions)} персональных функций")
        
        # 3. Отключение функций
        print("\n🚫 Отключение персональных функций...")
        disabled_count = 0
        for func_info in personal_functions:
            if self.disable_family_functions(func_info["file"]):
                disabled_count += 1
        
        print(f"✅ Отключено {disabled_count} функций")
        
        # 4. Создание анонимных оберток
        print("\n🔧 Создание анонимных оберток...")
        if self.create_anonymous_wrappers():
            print("✅ Анонимные обертки созданы")
        
        # 5. Обновление импортов
        print("\n📝 Обновление импортов...")
        if self.update_imports():
            print("✅ Импорты обновлены")
        
        print("\n🎉 ОТКЛЮЧЕНИЕ ПЕРСОНАЛЬНЫХ ФУНКЦИЙ ЗАВЕРШЕНО!")
        print("=" * 50)
        return True


def main():
    """Основная функция"""
    disabler = PersonalFunctionsDisabler()
    success = disabler.run_disabling_process()
    
    if success:
        print("\n✅ Все персональные функции успешно отключены!")
        print("🔒 Система готова к работе в анонимном режиме")
        print("📋 Резервные копии сохранены в backups/personal_functions_backup/")
    else:
        print("\n❌ Произошли ошибки при отключении функций")
        print("🔧 Проверьте логи и исправьте ошибки")


if __name__ == "__main__":
    main()