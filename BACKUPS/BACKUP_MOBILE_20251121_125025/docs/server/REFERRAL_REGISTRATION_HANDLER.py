"""
============================================
РЕФЕРАЛЬНАЯ ПРОГРАММА: Обработка регистрации
============================================
Сервер: 149.154.65.180
Дата: 21 ноября 2024
============================================
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

# Импорты ваших моделей и зависимостей
# from app.database import get_db
# from app.auth import get_current_user
# from app.models import User, ReferralCode, Referral

router = APIRouter()


# ============================================
# МОДЕЛИ
# ============================================

class UserRegistration(BaseModel):
    email: str
    password: str
    name: str
    referral_code: Optional[str] = None  # Реферальный код из ?ref=ABC123


class RegistrationResponse(BaseModel):
    success: bool
    user_id: str
    message: str


# ============================================
# ОБРАБОТКА РЕГИСТРАЦИИ С РЕФЕРАЛЬНЫМ КОДОМ
# ============================================

@router.post("/api/register", response_model=RegistrationResponse)
async def register_user(
    user_data: UserRegistration,
    # db: Session = Depends(get_db)
):
    """
    Регистрация пользователя с обработкой реферального кода.
    
    Если передан referral_code, создается запись в таблице referrals
    со status='pending' (реферал засчитывается только при оплате).
    """
    # 1. Создать пользователя
    # new_user = create_user(user_data)
    # 
    # # 2. Если есть реферальный код, создать запись в referrals
    # if user_data.referral_code:
    #     # Проверить, что код существует
    #     referral_code_obj = db.query(ReferralCode).filter(
    #         ReferralCode.code == user_data.referral_code
    #     ).first()
    #     
    #     if referral_code_obj:
    #         # Проверить, что пользователь не приглашает сам себя
    #         if referral_code_obj.user_id == new_user.id:
    #             raise HTTPException(
    #                 status_code=400,
    #                 detail="Нельзя использовать свой собственный реферальный код"
    #             )
    #         
    #         # Создать запись о реферале
    #         referral = Referral(
    #             referrer_id=referral_code_obj.user_id,
    #             invited_user_id=new_user.id,
    #             referral_code=user_data.referral_code,
    #             status="pending"  # Пока не оплатил
    #         )
    #         db.add(referral)
    #         db.commit()
    #         
    #         return RegistrationResponse(
    #             success=True,
    #             user_id=str(new_user.id),
    #             message=f"Регистрация успешна. Реферальный код {user_data.referral_code} применен."
    #         )
    #     else:
    #         # Код не найден, но регистрация продолжается
    #         return RegistrationResponse(
    #             success=True,
    #             user_id=str(new_user.id),
    #             message="Регистрация успешна. Реферальный код не найден."
    #         )
    
    # Временный ответ для тестирования
    return RegistrationResponse(
        success=True,
        user_id="123",
        message="Регистрация успешна"
    )


# ============================================
# JAVASCRIPT ДЛЯ ФРОНТЕНДА (страница /register)
# ============================================

"""
// На странице регистрации (/register)

// 1. Проверить параметр ?ref=ABC123 в URL
const urlParams = new URLSearchParams(window.location.search);
const referralCode = urlParams.get('ref');

if (referralCode) {
    // Сохранить код в localStorage
    localStorage.setItem('referral_code', referralCode);
    
    // Показать сообщение пользователю
    showMessage(`Вы приглашены по коду: ${referralCode}. Вы оба получите скидку -20%!`);
}

// 2. При отправке формы регистрации
function submitRegistration(formData) {
    const referralCode = localStorage.getItem('referral_code');
    
    if (referralCode) {
        formData.referral_code = referralCode;
    }
    
    // Отправить на сервер
    fetch('/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Регистрация успешна
            localStorage.removeItem('referral_code'); // Очистить после использования
            window.location.href = '/dashboard';
        }
    })
    .catch(error => {
        console.error('Ошибка регистрации:', error);
    });
}
"""

