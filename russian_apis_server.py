#!/usr/bin/env python3
"""
REST API Server для российских API
Яндекс Карты, ГЛОНАСС и другие российские сервисы
"""

import asyncio
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from security.russian_api_manager import russian_api_manager, RussianAPIType, GeocodingResult, RoutingResult
from core.logging_module import LoggingManager

app = Flask(__name__)
CORS(app)
logger = LoggingManager(name="RussianAPIsServer")


@app.route('/api/russian/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервера российских API"""
    logger.log("INFO", "Health check запрошен для Russian APIs Server")
    
    try:
        status = russian_api_manager.get_status()
        return jsonify({
            "status": "ok",
            "timestamp": asyncio.get_event_loop().time(),
            "manager_status": status
        }), 200
    except Exception as e:
        logger.log("ERROR", f"Ошибка health check: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route('/api/russian/geocode', methods=['POST'])
def geocode_address():
    """Геокодирование адреса в координаты"""
    try:
        data = request.get_json()
        address = data.get('address')
        api_type_str = data.get('api_type', 'yandex_geocoder')
        
        if not address:
            logger.log("WARNING", "Запрос геокодирования без адреса")
            return jsonify({"error": "Отсутствует параметр 'address'"}), 400
        
        # Преобразуем строку в enum
        try:
            api_type = RussianAPIType(api_type_str)
        except ValueError:
            api_type = RussianAPIType.YANDEX_GEOCODER
        
        logger.log("INFO", f"Геокодирование адреса: {address} через {api_type.value}")
        
        # Выполняем геокодирование асинхронно
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                russian_api_manager.geocode_address(address, api_type)
            )
            
            response_data = {
                "success": True,
                "address": result.address,
                "coordinates": result.coordinates,
                "country": result.country,
                "city": result.city,
                "region": result.region,
                "precision": result.precision,
                "api_source": result.api_source
            }
            
            logger.log("INFO", f"Геокодирование успешно: {address} -> {result.coordinates}")
            return jsonify(response_data), 200
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.log("ERROR", f"Ошибка геокодирования: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "address": address if 'address' in locals() else None
        }), 500


@app.route('/api/russian/route', methods=['POST'])
def build_route():
    """Построение маршрута между точками"""
    try:
        data = request.get_json()
        from_point = data.get('from_point')
        to_point = data.get('to_point')
        route_type = data.get('route_type', 'auto')
        api_type_str = data.get('api_type', 'yandex_routing')
        
        if not from_point or not to_point:
            logger.log("WARNING", "Запрос маршрута без точек")
            return jsonify({"error": "Отсутствуют параметры 'from_point' или 'to_point'"}), 400
        
        # Преобразуем строку в enum
        try:
            api_type = RussianAPIType(api_type_str)
        except ValueError:
            api_type = RussianAPIType.YANDEX_ROUTING
        
        logger.log("INFO", f"Построение маршрута: {from_point} -> {to_point} через {api_type.value}")
        
        # Выполняем построение маршрута асинхронно
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                russian_api_manager.build_route(from_point, to_point, route_type, api_type)
            )
            
            response_data = {
                "success": True,
                "from_point": result.from_point,
                "to_point": result.to_point,
                "distance": result.distance,
                "duration": result.duration,
                "route_type": result.route_type,
                "api_source": result.api_source
            }
            
            logger.log(f"Маршрут построен: {result.distance}m, {result.duration}s")
            return jsonify(response_data), 200
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.log("ERROR", f"Ошибка построения маршрута: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "from_point": from_point if 'from_point' in locals() else None,
            "to_point": to_point if 'to_point' in locals() else None
        }), 500


@app.route('/api/russian/glonass', methods=['POST'])
def get_glonass_coordinates():
    """Получение координат через ГЛОНАСС"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        
        if not device_id:
            logger.log("WARNING", "Запрос ГЛОНАСС без device_id")
            return jsonify({"error": "Отсутствует параметр 'device_id'"}), 400
        
        logger.log("INFO", f"Получение ГЛОНАСС координат для устройства: {device_id}")
        
        # Выполняем запрос ГЛОНАСС асинхронно
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            coordinates = loop.run_until_complete(
                russian_api_manager.get_glonass_coordinates(device_id)
            )
            
            if coordinates:
                response_data = {
                    "success": True,
                    "device_id": device_id,
                    "coordinates": coordinates,
                    "latitude": coordinates[0],
                    "longitude": coordinates[1],
                    "api_source": "ГЛОНАСС"
                }
                
                logger.log("INFO", f"ГЛОНАСС координаты получены: {coordinates}")
                return jsonify(response_data), 200
            else:
                return jsonify({
                    "success": False,
                    "error": "Координаты не найдены",
                    "device_id": device_id
                }), 404
                
        finally:
            loop.close()
            
    except Exception as e:
        logger.log("ERROR", f"Ошибка получения ГЛОНАСС координат: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "device_id": device_id if 'device_id' in locals() else None
        }), 500


@app.route('/api/russian/statistics', methods=['GET'])
def get_statistics():
    """Получение статистики использования российских API"""
    logger.log("INFO", "Запрос статистики российских API")
    
    try:
        stats = russian_api_manager.get_usage_statistics()
        return jsonify({
            "success": True,
            "statistics": stats,
            "timestamp": asyncio.get_event_loop().time()
        }), 200
    except Exception as e:
        logger.log("ERROR", f"Ошибка получения статистики: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/russian/status', methods=['GET'])
def get_api_status():
    """Получение статуса всех российских API"""
    logger.log("INFO", "Запрос статуса российских API")
    
    try:
        status = russian_api_manager.get_status()
        return jsonify({
            "success": True,
            "status": status,
            "timestamp": asyncio.get_event_loop().time()
        }), 200
    except Exception as e:
        logger.log("ERROR", f"Ошибка получения статуса: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/russian/clear-cache', methods=['POST'])
def clear_cache():
    """Очистка кэша российских API"""
    logger.log("INFO", "Очистка кэша российских API")
    
    try:
        russian_api_manager.clear_cache()
        return jsonify({
            "success": True,
            "message": "Кэш очищен",
            "timestamp": asyncio.get_event_loop().time()
        }), 200
    except Exception as e:
        logger.log("ERROR", f"Ошибка очистки кэша: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/russian/test-all', methods=['POST'])
def test_all_apis():
    """Тестирование всех российских API"""
    logger.log("INFO", "Тестирование всех российских API")
    
    try:
        test_results = {}
        
        # Тест геокодирования
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            geocode_result = loop.run_until_complete(
                russian_api_manager.geocode_address("Москва, Красная площадь")
            )
            test_results["geocoding"] = {
                "success": True,
                "result": geocode_result.__dict__
            }
            loop.close()
        except Exception as e:
            test_results["geocoding"] = {
                "success": False,
                "error": str(e)
            }
        
        # Тест маршрутизации
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            route_result = loop.run_until_complete(
                russian_api_manager.build_route("Москва", "Санкт-Петербург")
            )
            test_results["routing"] = {
                "success": True,
                "result": route_result.__dict__
            }
            loop.close()
        except Exception as e:
            test_results["routing"] = {
                "success": False,
                "error": str(e)
            }
        
        # Тест ГЛОНАСС
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            glonass_result = loop.run_until_complete(
                russian_api_manager.get_glonass_coordinates("test_device")
            )
            test_results["glonass"] = {
                "success": True,
                "coordinates": glonass_result
            }
            loop.close()
        except Exception as e:
            test_results["glonass"] = {
                "success": False,
                "error": str(e)
            }
        
        return jsonify({
            "success": True,
            "test_results": test_results,
            "timestamp": asyncio.get_event_loop().time()
        }), 200
        
    except Exception as e:
        logger.log("ERROR", f"Ошибка тестирования API: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    print("🚀 Запуск Russian APIs Server...")
    print("📊 API будет доступно по адресу: http://localhost:5005")
    print("🔧 Health check: http://localhost:5005/api/russian/health")
    print("🛑 Для остановки нажмите Ctrl+C")
    
    try:
        app.run(host='0.0.0.0', port=5005, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.log("CRITICAL", "\n🛑 Russian APIs Server остановлен")
    except Exception as e:
        logger.log("INFO", f"❌ Ошибка запуска Russian APIs Server: {e}")