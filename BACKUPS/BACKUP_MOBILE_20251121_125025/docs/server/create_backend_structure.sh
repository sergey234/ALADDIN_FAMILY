#!/usr/bin/expect -f
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== 🚀 СОЗДАНИЕ ПОЛНОЙ СТРУКТУРЫ BACKEND ==="
puts ""

# 1. Создать структуру директорий
spawn ssh $server "mkdir -p /opt/aladdin-backend/{app/{routers,models,database,auth},requirements}"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 2. Создать main.py
spawn ssh $server "cat > /opt/aladdin-backend/app/main.py << 'MAINEOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import referral

app = FastAPI(title=\"ALADDIN API\", version=\"1.0.0\")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[\"*\"],
    allow_credentials=True,
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

app.include_router(referral.router, prefix=\"/api/referral\", tags=[\"referral\"])

@app.get(\"/api/health\")
async def health():
    return {\"status\": \"ok\"}

if __name__ == \"__main__\":
    import uvicorn
    uvicorn.run(app, host=\"0.0.0.0\", port=8000)
MAINEOF
"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 3. Создать __init__.py для routers
spawn ssh $server "touch /opt/aladdin-backend/app/__init__.py /opt/aladdin-backend/app/routers/__init__.py"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

puts "✅ Структура создана"

