# ============================================
# РЕФЕРАЛЬНАЯ ПРОГРАММА: Полная реализация на сервере
# ============================================
# Сервер: 149.154.65.180
# Дата: 22 ноября 2024
# ============================================

"""
Полная реализация реферальной программы для FastAPI/Python backend.

ИНСТРУКЦИЯ ПО ИНТЕГРАЦИИ:
1. Скопировать функции в ваш основной файл роутеров
2. Импортировать необходимые зависимости
3. Подключить роутеры в main.py
4. Настроить подключение к БД
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
from decimal import Decimal

# ============================================
# МОДЕЛИ ДАННЫХ (Pydantic)
# ============================================

class ReferralCodeResponse(BaseModel):
    referral_code: str
    referral_url: str
    qr_code: Optional[str] = None
    invitations_count: int
    earned_bonus: float
    invited_friends: List[dict]

class ReferralStatsResponse(BaseModel):
    total_referrals: int
    converted_referrals: int
    pending_referrals: int
    total_rewards: float
    conversion_rate: float
    referral_tier: str
    active_links: int

class ReferralHistoryItem(BaseModel):
    referral_id: int
    friend_id: int
    status: str
    created_at: datetime
    converted_at: Optional[datetime]
    referral_code: str
    discount_applied: float
    reward_amount: float

class ReferralRewardsResponse(BaseModel):
    total_converted: int
    rewards: List[dict]

class PaymentCreate(BaseModel):
    tariffId: str
    userAlias: str
    pin: str
    paymentMethod: str
    periodMonths: int
    amount: float
    referralCode: Optional[str] = None  # ✅ НОВОЕ: Реферальный код

# ============================================
# РОУТЕРЫ
# ============================================

router = APIRouter()

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ БД
# ============================================

class ReferralDB:
    """
    Класс для работы с реферальной программой в БД.
    Замените методы на реальные запросы к вашей БД.
    """
    
    @staticmethod
    def get_or_create_referral_code(user_id: int) -> dict:
        """
        Получить или создать реферальный код для пользователя.
        Использует функцию get_or_create_referral_code() из SQL.
        """
        # Пример для PostgreSQL:
        # SELECT get_or_create_referral_code(user_id);
        # Или через ORM:
        # referral = db.query(ReferralCode).filter_by(user_id=user_id).first()
        # if not referral:
        #     referral = ReferralCode(user_id=user_id, code=generate_code())
        #     db.add(referral)
        #     db.commit()
        # return referral
        pass
    
    @staticmethod
    def get_referral_code(code: str) -> Optional[dict]:
        """Найти реферальный код по коду."""
        # SELECT * FROM referral_codes WHERE code = ?
        pass
    
    @staticmethod
    def count_referrals(user_id: int) -> int:
        """Подсчитать количество приглашенных."""
        # SELECT COUNT(*) FROM referrals WHERE referrer_id = ?
        pass
    
    @staticmethod
    def count_converted_referrals(user_id: int) -> int:
        """Подсчитать количество оплативших."""
        # SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND status = 'completed'
        pass
    
    @staticmethod
    def calculate_earned_bonus(user_id: int) -> float:
        """Вычислить заработанный бонус."""
        # SELECT COALESCE(SUM(reward_amount), 0) FROM referrals WHERE referrer_id = ? AND status = 'completed'
        pass
    
    @staticmethod
    def get_invited_friends(user_id: int) -> List[dict]:
        """Получить список приглашенных друзей."""
        # SELECT * FROM referrals WHERE referrer_id = ? ORDER BY created_at DESC
        pass
    
    @staticmethod
    def create_referral(referrer_id: int, invited_user_id: int, referral_code: str, discount_applied: float) -> int:
        """
        Создать запись о реферале.
        Возвращает ID созданной записи.
        """
        # INSERT INTO referrals (referrer_id, invited_user_id, referral_code, status, discount_applied)
        # VALUES (?, ?, ?, 'pending', ?)
        # RETURNING id
        pass
    
    @staticmethod
    def get_referral_by_invited_user(invited_user_id: int) -> Optional[dict]:
        """Найти реферальную запись по ID приглашенного пользователя."""
        # SELECT * FROM referrals WHERE invited_user_id = ? AND status = 'pending' LIMIT 1
        pass
    
    @staticmethod
    def update_referral(referral_id: int, status: str, converted_at: datetime, reward_amount: float):
        """Обновить статус реферала."""
        # UPDATE referrals SET status = ?, converted_at = ?, reward_amount = ? WHERE id = ?
        pass
    
    @staticmethod
    def create_referral_discount(user_id: int, discount_percent: float, valid_from: datetime, valid_until: datetime, referral_id: int):
        """Создать скидку для реферера."""
        # INSERT INTO referral_discounts (user_id, discount_percent, valid_from, valid_until, referral_id)
        # VALUES (?, ?, ?, ?, ?)
        pass
    
    @staticmethod
    def get_active_referral_discount(user_id: int, current_date: datetime) -> Optional[dict]:
        """
        Получить активную скидку для пользователя.
        Скидка активна, если valid_until >= current_date AND used_at IS NULL
        """
        # SELECT * FROM referral_discounts 
        # WHERE user_id = ? AND valid_until >= ? AND used_at IS NULL
        # ORDER BY valid_until ASC LIMIT 1
        pass
    
    @staticmethod
    def mark_discount_as_used(discount_id: int, used_at: datetime):
        """Пометить скидку как использованную."""
        # UPDATE referral_discounts SET used_at = ? WHERE id = ?
        pass

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def verify_token(token: str) -> Optional[dict]:
    """
    Проверить токен авторизации и вернуть данные пользователя.
    Замените на вашу функцию проверки токена.
    """
    # Ваша логика проверки JWT токена
    # return {"id": user_id, "email": user_email, ...}
    pass

def calculate_next_month_start() -> datetime:
    """Вычислить начало следующего месяца."""
    now = datetime.now()
    if now.month == 12:
        return datetime(now.year + 1, 1, 1)
    return datetime(now.year, now.month + 1, 1)

def calculate_next_month_end() -> datetime:
    """Вычислить конец следующего месяца."""
    next_month_start = calculate_next_month_start()
    if next_month_start.month == 12:
        return datetime(next_month_start.year + 1, 1, 1) - timedelta(days=1)
    return datetime(next_month_start.year, next_month_start.month + 1, 1) - timedelta(days=1)

def get_referral_tier(converted_count: int) -> str:
    """Определить уровень реферальной программы."""
    if converted_count >= 10:
        return "gold"
    elif converted_count >= 5:
        return "silver"
    else:
        return "bronze"

# ============================================
# API ENDPOINTS
# ============================================

@router.get("/api/referral/code")
async def get_referral_code(request: Request):
    """
    Получить реферальный код пользователя и статистику.
    Требует авторизации.
    """
    # 1. Проверить токен
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # 2. Найти или создать код
    referral_code_obj = ReferralDB.get_or_create_referral_code(user["id"])
    if not referral_code_obj:
        raise HTTPException(status_code=500, detail="Failed to create referral code")
    
    # 3. Посчитать статистику
    invitations_count = ReferralDB.count_referrals(user["id"])
    earned_bonus = ReferralDB.calculate_earned_bonus(user["id"])
    invited_friends = ReferralDB.get_invited_friends(user["id"])
    
    # 4. Сформировать ответ
    return ReferralCodeResponse(
        referral_code=referral_code_obj["code"],
        referral_url=f"https://aladdin-ai.ru/invite/{referral_code_obj['code']}",
        qr_code=None,  # Опционально: сгенерировать QR код
        invitations_count=invitations_count,
        earned_bonus=float(earned_bonus),
        invited_friends=invited_friends
    )

@router.get("/api/referral/stats")
async def get_referral_stats(request: Request):
    """
    Получить статистику реферальной программы.
    Требует авторизации.
    """
    # 1. Проверить токен
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # 2. Посчитать статистику
    total_referrals = ReferralDB.count_referrals(user["id"])
    converted_referrals = ReferralDB.count_converted_referrals(user["id"])
    pending_referrals = total_referrals - converted_referrals
    total_rewards = ReferralDB.calculate_earned_bonus(user["id"])
    
    # 3. Вычислить конверсию
    conversion_rate = (converted_referrals / total_referrals * 100) if total_referrals > 0 else 0.0
    
    # 4. Определить уровень
    referral_tier = get_referral_tier(converted_referrals)
    
    # 5. Активные ссылки (за последние 30 дней)
    # TODO: Реализовать подсчет активных ссылок
    active_links = 1  # Заглушка
    
    return ReferralStatsResponse(
        total_referrals=total_referrals,
        converted_referrals=converted_referrals,
        pending_referrals=pending_referrals,
        total_rewards=float(total_rewards),
        conversion_rate=conversion_rate,
        referral_tier=referral_tier,
        active_links=active_links
    )

@router.get("/api/referral/history")
async def get_referral_history(request: Request):
    """
    Получить историю приглашений.
    Требует авторизации.
    """
    # 1. Проверить токен
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # 2. Получить историю
    referrals = ReferralDB.get_invited_friends(user["id"])
    
    # 3. Преобразовать в формат ответа
    history = []
    for ref in referrals:
        history.append(ReferralHistoryItem(
            referral_id=ref["id"],
            friend_id=ref["invited_user_id"],
            status=ref["status"],
            created_at=ref["created_at"],
            converted_at=ref.get("converted_at"),
            referral_code=ref["referral_code"],
            discount_applied=float(ref.get("discount_applied", 0)),
            reward_amount=float(ref.get("reward_amount", 0))
        ))
    
    return history

@router.get("/api/referral/rewards")
async def get_referral_rewards(request: Request):
    """
    Получить информацию о наградах.
    Требует авторизации.
    """
    # 1. Проверить токен
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # 2. Посчитать количество оплативших
    total_converted = ReferralDB.count_converted_referrals(user["id"])
    
    # 3. Определить награды (заглушка)
    rewards = [
        {
            "reward_id": "reward_1",
            "title_key": "referral_reward_1_title",
            "subtitle_key": "referral_reward_1_subtitle",
            "amount_key": "referral_reward_1_amount",
            "reward_value": "10%",
            "icon": "percent.circle.fill",
            "required_converted": 1,
            "status": "unlocked" if total_converted >= 1 else "locked",
            "remaining": max(0, 1 - total_converted),
            "unlocked_at": datetime.now() if total_converted >= 1 else None
        }
    ]
    
    return ReferralRewardsResponse(
        total_converted=total_converted,
        rewards=rewards
    )

# ============================================
# ОБРАБОТКА РЕФЕРАЛЬНОГО КОДА ПРИ ОПЛАТЕ
# ============================================

def process_referral_code_on_payment(payment_data: PaymentCreate, payment_user_id: int) -> Optional[int]:
    """
    Обработать реферальный код при создании платежа.
    Возвращает ID созданной записи в referrals или None.
    """
    if not payment_data.referralCode:
        return None
    
    # 1. Найти реферальный код
    referral_code_obj = ReferralDB.get_referral_code(payment_data.referralCode)
    if not referral_code_obj:
        # Код не найден - игнорируем
        return None
    
    # 2. Вычислить оригинальную цену (до скидки)
    # Если скидка 20%, то: original_price = amount / 0.8
    original_price = payment_data.amount / 0.8
    discount_applied = original_price - payment_data.amount
    
    # 3. Создать запись о реферале
    referral_id = ReferralDB.create_referral(
        referrer_id=referral_code_obj["user_id"],
        invited_user_id=payment_user_id,
        referral_code=payment_data.referralCode,
        discount_applied=discount_applied
    )
    
    return referral_id

def process_referral_on_payment_confirmation(payment_user_id: int, payment_amount: float):
    """
    Обработать реферальную программу при подтверждении оплаты.
    Вызывается когда платеж подтвержден (status = 'paid').
    """
    # 1. Найти реферальную запись
    referral = ReferralDB.get_referral_by_invited_user(payment_user_id)
    if not referral or referral["status"] != "pending":
        return  # Нет реферальной записи или уже обработана
    
    # 2. Вычислить оригинальную цену и награду
    original_price = payment_amount / 0.8  # Восстанавливаем оригинальную цену
    reward_amount = original_price * 0.2  # 20% награда рефереру
    
    # 3. Обновить статус реферала
    ReferralDB.update_referral(
        referral_id=referral["id"],
        status="completed",
        converted_at=datetime.now(),
        reward_amount=reward_amount
    )
    
    # 4. Начислить скидку -20% рефереру на следующий месяц
    next_month_start = calculate_next_month_start()
    next_month_end = calculate_next_month_end()
    
    ReferralDB.create_referral_discount(
        user_id=referral["referrer_id"],
        discount_percent=20.0,
        valid_from=next_month_start,
        valid_until=next_month_end,
        referral_id=referral["id"]
    )
    
    # 5. Опционально: Отправить уведомление рефереру
    # send_notification(referral["referrer_id"], "Ваш друг оплатил подписку! Вы получили скидку -20% на следующий месяц!")

def apply_referral_discount(user_id: int, original_price: float) -> float:
    """
    Применить реферальную скидку -20% к цене для реферера.
    Вызывается при создании платежа для реферера.
    
    Возвращает итоговую цену со скидкой.
    """
    # 1. Проверить, есть ли активная скидка
    discount = ReferralDB.get_active_referral_discount(user_id, datetime.now())
    
    if not discount:
        return original_price  # Нет активной скидки
    
    # 2. Применить скидку
    discount_amount = original_price * (discount["discount_percent"] / 100)
    final_price = original_price - discount_amount
    
    # 3. Пометить скидку как использованную
    ReferralDB.mark_discount_as_used(discount["id"], datetime.now())
    
    return final_price

# ============================================
# ИНТЕГРАЦИЯ В СУЩЕСТВУЮЩИЙ КОД
# ============================================

"""
ИНСТРУКЦИЯ ПО ИНТЕГРАЦИИ:

1. В вашем файле /api/payments/create:
   
   @router.post("/api/payments/create")
   async def create_payment(payment_data: PaymentCreate):
       # ... существующая логика создания платежа ...
       
       # ✅ ДОБАВИТЬ: Обработка реферального кода
       referral_id = process_referral_code_on_payment(payment_data, new_user_id)
       
       # ... остальная логика ...
       return {"paymentId": payment.id, ...}

2. В вашем файле /api/payments/status/{payment_id}:
   
   @router.get("/api/payments/status/{payment_id}")
   async def check_payment_status(payment_id: str):
       payment = get_payment(payment_id)
       
       # ... существующая логика проверки статуса ...
       
       if payment.status == 'paid':
           # ✅ ДОБАВИТЬ: Обработка реферальной программы
           process_referral_on_payment_confirmation(payment.user_id, payment.amount)
       
       return {"status": payment.status, ...}

3. При создании платежа для реферера (если это не приглашенный):
   
   @router.post("/api/payments/create")
   async def create_payment(payment_data: PaymentCreate):
       # ... вычисление цены ...
       
       # ✅ ДОБАВИТЬ: Применить скидку рефереру, если есть
       if not payment_data.referralCode:  # Если это не приглашенный
           final_amount = apply_referral_discount(current_user.id, calculated_price)
           payment_data.amount = final_amount
       
       # ... остальная логика ...
"""

# ============================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================

"""
# Пример 1: Приглашенный оплачивает подписку
payment_data = PaymentCreate(
    tariffId="family",
    userAlias="newUser",
    pin="1234",
    paymentMethod="qr_sbp",
    periodMonths=12,
    amount=800.0,  # Уже со скидкой -20%
    referralCode="ABC123"  # ✅ Реферальный код
)

# При создании платежа:
referral_id = process_referral_code_on_payment(payment_data, new_user_id)
# → Создается запись в referrals (status: pending)

# При подтверждении оплаты:
process_referral_on_payment_confirmation(new_user_id, 800.0)
# → Обновляется статус на completed
# → Начисляется скидка -20% рефереру на следующий месяц

# Пример 2: Реферер оплачивает следующий месяц
original_price = 1000.0
final_price = apply_referral_discount(referrer_user_id, original_price)
# → final_price = 800.0 (скидка -20% применена)
"""

