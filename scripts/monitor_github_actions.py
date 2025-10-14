#!/usr/bin/env python3
"""
Мониторинг всех GitHub Actions workflow
Проверяет статус всех workflow в одном месте
"""

import requests
import json
import time
from datetime import datetime
import os

class GitHubActionsMonitor:
    def __init__(self, repo_owner="sergey234", repo_name="ALADDIN_FAMILY"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ALADDIN-Monitor"
        }
        
        # Попробуем получить токен из переменных окружения
        token = os.getenv("GITHUB_TOKEN")
        if token:
            self.headers["Authorization"] = f"token {token}"

    def get_workflow_runs(self, limit=10):
        """Получить последние запуски workflow"""
        try:
            url = f"{self.base_url}/actions/runs"
            params = {"per_page": limit}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"❌ Ошибка получения workflow runs: {e}")
            return None

    def get_workflow_jobs(self, run_id):
        """Получить jobs для конкретного workflow run"""
        try:
            url = f"{self.base_url}/actions/runs/{run_id}/jobs"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"❌ Ошибка получения jobs для run {run_id}: {e}")
            return None

    def get_workflow_logs(self, run_id, job_id):
        """Получить логи для конкретного job"""
        try:
            url = f"{self.base_url}/actions/jobs/{job_id}/logs"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.text
        except Exception as e:
            print(f"❌ Ошибка получения логов для job {job_id}: {e}")
            return None

    def format_status(self, status, conclusion):
        """Форматировать статус с эмодзи"""
        if conclusion == "success":
            return "✅ SUCCESS"
        elif conclusion == "failure":
            return "❌ FAILURE"
        elif conclusion == "cancelled":
            return "⏹️ CANCELLED"
        elif status == "in_progress":
            return "🔄 IN PROGRESS"
        elif status == "queued":
            return "⏳ QUEUED"
        else:
            return f"⚠️ {status.upper()}"

    def monitor_all_workflows(self):
        """Мониторить все workflow"""
        print("🚀 ALADDIN GITHUB ACTIONS MONITOR")
        print("=" * 60)
        print(f"📁 Repository: {self.repo_owner}/{self.repo_name}")
        print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Получить последние workflow runs
        runs_data = self.get_workflow_runs(20)
        if not runs_data:
            print("❌ Не удалось получить данные о workflow runs")
            return
        
        workflow_runs = runs_data.get("workflow_runs", [])
        
        if not workflow_runs:
            print("📭 Нет запущенных workflow")
            return
        
        print(f"📊 Найдено {len(workflow_runs)} последних запусков")
        print()
        
        # Группировать по workflow
        workflows = {}
        for run in workflow_runs:
            workflow_name = run.get("name", "Unknown")
            if workflow_name not in workflows:
                workflows[workflow_name] = []
            workflows[workflow_name].append(run)
        
        # Показать статус каждого workflow
        for workflow_name, runs in workflows.items():
            print(f"🔧 WORKFLOW: {workflow_name}")
            print("-" * 40)
            
            for run in runs[:3]:  # Показать последние 3 запуска
                run_id = run.get("id")
                status = run.get("status")
                conclusion = run.get("conclusion")
                created_at = run.get("created_at", "")
                head_sha = run.get("head_sha", "")[:8]
                html_url = run.get("html_url", "")
                
                status_emoji = self.format_status(status, conclusion)
                
                print(f"  {status_emoji} Run #{run_id}")
                print(f"     Commit: {head_sha}")
                print(f"     Time: {created_at}")
                print(f"     URL: {html_url}")
                
                # Получить детали jobs
                jobs_data = self.get_workflow_jobs(run_id)
                if jobs_data and "jobs" in jobs_data:
                    jobs = jobs_data["jobs"]
                    for job in jobs:
                        job_name = job.get("name", "Unknown Job")
                        job_status = job.get("status")
                        job_conclusion = job.get("conclusion")
                        job_status_emoji = self.format_status(job_status, job_conclusion)
                        
                        print(f"     └─ {job_status_emoji} {job_name}")
                        
                        # Если job упал, показать краткую ошибку
                        if job_conclusion == "failure":
                            print(f"        ⚠️ Job failed - check logs for details")
                
                print()
            
            print()
        
        # Показать общую статистику
        print("📈 ОБЩАЯ СТАТИСТИКА")
        print("-" * 40)
        
        total_runs = len(workflow_runs)
        success_runs = len([r for r in workflow_runs if r.get("conclusion") == "success"])
        failure_runs = len([r for r in workflow_runs if r.get("conclusion") == "failure"])
        in_progress_runs = len([r for r in workflow_runs if r.get("status") == "in_progress"])
        
        print(f"📊 Всего запусков: {total_runs}")
        print(f"✅ Успешных: {success_runs}")
        print(f"❌ Неудачных: {failure_runs}")
        print(f"🔄 В процессе: {in_progress_runs}")
        
        if total_runs > 0:
            success_rate = (success_runs / total_runs) * 100
            print(f"📈 Процент успеха: {success_rate:.1f}%")
        
        print("=" * 60)
        
        # Рекомендации
        if failure_runs > 0:
            print("🔧 РЕКОМЕНДАЦИИ:")
            print("1. Проверьте логи неудачных workflow")
            print("2. Убедитесь что все файлы на месте")
            print("3. Проверьте зависимости и конфигурацию")
        else:
            print("🎉 ВСЕ WORKFLOW РАБОТАЮТ ОТЛИЧНО!")

    def check_specific_workflow(self, workflow_name):
        """Проверить конкретный workflow"""
        print(f"🔍 ПРОВЕРКА WORKFLOW: {workflow_name}")
        print("=" * 50)
        
        runs_data = self.get_workflow_runs(50)
        if not runs_data:
            return
        
        workflow_runs = runs_data.get("workflow_runs", [])
        matching_runs = [r for r in workflow_runs if r.get("name") == workflow_name]
        
        if not matching_runs:
            print(f"❌ Workflow '{workflow_name}' не найден")
            return
        
        latest_run = matching_runs[0]
        run_id = latest_run.get("id")
        status = latest_run.get("status")
        conclusion = latest_run.get("conclusion")
        
        print(f"📊 Последний запуск: #{run_id}")
        print(f"📈 Статус: {self.format_status(status, conclusion)}")
        print(f"🕐 Время: {latest_run.get('created_at', 'Unknown')}")
        print(f"🔗 URL: {latest_run.get('html_url', 'N/A')}")
        
        # Получить детали jobs
        jobs_data = self.get_workflow_jobs(run_id)
        if jobs_data and "jobs" in jobs_data:
            jobs = jobs_data["jobs"]
            print(f"\n📋 JOBS ({len(jobs)}):")
            for job in jobs:
                job_name = job.get("name", "Unknown")
                job_status = job.get("status")
                job_conclusion = job.get("conclusion")
                job_status_emoji = self.format_status(job_status, job_conclusion)
                
                print(f"  {job_status_emoji} {job_name}")
                
                if job_conclusion == "failure":
                    print(f"     ⚠️ Ошибка в job - проверьте логи")

def main():
    monitor = GitHubActionsMonitor()
    
    # Автоматически запускаем полный мониторинг
    print("🚀 АВТОМАТИЧЕСКИЙ МОНИТОРИНГ GITHUB ACTIONS")
    print("=" * 60)
    
    # Сначала быстрая проверка
    print("🔍 БЫСТРАЯ ПРОВЕРКА СТАТУСА...")
    runs_data = monitor.get_workflow_runs(10)
    if runs_data:
        workflow_runs = runs_data.get("workflow_runs", [])
        print(f"📊 Найдено {len(workflow_runs)} последних запусков:")
        print()
        
        for run in workflow_runs[:5]:
            name = run.get("name", "Unknown")
            status = run.get("status")
            conclusion = run.get("conclusion")
            status_emoji = monitor.format_status(status, conclusion)
            created_at = run.get("created_at", "")[:19].replace("T", " ")
            head_sha = run.get("head_sha", "")[:8]
            print(f"  {status_emoji} {name} | {head_sha} | {created_at}")
        
        print()
    
    # Затем полный мониторинг
    print("📋 ПОЛНЫЙ МОНИТОРИНГ...")
    print()
    monitor.monitor_all_workflows()

if __name__ == "__main__":
    main()
