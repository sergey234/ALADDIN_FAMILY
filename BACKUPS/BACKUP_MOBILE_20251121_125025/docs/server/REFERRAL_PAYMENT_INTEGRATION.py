# ============================================
# РЕФЕРАЛЬНАЯ ПРОГРАММА: Интеграция в оплату
# ============================================
# Сервер: 149.154.65.180
# Дата: 22 ноября 2024
# ============================================

"""
ГОТОВЫЕ ФУНКЦИИ ДЛЯ ИНТЕГРАЦИИ В СУЩЕСТВУЮЩИЙ КОД ОПЛАТЫ.

ИНСТРУКЦИЯ:
1. Скопировать функции в ваш файл обработки платежей
2. Вызвать функции в нужных местах
3. Настроить подключение к БД
"""

from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal

# ============================================
# ФУНКЦИЯ 1: Обработка реферального кода при создании платежа
# ============================================

def process_referral_code_on_payment(
    db_session,  # Ваша сессия БД (SQLAlchemy Session)
    referral_code: Optional[str],
    payment_user_id: int,
    payment_amount: float
) -> Optional[int]:
    """
    Обработать реферальный код при создании платежа.
    
    Args:
        db_session: Сессия базы данных
        referral_code: Реферальный код из запроса (может быть None)
        payment_user_id: ID пользователя, который оплачивает
        payment_amount: Сумма платежа (уже со скидкой -20%)
    
    Returns:
        ID созданной записи в referrals или None
    
    Использование:
        referral_id = process_referral_code_on_payment(
            db, payment_data.referralCode, new_user_id, payment_data.amount
        )
    """
    if not referral_code:
        return None
    
    try:
        # 1. Найти реферальный код
        referral_code_obj = db_session.execute(
            "SELECT user_id, code FROM referral_codes WHERE code = :code",
            {"code": referral_code}
        ).fetchone()
        
        if not referral_code_obj:
            # Код не найден - игнорируем (не ошибка)
            return None
        
        referrer_id = referral_code_obj.user_id
        
        # Проверить, что пользователь не приглашает сам себя
        if referrer_id == payment_user_id:
            # Нельзя использовать свой код
            return None
        
        # 2. Вычислить оригинальную цену (до скидки)
        # Если скидка 20%, то: original_price = amount / 0.8
        original_price = payment_amount / 0.8
        discount_applied = original_price - payment_amount
        
        # 3. Создать запись о реферале
        result = db_session.execute(
            """
            INSERT INTO referrals (referrer_id, invited_user_id, referral_code, status, discount_applied)
            VALUES (:referrer_id, :invited_user_id, :referral_code, 'pending', :discount_applied)
            ON CONFLICT (referrer_id, invited_user_id) DO NOTHING
            RETURNING id
            """,
            {
                "referrer_id": referrer_id,
                "invited_user_id": payment_user_id,
                "referral_code": referral_code,
                "discount_applied": discount_applied
            }
        )
        
        referral_id = result.fetchone()
        if referral_id:
            db_session.commit()
            return referral_id[0]
        else:
            # Запись уже существует
            existing = db_session.execute(
                "SELECT id FROM referrals WHERE referrer_id = :referrer_id AND invited_user_id = :invited_user_id",
                {"referrer_id": referrer_id, "invited_user_id": payment_user_id}
            ).fetchone()
            return existing[0] if existing else None
            
    except Exception as e:
        db_session.rollback()
        print(f"❌ Ошибка обработки реферального кода: {e}")
        return None

# ============================================
# ФУНКЦИЯ 2: Обработка реферальной программы при подтверждении оплаты
# ============================================

def process_referral_on_payment_confirmation(
    db_session,  # Ваша сессия БД
    payment_user_id: int,
    payment_amount: float
) -> bool:
    """
    Обработать реферальную программу при подтверждении оплаты.
    Вызывается когда платеж подтвержден (status = 'paid').
    
    Args:
        db_session: Сессия базы данных
        payment_user_id: ID пользователя, который оплатил
        payment_amount: Сумма платежа (уже со скидкой)
    
    Returns:
        True если реферальная программа обработана, False если нет
    
    Использование:
        if payment.status == 'paid':
            process_referral_on_payment_confirmation(db, payment.user_id, payment.amount)
    """
    try:
        # 1. Найти реферальную запись
        referral = db_session.execute(
            """
            SELECT id, referrer_id, referral_code, status, discount_applied
            FROM referrals
            WHERE invited_user_id = :user_id AND status = 'pending'
            LIMIT 1
            """,
            {"user_id": payment_user_id}
        ).fetchone()
        
        if not referral or referral.status != "pending":
            return False  # Нет реферальной записи или уже обработана
        
        referral_id = referral.id
        referrer_id = referral.referrer_id
        
        # 2. Вычислить оригинальную цену и награду
        original_price = payment_amount / 0.8  # Восстанавливаем оригинальную цену
        reward_amount = original_price * 0.2  # 20% награда рефереру
        
        # 3. Обновить статус реферала
        db_session.execute(
            """
            UPDATE referrals
            SET status = 'completed',
                converted_at = NOW(),
                reward_amount = :reward_amount
            WHERE id = :referral_id
            """,
            {
                "referral_id": referral_id,
                "reward_amount": reward_amount
            }
        )
        
        # 4. Вычислить даты для скидки (следующий месяц)
        now = datetime.now()
        if now.month == 12:
            next_month_start = datetime(now.year + 1, 1, 1)
            next_month_end = datetime(now.year + 1, 2, 1) - timedelta(days=1)
        else:
            next_month_start = datetime(now.year, now.month + 1, 1)
            if now.month + 1 == 12:
                next_month_end = datetime(now.year + 1, 1, 1) - timedelta(days=1)
            else:
                next_month_end = datetime(now.year, now.month + 2, 1) - timedelta(days=1)
        
        # 5. Начислить скидку -20% рефереру на следующий месяц
        db_session.execute(
            """
            INSERT INTO referral_discounts (user_id, discount_percent, valid_from, valid_until, referral_id)
            VALUES (:user_id, 20.0, :valid_from, :valid_until, :referral_id)
            """,
            {
                "user_id": referrer_id,
                "valid_from": next_month_start,
                "valid_until": next_month_end,
                "referral_id": referral_id
            }
        )
        
        db_session.commit()
        
        # 6. Опционально: Отправить уведомление рефереру
        # send_notification(referrer_id, "Ваш друг оплатил подписку! Вы получили скидку -20% на следующий месяц!")
        
        return True
        
    except Exception as e:
        db_session.rollback()
        print(f"❌ Ошибка обработки реферальной программы: {e}")
        return False

# ============================================
# ФУНКЦИЯ 3: Применение скидки рефереру при оплате
# ============================================

def apply_referral_discount(
    db_session,  # Ваша сессия БД
    user_id: int,
    original_price: float
) -> float:
    """
    Применить реферальную скидку -20% к цене для реферера.
    Вызывается при создании платежа для реферера.
    
    Args:
        db_session: Сессия базы данных
        user_id: ID реферера
        original_price: Оригинальная цена (без скидки)
    
    Returns:
        Итоговая цена со скидкой
    
    Использование:
        final_price = apply_referral_discount(db, current_user.id, calculated_price)
        payment_data.amount = final_price
    """
    try:
        # 1. Проверить, есть ли активная скидка
        discount = db_session.execute(
            """
            SELECT id, discount_percent
            FROM referral_discounts
            WHERE user_id = :user_id
              AND valid_until >= NOW()
              AND used_at IS NULL
            ORDER BY valid_until ASC
            LIMIT 1
            """,
            {"user_id": user_id}
        ).fetchone()
        
        if not discount:
            return original_price  # Нет активной скидки
        
        # 2. Применить скидку
        discount_percent = float(discount.discount_percent)
        discount_amount = original_price * (discount_percent / 100)
        final_price = original_price - discount_amount
        
        # 3. Пометить скидку как использованную
        db_session.execute(
            "UPDATE referral_discounts SET used_at = NOW() WHERE id = :discount_id",
            {"discount_id": discount.id}
        )
        db_session.commit()
        
        return final_price
        
    except Exception as e:
        db_session.rollback()
        print(f"❌ Ошибка применения скидки: {e}")
        return original_price  # В случае ошибки возвращаем оригинальную цену

# ============================================
# ПРИМЕРЫ ИНТЕГРАЦИИ
# ============================================

"""
ПРИМЕР 1: Интеграция в /api/payments/create

@router.post("/api/payments/create")
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ... существующая логика создания платежа ...
    
    # ✅ ДОБАВИТЬ: Обработка реферального кода
    referral_id = process_referral_code_on_payment(
        db, payment_data.referralCode, new_user_id, payment_data.amount
    )
    
    # ✅ ДОБАВИТЬ: Если это реферер (не приглашенный), применить скидку
    if not payment_data.referralCode:
        final_amount = apply_referral_discount(db, current_user.id, calculated_price)
        payment_data.amount = final_amount
    
    # ... остальная логика ...
    return {"paymentId": payment.id, ...}

ПРИМЕР 2: Интеграция в /api/payments/status/{payment_id}

@router.get("/api/payments/status/{payment_id}")
async def check_payment_status(
    payment_id: str,
    db: Session = Depends(get_db)
):
    payment = get_payment(payment_id, db)
    
    # ... существующая логика проверки статуса ...
    
    if payment.status == 'paid':
        # ✅ ДОБАВИТЬ: Обработка реферальной программы
        process_referral_on_payment_confirmation(db, payment.user_id, payment.amount)
    
    return {"status": payment.status, ...}
"""

