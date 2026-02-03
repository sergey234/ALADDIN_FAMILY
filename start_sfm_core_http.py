#!/usr/bin/env python3
"""
SFM HTTP API SERVICE - HTTP интерфейс для SafeFunctionManager
Предоставляет REST API для выполнения SFM функций
"""

import sys
import os
import asyncio
from datetime import datetime
from aiohttp import web
from aiohttp import ClientTimeout

# Backend path for SFM imports
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Add security module path
security_path = "/opt/aladdin-backend/security"
if security_path not in sys.path:
    sys.path.insert(0, security_path)

# Initialize SFM
try:
    from security.safe_function_manager import SafeFunctionManager
    sfm = SafeFunctionManager()
    print(f"✅ SFM HTTP Service initialized with {len(sfm.functions)} functions")
except Exception as e:
    print(f"❌ Failed to initialize SFM: {e}")
    sys.exit(1)

async def execute_function(request):
    """
    Execute SFM function via HTTP API
    POST /api/execute
    Body: {"function": "function_name", "params": {...}}
    """
    try:
        # Parse request
        data = await request.json()
        func_name = data.get('function')
        params = data.get('params', {})

        if not func_name:
            return web.json_response({
                'success': False,
                'error': 'Function name is required',
                'timestamp': datetime.utcnow().isoformat()
            }, status=400)

        print(f"🔧 Executing SFM function: {func_name}")

        # Execute function
        result = sfm.execute_function(func_name, params)

        print(f"✅ SFM execution successful for: {func_name}")

        # Return success response
        return web.json_response({
            'success': True,
            'result': result,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'real_sfm',
            'function': func_name
        })

    except Exception as e:
        error_msg = f"SFM execution failed: {str(e)}"
        print(f"❌ {error_msg}")

        return web.json_response({
            'success': False,
            'error': error_msg,
            'timestamp': datetime.utcnow().isoformat()
        }, status=500)

async def health_check(request):
    """
    Health check endpoint
    GET /api/health
    """
    return web.json_response({
        'status': 'healthy',
        'service': 'sfm-http-api',
        'functions_count': len(sfm.functions),
        'timestamp': datetime.utcnow().isoformat()
    })

async def list_functions(request):
    """
    List all available SFM functions
    GET /api/functions
    """
    functions_list = list(sfm.functions.keys())
    return web.json_response({
        'functions': functions_list,
        'count': len(functions_list),
        'timestamp': datetime.utcnow().isoformat()
    })

def create_app():
    """Create aiohttp application"""
    app = web.Application()

    # Routes
    app.router.add_post('/api/execute', execute_function)
    app.router.add_get('/api/health', health_check)
    app.router.add_get('/api/functions', list_functions)

    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting SFM HTTP API Service on port 8003")
    print("📋 Available endpoints:")
    print("  POST /api/execute - Execute SFM function")
    print("  GET  /api/health  - Health check")
    print("  GET  /api/functions - List functions")
    print("")

    # Start server
    web.run_app(app, host='127.0.0.1', port=8003)