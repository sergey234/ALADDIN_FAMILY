#!/usr/bin/env python3
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('149.154.65.180', username='root', password='Sergio675')

print('🔧 Удаление битого комментария...')

# Удалим битый комментарий
stdin, stdout, stderr = ssh.exec_command('cd /opt/aladdin-backend && sed -i "186d" api_gateway.py')

print('✅ Комментарий удален')

ssh.close()