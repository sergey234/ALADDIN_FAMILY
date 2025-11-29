# 🤖 ИНСТРУКЦИЯ ДЛЯ ML МОДЕЛИ: РЕАЛИЗАЦИЯ IoT ЗАЩИТЫ

**Дата:** 04.11.2025  
**Статус:** ✅ **ПОЛНАЯ ИНСТРУКЦИЯ ГОТОВА**

---

## 🎯 ЦЕЛЬ ЗАДАЧИ

**Реализовать защиту умного дома (IoT Security) для системы ALADDIN**

**Результат:**
- ✅ IoT угрозы: **0% → 100%** (0/10 → 10/10)
- ✅ Покрытие системы: **81% → 91%** (81/100 → 91/100)
- ✅ Готово к продакшену

---

## 📋 ОБЩАЯ СТРУКТУРА ЗАДАЧИ

### **4 ФАЗЫ РЕАЛИЗАЦИИ:**

1. **ФАЗА 1.1:** IoT Security Agent (Backend) - 1-2 недели
2. **ФАЗА 1.2:** IoT Security Module (iOS) - 1 неделя
3. **ФАЗА 1.3:** IoT Security UI Screen (iOS) - 2-3 дня
4. **ФАЗА 1.4:** IoT API Endpoints (Backend) - 2-3 дня

**ИТОГО:** 2-3 недели | $70K-100K

---

## 🔴 ФАЗА 1.1: IoT SECURITY AGENT (BACKEND)

### **ЗАДАЧА: Создать IoT Security Agent на Python Backend**

**Файл:** `security/ai_agents/iot_security_agent.py` (НОВЫЙ файл)

**Расположение:** `ALADDIN_NEW/security/ai_agents/iot_security_agent.py`

**Время:** 1-2 недели  
**Стоимость:** $40K-60K

---

### **ШАГ 1.1.1: Создать базовую структуру класса**

```python
"""
IoT Security Agent - Защита умного дома
Покрывает: 10 IoT угроз
"""

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
        super().__init__()
        self.agent_name = "IoT Security Agent"
        self.version = "1.0.0"
        
    async def scan_iot_devices(self, home_id: str) -> List[Dict]:
        """
        Сканирование всех IoT устройств в сети
        
        Args:
            home_id: ID умного дома
            
        Returns:
            List[Dict]: Список обнаруженных IoT устройств
        """
        # TODO: Реализовать сканирование
        pass
```

**Критерии успеха:**
- ✅ Класс создан
- ✅ Наследуется от `SecurityBase`
- ✅ Имеет базовую структуру
- ✅ Документация добавлена

---

### **ШАГ 1.1.2: Реализовать scan_iot_devices()**

```python
async def scan_iot_devices(self, home_id: str) -> List[Dict]:
    """
    Сканирование всех IoT устройств в сети
    
    Технологии:
    - Network scanning (nmap, arp-scan)
    - Device fingerprinting
    - AI анализ устройств
    
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
```

**Критерии успеха:**
- ✅ Обнаруживает все IoT устройства в сети
- ✅ Определяет тип, производителя, модель
- ✅ Возвращает структурированные данные

---

### **ШАГ 1.1.3: Реализовать detect_camera_intrusion()**

```python
async def detect_camera_intrusion(self, device_id: str) -> Dict:
    """
    Обнаружение вторжения в камеры
    
    Анализирует:
    - Подозрительные подключения к камере
    - Неавторизованный доступ
    - Необычные запросы к камере
    - Изменения в настройках камеры
    
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
    
    return threat_detection
```

**Критерии успеха:**
- ✅ Обнаруживает вторжения в камеры
- ✅ Определяет уровень угрозы
- ✅ Предоставляет рекомендации

---

### **ШАГ 1.1.4: Реализовать detect_speaker_eavesdropping()**

```python
async def detect_speaker_eavesdropping(self, device_id: str) -> Dict:
    """
    Обнаружение подслушивания через умные колонки
    
    Анализирует:
    - Подозрительные голосовые команды
    - Неавторизованный доступ к микрофону
    - Необычные запросы к колонке
    - Активация без команды
    
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
    
    return threat_detection
```

**Критерии успеха:**
- ✅ Обнаруживает подслушивание
- ✅ Анализирует голосовые команды
- ✅ Предупреждает пользователя

---

### **ШАГ 1.1.5: Реализовать detect_weak_passwords()**

```python
async def detect_weak_passwords(self, device_id: str) -> Dict:
    """
    Обнаружение слабых паролей
    
    Проверяет:
    - Длина пароля (минимум 8 символов)
    - Сложность пароля (буквы, цифры, символы)
    - Использование словарных слов
    - Повторяющиеся символы
    
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
    
    return security_issue
```

**Критерии успеха:**
- ✅ Обнаруживает слабые пароли
- ✅ Проверяет сложность
- ✅ Предоставляет рекомендации

---

### **ШАГ 1.1.6: Реализовать block_compromised_device()**

```python
async def block_compromised_device(self, device_id: str) -> bool:
    """
    Блокировка скомпрометированного устройства
    
    Действия:
    - Блокировка устройства в сети
    - Изоляция от остальных устройств
    - Уведомление пользователя
    - Логирование события
    
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
```

**Критерии успеха:**
- ✅ Блокирует устройство
- ✅ Изолирует от сети
- ✅ Уведомляет пользователя

---

### **ШАГ 1.1.7: Реализовать monitor_voice_commands()**

```python
async def monitor_voice_commands(self, device_id: str) -> List[Dict]:
    """
    Мониторинг голосовых команд
    
    Анализирует:
    - Все голосовые команды в реальном времени
    - Подозрительные команды
    - Манипуляции с командами
    - Неавторизованные команды
    
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
    
    return threat_detections
```

**Критерии успеха:**
- ✅ Мониторит голосовые команды
- ✅ Обнаруживает подозрительные команды
- ✅ Блокирует опасные команды

---

### **ШАГ 1.1.8: Реализовать protect_smart_home()**

```python
async def protect_smart_home(self, home_id: str) -> Dict:
    """
    Комплексная защита умного дома
    
    Агрегирует:
    - Все обнаруженные устройства
    - Все обнаруженные угрозы
    - Все рекомендации
    - Общий статус безопасности
    
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
        if device["type"] == "camera":
            threat = await self.detect_camera_intrusion(device["id"])
            if threat["threat_detected"]:
                threats.append(threat)
        
        if device["type"] == "speaker":
            threat = await self.detect_speaker_eavesdropping(device["id"])
            if threat["threat_detected"]:
                threats.append(threat)
        
        # Проверка паролей
        password_issue = await self.detect_weak_passwords(device["id"])
        if password_issue["issue_detected"]:
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
```

**Критерии успеха:**
- ✅ Агрегирует все данные
- ✅ Вычисляет уровень защиты
- ✅ Генерирует рекомендации

---

### **ШАГ 1.1.9: Реализовать detect_default_credentials()**

```python
async def detect_default_credentials(self, device_id: str) -> Dict:
    """
    Обнаружение дефолтных креденшейлов
    
    Проверяет:
    - Использование дефолтных паролей
    - Использование дефолтных логинов
    - Сравнение с базой дефолтных паролей
    
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
    
    return security_issue
```

**Критерии успеха:**
- ✅ Обнаруживает дефолтные пароли
- ✅ Проверяет против базы данных
- ✅ Предоставляет рекомендации

---

### **ШАГ 1.1.10: Реализовать detect_physical_tampering()**

```python
async def detect_physical_tampering(self, device_id: str) -> Dict:
    """
    Обнаружение физического вмешательства
    
    Анализирует:
    - Изменения в устройстве
    - Детекция физического доступа
    - Предупреждения о краже
    
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
    
    return threat_detection
```

**Критерии успеха:**
- ✅ Обнаруживает физическое вмешательство
- ✅ Анализирует изменения
- ✅ Предупреждает о краже

---

### **ШАГ 1.1.11: Реализовать analyze_iot_traffic()**

```python
async def analyze_iot_traffic(self, device_id: str) -> Dict:
    """
    Анализ IoT трафика
    
    Анализирует:
    - Сетевой трафик устройства
    - Обнаружение подозрительной активности
    - ML анализ трафика
    
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
    
    return network_analysis
```

**Критерии успеха:**
- ✅ Анализирует трафик
- ✅ Обнаруживает подозрительную активность
- ✅ Предоставляет рекомендации

---

### **ШАГ 1.1.12: Зарегистрировать все функции в SFM**

```python
# В файле security/ai_agents/iot_security_agent.py

from security.sfm import SafeFunctionManager

# После создания класса IoTSecurityAgent

def register_iot_functions():
    """Регистрация всех IoT функций в SFM"""
    sfm = SafeFunctionManager()
    agent = IoTSecurityAgent()
    
    # Регистрация функций
    sfm.register_function(
        name="iot_scan_devices",
        function=agent.scan_iot_devices,
        category="iot",
        priority="high",
        description="Сканирование IoT устройств"
    )
    
    sfm.register_function(
        name="iot_detect_camera_intrusion",
        function=agent.detect_camera_intrusion,
        category="iot",
        priority="critical",
        description="Обнаружение вторжения в камеры"
    )
    
    sfm.register_function(
        name="iot_detect_speaker_eavesdropping",
        function=agent.detect_speaker_eavesdropping,
        category="iot",
        priority="critical",
        description="Обнаружение подслушивания через колонки"
    )
    
    sfm.register_function(
        name="iot_detect_weak_passwords",
        function=agent.detect_weak_passwords,
        category="iot",
        priority="high",
        description="Обнаружение слабых паролей"
    )
    
    sfm.register_function(
        name="iot_block_compromised_device",
        function=agent.block_compromised_device,
        category="iot",
        priority="critical",
        description="Блокировка скомпрометированного устройства"
    )
    
    sfm.register_function(
        name="iot_monitor_voice_commands",
        function=agent.monitor_voice_commands,
        category="iot",
        priority="high",
        description="Мониторинг голосовых команд"
    )
    
    sfm.register_function(
        name="iot_protect_smart_home",
        function=agent.protect_smart_home,
        category="iot",
        priority="critical",
        description="Комплексная защита умного дома"
    )
    
    sfm.register_function(
        name="iot_detect_default_credentials",
        function=agent.detect_default_credentials,
        category="iot",
        priority="high",
        description="Обнаружение дефолтных креденшейлов"
    )
    
    sfm.register_function(
        name="iot_detect_physical_tampering",
        function=agent.detect_physical_tampering,
        category="iot",
        priority="high",
        description="Обнаружение физического вмешательства"
    )
    
    sfm.register_function(
        name="iot_analyze_traffic",
        function=agent.analyze_iot_traffic,
        category="iot",
        priority="medium",
        description="Анализ IoT трафика"
    )

# Вызвать при инициализации
register_iot_functions()
```

**Критерии успеха:**
- ✅ Все 10 функций зарегистрированы в SFM
- ✅ Правильные категории и приоритеты
- ✅ Функции доступны через SFM

---

## 📱 ФАЗА 1.2: IoT SECURITY MODULE (iOS)

### **ЗАДАЧА: Создать iOS модуль для запросов к API**

**Файл:** `Core/IoT/IoTSecurityModule.swift` (НОВЫЙ файл)

**Расположение:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/Core/IoT/IoTSecurityModule.swift`

**Время:** 1 неделя  
**Стоимость:** $20K-30K

---

### **ШАГ 1.2.1: Создать базовую структуру класса**

```swift
import Foundation
import Combine

/// 🏡 IoT Security Module
/// ТОЛЬКО запросы к API, НИКАКОЙ бизнес-логики
class IoTSecurityModule: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var iotDevices: [IoTDevice] = []
    @Published var threatsDetected: [IoTThreat] = []
    @Published var isScanning: Bool = false
    
    // MARK: - Private Properties
    
    private let apiService: APIService
    
    // MARK: - Initialization
    
    init(apiService: APIService) {
        self.apiService = apiService
    }
}
```

**Критерии успеха:**
- ✅ Класс создан
- ✅ Наследуется от `ObservableObject`
- ✅ Имеет `@Published` свойства
- ✅ Принимает `APIService` в конструкторе

---

### **ШАГ 1.2.2: Реализовать scanDevices()**

```swift
/// ТОЛЬКО запрос к API
func scanDevices(homeId: String) async throws {
    isScanning = true
    defer { isScanning = false }
    
    // ПРОСТО запрос к серверу
    let response = try await apiService.getIoTDevices(homeId: homeId)
    
    // Обновление UI
    await MainActor.run {
        iotDevices = response.devices
        threatsDetected = response.threats
    }
}
```

**Критерии успеха:**
- ✅ Отправляет запрос к API
- ✅ Обновляет UI
- ✅ Обрабатывает ошибки

---

### **ШАГ 1.2.3: Реализовать monitorCameras()**

```swift
/// ТОЛЬКО запрос к API
func monitorCameras(homeId: String) async throws {
    let response = try await apiService.getIoTThreats(homeId: homeId)
    
    // Фильтрация угроз по камерам
    await MainActor.run {
        threatsDetected = response.filter { $0.type == .camera }
    }
}
```

**Критерии успеха:**
- ✅ Отправляет запрос к API
- ✅ Фильтрует угрозы по камерам
- ✅ Обновляет UI

---

### **ШАГ 1.2.4: Реализовать checkPasswords()**

```swift
/// ТОЛЬКО запрос к API
func checkPasswords(homeId: String) async throws {
    let response = try await apiService.getIoTStatus(homeId: homeId)
    
    // Отображаем рекомендации с сервера
    await MainActor.run {
        // Рекомендации уже в response.recommendations
        // Просто отображаем их в UI
    }
}
```

**Критерии успеха:**
- ✅ Отправляет запрос к API
- ✅ Получает рекомендации
- ✅ Обновляет UI

---

### **ШАГ 1.2.5: Реализовать blockDevice()**

```swift
/// ТОЛЬКО команда на сервер
func blockDevice(_ deviceId: String) async throws {
    try await apiService.blockIoTDevice(deviceId: deviceId)
    
    // Обновляем список устройств
    // Получаем homeId из текущего контекста
    if let homeId = currentHomeId {
        await scanDevices(homeId: homeId)
    }
}
```

**Критерии успеха:**
- ✅ Отправляет команду на сервер
- ✅ Обновляет список устройств
- ✅ Обрабатывает ошибки

---

### **ШАГ 1.2.6: Реализовать alertCompromised()**

```swift
/// ТОЛЬКО уведомление пользователя
func alertCompromised(_ device: IoTDevice) {
    // Показываем уведомление
    NotificationManager.shared.show(
        title: "⚠️ Устройство скомпрометировано",
        message: "\(device.name) требует внимания",
        type: .warning
    )
}
```

**Критерии успеха:**
- ✅ Показывает уведомление
- ✅ Использует NotificationManager
- ✅ Правильный тип уведомления

---

## 🎨 ФАЗА 1.3: IoT SECURITY UI SCREEN (iOS)

### **ЗАДАЧА: Создать UI экран для IoT устройств**

**Файл:** `Screens/IoTSecurityScreen.swift` (НОВЫЙ файл)

**Расположение:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/Screens/IoTSecurityScreen.swift`

**Время:** 2-3 дня  
**Стоимость:** $5K-10K

---

### **ШАГ 1.3.1: Создать базовую структуру экрана**

```swift
import SwiftUI

/// 🏡 IoT Security Screen
/// ТОЛЬКО UI, НИКАКОЙ бизнес-логики
struct IoTSecurityScreen: View {
    @StateObject private var viewModel = IoTSecurityViewModel()
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // TODO: Добавить компоненты
            }
            .padding()
        }
        .onAppear {
            Task {
                await viewModel.loadStatus()
            }
        }
    }
}
```

**Критерии успеха:**
- ✅ Экран создан
- ✅ Использует ViewModel
- ✅ Загружает данные при появлении

---

### **ШАГ 1.3.2: Создать SecurityStatusCard**

```swift
/// Карточка статуса безопасности
struct SecurityStatusCard: View {
    let devicesCount: Int
    let threatsCount: Int
    let protectionLevel: Int
    
    var body: some View {
        VStack(spacing: 12) {
            Text("Статус безопасности")
                .font(.headline)
            
            HStack {
                VStack {
                    Text("\(devicesCount)")
                        .font(.title)
                    Text("Устройств")
                        .font(.caption)
                }
                
                Spacer()
                
                VStack {
                    Text("\(threatsCount)")
                        .font(.title)
                        .foregroundColor(threatsCount > 0 ? .red : .green)
                    Text("Угроз")
                        .font(.caption)
                }
                
                Spacer()
                
                VStack {
                    Text("\(protectionLevel)%")
                        .font(.title)
                        .foregroundColor(protectionLevelColor)
                    Text("Защита")
                        .font(.caption)
                }
            }
        }
        .padding()
        .background(Color.cardBackground)
        .cornerRadius(12)
    }
}
```

**Критерии успеха:**
- ✅ Отображает статус безопасности
- ✅ Показывает количество устройств
- ✅ Показывает количество угроз
- ✅ Показывает уровень защиты

---

### **ШАГ 1.3.3: Создать DevicesListSection**

```swift
/// Список IoT устройств
struct DevicesListSection: View {
    let devices: [IoTDevice]
    let onBlock: (String) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Устройства")
                .font(.headline)
            
            ForEach(devices) { device in
                DeviceRow(
                    device: device,
                    onBlock: { onBlock(device.id) }
                )
            }
        }
        .padding()
        .background(Color.cardBackground)
        .cornerRadius(12)
    }
}
```

**Критерии успеха:**
- ✅ Отображает список устройств
- ✅ Показывает статус каждого устройства
- ✅ Имеет кнопку блокировки

---

### **ШАГ 1.3.4: Создать ThreatsSection**

```swift
/// Секция с обнаруженными угрозами
struct ThreatsSection: View {
    let threats: [IoTThreat]
    let onFix: (String) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Обнаруженные угрозы")
                .font(.headline)
                .foregroundColor(threats.isEmpty ? .green : .red)
            
            if threats.isEmpty {
                Text("Угроз не обнаружено")
                    .foregroundColor(.green)
            } else {
                ForEach(threats) { threat in
                    ThreatRow(
                        threat: threat,
                        onFix: { onFix(threat.id) }
                    )
                }
            }
        }
        .padding()
        .background(Color.cardBackground)
        .cornerRadius(12)
    }
}
```

**Критерии успеха:**
- ✅ Отображает список угроз
- ✅ Показывает уровень угрозы
- ✅ Имеет кнопку исправления

---

### **ШАГ 1.3.5: Создать RecommendationsSection**

```swift
/// Секция с рекомендациями
struct RecommendationsSection: View {
    let recommendations: [String]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Рекомендации")
                .font(.headline)
            
            ForEach(recommendations, id: \.self) { recommendation in
                HStack {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.blue)
                    Text(recommendation)
                        .font(.body)
                }
            }
        }
        .padding()
        .background(Color.cardBackground)
        .cornerRadius(12)
    }
}
```

**Критерии успеха:**
- ✅ Отображает рекомендации
- ✅ Понятный формат
- ✅ Иконки для визуализации

---

### **ШАГ 1.3.6: Добавить pull-to-refresh**

```swift
.refreshable {
    await viewModel.refreshStatus()
}
```

**Критерии успеха:**
- ✅ Pull-to-refresh работает
- ✅ Обновляет данные
- ✅ Показывает индикатор загрузки

---

## 🔌 ФАЗА 1.4: IoT API ENDPOINTS (BACKEND)

### **ЗАДАЧА: Создать API endpoints для iOS**

**Расположение:** `ALADDIN_NEW/security/api/routers/iot_router.py` (НОВЫЙ файл)

**Время:** 2-3 дня  
**Стоимость:** $5K-10K

---

### **ШАГ 1.4.1: Создать базовую структуру роутера**

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from security.ai_agents.iot_security_agent import IoTSecurityAgent

router = APIRouter(prefix="/api/iot", tags=["IoT Security"])

# Инициализация агента
iot_agent = IoTSecurityAgent()
```

**Критерии успеха:**
- ✅ Роутер создан
- ✅ Правильный префикс
- ✅ Агент инициализирован

---

### **ШАГ 1.4.2: Реализовать GET /api/iot/status/{home_id}**

```python
@router.get("/status/{home_id}")
async def get_iot_status(home_id: str) -> Dict:
    """
    Возвращает готовый статус безопасности
    
    Returns:
        {
            "devices": [...],
            "threats": [...],
            "recommendations": [...],
            "protection_level": 85,
            "last_scan": "2025-11-04T10:30:00Z"
        }
    """
    try:
        status = await iot_agent.protect_smart_home(home_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Критерии успеха:**
- ✅ Endpoint работает
- ✅ Возвращает статус
- ✅ Обрабатывает ошибки

---

### **ШАГ 1.4.3: Реализовать GET /api/iot/devices/{home_id}**

```python
@router.get("/devices/{home_id}")
async def get_iot_devices(home_id: str) -> Dict:
    """
    Возвращает список устройств с анализом
    
    Returns:
        {
            "devices": [...],
            "total": 15,
            "compromised": 2,
            "safe": 13
        }
    """
    try:
        devices = await iot_agent.scan_iot_devices(home_id)
        
        compromised = [d for d in devices if d.get("status") == "compromised"]
        safe = [d for d in devices if d.get("status") == "safe"]
        
        return {
            "devices": devices,
            "total": len(devices),
            "compromised": len(compromised),
            "safe": len(safe)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Критерии успеха:**
- ✅ Endpoint работает
- ✅ Возвращает список устройств
- ✅ Возвращает статистику

---

### **ШАГ 1.4.4: Реализовать POST /api/iot/scan/{home_id}**

```python
@router.post("/scan/{home_id}")
async def start_iot_scan(home_id: str) -> Dict:
    """
    Запускает сканирование устройств
    
    Returns:
        {
            "status": "scanning",
            "estimated_time": 300  # секунд
        }
    """
    try:
        # Запускаем сканирование в фоне
        # TODO: Реализовать асинхронное сканирование
        
        return {
            "status": "scanning",
            "estimated_time": 300
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Критерии успеха:**
- ✅ Endpoint работает
- ✅ Запускает сканирование
- ✅ Возвращает статус

---

### **ШАГ 1.4.5: Реализовать POST /api/iot/device/{device_id}/block**

```python
@router.post("/device/{device_id}/block")
async def block_iot_device(device_id: str) -> Dict:
    """
    Блокирует устройство
    
    Returns:
        {
            "status": "blocked",
            "device_id": "device_123"
        }
    """
    try:
        success = await iot_agent.block_compromised_device(device_id)
        
        if success:
            return {
                "status": "blocked",
                "device_id": device_id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to block device")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Критерии успеха:**
- ✅ Endpoint работает
- ✅ Блокирует устройство
- ✅ Возвращает статус

---

### **ШАГ 1.4.6: Реализовать GET /api/iot/threats/{home_id}**

```python
@router.get("/threats/{home_id}")
async def get_iot_threats(home_id: str) -> Dict:
    """
    Возвращает список угроз
    
    Returns:
        {
            "threats": [...],
            "total": 5,
            "high": 2,
            "medium": 2,
            "low": 1
        }
    """
    try:
        status = await iot_agent.protect_smart_home(home_id)
        threats = status.get("threats", [])
        
        high = [t for t in threats if t.get("severity") == "high"]
        medium = [t for t in threats if t.get("severity") == "medium"]
        low = [t for t in threats if t.get("severity") == "low"]
        
        return {
            "threats": threats,
            "total": len(threats),
            "high": len(high),
            "medium": len(medium),
            "low": len(low)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Критерии успеха:**
- ✅ Endpoint работает
- ✅ Возвращает список угроз
- ✅ Возвращает статистику

---

### **ШАГ 1.4.7: Реализовать POST /api/iot/fix/{threat_id}**

```python
@router.post("/fix/{threat_id}")
async def fix_iot_threat(threat_id: str) -> Dict:
    """
    Исправляет проблему
    
    Returns:
        {
            "status": "fixed",
            "threat_id": "threat_456",
            "recommendations": ["Перезагрузить устройство"]
        }
    """
    try:
        # TODO: Реализовать исправление проблемы
        # Это может включать автоматическое исправление или рекомендации
        
        return {
            "status": "fixed",
            "threat_id": threat_id,
            "recommendations": ["Перезагрузить устройство"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Критерии успеха:**
- ✅ Endpoint работает
- ✅ Исправляет проблему
- ✅ Возвращает рекомендации

---

### **ШАГ 1.4.8: Добавить валидацию и обработку ошибок**

```python
from pydantic import BaseModel, Field

class IoTScanRequest(BaseModel):
    home_id: str = Field(..., description="ID умного дома")

class IoTBlockRequest(BaseModel):
    device_id: str = Field(..., description="ID устройства")

# Добавить валидацию во все endpoints
@router.post("/scan/{home_id}")
async def start_iot_scan(home_id: str, request: IoTScanRequest) -> Dict:
    # Валидация
    if not home_id or not request.home_id:
        raise HTTPException(status_code=400, detail="home_id is required")
    
    # Обработка ошибок
    try:
        # ... код ...
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Критерии успеха:**
- ✅ Валидация запросов
- ✅ Обработка ошибок
- ✅ Правильные HTTP коды

---

### **ШАГ 1.4.9: Добавить документацию API**

```python
from fastapi import APIRouter
from fastapi.openapi.utils import get_openapi

# Добавить описания к каждому endpoint
@router.get("/status/{home_id}", 
    summary="Получить статус безопасности",
    description="Возвращает готовый статус безопасности умного дома",
    response_description="Статус безопасности с устройствами, угрозами и рекомендациями"
)
async def get_iot_status(home_id: str) -> Dict:
    # ... код ...
```

**Критерии успеха:**
- ✅ Документация добавлена
- ✅ Swagger UI работает
- ✅ Все endpoints документированы

---

## 🧪 ФАЗА 1.5: ИНТЕГРАЦИЯ И ТЕСТИРОВАНИЕ

### **ШАГ 1.5.1: Протестировать IoT Security Agent на сервере**

**Что тестировать:**
- ✅ Все 10 методов работают
- ✅ Все методы возвращают правильные данные
- ✅ Все методы обрабатывают ошибки
- ✅ Все функции зарегистрированы в SFM

**Как тестировать:**
```python
# tests/test_iot_security_agent.py
import pytest
from security.ai_agents.iot_security_agent import IoTSecurityAgent

@pytest.mark.asyncio
async def test_scan_iot_devices():
    agent = IoTSecurityAgent()
    devices = await agent.scan_iot_devices("home_123")
    assert len(devices) > 0
    assert all("id" in d for d in devices)

@pytest.mark.asyncio
async def test_detect_camera_intrusion():
    agent = IoTSecurityAgent()
    threat = await agent.detect_camera_intrusion("device_123")
    assert "threat_detected" in threat
    # ... другие проверки ...
```

**Критерии успеха:**
- ✅ Все тесты проходят
- ✅ Все методы работают
- ✅ Обработка ошибок работает

---

### **ШАГ 1.5.2: Протестировать iOS модуль с реальными API**

**Что тестировать:**
- ✅ Все методы отправляют запросы к API
- ✅ Все методы обновляют UI
- ✅ Все методы обрабатывают ошибки

**Как тестировать:**
```swift
// Tests/IoTSecurityModuleTests.swift
import XCTest
@testable import ALADDIN

class IoTSecurityModuleTests: XCTestCase {
    func testScanDevices() async throws {
        let module = IoTSecurityModule(apiService: MockAPIService())
        try await module.scanDevices(homeId: "home_123")
        XCTAssertFalse(module.iotDevices.isEmpty)
    }
}
```

**Критерии успеха:**
- ✅ Все тесты проходят
- ✅ Все методы работают
- ✅ Обработка ошибок работает

---

### **ШАГ 1.5.3: Протестировать UI Screen на реальных устройствах**

**Что тестировать:**
- ✅ Экран отображается правильно
- ✅ Все компоненты работают
- ✅ Данные загружаются
- ✅ Pull-to-refresh работает

**Критерии успеха:**
- ✅ Экран работает на iPhone
- ✅ Все компоненты отображаются
- ✅ Данные загружаются корректно

---

### **ШАГ 1.5.4: Проверить покрытие всех 10 IoT угроз**

**Что проверять:**
- ✅ Все 10 IoT угроз покрыты методами
- ✅ Все методы работают
- ✅ Все угрозы детектируются

**Чеклист:**
- ✅ IoT device compromise → `scan_iot_devices()`
- ✅ Smart home infiltration → `protect_smart_home()`
- ✅ Compromised cameras → `detect_camera_intrusion()`
- ✅ Smart speaker eavesdropping → `detect_speaker_eavesdropping()`
- ✅ Home network breaches → `analyze_iot_traffic()`
- ✅ Smart device data leaks → `analyze_iot_traffic()`
- ✅ Voice command manipulation → `monitor_voice_commands()`
- ✅ Weak IoT passwords → `detect_weak_passwords()`
- ✅ Default credential abuse → `detect_default_credentials()`
- ✅ Physical device theft → `detect_physical_tampering()`

**Критерии успеха:**
- ✅ Все 10 угроз покрыты
- ✅ Все методы работают
- ✅ Детекция работает корректно

---

### **ШАГ 1.5.5: Проверить производительность**

**Что проверять:**
- ✅ iOS код: **-90%** (с 500 строк до 50)
- ✅ CPU на iOS: **-100%** (всё на сервере)
- ✅ Батарея: **-95%** (минимальная нагрузка)

**Как проверить:**
```bash
# Проверка размера кода
wc -l Core/IoT/IoTSecurityModule.swift

# Проверка использования CPU
# Использовать Instruments в Xcode

# Проверка использования батареи
# Использовать Energy Log в Xcode
```

**Критерии успеха:**
- ✅ iOS код: ~50 строк (вместо 500)
- ✅ CPU: минимальная нагрузка
- ✅ Батарея: минимальная нагрузка

---

## 📋 ЧЕКЛИСТ ДЛЯ ML МОДЕЛИ

### **ПЕРЕД НАЧАЛОМ РАБОТЫ:**

- [ ] Прочитать документ `ВСЕ_РЕШЕНИЯ_IoT_УМНЫЙ_ДОМ.md`
- [ ] Понять архитектуру (90% сервер, 10% iOS)
- [ ] Изучить существующие агенты для примера
- [ ] Изучить SFM (Safe Function Manager) для регистрации

### **ПОСЛЕ КАЖДОГО ШАГА:**

- [ ] Проверить код на ошибки
- [ ] Убедиться, что код соответствует требованиям
- [ ] Проверить, что код интегрируется с существующей системой
- [ ] Обновить TODO лист

### **ПОСЛЕ ЗАВЕРШЕНИЯ:**

- [ ] Все тесты проходят
- [ ] Все функции зарегистрированы в SFM
- [ ] Все API endpoints работают
- [ ] iOS модуль работает
- [ ] UI экран работает
- [ ] Покрытие всех 10 IoT угроз

---

## ✅ КРИТЕРИИ УСПЕХА ВСЕГО ПРОЕКТА

### **Функциональность:**
- ✅ IoT Security Agent создан и работает
- ✅ iOS модуль интегрирован
- ✅ API endpoints работают
- ✅ UI отображает устройства и угрозы
- ✅ Обнаружение 10 типов IoT угроз

### **Производительность:**
- ✅ iOS код: **-90%** (с 500 строк до 50)
- ✅ CPU на iOS: **-100%** (с 100% до 0%)
- ✅ Батарея: **-95%** (с высокой нагрузки до минимальной)
- ✅ Размер приложения: **-80%** (без ML моделей)

### **Покрытие:**
- ✅ IoT угрозы: **0% → 100%** (0/10 → 10/10)

---

## 🎯 ГОТОВО К РЕАЛИЗАЦИИ!

**Все инструкции готовы:**
- ✅ Детальные инструкции для каждой фазы
- ✅ Примеры кода для каждого шага
- ✅ Критерии успеха для каждого шага
- ✅ Чеклист для проверки

**Статус:** ✅ **ГОТОВО К РЕАЛИЗАЦИИ!**

---

**Дата создания:** 04.11.2025  
**Последнее обновление:** 04.11.2025  
**Версия:** 1.0

