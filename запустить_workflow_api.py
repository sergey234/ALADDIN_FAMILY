#!/usr/bin/env python3
"""
Скрипт для запуска GitHub Actions workflow через API
"""
import os
import sys
import json
import urllib.request
import urllib.error

REPO = "sergey234/ALADDIN_FAMILY"
WORKFLOW_FILE = "appstore.yml"
BRANCH = "master"

def get_workflow_id(token):
    """Получить ID workflow по имени файла"""
    url = f"https://api.github.com/repos/{REPO}/actions/workflows"
    
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
            # Найти workflow по имени файла
            for workflow in data.get("workflows", []):
                if workflow.get("path", "").endswith(WORKFLOW_FILE):
                    return workflow.get("id")
            
            # Если не найден по пути, попробовать по имени
            for workflow in data.get("workflows", []):
                if "appstore" in workflow.get("name", "").lower():
                    return workflow.get("id")
            
            return None
    except urllib.error.HTTPError as e:
        print(f"❌ Ошибка при получении workflow ID: {e.code}")
        if e.code == 401:
            print("⚠️  Неверный токен доступа")
        return None

def trigger_workflow(token, workflow_id):
    """Запустить workflow"""
    url = f"https://api.github.com/repos/{REPO}/actions/workflows/{workflow_id}/dispatches"
    
    data = json.dumps({"ref": BRANCH}).encode()
    
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 204:
                return True
            else:
                print(f"⚠️  Неожиданный статус: {response.status}")
                return False
    except urllib.error.HTTPError as e:
        print(f"❌ Ошибка при запуске workflow: {e.code}")
        error_body = e.read().decode()
        print(f"Ответ: {error_body}")
        return False

def main():
    # Попробовать получить токен из переменной окружения
    token = os.environ.get("GITHUB_TOKEN")
    
    if not token:
        print("❌ GITHUB_TOKEN не установлен!")
        print("")
        print("Для запуска workflow нужен GitHub Personal Access Token.")
        print("")
        print("Инструкция:")
        print("1. Откройте: https://github.com/settings/tokens")
        print("2. Нажмите 'Generate new token (classic)'")
        print("3. Выберите права:")
        print("   - repo (полный доступ к репозиторию)")
        print("   - workflow (управление GitHub Actions)")
        print("4. Скопируйте токен")
        print("5. Запустите команду:")
        print("   export GITHUB_TOKEN=ваш_токен")
        print("   python3 запустить_workflow_api.py")
        print("")
        print("Или введите токен сейчас:")
        token = input("GitHub Token: ").strip()
        
        if not token:
            print("❌ Токен не введен. Выход.")
            sys.exit(1)
    
    print("🚀 Запуск workflow appstore.yml...")
    print("")
    
    # Получить workflow ID
    print("📋 Получение ID workflow...")
    workflow_id = get_workflow_id(token)
    
    if not workflow_id:
        print("❌ Не удалось найти workflow ID")
        print("Проверьте, что:")
        print(f"1. Workflow файл существует: .github/workflows/{WORKFLOW_FILE}")
        print("2. У вас есть доступ к репозиторию")
        print("3. Токен имеет права 'workflow'")
        sys.exit(1)
    
    print(f"✅ Workflow ID найден: {workflow_id}")
    print("")
    
    # Запустить workflow
    print("🚀 Запуск workflow...")
    if trigger_workflow(token, workflow_id):
        print("✅ Workflow успешно запущен!")
        print("")
        print("🔗 Проверьте статус:")
        print(f"https://github.com/{REPO}/actions")
        print("")
        print("Workflow: Build and Upload to App Store")
    else:
        print("❌ Не удалось запустить workflow")
        sys.exit(1)

if __name__ == "__main__":
    main()

