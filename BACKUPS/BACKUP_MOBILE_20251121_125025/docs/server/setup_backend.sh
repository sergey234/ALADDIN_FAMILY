#!/usr/bin/expect -f
set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== 🚀 НАСТРОЙКА BACKEND ==="
puts ""

# 1. Создание структуры директорий
puts "📦 Шаг 1: Создание структуры..."
spawn ssh $server "mkdir -p /opt/aladdin-backend/app/{routers,models,database}"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 2. Копирование database.py
puts ""
puts "📤 Шаг 2: Копирование database.py..."
spawn scp docs/server/database.py $server:/opt/aladdin-backend/app/database/database.py
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 3. Копирование main.py
puts ""
puts "📤 Шаг 3: Копирование main.py..."
spawn scp docs/server/main.py $server:/opt/aladdin-backend/main.py
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 4. Создание __init__.py файлов
puts ""
puts "📝 Шаг 4: Создание __init__.py файлов..."
spawn ssh $server "touch /opt/aladdin-backend/app/__init__.py /opt/aladdin-backend/app/routers/__init__.py /opt/aladdin-backend/app/database/__init__.py"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 5. Обновление referral.py с правильными импортами
puts ""
puts "🔧 Шаг 5: Обновление referral.py..."
spawn ssh $server "cat > /opt/aladdin-backend/app/routers/referral.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

# Модели ответов
class ReferralOverviewResponse(BaseModel):
    referral_code: str
    referral_url: str
    invitations_count: int = 0
    earned_bonus: float = 0.0
    invited_friends: List[dict] = []

@router.get(\"/code\")
async def get_referral_code(
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user)  # Раскомментировать когда будет auth
):
    # Заглушка - нужно реализовать логику
    return ReferralOverviewResponse(
        referral_code=\"ABC123\",
        referral_url=\"https://aladdin-ai.ru/invite/ABC123\",
        invitations_count=0,
        earned_bonus=0.0,
        invited_friends=[]
    )
EOF
"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

puts ""
puts "✅ Backend настроен!"
puts ""
puts "📝 Следующие шаги:"
puts "   1. Установить зависимости: pip install fastapi uvicorn sqlalchemy psycopg2-binary"
puts "   2. Запустить: cd /opt/aladdin-backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000"

