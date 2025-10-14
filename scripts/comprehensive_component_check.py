#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALADDIN Security System - Комплексная проверка всех компонентов из списка

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-09-11
"""

import os
import ast
import sys
from pathlib import Path
import re

def find_component_by_name(component_name, search_paths):
    """Поиск компонента по точному имени"""
    found_files = []
    
    for search_path in search_paths:
        if not os.path.exists(search_path):
            continue
            
        for file_path in Path(search_path).rglob('*.py'):
            if file_path.name.startswith('__'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Поиск по имени класса
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if component_name.lower() == node.name.lower():
                            found_files.append({
                                'file': str(file_path),
                                'class': node.name,
                                'line': node.lineno,
                                'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                            })
            except Exception as e:
                continue
    
    return found_files

def analyze_all_components_from_list():
    """Анализ всех компонентов из предоставленного списка"""
    
    print("🔍 КОМПЛЕКСНАЯ ПРОВЕРКА ВСЕХ КОМПОНЕНТОВ ИЗ СПИСКА")
    print("="*80)
    
    # Все компоненты из вашего списка
    all_components = {
        # Критические компоненты безопасности
        "SafeFunctionManager": "Центральный менеджер функций",
        "ThreatIntelligence": "Разведка угроз", 
        "SecurityAudit": "Аудит безопасности",
        "SecurityMonitoring": "Мониторинг безопасности",
        "SecurityLayer": "Слой безопасности",
        "SecurityPolicy": "Политики безопасности",
        "SecurityReporting": "Отчетность по безопасности",
        "AccessControl": "Контроль доступа",
        "Authentication": "Аутентификация",
        "ComplianceManager": "Менеджер соответствия",
        "IncidentResponse": "Реагирование на инцидентах",
        "SecurityAnalytics": "Аналитика безопасности",
        
        # AI агенты
        "MobileSecurityAgent": "Агент мобильной безопасности",
        "ThreatDetectionAgent": "Агент обнаружения угроз",
        "BehavioralAnalysisAgent": "Агент анализа поведения",
        "PasswordSecurityAgent": "Агент безопасности паролей",
        "IncidentResponseAgent": "Агент реагирования на инциденты",
        "ThreatIntelligenceAgent": "Агент разведки угроз",
        "NetworkSecurityAgent": "Агент сетевой безопасности",
        "DataProtectionAgent": "Агент защиты данных",
        "ComplianceAgent": "Агент соответствия требованиям",
        "PerformanceOptimizationAgent": "Агент оптимизации производительности",
        
        # Боты безопасности
        "MobileNavigationBot": "Бот навигации по мобильным устройствам",
        "GamingSecurityBot": "Бот безопасности игр",
        "EmergencyResponseBot": "Бот экстренного реагирования",
        "ParentalControlBot": "Бот родительского контроля",
        "NotificationBot": "Бот уведомлений",
        "WhatsAppSecurityBot": "Бот безопасности WhatsApp",
        "TelegramSecurityBot": "Бот безопасности Telegram",
        "InstagramSecurityBot": "Бот безопасности Instagram",
        "MaxMessengerSecurityBot": "Бот безопасности российского мессенджера MAX",
        "AnalyticsBot": "Бот аналитики",
        "WebsiteNavigationBot": "Бот навигации по сайтам",
        "BrowserSecurityBot": "Бот безопасности браузера",
        "CloudStorageSecurityBot": "Бот безопасности облачного хранилища",
        "NetworkSecurityBot": "Бот сетевой безопасности",
        "DeviceSecurityBot": "Бот безопасности устройств",
        
        # Микросервисы
        "APIGateway": "API шлюз",
        "LoadBalancer": "Балансировщик нагрузки",
        "RateLimiter": "Ограничитель скорости",
        "CircuitBreaker": "Автоматический выключатель",
        "UserInterfaceManager": "Менеджер пользовательского интерфейса",
        "RedisCacheManager": "Менеджер кэша Redis",
        "ServiceMeshManager": "Менеджер сервисной сетки",
        
        # Семейные компоненты
        "FamilyDashboardManager": "Семейная панель управления",
        "ParentalControls": "Родительский контроль",
        "ElderlyProtection": "Защита пожилых",
        "ChildProtection": "Защита детей",
        "FamilyProfileManager": "Управление семейными профилями",
        "ChildInterfaceManager": "Интерфейс для детей",
        "ElderlyInterfaceManager": "Интерфейс для пожилых",
        "ParentControlPanel": "Панель управления родителей",
        "FamilyCommunicationHub": "Семейный коммуникационный центр",
        
        # Голосовое управление
        "SpeechRecognitionEngine": "Движок распознавания речи",
        "NaturalLanguageProcessor": "Обработка естественного языка",
        "VoiceResponseGenerator": "Генератор голосовых ответов",
        "VoiceSecurityValidator": "Валидация голосовых команд",
        "VoiceControlManager": "Голосовое управление",
        "VoiceAnalysisEngine": "Движок анализа голоса",
        
        # Умные уведомления
        "SmartNotificationManager": "Умные уведомления",
        "ContextualAlertSystem": "Контекстные оповещения",
        "EmergencyResponseInterface": "Интерфейс экстренного реагирования",
        
        # Аналитика и мониторинг
        "MonitorManager": "Менеджер мониторинга",
        "AlertManager": "Менеджер оповещений",
        "ReportManager": "Менеджер отчетов",
        "AnalyticsManager": "Менеджер аналитики",
        "DashboardManager": "Менеджер панели управления",
        "BehavioralAnalyticsEngine": "Движок поведенческой аналитики",
        "MessengerIntegration": "Интеграция с мессенджерами",
        
        # Активные компоненты безопасности
        "DeviceSecurity": "Безопасность устройств",
        "IntrusionPrevention": "Предотвращение вторжений",
        "MalwareProtection": "Защита от вредоносного ПО",
        "NetworkMonitoring": "Мониторинг сети",
        "ThreatDetection": "Обнаружение угроз",
        
        # Реактивные компоненты
        "PerformanceOptimizer": "Оптимизатор производительности",
        "ForensicsService": "Криминалистический сервис",
        "RecoveryService": "Сервис восстановления",
        
        # Предварительные компоненты
        "ContextAwareAccess": "Контекстно-зависимый доступ",
        "TrustScoring": "Система оценки доверия",
        "PolicyEngine": "Движок политик",
        "RiskAssessment": "Оценка рисков",
        "BehavioralAnalysis": "Анализ поведения",
        "MFAService": "Многофакторная аутентификация",
        "ZeroTrustService": "Сервис нулевого доверия",
        
        # Компоненты соответствия и приватности
        "COPPAComplianceManager": "Соответствие COPPA",
        "UniversalPrivacyManager": "Универсальный менеджер приватности",
        "RussianChildProtectionManager": "Российская защита детей",
        
        # Дополнительные компоненты
        "AntiFraudMasterAI": "Главный агент защиты от мошенничества",
        "DeepfakeProtectionSystem": "Система защиты от deepfake",
        "FinancialProtectionHub": "Хаб финансовой защиты",
        "EmergencyResponseSystem": "Система экстренного реагирования",
        "ElderlyProtectionInterface": "Интерфейс для пожилых",
        "MobileUserAIAgent": "Мобильный AI агент",
        "VPNSecuritySystem": "Система VPN безопасности",
        "AntivirusSecuritySystem": "Система антивирусной безопасности",
        "ZeroTrustManager": "Менеджер нулевого доверия",
        "RansomwareProtection": "Защита от ransomware",
        "SecureConfigManager": "Безопасный менеджер конфигурации",
        
        # Масштабирование и оркестрация
        "KubernetesOrchestrator": "Оркестратор Kubernetes",
        "AutoScalingEngine": "Движок автоматического масштабирования",
        
        # CI/CD
        "CIPipelineManager": "Менеджер CI/CD пайплайна"
    }
    
    # Пути для поиска
    search_paths = [
        '/Users/sergejhlystov/ALADDIN_NEW/security',
        '/Users/sergejhlystov/ALADDIN_NEW/core',
        '/Users/sergejhlystov/ALADDIN_NEW/ai_agents',
        '/Users/sergejhlystov/ALADDIN_NEW/bots',
        '/Users/sergejhlystov/ALADDIN_NEW/microservices',
        '/Users/sergejhlystov/ALADDIN_NEW/family',
        '/Users/sergejhlystov/ALADDIN_NEW/compliance',
        '/Users/sergejhlystov/ALADDIN_NEW/privacy',
        '/Users/sergejhlystov/ALADDIN_NEW/reactive',
        '/Users/sergejhlystov/ALADDIN_NEW/active',
        '/Users/sergejhlystov/ALADDIN_NEW/preliminary',
        '/Users/sergejhlystov/ALADDIN_NEW/orchestration',
        '/Users/sergejhlystov/ALADDIN_NEW/scaling'
    ]
    
    found_components = {}
    missing_components = {}
    
    print(f"🔍 ПРОВЕРКА {len(all_components)} КОМПОНЕНТОВ:")
    print("-" * 50)
    
    for component_name, description in all_components.items():
        found_files = find_component_by_name(component_name, search_paths)
        
        if found_files:
            found_components[component_name] = {
                'description': description,
                'files': found_files
            }
            print(f"  ✅ {component_name}: {len(found_files)} файлов")
        else:
            missing_components[component_name] = description
            print(f"  ❌ {component_name}: НЕ НАЙДЕН")
    
    # Детальный анализ найденных компонентов
    print(f"\n📊 ДЕТАЛЬНЫЙ АНАЛИЗ НАЙДЕННЫХ КОМПОНЕНТОВ:")
    print("="*80)
    
    total_methods = 0
    for component_name, info in found_components.items():
        print(f"\n🔹 {component_name} - {info['description']}")
        for file_info in info['files']:
            print(f"  📄 {os.path.basename(file_info['file'])}")
            print(f"    🏗️ Класс: {file_info['class']} (строка {file_info['line']})")
            print(f"    ⚙️ Методов: {file_info['methods']}")
            total_methods += file_info['methods']
    
    # Анализ отсутствующих компонентов
    print(f"\n❌ ОТСУТСТВУЮЩИЕ КОМПОНЕНТЫ ({len(missing_components)}):")
    print("="*80)
    
    for i, (component_name, description) in enumerate(missing_components.items(), 1):
        print(f"  {i:2d}. {component_name} - {description}")
    
    # Статистика
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print("="*80)
    print(f"✅ НАЙДЕНО КОМПОНЕНТОВ: {len(found_components)}")
    print(f"❌ ОТСУТСТВУЕТ КОМПОНЕНТОВ: {len(missing_components)}")
    print(f"📊 ПРОЦЕНТ ПОКРЫТИЯ: {len(found_components)/(len(found_components)+len(missing_components))*100:.1f}%")
    print(f"⚙️ ВСЕГО МЕТОДОВ: {total_methods}")
    
    # Рекомендации
    print(f"\n🎯 РЕКОМЕНДАЦИИ:")
    print("="*80)
    
    if missing_components:
        print(f"🔴 КРИТИЧЕСКИЕ ОТСУТСТВУЮЩИЕ КОМПОНЕНТЫ:")
        critical_missing = [name for name in missing_components.keys() if any(keyword in name.lower() for keyword in ['security', 'manager', 'agent', 'bot'])]
        for component in critical_missing[:10]:  # Топ-10 критических
            print(f"  - {component}")
    
    print(f"\n🟡 ДОПОЛНИТЕЛЬНЫЕ КОМПОНЕНТЫ ДЛЯ СОЗДАНИЯ:")
    additional_components = [name for name in missing_components.keys() if name not in critical_missing]
    for component in additional_components[:10]:  # Топ-10 дополнительных
        print(f"  - {component}")
    
    return {
        'found_components': found_components,
        'missing_components': missing_components,
        'total_methods': total_methods,
        'coverage_percentage': len(found_components)/(len(found_components)+len(missing_components))*100
    }

def main():
    """Главная функция"""
    analyze_all_components_from_list()

if __name__ == "__main__":
    main()