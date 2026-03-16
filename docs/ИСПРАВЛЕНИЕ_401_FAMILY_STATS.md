# 🔧 ИСПРАВЛЕНИЕ: 401 ошибка для `/api/family/stats`

## 📋 Проблема

`/api/family/stats` возвращал `401 Unauthorized` с сообщением "Невалидный или истекший токен", хотя:
- ✅ Токен валиден (22 часа до истечения)
- ✅ Другие endpoints (`/api/reports/*`) работают с тем же токеном
- ✅ Токен правильно передается в заголовке `Authorization: Bearer {token}`

## 🔍 Анализ

### Причина проблемы

Серверный код `get_current_user` в `app/auth/auth.py` проверял наличие полей `user_id` или `id` в JWT payload:

```python
if "user_id" not in payload and "id" not in payload:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Токен не содержит user_id",
        ...
    )
```

Но при регистрации устройства токен создается с полем `sub` (subject), а не `user_id` или `id`:

```python
token_data = {
    "sub": device_user.id,  # <-- Используется "sub"
    "device_id": request.deviceId,
    "subscription": subscription_data,
    "type": "device_auth"
}
```

### Почему `/api/reports/*` работали?

Endpoints `/api/reports/*` используют другую логику авторизации или не требуют `user_id` в токене, поэтому они работали корректно.

## ✅ Исправление

Исправлен `get_current_user` в `app/auth/auth.py` для поддержки поля `sub`:

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

## 📊 Результат

После исправления:
- ✅ `/api/family/stats` будет работать с device tokens (с полем `sub`)
- ✅ Обратная совместимость сохранена (user tokens с `user_id` или `id` продолжают работать)
- ✅ Приоритет: `user_id` > `id` > `sub`

## 🧪 Тестирование

После деплоя исправления на сервер нужно проверить:
1. ✅ `/api/family/stats` возвращает `200 OK` вместо `401`
2. ✅ Данные статистики семьи загружаются корректно
3. ✅ Другие endpoints продолжают работать

## 📝 Файлы изменены

- `app/auth/auth.py` - исправлена функция `get_current_user()`
