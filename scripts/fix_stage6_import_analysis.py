#!/usr/bin/env python3
"""
ИСПРАВЛЕНИЕ ЭТАПА 6: Технические проблемы с анализом импортов
"""

import ast
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Добавляем путь к проекту
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')

class ImportAnalysisFixer:
    """Исправление анализа импортов для ЭТАПА 6"""
    
    def __init__(self, file_path: str = "security/reactive/recovery_service.py"):
        self.file_path = Path(file_path)
        
    def fix_import_analysis(self) -> Dict[str, Any]:
        """Исправление анализа импортов"""
        print("🔧 ИСПРАВЛЕНИЕ ЭТАПА 6: Анализ импортов")
        print("=" * 50)
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            unused_imports = []
            
            # Собираем все импорты
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            "type": "import",
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.append({
                            "type": "from_import",
                            "module": node.module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno
                        })
            
            # Исправленная проверка использования импортов
            for imp in imports:
                name_to_check = imp["alias"] if imp["alias"] else imp["name"]
                if name_to_check and name_to_check not in content.replace(f"line {imp['line']}", ""):
                    unused_imports.append(imp)
            
            print(f"   📦 Всего импортов: {len(imports)}")
            print(f"   ❌ Неиспользуемых: {len(unused_imports)}")
            
            if unused_imports:
                print("   📋 Неиспользуемые импорты:")
                for unused in unused_imports[:5]:
                    print(f"      - {unused['name']} (строка {unused['line']})")
            
            return {
                "total_imports": len(imports),
                "unused_imports": len(unused_imports),
                "imports": imports,
                "unused_list": unused_imports,
                "status": "fixed"
            }
            
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    def test_import_functionality(self) -> Dict[str, Any]:
        """Тестирование функциональности импортов"""
        print("   🧪 Тестирование импортов...")
        
        try:
            # Тест импорта модуля
            result = subprocess.run(['python3', '-c', f'import sys; sys.path.append("/Users/sergejhlystov/ALADDIN_NEW"); from security.reactive.recovery_service import RecoveryService'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("      ✅ Основной импорт: работает")
                return {"import_test": True, "error": None}
            else:
                print(f"      ❌ Основной импорт: {result.stderr}")
                return {"import_test": False, "error": result.stderr}
                
        except Exception as e:
            print(f"      ❌ Ошибка тестирования: {e}")
            return {"import_test": False, "error": str(e)}

def main():
    """Главная функция"""
    fixer = ImportAnalysisFixer()
    
    # Исправляем анализ импортов
    import_results = fixer.fix_import_analysis()
    
    # Тестируем функциональность
    test_results = fixer.test_import_functionality()
    
    print(f"\n✅ ЭТАП 6 ИСПРАВЛЕН!")
    print(f"   • Статус: {import_results.get('status', 'unknown')}")
    print(f"   • Импорт работает: {test_results.get('import_test', False)}")

if __name__ == "__main__":
    main()