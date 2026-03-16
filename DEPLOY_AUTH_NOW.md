# 🚀 ДЕПЛОЙ auth.py - ГОТОВЫЙ КОД ДЛЯ КОПИРОВАНИЯ

## ✅ Файл готов к деплою

**Локальный файл:** `app/auth/auth.py`  
**Серверный путь:** `/opt/aladdin-backend/app/auth/auth.py`

---

## 📋 СПОСОБ 1: Через терминал (если SSH работает)

Выполните команды по очереди:

```bash
# 1. Backup на сервере
ssh root@149.154.65.180 "cd /opt/aladdin-backend/app/auth && cp auth.py auth.py.backup_\$(date +%Y%m%d_%H%M%S)"

# 2. Загрузка файла
scp app/auth/auth.py root@149.154.65.180:/opt/aladdin-backend/app/auth/auth.py

# 3. Проверка синтаксиса
ssh root@149.154.65.180 "python3 -m py_compile /opt/aladdin-backend/app/auth/auth.py"

# 4. Перезапуск
ssh root@149.154.65.180 "systemctl restart aladdin-backend || pm2 restart aladdin-backend"
```

---

## 📋 СПОСОБ 2: Ручное копирование через SSH

1. Подключитесь к серверу:
```bash
ssh root@149.154.65.180
# Пароль: Sergio675
```

2. Создайте backup:
```bash
cd /opt/aladdin-backend/app/auth
cp auth.py auth.py.backup_$(date +%Y%m%d_%H%M%S)
```

3. Откройте файл для редактирования:
```bash
nano auth.py
```

4. Найдите строки 69-80 и замените на:

```python
    # ✅ BUILD 121: Проверяем что в payload есть user_id, id или sub (для device tokens)
    # Device tokens используют "sub" (subject), а user tokens используют "user_id" или "id"
    if "user_id" not in payload and "id" not in payload and "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не содержит user_id, id или sub",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # ✅ BUILD 121: Нормализуем user_id (может быть "user_id", "id" или "sub")
    # Приоритет: user_id > id > sub (для обратной совместимости)
    user_id = payload.get("user_id") or payload.get("id") or payload.get("sub")
```

5. Сохраните (Ctrl+O, Enter, Ctrl+X)

6. Проверьте синтаксис:
```bash
python3 -m py_compile auth.py
```

7. Перезапустите сервер:
```bash
systemctl restart aladdin-backend
# ИЛИ
pm2 restart aladdin-backend
```

---

## 📋 СПОСОБ 3: Через SFTP клиент (FileZilla, Cyberduck)

1. Подключитесь:
   - Host: `149.154.65.180`
   - Port: `22`
   - Username: `root`
   - Password: `Sergio675`
   - Protocol: `SFTP`

2. Перейдите в `/opt/aladdin-backend/app/auth/`

3. Создайте backup файла `auth.py`

4. Загрузите локальный файл `app/auth/auth.py`

5. Подключитесь по SSH и перезапустите:
```bash
ssh root@149.154.65.180
systemctl restart aladdin-backend
```

---

## ✅ Проверка после деплоя

```bash
curl https://aladdin-ai.ru/api/health
curl -H "Authorization: Bearer YOUR_DEVICE_TOKEN" https://aladdin-ai.ru/api/family/stats
```

Ожидается: **200 OK** вместо **401 Unauthorized**
