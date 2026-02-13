# ✅ ФИНАЛЬНЫЙ ЧЕКЛИСТ ДЛЯ ПРОДАКШН

**Дата:** 2026-02-13  
**Цель:** Убедиться, что все работает идеально для продакшн

---

## 📋 ЗАДАЧИ ДЛЯ ВЫПОЛНЕНИЯ:

### **1. Проверка и исправление Metrics Router** ⚠️

**Статус:** ⚠️ Требует проверки на сервере

**Действия:**

1. **Подключиться к серверу:**
```bash
ssh root@149.154.65.180
```

2. **Запустить скрипт проверки:**
```bash
cd /opt/aladdin-backend
bash /path/to/check_metrics_router.sh
```

3. **Если есть проблемы, запустить скрипт исправления:**
```bash
bash /path/to/fix_metrics_router.sh
```

4. **Или исправить вручную:**

**A. Проверить подключение в main.py:**
```bash
grep -n "metrics_router" /opt/aladdin-backend/main.py
```

**B. Убедиться, что роутер подключен независимо:**
```python
# Должно быть:
if metrics_router_available:
    try:
        app.include_router(metrics_router)
        print("✅ Роутер Metrics подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения Metrics: {e}")
```

**C. Проверить префикс роутера:**
```bash
grep -A 2 "APIRouter" /opt/aladdin-backend/security/api/routers/metrics_router.py
```

**Должно быть:**
```python
router = APIRouter(prefix="/metrics", tags=["metrics"])  # Без /api
```

**D. Перезапустить сервис:**
```bash
sudo systemctl restart aladdin-production-api
sleep 5
systemctl status aladdin-production-api
```

**E. Протестировать endpoint:**
```bash
curl -X POST https://aladdin-ai.ru/api/metrics/upload \
  -H "Content-Type: application/json" \
  -d '{"deviceId":"test","appVersion":"1.0.0","platform":"ios","metrics":[]}'
```

**Ожидаемый результат:** HTTP 200 OK

---

### **2. Реализация /api/user/profile на сервере** ⏳

**Статус:** ⏳ Долгосрочное решение (не критично, но желательно)

**Действия:**

1. **Создать endpoint на сервере:**

**Файл:** `/opt/aladdin-backend/security/api/routers/user_router.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from security.api.dependencies import get_current_user
from security.api.models.user import User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/user", tags=["user"])

class UserProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str | None
    registrationDate: str
    subscriptionType: str
    subscriptionEndDate: str | None
    threatsBlocked: int
    familyMembers: int
    devices: int

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Получить профиль текущего пользователя из токена
    """
    try:
        # Получаем данные пользователя из БД или токена
        return UserProfileResponse(
            id=current_user.id,
            name=current_user.name or "Пользователь",
            email=current_user.email or "",
            phone=current_user.phone,
            registrationDate=current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else datetime.now().isoformat(),
            subscriptionType="free",  # TODO: Получить из БД
            subscriptionEndDate=None,  # TODO: Получить из БД
            threatsBlocked=0,  # TODO: Получить из БД
            familyMembers=0,  # TODO: Получить из БД
            devices=1  # TODO: Получить из БД
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения профиля: {str(e)}")
```

2. **Подключить роутер в main.py:**
```python
try:
    from security.api.routers.user_router import router as user_router
    user_router_available = True
except ImportError as e:
    print(f"⚠️ user_router недоступен: {e}")
    user_router_available = False
    user_router = None

# ...

if user_router_available:
    try:
        app.include_router(user_router)
        print("✅ Роутер User подключен")
    except Exception as e:
        print(f"❌ Ошибка подключения User: {e}")
```

3. **Перезапустить сервис:**
```bash
sudo systemctl restart aladdin-production-api
```

4. **Протестировать endpoint:**
```bash
curl -X GET https://aladdin-ai.ru/api/user/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Ожидаемый результат:** HTTP 200 OK с данными профиля

---

## ✅ ПРОВЕРКА ВСЕХ КОМПОНЕНТОВ:

### **1. Авторизация:**
- [ ] Токены сохраняются в Keychain
- [ ] Токены используются в запросах
- [ ] Защищенные endpoint'ы требуют токен
- [ ] Публичные endpoint'ы работают без токена

### **2. Профиль пользователя:**
- [ ] Профиль загружается после авторизации
- [ ] Используется гибридный подход (getUserProfile → syncUserProfile)
- [ ] Профиль перезагружается после авторизации
- [ ] Кеш профиля работает правильно

### **3. Демо режим:**
- [ ] Демо режим отключен в продакшн
- [ ] В DEBUG демо режим работает
- [ ] После авторизации демо режим отключается

### **4. Metrics Upload:**
- [ ] Endpoint `/api/metrics/upload` работает
- [ ] Метрики отправляются успешно
- [ ] Ошибки обрабатываются правильно

### **5. API Endpoints:**
- [ ] Все endpoint'ы работают
- [ ] Нет двойных `/api/api/` в URL
- [ ] Все endpoint'ы требуют авторизацию (кроме публичных)

---

## 🧪 ТЕСТИРОВАНИЕ:

### **1. Тест регистрации:**
```bash
# Регистрация семьи
curl -X POST https://aladdin-ai.ru/api/family/create \
  -H "Content-Type: application/json" \
  -d '{"role":"parent","age_group":"24-55","personal_letter":"A"}'
```

### **2. Тест авторизации:**
```bash
# Авторизация по recovery code
curl -X POST https://aladdin-ai.ru/api/auth/login-by-recovery-code \
  -H "Content-Type: application/json" \
  -d '{"family_id":"FAM_XXX","recovery_code":"FAM-XXX-XXX-XXX"}'
```

### **3. Тест загрузки профиля:**
```bash
# Загрузка профиля
curl -X GET https://aladdin-ai.ru/api/user/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **4. Тест metrics upload:**
```bash
# Отправка метрик
curl -X POST https://aladdin-ai.ru/api/metrics/upload \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"deviceId":"test","appVersion":"1.0.0","platform":"ios","metrics":[]}'
```

---

## 📊 ИТОГОВАЯ ПРОВЕРКА:

После выполнения всех задач:

1. ✅ Metrics Router подключен и работает
2. ✅ Endpoint `/api/user/profile` реализован (опционально)
3. ✅ Все компоненты протестированы
4. ✅ Нет критичных ошибок
5. ✅ Приложение готово к продакшн

---

**Последнее обновление:** 2026-02-13
