#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Регистрация VPN функций в JSON регистре
"""

import json
import os
from datetime import datetime

def register_vpn_functions_in_json():
    """Регистрация VPN функций в web_services_registry.json"""
    
    registry_path = "/Users/sergejhlystov/ALADDIN_NEW/data/web_services_registry.json"
    
    # Загружаем существующий реестр
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки реестра: {e}")
        return False
    
    # VPN функции для регистрации
    vpn_services = {
        "vpn_core_service": {
            "service_id": "vpn_core_service",
            "name": "VPN Core Service",
            "description": "Основной сервис VPN системы с поддержкой всех протоколов",
            "service_type": "core",
            "port": 8001,
            "status": "active",
            "version": "1.0",
            "features": [
                "multi_protocol_support",
                "encryption",
                "connection_management",
                "user_authentication"
            ],
            "dependencies": [],
            "endpoints": [
                "/api/v1/vpn/connect",
                "/api/v1/vpn/disconnect",
                "/api/v1/vpn/status"
            ],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        },
        "vpn_security_service": {
            "service_id": "vpn_security_service",
            "name": "VPN Security Service",
            "description": "Сервис безопасности VPN с защитой от DDoS и обнаружением вторжений",
            "service_type": "security",
            "port": 8002,
            "status": "active",
            "version": "1.0",
            "features": [
                "ddos_protection",
                "intrusion_detection",
                "rate_limiting",
                "two_factor_auth"
            ],
            "dependencies": ["vpn_core_service"],
            "endpoints": [
                "/api/v1/security/ddos",
                "/api/v1/security/ids",
                "/api/v1/security/2fa"
            ],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        },
        "vpn_protocols_service": {
            "service_id": "vpn_protocols_service",
            "name": "VPN Protocols Service",
            "description": "Сервис протоколов VPN (Shadowsocks, V2Ray, обфускация)",
            "service_type": "protocol",
            "port": 8003,
            "status": "active",
            "version": "1.0",
            "features": [
                "shadowsocks_client",
                "v2ray_client",
                "traffic_obfuscation",
                "protocol_switching"
            ],
            "dependencies": ["vpn_core_service"],
            "endpoints": [
                "/api/v1/protocols/shadowsocks",
                "/api/v1/protocols/v2ray",
                "/api/v1/protocols/obfuscation"
            ],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        },
        "vpn_monitoring_service": {
            "service_id": "vpn_monitoring_service",
            "name": "VPN Monitoring Service",
            "description": "Сервис мониторинга VPN с метриками и аналитикой",
            "service_type": "monitoring",
            "port": 8004,
            "status": "active",
            "version": "1.0",
            "features": [
                "performance_metrics",
                "business_analytics",
                "real_time_monitoring",
                "alerting"
            ],
            "dependencies": ["vpn_core_service"],
            "endpoints": [
                "/api/v1/monitoring/metrics",
                "/api/v1/monitoring/analytics",
                "/api/v1/monitoring/alerts"
            ],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        },
        "vpn_features_service": {
            "service_id": "vpn_features_service",
            "name": "VPN Features Service",
            "description": "Сервис дополнительных функций VPN (Split Tunneling, Multi-Hop)",
            "service_type": "feature",
            "port": 8005,
            "status": "active",
            "version": "1.0",
            "features": [
                "split_tunneling",
                "multi_hop",
                "auto_reconnect",
                "performance_optimization"
            ],
            "dependencies": ["vpn_core_service"],
            "endpoints": [
                "/api/v1/features/split_tunnel",
                "/api/v1/features/multi_hop",
                "/api/v1/features/auto_reconnect"
            ],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        },
        "vpn_compliance_service": {
            "service_id": "vpn_compliance_service",
            "name": "VPN Compliance Service",
            "description": "Сервис соответствия требованиям 152-ФЗ и локализации данных",
            "service_type": "compliance",
            "port": 8006,
            "status": "active",
            "version": "1.0",
            "features": [
                "russia_compliance",
                "data_localization",
                "no_logs_policy",
                "audit_trail"
            ],
            "dependencies": ["vpn_core_service"],
            "endpoints": [
                "/api/v1/compliance/152fz",
                "/api/v1/compliance/localization",
                "/api/v1/compliance/audit"
            ],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        },
        "vpn_api_service": {
            "service_id": "vpn_api_service",
            "name": "VPN API Service",
            "description": "API сервис VPN с поддержкой GraphQL и WebSocket",
            "service_type": "api",
            "port": 8007,
            "status": "active",
            "version": "1.0",
            "features": [
                "graphql_api",
                "websocket_api",
                "rest_api",
                "api_documentation"
            ],
            "dependencies": ["vpn_core_service"],
            "endpoints": [
                "/api/v1/graphql",
                "/api/v1/websocket",
                "/api/v1/docs"
            ],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        },
        "vpn_integration_service": {
            "service_id": "vpn_integration_service",
            "name": "VPN Integration Service",
            "description": "Сервис интеграции с внешними сервисами и платформами",
            "service_type": "integration",
            "port": 8008,
            "status": "active",
            "version": "1.0",
            "features": [
                "external_services",
                "webhook_support",
                "third_party_apis",
                "data_synchronization"
            ],
            "dependencies": ["vpn_core_service"],
            "endpoints": [
                "/api/v1/integrations/external",
                "/api/v1/integrations/webhooks",
                "/api/v1/integrations/sync"
            ],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        },
        "vpn_web_interface": {
            "service_id": "vpn_web_interface",
            "name": "VPN Web Interface",
            "description": "Веб-интерфейс для управления VPN системой",
            "service_type": "web_interface",
            "port": 8009,
            "status": "active",
            "version": "1.0",
            "features": [
                "user_dashboard",
                "connection_management",
                "settings_configuration",
                "real_time_status"
            ],
            "dependencies": ["vpn_core_service", "vpn_api_service"],
            "endpoints": [
                "/",
                "/dashboard",
                "/settings",
                "/status"
            ],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    }
    
    # Добавляем VPN сервисы в реестр
    if 'web_services' not in registry:
        registry['web_services'] = {}
    
    added_count = 0
    for service_id, service_data in vpn_services.items():
        if service_id not in registry['web_services']:
            registry['web_services'][service_id] = service_data
            added_count += 1
            print(f"✅ Добавлен сервис: {service_id}")
        else:
            print(f"⚠️  Сервис {service_id} уже существует")
    
    # Сохраняем обновленный реестр
    try:
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Добавлено VPN сервисов: {added_count}/{len(vpn_services)}")
        print(f"✅ Реестр сохранен: {registry_path}")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения реестра: {e}")
        return False

def main():
    """Основная функция"""
    print("🔧 РЕГИСТРАЦИЯ VPN ФУНКЦИЙ В JSON РЕЕСТРЕ")
    print("=" * 50)
    
    if register_vpn_functions_in_json():
        print("\n🎉 Все VPN функции успешно зарегистрированы в JSON реестре!")
    else:
        print("\n❌ Ошибка регистрации VPN функций")

if __name__ == "__main__":
    main()