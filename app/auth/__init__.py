import os

# ✅ JWT-011: Унифицированный JWT_SECRET (совпадает с auth.py и jwt_service.py)
# JWT константы для использования в других модулях
JWT_SECRET = os.getenv("JWT_SECRET", "aladdin-super-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Экспортируем все функции из auth.py
from .auth import decode_token, get_current_user, get_current_user_optional

__all__ = ["JWT_SECRET", "JWT_ALGORITHM", "decode_token", "get_current_user", "get_current_user_optional"]
