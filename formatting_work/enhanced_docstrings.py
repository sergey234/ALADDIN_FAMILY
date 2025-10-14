# -*- coding: utf-8 -*-
"""
Примеры расширенных docstrings для улучшения документации
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class IntrusionType(Enum):
    """
    Типы вторжений в системе безопасности.
    
    Этот enum определяет различные типы атак, которые может обнаружить
    система предотвращения вторжений.
    
    Attributes:
        BRUTE_FORCE: Атака методом перебора паролей
        DDoS_ATTACK: Распределенная атака типа "отказ в обслуживании"
        PORT_SCAN: Сканирование портов для поиска уязвимостей
        SQL_INJECTION: SQL-инъекция в базу данных
        XSS_ATTACK: Межсайтовый скриптинг
        UNAUTHORIZED_ACCESS: Несанкционированный доступ
        SUSPICIOUS_BEHAVIOR: Подозрительное поведение
        MALWARE_UPLOAD: Загрузка вредоносного ПО
        DATA_EXFILTRATION: Утечка данных
        PRIVILEGE_ESCALATION: Повышение привилегий
    
    Example:
        >>> attack_type = IntrusionType.BRUTE_FORCE
        >>> print(attack_type.value)
        'brute_force'
        
        >>> # Проверка типа атаки
        >>> if attack_type == IntrusionType.BRUTE_FORCE:
        ...     print("Обнаружена атака перебора паролей")
    """
    BRUTE_FORCE = "brute_force"
    DDoS_ATTACK = "ddos_attack"
    PORT_SCAN = "port_scan"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    MALWARE_UPLOAD = "malware_upload"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"

def detect_intrusion_enhanced(
    self,
    event_data: Dict[str, Any],
    user_id: Optional[str] = None,
    user_age: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Обнаружение попыток вторжения с расширенной аналитикой.
    
    Этот метод анализирует входящие события на предмет признаков
    различных типов атак, используя машинное обучение и эвристические
    алгоритмы. Поддерживает семейную защиту с учетом возраста пользователей.
    
    Args:
        event_data (Dict[str, Any]): Данные события для анализа.
            Должен содержать:
            - source_ip (str): IP адрес источника
            - timestamp (str, optional): Время события в ISO формате
            - user_agent (str, optional): User-Agent браузера
            - failed_logins (int, optional): Количество неудачных попыток входа
            - request_count (int, optional): Количество запросов
            - sql_keywords (List[str], optional): SQL ключевые слова
            - script_tags (List[str], optional): HTML теги скриптов
        user_id (Optional[str]): Уникальный идентификатор пользователя.
            Используется для персонализированной защиты и истории.
            Defaults to None.
        user_age (Optional[int]): Возраст пользователя в годах.
            Используется для активации детской/пожилой защиты.
            Должен быть от 0 до 150. Defaults to None.
    
    Returns:
        List[Dict[str, Any]]: Список обнаруженных вторжений. Каждый элемент
            содержит:
            - attempt_id (str): Уникальный ID попытки
            - intrusion_type (IntrusionType): Тип обнаруженного вторжения
            - severity (IntrusionSeverity): Уровень серьезности
            - confidence (float): Уверенность в обнаружении (0.0-1.0)
            - source_ip (str): IP адрес источника
            - timestamp (datetime): Время обнаружения
            - description (str): Описание атаки
            - prevention_actions (List[PreventionAction]): Рекомендуемые действия
    
    Raises:
        ValueError: Если event_data пустой или содержит невалидные данные
        TypeError: Если user_age не является числом
        RuntimeError: Если произошла ошибка при анализе
    
    Example:
        >>> service = IntrusionPreventionService()
        >>> 
        >>> # Пример 1: Обнаружение атаки перебора паролей
        >>> event = {
        ...     'source_ip': '192.168.1.100',
        ...     'failed_logins': 15,
        ...     'timestamp': '2025-01-22T10:30:00Z',
        ...     'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        ... }
        >>> detections = service.detect_intrusion(event, 'user123', 25)
        >>> print(f"Обнаружено {len(detections)} атак")
        >>> for detection in detections:
        ...     print(f"Тип: {detection['intrusion_type']}, "
        ...           f"Серьезность: {detection['severity']}")
        
        >>> # Пример 2: Семейная защита для ребенка
        >>> child_event = {
        ...     'source_ip': '10.0.0.50',
        ...     'inappropriate_content': True,
        ...     'financial_requests': True
        ... }
        >>> child_detections = service.detect_intrusion(
        ...     child_event, 'child_user', 12
        ... )
        >>> # Активируется детская защита
        
        >>> # Пример 3: Обнаружение DDoS атаки
        >>> ddos_event = {
        ...     'source_ip': '203.0.113.1',
        ...     'request_count': 1000,
        ...     'high_request_volume': True,
        ...     'multiple_source_ips': True
        ... }
        >>> ddos_detections = service.detect_intrusion(ddos_event)
        >>> # Обнаружится DDoS атака с высокой серьезностью
    
    Note:
        - Метод использует кэширование для оптимизации производительности
        - Поддерживает параллельную обработку множественных паттернов
        - Автоматически применяет семейные правила защиты
        - Логирует все обнаружения для последующего анализа
    
    See Also:
        prevent_intrusion: Предотвращение обнаруженных атак
        get_intrusion_summary: Получение сводки по атакам
        _calculate_pattern_confidence: Расчет уверенности в паттерне
    
    Version:
        2.5
    
    Author:
        ALADDIN Security Team
    
    Since:
        1.0
    """
    pass

class IntrusionAttempt:
    """
    Представление попытки вторжения в системе безопасности.
    
    Этот dataclass содержит всю информацию о конкретной попытке
    вторжения, включая метаданные, временные метки и результаты анализа.
    
    Attributes:
        attempt_id (str): Уникальный идентификатор попытки.
            Формат: "intrusion_{timestamp}_{hash}"
        intrusion_type (IntrusionType): Тип обнаруженного вторжения.
        severity (IntrusionSeverity): Уровень серьезности атаки.
        source_ip (str): IP адрес источника атаки.
        user_id (Optional[str]): ID пользователя, если атака направлена
            на конкретного пользователя.
        timestamp (datetime): Время обнаружения попытки.
        description (str): Человекочитаемое описание атаки.
        status (IntrusionStatus): Текущий статус обработки попытки.
        prevention_actions (List[PreventionAction]): Список примененных
            или рекомендуемых действий предотвращения.
        metadata (Dict[str, Any]): Дополнительные метаданные атаки.
            Может содержать:
            - user_agent: User-Agent браузера
            - request_headers: HTTP заголовки
            - payload: Данные атаки
            - confidence: Уверенность в обнаружении
            - false_positive_probability: Вероятность ложного срабатывания
    
    Example:
        >>> from datetime import datetime
        >>> from security.active.intrusion_prevention import (
        ...     IntrusionType, IntrusionSeverity, IntrusionStatus
        ... )
        >>> 
        >>> # Создание попытки вторжения
        >>> attempt = IntrusionAttempt(
        ...     attempt_id="intrusion_1640995200000_abc12345",
        ...     intrusion_type=IntrusionType.BRUTE_FORCE,
        ...     severity=IntrusionSeverity.HIGH,
        ...     source_ip="192.168.1.100",
        ...     user_id="admin",
        ...     timestamp=datetime.now(),
        ...     description="Множественные неудачные попытки входа",
        ...     status=IntrusionStatus.DETECTED,
        ...     metadata={
        ...         "failed_attempts": 15,
        ...         "time_window": 300,
        ...         "confidence": 0.95
        ...     }
        ... )
        >>> 
        >>> print(f"Атака: {attempt.intrusion_type.value}")
        >>> print(f"Источник: {attempt.source_ip}")
        >>> print(f"Серьезность: {attempt.severity.value}")
    
    Note:
        - Все поля обязательны, кроме user_id
        - timestamp должен быть в UTC
        - attempt_id генерируется автоматически при создании
        - metadata может быть расширен для специфических типов атак
    
    See Also:
        IntrusionType: Типы вторжений
        IntrusionSeverity: Уровни серьезности
        IntrusionStatus: Статусы обработки
    """
    pass