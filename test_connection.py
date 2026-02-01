#!/usr/bin/env python3
"""
Быстрая проверка подключения к серверу
"""
import socket
import sys

SERVER = "149.154.65.180"
PORT = 22

print("🔍 Проверка подключения к серверу...")
print(f"Сервер: {SERVER}:{PORT}")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex((SERVER, PORT))
    sock.close()
    
    if result == 0:
        print(f"✅ Сервер {SERVER}:{PORT} ДОСТУПЕН!")
        sys.exit(0)
    else:
        print(f"❌ Сервер недоступен (код: {result})")
        sys.exit(1)
except Exception as e:
    print(f"❌ Ошибка: {e}")
    sys.exit(1)



