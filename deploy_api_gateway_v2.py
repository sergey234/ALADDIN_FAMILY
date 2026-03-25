#!/usr/bin/env python3
import paramiko
import os

def run_command(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode('utf-8').strip()

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ✅ Security: never hardcode secrets in repo. Use SSH key or env var for password.
    host = os.environ.get("ALADDIN_SSH_HOST", "149.154.65.180")
    username = os.environ.get("ALADDIN_SSH_USER", "root")
    password = os.environ.get("ALADDIN_SSH_PASSWORD")  # optional; prefer SSH keys/agent
    ssh.connect(host, username=username, password=password)

    print('🚀 РАЗВЕРТЫВАНИЕ API GATEWAY (STAGE 2)')

    # 1. Загружаем файлы на сервер
    routers = [
        'gamification_router.py',
        'subscription_sync_router.py',
        'parental_control_sync_router.py',
        'user_profile_sync_router.py',
        'app_settings_sync_router.py',
        'other_functions_sync_router.py',
        'offline_storage_sync_router.py',
        'crash_detection_sync_router.py',
        'elderly_interface_sync_router.py',
        'subscription_router.py',
        'crash_detection_router.py',
        'components_router.py',
        'system_router.py',
        'metrics_router.py',
        'crash_detection_router_optimized.py'
    ]

    for filename in routers:
        if os.path.exists(filename):
            print(f'📤 Загрузка {filename} в security/api/routers/...')
            with open(filename, 'r') as f:
                content = f.read()
            
            create_cmd = f"cd /opt/aladdin-backend/security/api/routers && cat > {filename} << 'EOF'\n{content}\nEOF"
            run_command(ssh, create_cmd)
            print(f'✅ {filename} загружен')

    # Загружаем основные файлы
    main_files = ['main.py', 'sfm_adapter.py']
    for filename in main_files:
        if os.path.exists(filename):
            print(f'📤 Загрузка {filename} в корень...')
            with open(filename, 'r') as f:
                content = f.read()
            create_cmd = f"cd /opt/aladdin-backend && cat > {filename} << 'EOF'\n{content}\nEOF"
            run_command(ssh, create_cmd)
            print(f'✅ {filename} загружен')

    # 2. Перезапуск сервиса API Gateway
    print('\n🔄 Очистка порта 8002 и перезапуск сервиса...')
    run_command(ssh, "netstat -nlp | grep :8002 | awk '{print $7}' | cut -d'/' -f1 | xargs kill -9 || true")
    run_command(ssh, "fuser -k 8002/tcp || true")
    run_command(ssh, 'systemctl stop aladdin-api-gateway || true')
    run_command(ssh, 'sleep 2')
    run_command(ssh, 'systemctl start aladdin-api-gateway')

    print('\n🔍 Проверка статуса...')
    health_check = run_command(ssh, 'curl -s http://127.0.0.1:8002/api/health')
    print(f'Health check (port 8002): {health_check}')

    ssh.close()
    print('\n🎯 ДЕПЛОЙ ЗАВЕРШЕН!')

if __name__ == '__main__':
    main()
