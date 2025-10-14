# ИЕРАРХИЯ КЛАССОВ: PHISHING_PROTECTION_AGENT.PY

## 📅 Дата анализа: $(date +%Y%m%d_%H%M%S)

---

## 🏗️ СТРУКТУРА КЛАССОВ

### 1. Enum классы (Перечисления)
```
Enum
├── PhishingType (строка 20)
│   ├── EMAIL = "email"
│   ├── SMS = "sms"
│   ├── WEBSITE = "website"
│   ├── SOCIAL_MEDIA = "social_media"
│   ├── VOICE = "voice"
│   ├── QR_CODE = "qr_code"
│   └── UNKNOWN = "unknown"
│
├── ThreatLevel (строка 32)
│   ├── LOW = "low"
│   ├── MEDIUM = "medium"
│   ├── HIGH = "high"
│   └── CRITICAL = "critical"
│
└── DetectionMethod (строка 41)
    ├── URL_ANALYSIS = "url_analysis"
    ├── CONTENT_ANALYSIS = "content_analysis"
    ├── DOMAIN_ANALYSIS = "domain_analysis"
    ├── BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    ├── MACHINE_LEARNING = "machine_learning"
    ├── BLACKLIST = "blacklist"
    └── WHITELIST = "whitelist"
```

### 2. Data классы (Структуры данных)
```
object
├── PhishingIndicator (строка 54) - @dataclass
│   ├── indicator_id: str
│   ├── name: str
│   ├── phishing_type: PhishingType
│   ├── threat_level: ThreatLevel
│   ├── pattern: str
│   ├── description: str
│   ├── detection_method: DetectionMethod
│   ├── confidence: float
│   ├── created_at: str
│   ├── is_active: bool
│   ├── to_dict() -> Dict[str, Any]
│   └── from_dict(data: Dict[str, Any]) -> PhishingIndicator
│
├── PhishingDetection (строка 103) - @dataclass
│   ├── detection_id: str
│   ├── source: str
│   ├── phishing_type: PhishingType
│   ├── threat_level: ThreatLevel
│   ├── confidence: float
│   ├── detected_at: str
│   ├── indicators: List[PhishingIndicator]
│   ├── details: Dict[str, Any]
│   └── to_dict() -> Dict[str, Any]
│
└── PhishingReport (строка 158) - @dataclass
    ├── report_id: str
    ├── user_id: Optional[str]
    ├── source: str
    ├── phishing_type: PhishingType
    ├── threat_level: ThreatLevel
    ├── confidence: float
    ├── created_at: str
    ├── status: str
    ├── details: Dict[str, Any]
    └── to_dict() -> Dict[str, Any]
```

### 3. Основной класс
```
object
└── PhishingProtectionAgent (строка 206)
    ├── __init__(name: str = "PhishingProtectionAgent")
    ├── name: str
    ├── indicators: List[PhishingIndicator]
    ├── detections: List[PhishingDetection]
    ├── reports: List[PhishingReport]
    ├── blocked_domains: set
    ├── trusted_domains: set
    └── suspicious_keywords: List[str]
```

---

## 🔍 АНАЛИЗ НАСЛЕДОВАНИЯ

### Базовые классы
- **Enum классы:** Наследуют от `Enum`
- **Data классы:** Наследуют от `object` (через @dataclass)
- **Основной класс:** Наследует от `object`

### MRO (Method Resolution Order)
- **PhishingType:** `PhishingType → Enum → object`
- **PhishingProtectionAgent:** `PhishingProtectionAgent → object`

### Полиморфизм
- ✅ Enum классы поддерживают полиморфизм через наследование от Enum
- ✅ Data классы используют полиморфизм через общие методы `to_dict()`
- ✅ Основной класс использует полиморфизм через методы работы с разными типами данных

---

## 📊 СТАТИСТИКА КЛАССОВ

- **Всего классов:** 7
- **Enum классов:** 3
- **Data классов:** 3
- **Основных классов:** 1
- **С наследованием:** 3 (Enum классы)
- **Без наследования:** 4 (Data классы + основной)

---

## ✅ ВЫВОДЫ

1. **Структура:** Хорошо организованная иерархия классов
2. **Наследование:** Правильное использование Enum и dataclass
3. **Полиморфизм:** Эффективно реализован через общие интерфейсы
4. **Типизация:** Полная типизация всех атрибутов и методов
5. **Документация:** Все классы имеют docstring