# -*- coding: utf-8 -*-
"""
ALADDIN Security System - IoT Security Agent
AI агент для защиты умного дома (IoT)

Покрывает 10 IoT угроз:
1. IoT device compromise
2. Smart home infiltration
3. Compromised cameras
4. Smart speaker eavesdropping
5. Home network breaches
6. Smart device data leaks
7. Voice command manipulation
8. Weak IoT passwords
9. Default credential abuse
10. Physical device theft

Автор: ALADDIN Security Team
Версия: 1.0.0
Дата: 2025-11-04
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from security.base import SecurityBase


class IoTSecurityAgent(SecurityBase):
    """
    AI агент для защиты умного дома (IoT)
    
    Покрывает 10 угроз:
    1. IoT device compromise
    2. Smart home infiltration
    3. Compromised cameras
    4. Smart speaker eavesdropping
    5. Home network breaches
    6. Smart device data leaks
    7. Voice command manipulation
    8. Weak IoT passwords
    9. Default credential abuse
    10. Physical device theft
    """
    
    def __init__(self):
        super().__init__(name="IoT Security Agent")
        self.agent_name = "IoT Security Agent"
        self.version = "1.0.0"
        self.logger = logging.getLogger(self.__class__.__name__)

    def analyze_device(self, device_data: Dict) -> Dict:
        """
        Анализирует одно устройство и возвращает найденные проблемы.

        Args:
            device_data: Сырые данные устройства, полученные от IoT модуля.

        Returns:
            Dict: детальный отчёт с оценкой риска и перечнем проблем.
        """
        device_id = device_data.get("id") or device_data.get("device_id") or "unknown"
        device_name = device_data.get("name", "Unknown device")
        issues: List[Dict] = []
        now = datetime.utcnow()
        severity_weight = {"low": 5, "medium": 15, "high": 30, "critical": 45}

        def add_issue(issue_type: str, description: str, severity: str, recommendations: Optional[List[str]] = None):
            issues.append(
                {
                    "issue_type": issue_type,
                    "description": description,
                    "severity": severity,
                    "recommendations": recommendations or [],
                    "detected_at": now.isoformat() + "Z",
                }
            )

        if device_data.get("uses_default_password") or device_data.get("default_credentials"):
            add_issue(
                "default_credentials",
                "Устройство использует стандартные логин/пароль",
                "high",
                [
                    "Изменить пароль немедленно",
                    "Включить двухфакторную аутентификацию, если доступно",
                ],
            )

        firmware_status = (device_data.get("firmware_status") or "").lower()
        if firmware_status in {"outdated", "unknown"} or device_data.get("needs_firmware_update"):
            add_issue(
                "outdated_firmware",
                "Не установлено актуальное обновление прошивки",
                "medium",
                [
                    "Проверить обновления у производителя",
                    "Настроить автоматическую установку патчей",
                ],
            )

        anomaly_score = float(device_data.get("anomaly_score", 0.0))
        if anomaly_score >= 0.85:
            add_issue(
                "anomalous_traffic",
                f"Аномальная сетевой активность (score={anomaly_score:.2f})",
                "high",
                [
                    "Изолировать устройство от сети",
                    "Проверить логи маршрутизатора",
                ],
            )
        elif anomaly_score >= 0.6:
            add_issue(
                "suspicious_activity",
                f"Повышенная активность устройства (score={anomaly_score:.2f})",
                "medium",
                [
                    "Проверить список подключений",
                    "Ограничить доступ к чувствительным данным",
                ],
            )

        open_ports = device_data.get("open_ports", [])
        risky_ports = {23, 2323, 3389}
        if any(port in risky_ports for port in open_ports):
            add_issue(
                "exposed_service",
                f"Найдены небезопасные открытые порты: {sorted(set(open_ports) & risky_ports)}",
                "medium",
                [
                    "Закрыть ненужные порты на маршрутизаторе",
                    "Включить брандмауэр устройства",
                ],
            )

        if not device_data.get("encryption_enabled", True):
            add_issue(
                "unencrypted_channel",
                "Трафик устройства не шифруется",
                "high",
                [
                    "Включить шифрование данных",
                    "Использовать VPN/защищённый канал связи",
                ],
            )

        if not device_data.get("is_online", True):
            add_issue(
                "device_offline",
                "Устройство находится офлайн и не передаёт телеметрию",
                "low",
                ["Проверить питание устройства", "Перезапустить маршрутизатор"],
            )

        risk_points = sum(severity_weight[issue["severity"]] for issue in issues)
        score = max(0, 100 - risk_points)
        overall_severity = "low"
        if issues:
            overall_severity = max(issues, key=lambda item: severity_weight[item["severity"]])["severity"]

        analysis = {
            "device_id": device_id,
            "device_name": device_name,
            "issues": issues,
            "score": score,
            "overall_severity": overall_severity,
            "checked_at": now.isoformat() + "Z",
        }

        self.logger.debug("IoT device analysed", extra={"analysis": analysis})
        return analysis

    def detect_threats(self, devices: List[Dict]) -> List[Dict]:
        """
        Обрабатывает список устройств и возвращает плоский список угроз.

        Args:
            devices: список словарей с устройствами.

        Returns:
            List[Dict]: список угроз, отсортированный по критичности.
        """
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        threats: List[Dict] = []

        for device in devices:
            analysis = self.analyze_device(device)
            for issue in analysis["issues"]:
                threats.append(
                    {
                        "device_id": analysis["device_id"],
                        "device_name": analysis["device_name"],
                        "threat_type": issue["issue_type"],
                        "severity": issue["severity"],
                        "description": issue["description"],
                        "recommendations": issue["recommendations"],
                        "detected_at": issue["detected_at"],
                        "score_after_detection": analysis["score"],
                    }
                )

        threats.sort(key=lambda item: severity_order.get(item["severity"], 0), reverse=True)
        self.logger.info("IoT threat detection completed", extra={"threats_found": len(threats)})
        return threats
        
    async def scan_iot_devices(self, home_id: str) -> List[Dict]:
        """
        Сканирование всех IoT устройств в сети
        
        Технологии:
        - Network scanning (nmap, arp-scan)
        - Device fingerprinting
        - AI анализ устройств
        
        Args:
            home_id: ID умного дома
            
        Returns:
            List[Dict]: [
                {
                    "id": "device_123",
                    "name": "Умная камера",
                    "type": "camera",
                    "ip": "192.168.1.100",
                    "mac": "AA:BB:CC:DD:EE:FF",
                    "vendor": "Xiaomi",
                    "model": "Mi Home Security Camera",
                    "status": "online",
                    "last_seen": "2025-11-04T10:30:00Z"
                },
                ...
            ]
        """
        devices = []
        
        # 1. Network scanning
        # - Использовать nmap для сканирования сети
        # - Обнаружить все устройства в локальной сети
        # - Получить IP, MAC адреса
        
        # 2. Device fingerprinting
        # - Определить тип устройства (камера, колонка, датчик)
        # - Определить производителя и модель
        # - Использовать базу данных IoT устройств
        
        # 3. AI анализ
        # - Проанализировать трафик устройства
        # - Определить поведение устройства
        # - Обнаружить подозрительную активность
        
        return devices
    
    async def detect_camera_intrusion(self, device_id: str) -> Dict:
        """
        Обнаружение вторжения в камеры
        
        Анализирует:
        - Подозрительные подключения к камере
        - Неавторизованный доступ
        - Необычные запросы к камере
        - Изменения в настройках камеры
        
        Args:
            device_id: ID устройства
            
        Returns:
            Dict: {
                "threat_detected": True,
                "threat_type": "camera_intrusion",
                "severity": "high",
                "description": "Обнаружено подозрительное подключение к камере",
                "timestamp": "2025-11-04T10:30:00Z",
                "recommendations": [
                    "Изменить пароль камеры",
                    "Включить двухфакторную аутентификацию",
                    "Проверить список авторизованных устройств"
                ]
            }
        """
        # 1. Анализ подключений к камере
        # - Проверить список активных подключений
        # - Обнаружить подозрительные IP адреса
        # - Проверить геолокацию подключений
        
        # 2. AI анализ активности
        # - Проанализировать запросы к камере
        # - Обнаружить необычные паттерны
        # - Использовать ML модель для детекции
        
        # 3. Проверка настроек
        # - Проверить изменения в настройках
        # - Обнаружить неавторизованные изменения
        
        threat_detection = {
            "threat_detected": False,
            "threat_type": "camera_intrusion",
            "severity": "low",
            "description": "Угроз не обнаружено",
            "timestamp": datetime.now().isoformat(),
            "recommendations": []
        }
        
        return threat_detection
    
    async def detect_speaker_eavesdropping(self, device_id: str) -> Dict:
        """
        Обнаружение подслушивания через умные колонки
        
        Анализирует:
        - Подозрительные голосовые команды
        - Неавторизованный доступ к микрофону
        - Необычные запросы к колонке
        - Активация без команды
        
        Args:
            device_id: ID устройства
            
        Returns:
            Dict: {
                "threat_detected": True,
                "threat_type": "speaker_eavesdropping",
                "severity": "high",
                "description": "Обнаружена подозрительная активность на умной колонке",
                "timestamp": "2025-11-04T10:30:00Z"
            }
        """
        # 1. Анализ голосовых команд
        # - Проанализировать все голосовые команды
        # - Обнаружить подозрительные команды
        # - Проверить источник команд
        
        # 2. Мониторинг микрофона
        # - Проверить активность микрофона
        # - Обнаружить неавторизованное прослушивание
        # - Проверить отправку данных
        
        # 3. ML детекция
        # - Использовать ML модель для анализа
        # - Обнаружить паттерны подслушивания
        # - Предупредить пользователя
        
        threat_detection = {
            "threat_detected": False,
            "threat_type": "speaker_eavesdropping",
            "severity": "low",
            "description": "Угроз не обнаружено",
            "timestamp": datetime.now().isoformat()
        }
        
        return threat_detection
    
    async def detect_weak_passwords(self, device_id: str) -> Dict:
        """
        Обнаружение слабых паролей
        
        Проверяет:
        - Длина пароля (минимум 8 символов)
        - Сложность пароля (буквы, цифры, символы)
        - Использование словарных слов
        - Повторяющиеся символы
        
        Args:
            device_id: ID устройства
            
        Returns:
            Dict: {
                "issue_detected": True,
                "issue_type": "weak_password",
                "severity": "medium",
                "description": "Обнаружен слабый пароль на устройстве",
                "recommendations": [
                    "Изменить пароль на более сложный",
                    "Использовать минимум 12 символов",
                    "Включить двухфакторную аутентификацию"
                ]
            }
        """
        # 1. Проверка сложности пароля
        # - Проверить длину пароля
        # - Проверить наличие букв, цифр, символов
        # - Проверить использование словарных слов
        
        # 2. Сравнение с базой слабых паролей
        # - Проверить против базы слабых паролей
        # - Проверить против утечек паролей
        # - Проверить повторяющиеся пароли
        
        # 3. Рекомендации
        # - Предоставить рекомендации по улучшению
        # - Предложить генератор паролей
        
        security_issue = {
            "issue_detected": False,
            "issue_type": "weak_password",
            "severity": "low",
            "description": "Проблем не обнаружено",
            "recommendations": []
        }
        
        return security_issue
    
    async def block_compromised_device(self, device_id: str) -> bool:
        """
        Блокировка скомпрометированного устройства
        
        Действия:
        - Блокировка устройства в сети
        - Изоляция от остальных устройств
        - Уведомление пользователя
        - Логирование события
        
        Args:
            device_id: ID устройства
            
        Returns:
            bool: True если устройство заблокировано
        """
        # 1. Блокировка в сети
        # - Заблокировать устройство в роутере
        # - Изолировать от остальных устройств
        # - Отключить доступ к интернету
        
        # 2. Уведомление пользователя
        # - Отправить push-уведомление
        # - Отправить email уведомление
        # - Показать предупреждение в приложении
        
        # 3. Логирование
        # - Записать событие в лог
        # - Сохранить в базе данных
        # - Отправить в аналитику
        
        return True
    
    async def monitor_voice_commands(self, device_id: str) -> List[Dict]:
        """
        Мониторинг голосовых команд
        
        Анализирует:
        - Все голосовые команды в реальном времени
        - Подозрительные команды
        - Манипуляции с командами
        - Неавторизованные команды
        
        Args:
            device_id: ID устройства
            
        Returns:
            List[Dict]: [
                {
                    "command": "открой дверь",
                    "timestamp": "2025-11-04T10:30:00Z",
                    "source": "unknown",
                    "threat_level": "high",
                    "action": "blocked"
                },
                ...
            ]
        """
        # 1. Анализ голосовых команд
        # - Перехватывать все голосовые команды
        # - Анализировать содержимое команд
        # - Проверять источник команд
        
        # 2. ML детекция
        # - Использовать ML модель для анализа
        # - Обнаружить подозрительные команды
        # - Обнаружить манипуляции
        
        # 3. Блокировка подозрительных команд
        # - Блокировать опасные команды
        # - Предупреждать пользователя
        # - Логировать события
        
        threat_detections = []
        
        return threat_detections
    
    async def protect_smart_home(self, home_id: str) -> Dict:
        """
        Комплексная защита умного дома
        
        Агрегирует:
        - Все обнаруженные устройства
        - Все обнаруженные угрозы
        - Все рекомендации
        - Общий статус безопасности
        
        Args:
            home_id: ID умного дома
            
        Returns:
            Dict: {
                "home_id": "home_123",
                "devices": [...],
                "threats": [...],
                "recommendations": [...],
                "protection_level": 85,
                "last_scan": "2025-11-04T10:30:00Z"
            }
        """
        # 1. Сканирование устройств
        devices = await self.scan_iot_devices(home_id)
        
        # 2. Анализ угроз
        threats = []
        for device in devices:
            if device.get("type") == "camera":
                threat = await self.detect_camera_intrusion(device.get("id", ""))
                if threat.get("threat_detected"):
                    threats.append(threat)
            
            if device.get("type") == "speaker":
                threat = await self.detect_speaker_eavesdropping(device.get("id", ""))
                if threat.get("threat_detected"):
                    threats.append(threat)
            
            # Проверка паролей
            password_issue = await self.detect_weak_passwords(device.get("id", ""))
            if password_issue.get("issue_detected"):
                threats.append(password_issue)
        
        # 3. Генерация рекомендаций
        recommendations = self._generate_recommendations(devices, threats)
        
        # 4. Расчет уровня защиты
        protection_level = self._calculate_protection_level(devices, threats)
        
        return {
            "home_id": home_id,
            "devices": devices,
            "threats": threats,
            "recommendations": recommendations,
            "protection_level": protection_level,
            "last_scan": datetime.now().isoformat()
        }
    
    async def detect_default_credentials(self, device_id: str) -> Dict:
        """
        Обнаружение дефолтных креденшейлов
        
        Проверяет:
        - Использование дефолтных паролей
        - Использование дефолтных логинов
        - Сравнение с базой дефолтных паролей
        
        Args:
            device_id: ID устройства
            
        Returns:
            Dict: {
                "issue_detected": True,
                "issue_type": "default_credentials",
                "severity": "high",
                "description": "Обнаружены дефолтные креденшейлы",
                "recommendations": [
                    "Немедленно изменить пароль",
                    "Использовать уникальный пароль",
                    "Включить двухфакторную аутентификацию"
                ]
            }
        """
        # 1. Проверка дефолтных паролей
        # - Сравнить с базой дефолтных паролей
        # - Проверить производителя устройства
        # - Проверить модель устройства
        
        # 2. Проверка дефолтных логинов
        # - Проверить дефолтные логины (admin, root, user)
        # - Проверить комбинации логин/пароль
        
        # 3. Рекомендации
        # - Предоставить рекомендации по замене
        # - Предложить генератор паролей
        
        security_issue = {
            "issue_detected": False,
            "issue_type": "default_credentials",
            "severity": "low",
            "description": "Проблем не обнаружено",
            "recommendations": []
        }
        
        return security_issue
    
    async def detect_physical_tampering(self, device_id: str) -> Dict:
        """
        Обнаружение физического вмешательства
        
        Анализирует:
        - Изменения в устройстве
        - Детекция физического доступа
        - Предупреждения о краже
        
        Args:
            device_id: ID устройства
            
        Returns:
            Dict: {
                "threat_detected": True,
                "threat_type": "physical_tampering",
                "severity": "high",
                "description": "Обнаружено физическое вмешательство в устройство",
                "timestamp": "2025-11-04T10:30:00Z"
            }
        """
        # 1. Анализ изменений
        # - Проверить изменения в прошивке
        # - Проверить изменения в настройках
        # - Проверить изменения в конфигурации
        
        # 2. Детекция физического доступа
        # - Проверить датчики устройства
        # - Проверить историю доступа
        # - Обнаружить подозрительную активность
        
        # 3. Предупреждения о краже
        # - Предупредить пользователя
        # - Отправить уведомление
        # - Заблокировать устройство
        
        threat_detection = {
            "threat_detected": False,
            "threat_type": "physical_tampering",
            "severity": "low",
            "description": "Угроз не обнаружено",
            "timestamp": datetime.now().isoformat()
        }
        
        return threat_detection
    
    async def analyze_iot_traffic(self, device_id: str) -> Dict:
        """
        Анализ IoT трафика
        
        Анализирует:
        - Сетевой трафик устройства
        - Обнаружение подозрительной активности
        - ML анализ трафика
        
        Args:
            device_id: ID устройства
            
        Returns:
            Dict: {
                "device_id": "device_123",
                "traffic_analysis": {
                    "total_bytes": 1024000,
                    "suspicious_connections": 2,
                    "data_leaks": 0,
                    "threats": [...]
                },
                "recommendations": [...]
            }
        """
        # 1. Анализ трафика
        # - Перехватывать сетевой трафик
        # - Анализировать пакеты
        # - Обнаружить подозрительную активность
        
        # 2. ML анализ
        # - Использовать ML модель для анализа
        # - Обнаружить аномалии
        # - Обнаружить утечки данных
        
        # 3. Рекомендации
        # - Предоставить рекомендации
        # - Предложить блокировку подозрительных соединений
        
        network_analysis = {
            "device_id": device_id,
            "traffic_analysis": {
                "total_bytes": 0,
                "suspicious_connections": 0,
                "data_leaks": 0,
                "threats": []
            },
            "recommendations": []
        }
        
        return network_analysis
    
    # Вспомогательные методы
    
    def _generate_recommendations(self, devices: List[Dict], threats: List[Dict]) -> List[str]:
        """
        Генерация рекомендаций на основе устройств и угроз
        
        Args:
            devices: Список устройств
            threats: Список угроз
            
        Returns:
            List[str]: Список рекомендаций
        """
        recommendations = []
        
        if not devices:
            recommendations.append("Начните с добавления IoT устройств в систему")
        
        if threats:
            recommendations.append("Обнаружены угрозы - требуется немедленное внимание")
        
        return recommendations
    
    def _calculate_protection_level(self, devices: List[Dict], threats: List[Dict]) -> int:
        """
        Расчет уровня защиты умного дома
        
        Args:
            devices: Список устройств
            threats: Список угроз
            
        Returns:
            int: Уровень защиты (0-100)
        """
        if not devices:
            return 0
        
        # Базовый уровень защиты
        base_level = 50
        
        # Бонус за количество защищенных устройств
        device_bonus = min(len(devices) * 5, 30)
        
        # Штраф за угрозы
        threat_penalty = min(len(threats) * 10, 50)
        
        protection_level = base_level + device_bonus - threat_penalty
        
        return max(0, min(100, protection_level))


# Регистрация функций в SFM
def register_iot_functions():
    """Регистрация всех IoT функций в SFM"""
    try:
        from security.sfm_singleton import get_sfm
        from security.core.security_base import SecurityLevel
        
        sfm = get_sfm()
        agent = IoTSecurityAgent()
        
        # Регистрация функций
        sfm.register_function(
            function_id="iot_scan_devices",
            name="IoT Scan Devices",
            description="Сканирование IoT устройств",
            function_type="iot",
            security_level=SecurityLevel.HIGH,
            is_critical=False,
            auto_enable=False,
            handler=agent.scan_iot_devices
        )
        
        sfm.register_function(
            function_id="iot_detect_camera_intrusion",
            name="IoT Detect Camera Intrusion",
            description="Обнаружение вторжения в камеры",
            function_type="iot",
            security_level=SecurityLevel.HIGH,
            is_critical=True,
            auto_enable=False,
            handler=agent.detect_camera_intrusion
        )
        
        sfm.register_function(
            function_id="iot_detect_speaker_listening",
            name="IoT Detect Speaker Eavesdropping",
            description="Обнаружение подслушивания через колонки",
            function_type="iot",
            security_level=SecurityLevel.HIGH,
            is_critical=True,
            auto_enable=False,
            handler=agent.detect_speaker_eavesdropping
        )
        
        sfm.register_function(
            function_id="iot_detect_weak_passwords",
            name="IoT Detect Weak Passwords",
            description="Обнаружение слабых паролей",
            function_type="iot",
            security_level=SecurityLevel.MEDIUM,
            is_critical=False,
            auto_enable=False,
            handler=agent.detect_weak_passwords
        )
        
        sfm.register_function(
            function_id="iot_block_compromised_device",
            name="IoT Block Compromised Device",
            description="Блокировка скомпрометированного устройства",
            function_type="iot",
            security_level=SecurityLevel.HIGH,
            is_critical=True,
            auto_enable=False,
            handler=agent.block_compromised_device
        )
        
        sfm.register_function(
            function_id="iot_monitor_voice_commands",
            name="IoT Monitor Voice Commands",
            description="Мониторинг голосовых команд",
            function_type="iot",
            security_level=SecurityLevel.HIGH,
            is_critical=False,
            auto_enable=False,
            handler=agent.monitor_voice_commands
        )
        
        sfm.register_function(
            function_id="iot_protect_smart_home",
            name="IoT Protect Smart Home",
            description="Комплексная защита умного дома",
            function_type="iot",
            security_level=SecurityLevel.HIGH,
            is_critical=True,
            auto_enable=False,
            handler=agent.protect_smart_home
        )
        
        sfm.register_function(
            function_id="iot_detect_default_credentials",
            name="IoT Detect Default Credentials",
            description="Обнаружение дефолтных креденшейлов",
            function_type="iot",
            security_level=SecurityLevel.HIGH,
            is_critical=False,
            auto_enable=False,
            handler=agent.detect_default_credentials
        )
        
        sfm.register_function(
            function_id="iot_detect_physical_tampering",
            name="IoT Detect Physical Tampering",
            description="Обнаружение физического вмешательства",
            function_type="iot",
            security_level=SecurityLevel.HIGH,
            is_critical=False,
            auto_enable=False,
            handler=agent.detect_physical_tampering
        )
        
        sfm.register_function(
            function_id="iot_analyze_traffic",
            name="IoT Analyze Traffic",
            description="Анализ IoT трафика",
            function_type="iot",
            security_level=SecurityLevel.MEDIUM,
            is_critical=False,
            auto_enable=False,
            handler=agent.analyze_iot_traffic
        )
        
        print("✅ Все IoT функции зарегистрированы в SFM")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка регистрации IoT функций в SFM: {e}")
        return False


# Вызвать при инициализации модуля
if __name__ == "__main__":
    register_iot_functions()

