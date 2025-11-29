# 🎯 ЛОГИКА РЕФЕРАЛЬНЫХ КОДОВ

**Важно:** У каждого пользователя свой уникальный реферальный код!

---

## ✅ ПРАВИЛЬНАЯ ЛОГИКА

### 📌 У каждого пользователя свой код

**Пример:**

1. **Пользователь А (Иван)** регистрируется:
   - Сервер создает для него код: `ABC123`
   - Его реферальная ссылка: `https://aladdin-ai.ru/invite/ABC123`

2. **Пользователь Б (Мария)** регистрируется:
   - Сервер создает для нее код: `XYZ789`
   - Ее реферальная ссылка: `https://aladdin-ai.ru/invite/XYZ789`

3. **Пользователь В (Петр)** регистрируется:
   - Сервер создает для него код: `DEF456`
   - Его реферальная ссылка: `https://aladdin-ai.ru/invite/DEF456`

**Каждый пользователь получает свой уникальный код!**

---

## 🔄 КАК ЭТО РАБОТАЕТ

### Сценарий 1: Иван приглашает Марию

```
1. Иван открывает экран "Пригласить друзей"
   → Видит свой код: ABC123
   → Видит свою ссылку: https://aladdin-ai.ru/invite/ABC123

2. Иван делится ссылкой с Марией (WhatsApp/Telegram/VK)

3. Мария переходит по ссылке: https://aladdin-ai.ru/invite/ABC123
   → Открывается landing страница
   → Кнопка "Зарегистрироваться" → /register?ref=ABC123

4. Мария регистрируется с кодом ABC123
   → В базе создается запись:
     - referrer_id = ID Ивана
     - invited_user_id = ID Марии
     - referral_code = "ABC123"
     - status = "pending"

5. Мария оплачивает подписку
   → Статус обновляется: status = "completed"
   → Иван получает награду
   → Мария получает скидку
```

### Сценарий 2: Мария хочет пригласить Петра

```
1. Мария открывает экран "Пригласить друзей"
   → Видит СВОЙ код: XYZ789 (не ABC123!)
   → Видит свою ссылку: https://aladdin-ai.ru/invite/XYZ789

2. Мария делится СВОЕЙ ссылкой с Петром

3. Петр переходит по ссылке: https://aladdin-ai.ru/invite/XYZ789
   → Открывается landing страница
   → Кнопка "Зарегистрироваться" → /register?ref=XYZ789

4. Петр регистрируется с кодом XYZ789
   → В базе создается запись:
     - referrer_id = ID Марии
     - invited_user_id = ID Петра
     - referral_code = "XYZ789"
     - status = "pending"

5. Петр оплачивает подписку
   → Статус обновляется: status = "completed"
   → Мария получает награду (не Иван!)
   → Петр получает скидку
```

---

## 🗄️ СТРУКТУРА БАЗЫ ДАННЫХ

### Таблица `referral_codes`

```sql
CREATE TABLE referral_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,  -- ✅ Один код на пользователя!
    code VARCHAR(20) NOT NULL UNIQUE, -- ✅ Код уникальный в базе!
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Важно:**
- `user_id UNIQUE` - у каждого пользователя может быть только ОДИН код
- `code UNIQUE` - каждый код уникален в базе (не может быть двух одинаковых кодов)

### Таблица `referrals`

```sql
CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    referrer_id INTEGER NOT NULL,     -- Кто пригласил (Иван)
    invited_user_id INTEGER NOT NULL, -- Кого пригласили (Мария)
    referral_code VARCHAR(20) NOT NULL, -- Код, по которому пригласили (ABC123)
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    converted_at TIMESTAMP NULL
);
```

**Пример данных:**

| id | referrer_id | invited_user_id | referral_code | status |
|----|--------------|-----------------|----------------|--------|
| 1  | 100 (Иван)   | 200 (Мария)     | ABC123         | completed |
| 2  | 200 (Мария)  | 300 (Петр)      | XYZ789         | pending |

---

## 💻 РЕАЛИЗАЦИЯ НА СЕРВЕРЕ

### Endpoint: GET `/api/referral/code`

**Логика:**

```python
@app.get("/api/referral/code")
async def get_referral_code(request: Request):
    # 1. Проверить токен
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_token(token)
    
    # 2. Найти или создать код ДЛЯ ЭТОГО ПОЛЬЗОВАТЕЛЯ
    referral_code = db.get_or_create_referral_code(user.id)
    
    # Если кода нет - создать новый уникальный код
    if not referral_code:
        # Генерировать уникальный код
        code = generate_unique_code()  # Например: "ABC123"
        
        # Проверить, что код уникален
        while db.code_exists(code):
            code = generate_unique_code()
        
        # Создать запись
        referral_code = db.create_referral_code(
            user_id=user.id,
            code=code
        )
    
    # 3. Вернуть код пользователя
    return {
        "referral_code": referral_code.code,
        "referral_url": f"https://aladdin-ai.ru/invite/{referral_code.code}"
    }
```

**Функция генерации кода:**

```python
import random
import string

def generate_unique_code(length=6):
    """Генерирует случайный уникальный код"""
    characters = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(characters) for _ in range(length))
    return code

# Примеры: ABC123, XYZ789, DEF456, GHI012
```

---

## ✅ ПРОВЕРКА УНИКАЛЬНОСТИ

### При создании кода:

```python
def create_referral_code(user_id: int):
    # 1. Проверить, есть ли уже код у пользователя
    existing = db.get_referral_code_by_user_id(user_id)
    if existing:
        return existing  # Вернуть существующий
    
    # 2. Генерировать новый код
    max_attempts = 100
    for _ in range(max_attempts):
        code = generate_unique_code()
        
        # 3. Проверить уникальность
        if not db.code_exists(code):
            # 4. Создать запись
            return db.insert_referral_code(user_id=user_id, code=code)
    
    raise Exception("Не удалось создать уникальный код")
```

---

## 🎯 ИТОГОВАЯ ЛОГИКА

### ✅ Правильно:

- ✅ У каждого пользователя свой уникальный код
- ✅ Код привязан к `user_id` (один код на пользователя)
- ✅ Код уникален в базе (не может быть двух одинаковых)
- ✅ Когда пользователь A приглашает по коду ABC123, это его код
- ✅ Когда пользователь B хочет пригласить, у него свой код (XYZ789)

### ❌ Неправильно:

- ❌ Все пользователи используют один код ABC123
- ❌ Коды повторяются
- ❌ Один пользователь может иметь несколько кодов

---

## 📊 ПРИМЕР РАБОТЫ

### База данных `referral_codes`:

| user_id | code    | created_at |
|---------|---------|------------|
| 100     | ABC123  | 2024-11-21 |
| 200     | XYZ789  | 2024-11-21 |
| 300     | DEF456  | 2024-11-21 |

### База данных `referrals`:

| referrer_id | invited_user_id | referral_code | status    |
|-------------|-----------------|---------------|-----------|
| 100         | 200             | ABC123        | completed |
| 200         | 300             | XYZ789        | pending   |

**Расшифровка:**
- Пользователь 100 (код ABC123) пригласил пользователя 200
- Пользователь 200 (код XYZ789) пригласил пользователя 300

---

## 🔐 БЕЗОПАСНОСТЬ

### Защита от дублирования:

1. **UNIQUE constraint** в базе данных:
   ```sql
   code VARCHAR(20) NOT NULL UNIQUE
   ```
   - База данных не позволит создать два одинаковых кода

2. **Проверка перед созданием:**
   ```python
   if db.code_exists(code):
       # Генерировать новый код
   ```

3. **Один код на пользователя:**
   ```sql
   user_id INTEGER NOT NULL UNIQUE
   ```
   - Пользователь не может иметь несколько кодов

---

## ✅ ПОДТВЕРЖДЕНИЕ

**Вопрос:** У каждого нового пользователя будет свой уникальный реферальный код?

**Ответ:** ✅ **ДА!**

- Каждый пользователь получает свой уникальный код при первом запросе `/api/referral/code`
- Код привязан к `user_id` (один код на пользователя)
- Код уникален в базе (не может быть двух одинаковых)
- Когда пользователь приглашает друзей, он использует свой код
- Когда приглашенный друг захочет пригласить кого-то, у него будет свой код

**Пример:**
- Иван → код `ABC123` → ссылка `https://aladdin-ai.ru/invite/ABC123`
- Мария → код `XYZ789` → ссылка `https://aladdin-ai.ru/invite/XYZ789`
- Петр → код `DEF456` → ссылка `https://aladdin-ai.ru/invite/DEF456`

Каждый использует свой код для приглашения!

---

**Последнее обновление:** 21 ноября 2024  
**Статус:** ✅ Логика подтверждена

