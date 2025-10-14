#!/usr/bin/env python3
"""
External APIs Server для ALADDIN Security System
REST API для интеграции с внешними сервисами
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import logging

# Импорт ExternalAPIManager
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from security.managers.external_api_manager import external_api_manager


class ExternalAPIServer:
    """Сервер для внешних API интеграций"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()
        self.logger = logging.getLogger("ExternalAPIServer")
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
    
    def setup_routes(self):
        """Настройка маршрутов API"""
        
        @self.app.route('/api/external/health', methods=['GET'])
        def health_check():
            """Проверка здоровья сервера"""
            return jsonify({
                "status": "ok",
                "service": "External APIs Server",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            })
        
        @self.app.route('/api/external/threat-intelligence', methods=['POST'])
        def check_threat_intelligence():
            """Проверка индикатора угрозы"""
            try:
                data = request.get_json()
                if not data or 'indicator' not in data:
                    return jsonify({
                        "success": False,
                        "error": "Missing required field: indicator"
                    }), 400
                
                indicator = data['indicator']
                indicator_type = data.get('type', 'ip')
                
                # Асинхронный вызов
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    external_api_manager.check_threat_intelligence(indicator, indicator_type)
                )
                loop.close()
                
                return jsonify({
                    "success": True,
                    "indicator": indicator,
                    "type": indicator_type,
                    "results": result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"Threat intelligence check error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/external/ip-geolocation', methods=['POST'])
        def get_ip_geolocation():
            """Получение геолокации IP"""
            try:
                data = request.get_json()
                if not data or 'ip' not in data:
                    return jsonify({
                        "success": False,
                        "error": "Missing required field: ip"
                    }), 400
                
                ip_address = data['ip']
                
                # Асинхронный вызов
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    external_api_manager.get_ip_geolocation(ip_address)
                )
                loop.close()
                
                return jsonify({
                    "success": True,
                    "ip": ip_address,
                    "results": result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"IP geolocation error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/external/email-validation', methods=['POST'])
        def validate_email():
            """Валидация email адреса"""
            try:
                data = request.get_json()
                if not data or 'email' not in data:
                    return jsonify({
                        "success": False,
                        "error": "Missing required field: email"
                    }), 400
                
                email_address = data['email']
                
                # Асинхронный вызов
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    external_api_manager.validate_email(email_address)
                )
                loop.close()
                
                return jsonify({
                    "success": True,
                    "email": email_address,
                    "results": result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"Email validation error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/external/statistics', methods=['GET'])
        def get_statistics():
            """Получение статистики использования API"""
            try:
                stats = external_api_manager.get_usage_statistics()
                return jsonify({
                    "success": True,
                    "statistics": stats,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Statistics error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/external/status', methods=['GET'])
        def get_api_status():
            """Получение статуса всех API"""
            try:
                status = external_api_manager.get_api_status()
                return jsonify({
                    "success": True,
                    "api_status": status,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"API status error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/external/clear-cache', methods=['POST'])
        def clear_cache():
            """Очистка кэша API"""
            try:
                external_api_manager.clear_cache()
                return jsonify({
                    "success": True,
                    "message": "Cache cleared successfully",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                self.logger.error(f"Clear cache error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/api/external/test-all', methods=['POST'])
        def test_all_apis():
            """Тестирование всех API"""
            try:
                test_data = request.get_json() or {}
                
                # Тестовые данные
                test_ip = test_data.get('ip', '8.8.8.8')
                test_email = test_data.get('email', 'test@example.com')
                test_indicator = test_data.get('indicator', '8.8.8.8')
                
                results = {}
                
                # Тест геолокации
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    geo_result = loop.run_until_complete(
                        external_api_manager.get_ip_geolocation(test_ip)
                    )
                    loop.close()
                    results['ip_geolocation'] = {
                        "success": True,
                        "data": geo_result
                    }
                except Exception as e:
                    results['ip_geolocation'] = {
                        "success": False,
                        "error": str(e)
                    }
                
                # Тест валидации email
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    email_result = loop.run_until_complete(
                        external_api_manager.validate_email(test_email)
                    )
                    loop.close()
                    results['email_validation'] = {
                        "success": True,
                        "data": email_result
                    }
                except Exception as e:
                    results['email_validation'] = {
                        "success": False,
                        "error": str(e)
                    }
                
                # Тест анализа угроз
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    threat_result = loop.run_until_complete(
                        external_api_manager.check_threat_intelligence(test_indicator)
                    )
                    loop.close()
                    results['threat_intelligence'] = {
                        "success": True,
                        "data": threat_result
                    }
                except Exception as e:
                    results['threat_intelligence'] = {
                        "success": False,
                        "error": str(e)
                    }
                
                return jsonify({
                    "success": True,
                    "test_results": results,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.error(f"Test all APIs error: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
    
    def run(self, host='0.0.0.0', port=5004, debug=False):
        """Запуск сервера"""
        print("🚀 Запуск External APIs Server...")
        print(f"📊 API будет доступно по адресу: http://localhost:{port}")
        print(f"🔧 Health check: http://localhost:{port}/api/external/health")
        print("🛑 Для остановки нажмите Ctrl+C")
        
        try:
            self.app.run(host=host, port=port, debug=debug, threaded=True)
        except KeyboardInterrupt:
            print("\n🛑 External APIs Server остановлен")
        except Exception as e:
            print(f"❌ Ошибка запуска сервера: {e}")


if __name__ == '__main__':
    server = ExternalAPIServer()
    server.run()