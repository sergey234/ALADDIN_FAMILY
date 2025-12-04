PAYMENT_METHODS = [
    {
        "id": "qr_sbp",
        "label": "QR / Система быстрых платежей",
        "banks": [
            "Сбербанк",
            "Тинькофф",
            "Альфа-Банк",
            "ВТБ",
            "Газпромбанк",
            "Россельхозбанк",
            "Совкомбанк",
            "Уралсиб",
            "Райффайзенбанк (RU)",
            "Московский кредитный банк",
            "Почта Банк",
            "Промсвязьбанк",
            "Росбанк",
            "Ситибанк (RU)",
            "Хоум Кредит",
            "МТС Банк",
            "Банк Открытие",
            "Ренессанс Кредит",
            "Русский Стандарт",
            "Синара",
            "Траст"
        ],
        "type": "qr"
    },
    {"id": "card_sber", "label": "Карта Сбербанк (Мир)", "banks": ["Сбербанк"], "type": "card"},
    {"id": "card_tinkoff", "label": "Карта Тинькофф", "banks": ["Тинькофф"], "type": "card"},
    {"id": "card_alfa", "label": "Карта Альфа-Банк", "banks": ["Альфа-Банк"], "type": "card"},
    {"id": "card_vtb", "label": "Карта ВТБ", "banks": ["ВТБ"], "type": "card"},
    {"id": "card_gpb", "label": "Карта Газпромбанк", "banks": ["Газпромбанк"], "type": "card"},
    {"id": "card_psb", "label": "Карта Промсвязьбанк", "banks": ["Промсвязьбанк"], "type": "card"},
    {"id": "card_rosselkhoz", "label": "Карта Россельхозбанк", "banks": ["Россельхозбанк"], "type": "card"},
    {"id": "card_uralsib", "label": "Карта Уралсиб", "banks": ["Уралсиб"], "type": "card"},
    {"id": "card_mkb", "label": "Карта МКБ", "banks": ["Московский кредитный банк"], "type": "card"},
    {"id": "card_rosbank", "label": "Карта Росбанк", "banks": ["Росбанк"], "type": "card"},
    {"id": "card_homecredit", "label": "Карта Хоум Кредит", "banks": ["Хоум Кредит"], "type": "card"},
    {"id": "card_mts", "label": "Карта МТС Банк", "banks": ["МТС Банк"], "type": "card"},
    {"id": "card_otkritie", "label": "Карта Банк Открытие", "banks": ["Банк Открытие"], "type": "card"},
    {"id": "card_rencredit", "label": "Карта Ренессанс Кредит", "banks": ["Ренессанс Кредит"], "type": "card"},
    {"id": "card_rsb", "label": "Карта Русский Стандарт", "banks": ["Русский Стандарт"], "type": "card"},
    {"id": "card_sinara", "label": "Карта Синара", "banks": ["Синара"], "type": "card"},
    {"id": "card_trust", "label": "Карта Траст", "banks": ["Траст"], "type": "card"},
    {"id": "sberpay", "label": "SberPay", "banks": ["Сбербанк"], "type": "pay_button"},
    {"id": "tinkoff_pay", "label": "Tinkoff Pay", "banks": ["Тинькофф"], "type": "pay_button"},
    {"id": "manual_transfer", "label": "Оплата на карту через СБП", "banks": [], "type": "manual"}
]

PAYMENT_METHOD_MAP = {method["id"]: method for method in PAYMENT_METHODS}


def get_payment_method(method_id: str):
    return PAYMENT_METHOD_MAP.get(method_id)


def list_payment_methods(visible_only: bool = True):
    """
    Возвращает список методов оплаты
    
    Args:
        visible_only: Если True, возвращает только видимые методы (из настроек).
                     Если False, возвращает все методы.
    
    Returns:
        Список методов оплаты
    """
    if not visible_only:
        return PAYMENT_METHODS
    
    # ✅ Получаем список видимых методов из настроек
    from app.config import settings
    
    visible_methods = set(
        method_id.strip() 
        for method_id in settings.visible_payment_methods.split(",") 
        if method_id.strip()
    )
    
    # Фильтруем методы: показываем только те, что в списке видимых
    filtered_methods = [
        method for method in PAYMENT_METHODS 
        if method["id"] in visible_methods
    ]
    
    return filtered_methods


def list_all_payment_methods():
    """Возвращает все методы оплаты (включая скрытые)"""
    return list_payment_methods(visible_only=False)

