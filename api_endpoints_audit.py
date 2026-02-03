#!/usr/bin/env python3
"""
🚀 ALADDIN API ENDPOINTS AUDIT SCRIPT
Аудит и подсчет всех API эндпоинтов в системе

Цель: Найти расхождение между заявленными 105 и текущими 96 эндпоинтами
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set

class APIEndpointsAuditor:
    """Аудитор API эндпоинтов"""

    def __init__(self):
        self.api_files = [
            "api_gateway_complete.py",
            "api_gateway_final.py",
            "api_gateway_production_final.py",
            "api_config_lockdown_system.py"
        ]

    def extract_endpoints_from_fastapi_file(self, filepath: str) -> List[Dict]:
        """Извлечение эндпоинтов из FastAPI файла"""
        endpoints = []

        if not os.path.exists(filepath):
            return endpoints

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Регулярное выражение для поиска FastAPI декораторов
            pattern = r'@app\.(get|post|put|delete)\s*\(\s*["\']([^"\']+)["\']\s*\)'
            matches = re.findall(pattern, content)

            for method, path in matches:
                # Очистка пути от параметров
                clean_path = re.sub(r'\{[^}]+\}', '{}', path)
                endpoints.append({
                    'method': method.upper(),
                    'path': clean_path,
                    'full_path': path,
                    'file': filepath
                })

        except Exception as e:
            print(f"Ошибка чтения {filepath}: {e}")

        return endpoints

    def extract_endpoints_from_lockdown_config(self, filepath: str) -> List[Dict]:
        """Извлечение эндпоинтов из конфигурации блокировки"""
        endpoints = []

        if not os.path.exists(filepath):
            return endpoints

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Найдем API_ENDPOINTS_CONFIG
            config_match = re.search(r'API_ENDPOINTS_CONFIG\s*=\s*\{(.*?)\}', content, re.DOTALL)
            if config_match:
                config_content = config_match.group(1)

                # Извлечем все эндпоинты из конфигурации
                endpoint_pattern = r'\{\s*"method":\s*"([^"]+)",\s*"path":\s*"([^"]+)"'
                matches = re.findall(endpoint_pattern, config_content)

                for method, path in matches:
                    endpoints.append({
                        'method': method,
                        'path': path,
                        'file': filepath,
                        'source': 'lockdown_config'
                    })

        except Exception as e:
            print(f"Ошибка чтения {filepath}: {e}")

        return endpoints

    def analyze_all_endpoints(self) -> Dict:
        """Анализ всех эндпоинтов в системе"""
        analysis = {
            'files_analysis': {},
            'unique_endpoints': set(),
            'duplicates': [],
            'missing_from_lockdown': [],
            'summary': {}
        }

        # Анализ каждого файла
        for filepath in self.api_files:
            if filepath.endswith('_lockdown_system.py'):
                endpoints = self.extract_endpoints_from_lockdown_config(filepath)
            else:
                endpoints = self.extract_endpoints_from_fastapi_file(filepath)

            analysis['files_analysis'][filepath] = {
                'endpoints': endpoints,
                'count': len(endpoints),
                'exists': os.path.exists(filepath)
            }

            # Добавляем в уникальные
            for ep in endpoints:
                key = f"{ep['method']} {ep['path']}"
                if key in analysis['unique_endpoints']:
                    analysis['duplicates'].append(key)
                analysis['unique_endpoints'].add(key)

        # Находим эндпоинты, отсутствующие в lockdown
        lockdown_eps = set()
        if 'api_config_lockdown_system.py' in analysis['files_analysis']:
            for ep in analysis['files_analysis']['api_config_lockdown_system.py']['endpoints']:
                lockdown_eps.add(f"{ep['method']} {ep['path']}")

        # Проверяем другие файлы
        for filename, data in analysis['files_analysis'].items():
            if filename != 'api_config_lockdown_system.py':
                for ep in data['endpoints']:
                    key = f"{ep['method']} {ep['path']}"
                    if key not in lockdown_eps:
                        analysis['missing_from_lockdown'].append({
                            'endpoint': key,
                            'file': filename
                        })

        # Сводка
        analysis['summary'] = {
            'total_unique_endpoints': len(analysis['unique_endpoints']),
            'total_duplicates': len(analysis['duplicates']),
            'files_analyzed': len(analysis['files_analysis']),
            'lockdown_endpoints': len(lockdown_eps),
            'missing_from_lockdown_count': len(analysis['missing_from_lockdown']),
            'documented_105_vs_actual': {
                'documented': 105,
                'lockdown_config': len(lockdown_eps),
                'max_in_files': max([data['count'] for data in analysis['files_analysis'].values()] or [0]),
                'difference': 105 - len(lockdown_eps)
            }
        }

        return analysis

    def print_analysis_report(self, analysis: Dict):
        """Печать отчета анализа"""
        print("🚀 ALADDIN API ENDPOINTS AUDIT REPORT")
        print("=" * 60)
        print()

        print("📊 АНАЛИЗ ФАЙЛОВ:")
        for filename, data in analysis['files_analysis'].items():
            status = "✅" if data['exists'] else "❌"
            print(f"  {status} {filename}: {data['count']} эндпоинтов")

        print()
        print("📈 СТАТИСТИКА:")
        summary = analysis['summary']
        print(f"  Уникальных эндпоинтов: {summary['total_unique_endpoints']}")
        print(f"  Дублированных: {summary['total_duplicates']}")
        print(f"  В lockdown конфиге: {summary['lockdown_endpoints']}")
        print(f"  Отсутствует в lockdown: {summary['missing_from_lockdown_count']}")

        print()
        print("🎯 СРАВНЕНИЕ С ДОКУМЕНТАЦИЕЙ:")
        doc_stats = summary['documented_105_vs_actual']
        print(f"  Задокументировано: {doc_stats['documented']} эндпоинтов")
        print(f"  В lockdown конфиге: {doc_stats['lockdown_config']} эндпоинтов")
        print(f"  Максимум в файлах: {doc_stats['max_in_files']} эндпоинтов")
        print(f"  Разница: {doc_stats['difference']} эндпоинтов")

        if analysis['duplicates']:
            print()
            print("⚠️  ДУБЛИРОВАННЫЕ ЭНДПОИНТЫ:")
            for dup in analysis['duplicates'][:10]:  # Показываем первые 10
                print(f"  - {dup}")
            if len(analysis['duplicates']) > 10:
                print(f"  ... и еще {len(analysis['duplicates']) - 10}")

        if analysis['missing_from_lockdown']:
            print()
            print("🔍 ЭНДПОИНТЫ, ОТСУТСТВУЮЩИЕ В LOCKDOWN:")
            for missing in analysis['missing_from_lockdown'][:15]:  # Показываем первые 15
                print(f"  - {missing['endpoint']} (в {missing['file']})")
            if len(analysis['missing_from_lockdown']) > 15:
                print(f"  ... и еще {len(analysis['missing_from_lockdown']) - 15}")

        print()
        print("🎯 ВЫВОДЫ:")
        if doc_stats['difference'] > 0:
            print(f"  ❌ Обнаружено расхождение: {doc_stats['difference']} эндпоинтов меньше заявленных")
            print("  🔧 Рекомендуется обновить lockdown конфигурацию")
        else:
            print("  ✅ Конфигурация соответствует документации")

def main():
    """Основная функция аудита"""
    auditor = APIEndpointsAuditor()
    analysis = auditor.analyze_all_endpoints()
    auditor.print_analysis_report(analysis)

    # Сохранение детального отчета
    import json
    report_file = "api_endpoints_audit_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Детальный отчет сохранен: {report_file}")

if __name__ == "__main__":
    main()