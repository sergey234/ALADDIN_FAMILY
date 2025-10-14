#!/usr/bin/env python3
"""
Анализ ошибок GitHub Actions
Определяет основные причины падения workflow
"""

import requests
import json
import re
from datetime import datetime

class GitHubFailureAnalyzer:
    def __init__(self, repo_owner="sergey234", repo_name="ALADDIN_FAMILY"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ALADDIN-Analyzer"
        }

    def analyze_common_failures(self):
        """Анализировать общие причины падения"""
        print("🔍 АНАЛИЗ ОШИБОК GITHUB ACTIONS")
        print("=" * 60)
        
        # Получить последние неудачные запуски
        url = f"{self.base_url}/actions/runs"
        params = {"status": "failure", "per_page": 10}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            runs_data = response.json()
        except Exception as e:
            print(f"❌ Ошибка получения данных: {e}")
            return
        
        workflow_runs = runs_data.get("workflow_runs", [])
        
        if not workflow_runs:
            print("📭 Нет неудачных запусков для анализа")
            return
        
        print(f"📊 Анализируем {len(workflow_runs)} неудачных запусков")
        print()
        
        # Анализ по типам ошибок
        error_patterns = {
            "xcodebuild": 0,
            "python": 0,
            "docker": 0,
            "flake8": 0,
            "import": 0,
            "permission": 0,
            "timeout": 0,
            "not_found": 0,
            "syntax": 0,
            "other": 0
        }
        
        workflow_errors = {}
        
        for run in workflow_runs:
            workflow_name = run.get("name", "Unknown")
            run_id = run.get("id")
            
            # Получить jobs для этого run
            jobs_url = f"{self.base_url}/actions/runs/{run_id}/jobs"
            try:
                jobs_response = requests.get(jobs_url, headers=self.headers)
                jobs_response.raise_for_status()
                jobs_data = jobs_response.json()
                
                if "jobs" in jobs_data:
                    for job in jobs_data["jobs"]:
                        if job.get("conclusion") == "failure":
                            job_name = job.get("name", "Unknown")
                            
                            # Анализировать логи job (если доступны)
                            logs_url = f"{self.base_url}/actions/jobs/{job['id']}/logs"
                            try:
                                logs_response = requests.get(logs_url, headers=self.headers)
                                if logs_response.status_code == 200:
                                    logs = logs_response.text
                                    
                                    # Определить тип ошибки
                                    error_type = self.classify_error(logs)
                                    error_patterns[error_type] += 1
                                    
                                    if workflow_name not in workflow_errors:
                                        workflow_errors[workflow_name] = []
                                    workflow_errors[workflow_name].append({
                                        "job": job_name,
                                        "error_type": error_type,
                                        "run_id": run_id
                                    })
                                    
                            except Exception as e:
                                print(f"⚠️ Не удалось получить логи для job {job['id']}: {e}")
                                
            except Exception as e:
                print(f"⚠️ Не удалось получить jobs для run {run_id}: {e}")
        
        # Показать результаты анализа
        print("📈 АНАЛИЗ ТИПОВ ОШИБОК:")
        print("-" * 40)
        
        for error_type, count in error_patterns.items():
            if count > 0:
                emoji = self.get_error_emoji(error_type)
                print(f"{emoji} {error_type.upper()}: {count} ошибок")
        
        print()
        
        # Анализ по workflow
        print("🔧 АНАЛИЗ ПО WORKFLOW:")
        print("-" * 40)
        
        for workflow_name, errors in workflow_errors.items():
            print(f"\n📋 {workflow_name}:")
            for error in errors:
                emoji = self.get_error_emoji(error["error_type"])
                print(f"  {emoji} {error['job']} - {error['error_type']}")
        
        print()
        
        # Рекомендации
        print("🔧 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ:")
        print("-" * 40)
        
        if error_patterns["xcodebuild"] > 0:
            print("🍎 iOS BUILD ПРОБЛЕМЫ:")
            print("  - Проверьте Xcode проект (.xcodeproj)")
            print("  - Убедитесь что все Swift файлы корректны")
            print("  - Проверьте Bundle Identifier и Signing")
        
        if error_patterns["python"] > 0:
            print("🐍 PYTHON ПРОБЛЕМЫ:")
            print("  - Проверьте requirements.txt")
            print("  - Убедитесь что все зависимости установлены")
            print("  - Проверьте версии Python")
        
        if error_patterns["flake8"] > 0:
            print("🔍 FLAKE8 ПРОБЛЕМЫ:")
            print("  - Исправьте синтаксические ошибки")
            print("  - Проверьте импорты")
            print("  - Запустите: python3 scripts/auto_format_all.py")
        
        if error_patterns["docker"] > 0:
            print("🐳 DOCKER ПРОБЛЕМЫ:")
            print("  - Проверьте Dockerfile")
            print("  - Убедитесь что все файлы на месте")
            print("  - Проверьте Docker контекст")
        
        if error_patterns["import"] > 0:
            print("📦 IMPORT ПРОБЛЕМЫ:")
            print("  - Проверьте все import statements")
            print("  - Убедитесь что модули существуют")
            print("  - Проверьте PYTHONPATH")
        
        print()
        print("=" * 60)

    def classify_error(self, logs):
        """Классифицировать тип ошибки по логам"""
        logs_lower = logs.lower()
        
        if "xcodebuild" in logs_lower or "xcode" in logs_lower:
            return "xcodebuild"
        elif "python" in logs_lower and ("error" in logs_lower or "failed" in logs_lower):
            return "python"
        elif "docker" in logs_lower and ("error" in logs_lower or "failed" in logs_lower):
            return "docker"
        elif "flake8" in logs_lower or "e999" in logs_lower or "f821" in logs_lower:
            return "flake8"
        elif "import" in logs_lower and ("error" in logs_lower or "failed" in logs_lower):
            return "import"
        elif "permission" in logs_lower or "denied" in logs_lower:
            return "permission"
        elif "timeout" in logs_lower or "timed out" in logs_lower:
            return "timeout"
        elif "not found" in logs_lower or "no such file" in logs_lower:
            return "not_found"
        elif "syntax" in logs_lower or "invalid" in logs_lower:
            return "syntax"
        else:
            return "other"

    def get_error_emoji(self, error_type):
        """Получить эмодзи для типа ошибки"""
        emojis = {
            "xcodebuild": "🍎",
            "python": "🐍",
            "docker": "🐳",
            "flake8": "🔍",
            "import": "📦",
            "permission": "🔒",
            "timeout": "⏰",
            "not_found": "❓",
            "syntax": "📝",
            "other": "⚠️"
        }
        return emojis.get(error_type, "❓")

    def suggest_fixes(self):
        """Предложить конкретные исправления"""
        print("🛠️ КОНКРЕТНЫЕ ИСПРАВЛЕНИЯ:")
        print("=" * 60)
        
        print("1. 🍎 iOS BUILD:")
        print("   - Проверить: mobile_apps/ALADDIN_iOS/ALADDIN.xcodeproj")
        print("   - Исправить: Bundle Identifier, Signing, Frameworks")
        print("   - Команда: cd mobile_apps/ALADDIN_iOS && xcodebuild -list")
        
        print("\n2. 🔍 QUALITY CHECK:")
        print("   - Запустить: python3 scripts/auto_format_all.py")
        print("   - Проверить: quality_report.txt создается")
        print("   - Исправить: flake8 ошибки в Python файлах")
        
        print("\n3. 🐳 DOCKER BUILD:")
        print("   - Проверить: Dockerfile в корне проекта")
        print("   - Убедиться: все файлы в .dockerignore")
        print("   - Тест: docker build .")
        
        print("\n4. 📦 PYTHON DEPENDENCIES:")
        print("   - Обновить: requirements.txt")
        print("   - Установить: pip install -r requirements.txt")
        print("   - Проверить: python3 -c 'import sys; print(sys.version)'")
        
        print("\n5. 🔧 ОБЩИЕ ИСПРАВЛЕНИЯ:")
        print("   - Проверить: .gitignore исключает ненужные файлы")
        print("   - Убедиться: все файлы закоммичены")
        print("   - Тест: git status --porcelain")

def main():
    analyzer = GitHubFailureAnalyzer()
    
    print("🚀 АНАЛИЗ ОШИБОК GITHUB ACTIONS")
    print("=" * 60)
    print(f"📁 Repository: {analyzer.repo_owner}/{analyzer.repo_name}")
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    analyzer.analyze_common_failures()
    analyzer.suggest_fixes()

if __name__ == "__main__":
    main()
