"""
Реферальная программа: Функции интеграции с платежами
Готовые функции для интеграции в существующий код обработки платежей
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta


def process_referral_code_on_payment(
    db: Session,
    referral_code: Optional[str],
    payment_user_id: int,
    payment_amount: float
) -> Optional[int]:
    """
    Обработать реферальный код при создании платежа.
    
    Вызывается в /api/payments/create когда пользователь создает платеж.
    
    Args:
        db: Сессия базы данных (SQLAlchemy Session)
        referral_code: Реферальный код из запроса (может быть None)
        payment_user_id: ID пользователя, который оплачивает
        payment_amount: Сумма платежа (уже со скидкой -20% если применена)
    
    Returns:
        ID созданной записи в referrals или None
    
    Пример использования:
        @router.post("/api/payments/create")
        async def create_payment(
            payment_data: PaymentCreate,
            db: Session = Depends(get_db),
            current_user: dict = Depends(get_current_user)
        ):
            # ... существующая логика ...
            
            # ✅ ДОБАВИТЬ: Обработка реферального кода
            referral_id = process_referral_code_on_payment(
                db, payment_data.referralCode, current_user["id"], payment_data.amount
            )
            
            # ... остальная логика ...
    """
    if not referral_code:
        return None
    
    try:
        # 1. Найти реферальный код
        result = db.execute(
            text("SELECT user_id, code FROM referral_codes WHERE code = :code"),
            {"code": referral_code}
        )
        referral_code_obj = result.fetchone()
        
        if not referral_code_obj:
            # Код не найден - игнорируем (не ошибка)
            return None
        
        referrer_id = referral_code_obj[0]  # user_id
        
        # Проверить, что пользователь не приглашает сам себя
        if referrer_id == payment_user_id:
            # Нельзя использовать свой код
            return None
        
        # 2. Вычислить оригинальную цену (до скидки)
        # Если скидка 20%, то: original_price = amount / 0.8
        original_price = payment_amount / 0.8
        discount_applied = original_price - payment_amount
        
        # 3. Создать запись о реферале
        result = db.execute(
            text("""
                INSERT INTO referrals (referrer_id, invited_user_id, referral_code, status, discount_applied)
                VALUES (:referrer_id, :invited_user_id, :referral_code, 'pending', :discount_applied)
                ON CONFLICT (referrer_id, invited_user_id) DO NOTHING
                RETURNING id
            """),
            {
                "referrer_id": referrer_id,
                "invited_user_id": payment_user_id,
                "referral_code": referral_code,
                "discount_applied": discount_applied
            }
        )
        
        referral_id_row = result.fetchone()
        if referral_id_row:
            db.commit()
            return referral_id_row[0]
        else:
            # Запись уже существует - получить существующий ID
            existing = db.execute(
                text("""
                    SELECT id FROM referrals 
                    WHERE referrer_id = :referrer_id AND invited_user_id = :invited_user_id
                """),
                {"referrer_id": referrer_id, "invited_user_id": payment_user_id}
            ).fetchone()
            return existing[0] if existing else None
            
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка обработки реферального кода: {e}")
        return None


def process_referral_on_payment_confirmation(
    db: Session,
    payment_user_id: int,
    payment_amount: float
) -> bool:
    """
    Обработать реферальную программу при подтверждении оплаты.
    
    Вызывается когда платеж подтвержден (status = 'paid' или 'completed').
    
    Args:
        db: Сессия базы данных
        payment_user_id: ID пользователя, который оплатил
        payment_amount: Сумма платежа (уже со скидкой)
    
    Returns:
        True если реферальная программа обработана, False если нет
    
    Пример использования:
        @router.post("/api/payments/confirm")
        async def confirm_payment(
            payment_id: str,
            db: Session = Depends(get_db)
        ):
            payment = get_payment(payment_id, db)
            
            if payment.status == 'paid':
                # ✅ ДОБАВИТЬ: Обработка реферальной программы
                process_referral_on_payment_confirmation(db, payment.user_id, payment.amount)
            
            return {"status": "ok"}
    """
    try:
        # 1. Найти реферальную запись
        result = db.execute(
            text("""
                SELECT id, referrer_id, referral_code, status, discount_applied
                FROM referrals
                WHERE invited_user_id = :user_id AND status = 'pending'
                LIMIT 1
            """),
            {"user_id": payment_user_id}
        )
        referral = result.fetchone()
        
        if not referral or referral[3] != "pending":  # status
            return False  # Нет реферальной записи или уже обработана
        
        referral_id = referral[0]  # id
        referrer_id = referral[1]  # referrer_id
        
        # 2. Вычислить оригинальную цену и награду
        original_price = payment_amount / 0.8  # Восстанавливаем оригинальную цену
        reward_amount = original_price * 0.2  # 20% награда рефереру
        
        # 3. Обновить статус реферала
        db.execute(
            text("""
                UPDATE referrals
                SET status = 'completed',
                    converted_at = NOW(),
                    reward_amount = :reward_amount
                WHERE id = :referral_id
            """),
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
        db.execute(
            text("""
                INSERT INTO referral_discounts (user_id, discount_percent, valid_from, valid_until, referral_id)
                VALUES (:user_id, 20.0, :valid_from, :valid_until, :referral_id)
            """),
            {
                "user_id": referrer_id,
                "valid_from": next_month_start,
                "valid_until": next_month_end,
                "referral_id": referral_id
            }
        )
        
        db.commit()
        
        # 6. Опционально: Отправить уведомление рефереру
        # send_notification(referrer_id, "Ваш друг оплатил подписку! Вы получили скидку -20% на следующий месяц!")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка обработки реферальной программы: {e}")
        return False


def apply_referral_discount(
    db: Session,
    user_id: int,
    original_price: float
) -> float:
    """
    Применить реферальную скидку -20% к цене для реферера.
    
    Вызывается при создании платежа для реферера (когда у него есть активная скидка).
    
    Args:
        db: Сессия базы данных
        user_id: ID реферера
        original_price: Оригинальная цена (без скидки)
    
    Returns:
        Итоговая цена со скидкой
    
    Пример использования:
        @router.post("/api/payments/create")
        async def create_payment(
            payment_data: PaymentCreate,
            db: Session = Depends(get_db),
            current_user: dict = Depends(get_current_user)
        ):
            calculated_price = calculate_price(payment_data.tariff_id)
            
            # ✅ ДОБАВИТЬ: Применить скидку рефереру (если есть)
            final_price = apply_referral_discount(db, current_user["id"], calculated_price)
            payment_data.amount = final_price
            
            # ... остальная логика ...
    """
    try:
        # 1. Проверить, есть ли активная скидка
        result = db.execute(
            text("""
                SELECT id, discount_percent
                FROM referral_discounts
                WHERE user_id = :user_id
                  AND valid_until >= NOW()
                  AND used_at IS NULL
                ORDER BY valid_until ASC
                LIMIT 1
            """),
            {"user_id": user_id}
        )
        discount = result.fetchone()
        
        if not discount:
            return original_price  # Нет активной скидки
        
        # 2. Применить скидку
        discount_percent = float(discount[1])  # discount_percent
        discount_amount = original_price * (discount_percent / 100)
        final_price = original_price - discount_amount
        
        # 3. Пометить скидку как использованную
        db.execute(
            text("UPDATE referral_discounts SET used_at = NOW() WHERE id = :discount_id"),
            {"discount_id": discount[0]}  # id
        )
        db.commit()
        
        return final_price
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка применения скидки: {e}")
        return original_price  # В случае ошибки возвращаем оригинальную цену

