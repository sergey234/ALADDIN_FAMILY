#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Endpoints для Dark Web Monitoring Agent

Этот модуль содержит Flask endpoints для интеграции Dark Web Monitoring
с мобильным приложением iOS.

Использование:
    В main.py добавить:
    from security.api.dark_web_monitoring_endpoints import dark_web_bp
    app.register_blueprint(dark_web_bp, url_prefix='/api/darkweb')

Дата создания: 9 декабря 2025
Версия: 1.0.0
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging
from typing import Optional
from datetime import datetime

# Импорты (будут доступны на сервере)
try:
    from security.ai_agents.dark_web_monitoring_agent import DarkWebMonitoringAgent
except ImportError:
    DarkWebMonitoringAgent = None

logger = logging.getLogger(__name__)

# Создаем Blueprint для dark web monitoring
dark_web_bp = Blueprint('dark_web_monitoring', __name__)

# Глобальный экземпляр агента (инициализируется при первом запросе)
_agent_instance: Optional[DarkWebMonitoringAgent] = None


def get_agent() -> DarkWebMonitoringAgent:
    """
    Получение экземпляра агента (singleton)
    
    Returns:
        Экземпляр DarkWebMonitoringAgent
    """
    global _agent_instance
    if _agent_instance is None:
        config = {
            "hibp_api_key": "",  # Должен быть установлен через переменные окружения
            "breachdirectory_api_key": "",  # Опционально
            "cache_ttl": 86400,  # 24 часа
            "monitoring_interval": 24
        }
        _agent_instance = DarkWebMonitoringAgent(config)
        logger.info("✅ DarkWebMonitoringAgent инициализирован")
    return _agent_instance


def require_auth(f):
    """
    Декоратор для проверки аутентификации
    
    Args:
        f: Функция для обертывания
        
    Returns:
        Обернутая функция с проверкой auth
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Реализовать проверку токена авторизации
        auth_token = request.headers.get('Authorization')
        if not auth_token:
            return jsonify({"error": "Authorization required"}), 401
        # Здесь можно добавить проверку токена через JWT или другой метод
        return f(*args, **kwargs)
    return decorated_function


def validate_email(email: str) -> bool:
    """
    Валидация email адреса
    
    Args:
        email: Email для валидации
        
    Returns:
        True если email валиден
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Валидация номера телефона
    
    Args:
        phone: Телефон для валидации
        
    Returns:
        True если телефон валиден
    """
    import re
    digits_only = re.sub(r'\D', '', phone)
    return 10 <= len(digits_only) <= 15


# MARK: - API Endpoints

@dark_web_bp.route('/check', methods=['POST'])
@require_auth
def check_email_breach():
    """
    Проверка email на утечки
    
    POST /api/darkweb/check
    Body: {
        "email": "user@example.com",
        "include_hibp": true,
        "include_breachdirectory": true,
        "include_russian": true
    }
    
    Returns:
        {
            "success": true,
            "email": "user@example.com",
            "breaches_found": 2,
            "breaches": [...],
            "checked_at": "2025-12-09T12:00:00"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        
        email = data.get("email")
        if not email:
            return jsonify({"error": "email field is required"}), 400
        
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        include_hibp = data.get("include_hibp", True)
        include_breachdirectory = data.get("include_breachdirectory", True)
        include_russian = data.get("include_russian", True)
        
        agent = get_agent()
        result = agent.check_email_breach(
            email=email,
            include_hibp=include_hibp,
            include_breachdirectory=include_breachdirectory,
            include_russian=include_russian
        )
        
        return jsonify({
            "success": True,
            **result
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке email: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@dark_web_bp.route('/start-monitoring', methods=['POST'])
@require_auth
def start_monitoring():
    """
    Запуск автоматического мониторинга
    
    POST /api/darkweb/start-monitoring
    Body: {
        "user_id": "user123",
        "email": "user@example.com",
        "phone": "+79991234567",
        "interval_hours": 24
    }
    
    Returns:
        {
            "success": true,
            "user_id": "user123",
            "next_check": "2025-12-10T12:00:00",
            "interval_hours": 24
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id field is required"}), 400
        
        email = data.get("email")
        phone = data.get("phone")
        
        if not email and not phone:
            return jsonify({
                "error": "email or phone must be provided"
            }), 400
        
        if email and not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        if phone and not validate_phone(phone):
            return jsonify({"error": "Invalid phone format"}), 400
        
        interval_hours = data.get("interval_hours", 24)
        if not isinstance(interval_hours, int) or interval_hours < 1:
            return jsonify({
                "error": "interval_hours must be a positive integer"
            }), 400
        
        agent = get_agent()
        result = agent.start_monitoring(
            user_id=user_id,
            email=email,
            phone=phone,
            interval_hours=interval_hours
        )
        
        if "error" in result:
            return jsonify({
                "success": False,
                **result
            }), 400
        
        return jsonify({
            "success": True,
            **result
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске мониторинга: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@dark_web_bp.route('/stop-monitoring', methods=['POST'])
@require_auth
def stop_monitoring():
    """
    Остановка автоматического мониторинга
    
    POST /api/darkweb/stop-monitoring
    Body: {
        "user_id": "user123"
    }
    
    Returns:
        {
            "success": true,
            "user_id": "user123"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id field is required"}), 400
        
        agent = get_agent()
        result = agent.stop_monitoring(user_id)
        
        if not result.get("success"):
            return jsonify({
                "success": False,
                **result
            }), 404
        
        return jsonify({
            "success": True,
            **result
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Ошибка при остановке мониторинга: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@dark_web_bp.route('/status', methods=['GET'])
@require_auth
def get_status():
    """
    Получение статуса мониторинга
    
    GET /api/darkweb/status?user_id=user123
    или
    GET /api/darkweb/status (для всех мониторингов)
    
    Returns:
        {
            "success": true,
            "is_monitoring": true,
            "user_id": "user123",
            "status": {...}
        }
        или
        {
            "success": true,
            "total_active": 5,
            "monitoring": {...}
        }
    """
    try:
        user_id = request.args.get("user_id")
        
        agent = get_agent()
        result = agent.get_monitoring_status(user_id)
        
        return jsonify({
            "success": True,
            **result
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Ошибка при получении статуса: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@dark_web_bp.route('/breaches', methods=['GET'])
@require_auth
def get_breaches():
    """
    Получение списка всех найденных утечек
    
    GET /api/darkweb/breaches
    
    Returns:
        {
            "success": true,
            "threats": [...],
            "analyzed_threats": [...],
            "total_threats": 10
        }
    """
    try:
        agent = get_agent()
        
        # Собираем угрозы
        threats = agent.collect_threats()
        
        # Анализируем угрозы
        analyzed_threats = agent.analyze_threats(threats)
        
        return jsonify({
            "success": True,
            "threats": threats,
            "analyzed_threats": analyzed_threats,
            "total_threats": len(analyzed_threats),
            "collected_at": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Ошибка при получении утечек: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@dark_web_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint (без авторизации)
    
    GET /api/darkweb/health
    
    Returns:
        {
            "status": "healthy",
            "agent_loaded": true
        }
    """
    try:
        agent = get_agent()
        cache_stats = agent.get_cache_stats()
        
        return jsonify({
            "status": "healthy",
            "agent_loaded": agent is not None,
            "cache_stats": cache_stats,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Ошибка при health check: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


# MARK: - Error Handlers

@dark_web_bp.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибок"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404


@dark_web_bp.errorhandler(500)
def internal_error(error):
    """Обработка 500 ошибок"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500
