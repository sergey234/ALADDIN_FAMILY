# ПРЕДЛОЖЕНИЕ ПО ВНЕДРЕНИЮ JWT REFRESH FLOW

Для повышения безопасности и стабильности системы авторизации ALADDIN (BUILD 123+) предлагается переход от "длинных" JWT (1 год) к модели **Access + Refresh Token** с ротацией.

## 1. ЦЕЛИ
1. **Безопасность**: Сокращение времени жизни `access_token` до **30-90 дней**.
2. **Удобство (UX)**: Бесшовное обновление сессии без участия пользователя.
3. **Контроль**: Возможность отозвать Refresh Token на стороне сервера в случае компрометации устройства.

---

## 2. СХЕМА БАЗЫ ДАННЫХ (PostgreSQL)

Предлагается создать таблицу `refresh_tokens` для хранения состояния сессий.

```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(255) NOT NULL,
    user_id INTEGER NULL, -- Для привязки к аккаунту (если есть)
    token_hash VARCHAR(255) NOT NULL, -- Хэш (SHA-256) refresh_token для безопасности
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE,
    replaced_by UUID NULL, -- Ссылка на новый токен (для отслеживания ротации)
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Индексы для быстрого поиска
CREATE INDEX idx_refresh_tokens_device_id ON refresh_tokens(device_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
```

---

## 3. ЛОГИКА РАБОТЫ (Backend)

### A. Регистрация устройства / Вход
При вызове `/api/auth/register-device` или `/api/auth/login`:
1. Генерируется `access_token` (expires: 30 days).
2. Генерируется `refresh_token` (expires: 1 year).
3. Хэш `refresh_token` сохраняется в БД с привязкой к `device_id`.
4. Оба токена возвращаются клиенту.

### B. Обновление токена (`POST /api/auth/refresh`)
Принимает: `{ "refresh_token": "...", "device_id": "..." }`
1. Валидация подписи JWT `refresh_token`.
2. Поиск хэша токена в БД.
3. Проверка: не истек ли срок (`expires_at`) и не отозван ли (`is_revoked`).
4. **РОТАЦИЯ**:
   - Старый токен помечается как `is_revoked = true` и `replaced_by = [new_id]`.
   - Генерируется новая пара `access` + `refresh`.
   - Новый `refresh` сохраняется в БД.
5. Возврат новой пары клиенту.

---

## 4. ЛОГИКА РАБОТЫ (iOS Client)

1. **Storage**: Хранение обоих токенов в **Keychain**.
2. **Auto-Refresh**: 
   - Перед каждым запросом `TokenValidator` проверяет `expires_at` текущего `access_token`.
   - Если до конца осталось < 24 часов, запускается фоновый запрос на `/api/auth/refresh`.
3. **Error Handling**: 
   - Если `/refresh` вернул 401, сессия считается невалидной (полная перерегистрация).
   - Если сеть недоступна, используется старый токен (пока он физически не истек).

---

## 5. ПЛАН РЕАЛИЗАЦИИ
1. [ ] Добавить миграцию БД для таблицы `refresh_tokens`.
2. [ ] Обновить `JWTService` (backend) для генерации пары токенов.
3. [ ] Реализовать `AuthRouter.refresh_token` с логикой ротации.
4. [ ] Обновить `JWTTokenManager.swift` (iOS) для поддержки хранения и обновления.

---
*Статус: Проектирование (BUILD 123)*
