#!/usr/bin/env python3
"""
ПРОСТАЯ ПРОВЕРКА СТАТУСА
"""

import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('149.154.65.180', username='root', password='Sergio675')

# Проверяем статус
stdin, stdout, stderr = ssh.exec_command('systemctl status aladdin-main-api-gateway --no-pager | head -3')
status = stdout.read().decode('utf-8').strip()
print('Status:', status)

# Проверяем API
stdin, stdout, stderr = ssh.exec_command('curl -s http://127.0.0.1:8002/api/health')
health = stdout.read().decode('utf-8').strip()
print('Health:', health)

ssh.close()