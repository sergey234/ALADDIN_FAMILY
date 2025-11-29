# ⚡ БЫСТРЫЙ СТАРТ: Реферальная программа

**Время:** 15-30 минут  
**Сервер:** 149.154.65.180

---

## 🎯 МИНИМАЛЬНАЯ РЕАЛИЗАЦИЯ (15 минут)

### 1. База данных (2 минуты)
```bash
psql -h localhost -U your_user -d your_database -f REFERRAL_DB_SETUP.sql
```

### 2. API Endpoint 1 (5 минут)
```python
# В вашем FastAPI проекте добавить:
@app.get("/api/referral/code")
async def get_referral_code(current_user: User = Depends(get_current_user)):
    code = db.execute("SELECT get_or_create_referral_code(:user_id)", 
                     {"user_id": current_user.id}).scalar()
    return {"referral_code": code, "referral_url": f"https://aladdin-ai.ru/invite/{code}"}
```

### 3. Landing страница (3 минуты)
```python
@app.get("/invite/{code}")
async def referral_invite(code: str):
    return FileResponse("templates/referral_landing.html")
```

### 4. Регистрация (3 минуты)
```python
# В вашем endpoint регистрации добавить:
if user_data.referral_code:
    db.execute("INSERT INTO referrals (referrer_id, invited_user_id, referral_code, status) "
              "SELECT user_id, :new_user_id, :code, 'pending' "
              "FROM referral_codes WHERE code = :code",
              {"new_user_id": new_user.id, "code": user_data.referral_code})
```

### 5. Оплата (2 минуты)
```python
# В вашем endpoint оплаты добавить:
db.execute("UPDATE referrals SET status='completed', converted_at=NOW() "
          "WHERE invited_user_id=:user_id AND status='pending'",
          {"user_id": user_id})
```

---

## ✅ ПРОВЕРКА (2 минуты)

```bash
# 1. Проверить таблицы
psql -U your_user -d your_database -c "SELECT * FROM referral_codes LIMIT 1;"

# 2. Проверить API
curl -X GET "https://aladdin-ai.ru/api/referral/code" -H "Authorization: Bearer TOKEN"

# 3. Проверить landing
curl "https://aladdin-ai.ru/invite/TEST123"
```

---

## 🚀 ГОТОВО!

Теперь реферальная программа работает на базовом уровне!

Для полной реализации см. `README.md`

