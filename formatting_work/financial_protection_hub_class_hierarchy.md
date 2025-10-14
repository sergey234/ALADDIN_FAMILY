# Иерархия классов financial_protection_hub.py

## Структура классов

### 1. Перечисления (Enums)
```
Enum
├── BankType
│   ├── SBERBANK
│   ├── VTB
│   ├── TINKOFF
│   ├── ALFA_BANK
│   ├── RAIFFEISEN
│   ├── GAZPROMBANK
│   └── ROSSELKHOZBANK
├── TransactionType
│   ├── TRANSFER
│   ├── PAYMENT
│   ├── WITHDRAWAL
│   ├── DEPOSIT
│   ├── CARD_PAYMENT
│   ├── ONLINE_PAYMENT
│   └── CRYPTO_TRANSACTION
└── RiskFactor
    ├── LARGE_AMOUNT
    ├── UNUSUAL_TIME
    ├── UNKNOWN_RECIPIENT
    ├── FOREIGN_COUNTRY
    ├── CRYPTO_CURRENCY
    ├── SUSPICIOUS_PATTERN
    ├── HIGH_FREQUENCY
    └── EMERGENCY_TRANSACTION
```

### 2. Датаклассы (DataClasses)
```
@dataclass
├── TransactionData
│   ├── transaction_id: str
│   ├── user_id: str
│   ├── amount: float
│   ├── currency: str
│   ├── recipient: str
│   ├── recipient_account: str
│   ├── transaction_type: TransactionType
│   ├── description: str
│   ├── timestamp: datetime
│   ├── bank: BankType
│   ├── location: Optional[str]
│   ├── ip_address: Optional[str]
│   └── device_info: Optional[Dict[str, Any]]
├── RiskAssessment
│   ├── transaction_id: str
│   ├── risk_score: float
│   ├── risk_factors: List[RiskFactor]
│   ├── risk_level: str
│   ├── confidence: float
│   ├── recommended_action: str
│   ├── family_notification_required: bool
│   ├── bank_verification_required: bool
│   └── additional_checks: List[str]
└── BankIntegration
    ├── bank_name: str
    ├── api_endpoint: str
    ├── api_key: str
    ├── is_active: bool
    ├── last_check: datetime
    └── success_rate: float
```

### 3. Основной класс
```
SecurityBase
└── FinancialProtectionHub
    ├── __init__(config: Optional[Dict[str, Any]])
    ├── _initialize_bank_integrations()
    ├── _initialize_security_rules()
    ├── _initialize_fraud_patterns()
    ├── analyze_transaction()
    ├── _analyze_risk_factors()
    ├── _calculate_risk_score()
    ├── _determine_risk_level()
    ├── _determine_recommended_action()
    ├── _determine_additional_checks()
    ├── _is_unknown_recipient()
    ├── _is_foreign_transaction()
    ├── _is_crypto_transaction()
    ├── _has_suspicious_pattern()
    ├── _is_high_frequency_transaction()
    ├── _block_transaction()
    ├── _notify_family_about_transaction()
    ├── verify_with_bank()
    ├── get_protection_statistics()
    └── get_status()
```

## Наследование и полиморфизм

### Наследование:
- **FinancialProtectionHub** наследует от **SecurityBase**
- **BankType, TransactionType, RiskFactor** наследуют от **Enum**
- **TransactionData, RiskAssessment, BankIntegration** - dataclasses (не наследуют)

### Полиморфизм:
- Методы **FinancialProtectionHub** переопределяют базовые методы **SecurityBase**
- Использование **Enum** для типизированных констант
- **@dataclass** автоматически генерирует методы `__init__`, `__repr__`, `__eq__`

## Атрибуты классов

### FinancialProtectionHub:
- `bank_integrations` - интеграции с банками
- `security_rules` - правила безопасности  
- `fraud_patterns` - паттерны мошенничества
- `total_transactions` - общее количество транзакций
- `blocked_transactions` - заблокированные транзакции
- `family_notifications` - уведомления семьи
- `protected_amount` - защищенная сумма
- `fraud_detections` - обнаружения мошенничества
- `max_daily_amount` - максимальная сумма в день
- `max_single_amount` - максимальная сумма за раз
- `suspicious_amount_threshold` - порог подозрительной суммы
- `emergency_amount_threshold` - порог экстренной суммы