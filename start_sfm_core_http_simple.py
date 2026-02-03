#!/usr/bin/env python3
"""
ПРОСТАЯ ВЕРСИЯ SFM HTTP API - с прединициализацией
"""

import sys
import os
import json
from datetime import datetime
from aiohttp import web

# Backend path
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

security_path = "/opt/aladdin-backend/security"
if security_path not in sys.path:
    sys.path.insert(0, security_path)

print("Инициализация SFM...")

# Прединициализация SFM (делаем это один раз)
sfm = None
try:
    from security.safe_function_manager import SafeFunctionManager
    print("SafeFunctionManager импортирован, инициализация...")
    sfm = SafeFunctionManager()
    print(f"✅ SFM инициализирован с {len(sfm.functions)} функциями")
except Exception as e:
    print(f"❌ Ошибка инициализации SFM: {e}")
    sfm = None

async def execute_function(request):
    """Выполнить функцию через SFM"""
    try:
        data = await request.json()
        func_name = data.get('function', '')
        params = data.get('params', {})

        if not sfm:
            return web.json_response({
                'success': False,
                'error': 'SFM not initialized',
                'timestamp': datetime.utcnow().isoformat()
            }, status=500)

        if not func_name:
            return web.json_response({
                'success': False,
                'error': 'Function name required',
                'timestamp': datetime.utcnow().isoformat()
            }, status=400)

        # Проверяем, есть ли функция
        if func_name not in sfm.functions:
            # Пробуем найти похожие функции
            available = [f for f in sfm.functions.keys() if func_name.lower() in f.lower()]
            if available:
                func_name = available[0]
                print(f"Использую функцию: {func_name}")

        # Выполняем функцию
        result = sfm.execute_function(func_name, params)

        return web.json_response({
            'success': True,
            'result': result,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'real_sfm',
            'function': func_name
        })

    except Exception as e:
        return web.json_response({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, status=500)

async def health_check(request):
    """Health check"""
    return web.json_response({
        'status': 'healthy' if sfm else 'error',
        'service': 'sfm-http-api',
        'functions_count': len(sfm.functions) if sfm else 0,
        'timestamp': datetime.utcnow().isoformat()
    })

async def list_functions(request):
    """Список функций"""
    functions = list(sfm.functions.keys()) if sfm else []
    return web.json_response({
        'functions': functions,
        'count': len(functions),
        'timestamp': datetime.utcnow().isoformat()
    })

def create_app():
    """Создание приложения"""
    app = web.Application()
    app.router.add_post('/api/execute', execute_function)
    app.router.add_get('/api/health', health_check)
    app.router.add_get('/api/functions', list_functions)
    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Запуск SFM HTTP API на порту 8003")
    print(f"📊 SFM статус: {'✅ Готов' if sfm else '❌ Ошибка'}")
    if sfm:
        print(f"📊 Функций: {len(sfm.functions)}")

    web.run_app(app, host='127.0.0.1', port=8003)