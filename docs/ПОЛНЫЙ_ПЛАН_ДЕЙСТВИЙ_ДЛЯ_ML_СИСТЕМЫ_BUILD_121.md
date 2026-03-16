# 📋 ПОЛНЫЙ ПЛАН ДЕЙСТВИЙ ДЛЯ ML СИСТЕМЫ - BUILD 121

## ✅ ЧТО УЖЕ СДЕЛАНО

### 1. Проблема найдена и исправлена локально ✅

**Проблема:** `/api/family/stats` возвращал `401 Unauthorized` для device tokens

**Причина:** Серверный код `get_current_user` проверял только `user_id` или `id`, но device tokens используют поле `sub`

**Исправление:** Добавлена поддержка поля `sub` с приоритетом: `user_id` > `id` > `sub`

**Файлы исправлены локально:**
- ✅ `app/auth/auth.py` - исправлено
- ✅ `docs/server/auth.py` - исправлено

### 2. Защита от ложного удаления токенов ✅

**Проблема:** Токены удалялись при валидном состоянии

**Исправления:**
- ✅ `KeychainAutoRecoveryService` - исправлена проверка токенов
- ✅ `MainViewModel.handleSessionExpired()` - добавлена проверка валидности токена
- ✅ `ALADDINApp` - добавлена защита от ложных `SessionExpired` уведомлений
- ✅ Добавлено логирование всех удалений токенов

**Файлы исправлены:**
- ✅ `Core/Security/KeychainManager.swift`
- ✅ `ViewModels/MainViewModel.swift`
- ✅ `ALADDINApp.swift`

### 3. Исправления моделей подписки ✅

**Проблема:** `DecodingError` при регистрации устройства

**Исправления:**
- ✅ `DeviceRegistrationSubscription` - добавлены `CodingKeys`, `isActive` опциональный
- ✅ `TrialInfo` - добавлен кастомный `init` для парсинга ISO дат
- ✅ `SubscriptionLimits` - добавлены `CodingKeys` для всех полей
- ✅ `UsageCounters` - добавлены `CodingKeys` и default значения

**Файлы исправлены:**
- ✅ `Core/Models/SubscriptionModels.swift`

### 4. Компиляция проекта ✅

- ✅ Все ошибки компиляции исправлены
- ✅ Проект успешно компилируется

---

## ⏳ ЧТО ОСТАЛОСЬ СДЕЛАТЬ

### ЗАДАЧА 1: Деплой исправления на сервер (КРИТИЧНО)

**Что нужно сделать:**
1. Скопировать исправленный файл `app/auth/auth.py` на сервер
2. Разместить в `/opt/aladdin-backend/app/auth/auth.py`
3. Перезапустить systemd сервис

**Инструкции:**
- См. `docs/ДЕПЛОЙ_ЧЕРЕЗ_NGINX_SSL_SYSTEMD.md`
- См. `docs/РУЧНОЙ_ДЕПЛОЙ_ИСПРАВЛЕНИЯ_401.md`

**Проверка после деплоя:**
```bash
curl -H "Authorization: Bearer DEVICE_TOKEN" https://aladdin-ai.ru/api/family/stats
# Ожидается: 200 OK (было: 401 Unauthorized)
```

---

### ЗАДАЧА 2: Тестирование исправлений (РЕКОМЕНДУЕТСЯ)

**Что нужно проверить:**

1. **Токены не удаляются ложно:**
   - Запустить приложение
   - Проверить логи: не должно быть `KeychainManager.delete(forKey: auth_token)` при валидном токене
   - Перейти на главную страницу → Аналитика → Отчет о вождении
   - Токен должен оставаться валидным

2. **`/api/family/stats` работает:**
   - После деплоя на сервер
   - Запрос с device token должен возвращать `200 OK`
   - Данные статистики семьи должны загружаться

3. **Обратная совместимость:**
   - User tokens с `user_id` или `id` продолжают работать
   - Device tokens с `sub` теперь тоже работают

---

### ЗАДАЧА 3: Мониторинг после деплоя (РЕКОМЕНДУЕТСЯ)

**Что мониторить:**

1. **Логи сервера:**
   ```bash
   journalctl -u aladdin-backend -f
   ```

2. **Логи приложения:**
   - Visual Logger в симуляторе
   - MasterLogger в консоли

3. **Метрики:**
   - Количество 401 ошибок (должно уменьшиться)
   - Количество успешных запросов к `/api/family/stats`

---

## 🎯 ПОШАГОВЫЙ ПЛАН ДЛЯ ML СИСТЕМЫ

### ЭТАП 1: Подготовка (5 минут)

1. **Проверить наличие файлов:**
   ```bash
   ls -la app/auth/auth.py
   ls -la docs/ДЕПЛОЙ_ЧЕРЕЗ_NGINX_SSL_SYSTEMD.md
   ```

2. **Проверить содержимое исправления:**
   ```bash
   grep -n "sub" app/auth/auth.py
   ```
   
   Должны быть строки:
   - `71: if "user_id" not in payload and "id" not in payload and "sub" not in payload:`
   - `80: user_id = payload.get("user_id") or payload.get("id") or payload.get("sub")`

---

### ЭТАП 2: Деплой на сервер (10-15 минут)

**Вариант A: Через SSH (если доступен)**

```bash
# 1. Подключиться к серверу
ssh root@149.154.65.180
# Пароль: Sergio675

# 2. Создать backup
cd /opt/aladdin-backend/app/auth
cp auth.py auth.py.backup_$(date +%Y%m%d_%H%M%S)

# 3. На локальной машине загрузить файл
scp app/auth/auth.py root@149.154.65.180:/opt/aladdin-backend/app/auth/auth.py

# 4. На сервере проверить синтаксис
python3 -m py_compile /opt/aladdin-backend/app/auth/auth.py

# 5. Перезапустить сервис
systemctl restart aladdin-backend

# 6. Проверить статус
systemctl status aladdin-backend --no-pager -l
```

**Вариант B: Через веб-интерфейс**

1. Войти в панель управления сервером
2. Открыть файловый менеджер
3. Перейти в `/opt/aladdin-backend/app/auth/`
4. Создать backup `auth.py`
5. Загрузить локальный `app/auth/auth.py`
6. Через терминал веб-интерфейса:
   ```bash
   python3 -m py_compile /opt/aladdin-backend/app/auth/auth.py
   systemctl restart aladdin-backend
   ```

**Вариант C: Через Git (если используется)**

```bash
# На сервере:
cd /opt/aladdin-backend
git pull origin main
systemctl restart aladdin-backend
```

---

### ЭТАП 3: Проверка деплоя (5 минут)

1. **Проверить что файл обновлен:**
   ```bash
   ssh root@149.154.65.180 "grep -n 'sub' /opt/aladdin-backend/app/auth/auth.py"
   ```

2. **Проверить синтаксис:**
   ```bash
   ssh root@149.154.65.180 "python3 -m py_compile /opt/aladdin-backend/app/auth/auth.py"
   ```

3. **Проверить статус сервиса:**
   ```bash
   ssh root@149.154.65.180 "systemctl status aladdin-backend --no-pager -l | head -20"
   ```

4. **Проверить через HTTPS:**
   ```bash
   curl -k https://aladdin-ai.ru/api/health
   ```

---

### ЭТАП 4: Тестирование (10 минут)

1. **Тест с device token:**
   ```bash
   # Получить device token (из логов приложения или после регистрации)
   TOKEN="your_device_token_here"
   
   # Проверить /api/family/stats
   curl -H "Authorization: Bearer $TOKEN" https://aladdin-ai.ru/api/family/stats
   
   # Ожидается: 200 OK с данными статистики семьи
   # Было: 401 Unauthorized
   ```

2. **Тест в iOS приложении:**
   - Запустить приложение
   - Перейти на главную страницу
   - Проверить что статистика семьи загружается
   - Проверить логи: не должно быть 401 ошибок

---

### ЭТАП 5: Мониторинг (непрерывно)

1. **Логи сервера:**
   ```bash
   journalctl -u aladdin-backend -f
   ```

2. **Метрики ошибок:**
   - Отслеживать количество 401 ошибок
   - Отслеживать успешные запросы к `/api/family/stats`

3. **Логи приложения:**
   - Visual Logger в симуляторе
   - Проверять что токены не удаляются ложно

---

## 📊 КРИТЕРИИ УСПЕХА

### ✅ Деплой успешен если:

1. **Файл обновлен:**
   - `/opt/aladdin-backend/app/auth/auth.py` содержит исправление с поддержкой `sub`

2. **Сервис работает:**
   - `systemctl status aladdin-backend` показывает `active (running)`
   - Нет ошибок в логах

3. **API работает:**
   - `/api/family/stats` возвращает `200 OK` для device tokens
   - Данные статистики семьи загружаются корректно

4. **Обратная совместимость:**
   - User tokens продолжают работать
   - Device tokens теперь тоже работают

---

## 🚨 ОТКАТ (если что-то пошло не так)

```bash
# На сервере:
cd /opt/aladdin-backend/app/auth

# Найти последний backup
ls -lt auth.py.backup_* | head -1

# Восстановить backup
cp auth.py.backup_YYYYMMDD_HHMMSS auth.py

# Перезапустить сервис
systemctl restart aladdin-backend

# Проверить статус
systemctl status aladdin-backend
```

---

## 📁 ВАЖНЫЕ ФАЙЛЫ

### Локальные файлы (уже исправлены):
- ✅ `app/auth/auth.py` - исправлен
- ✅ `docs/server/auth.py` - исправлен
- ✅ `Core/Security/KeychainManager.swift` - исправлен
- ✅ `ViewModels/MainViewModel.swift` - исправлен
- ✅ `ALADDINApp.swift` - исправлен
- ✅ `Core/Models/SubscriptionModels.swift` - исправлен

### Серверные файлы (нужно обновить):
- ⏳ `/opt/aladdin-backend/app/auth/auth.py` - **ТРЕБУЕТ ДЕПЛОЯ**

### Документация:
- ✅ `docs/ИСПРАВЛЕНИЕ_401_FAMILY_STATS.md` - описание проблемы
- ✅ `docs/ПЛАН_ДЕПЛОЯ_ИСПРАВЛЕНИЯ_401.md` - план деплоя
- ✅ `docs/РУЧНОЙ_ДЕПЛОЙ_ИСПРАВЛЕНИЯ_401.md` - инструкции
- ✅ `docs/ДЕПЛОЙ_ЧЕРЕЗ_NGINX_SSL_SYSTEMD.md` - деплой через systemd
- ✅ `docs/ПОЛНЫЙ_ПЛАН_ДЕЙСТВИЙ_ДЛЯ_ML_СИСТЕМЫ_BUILD_121.md` - этот файл

---

## 🎯 ИТОГОВЫЙ ЧЕКЛИСТ

### Для ML системы:

- [ ] **ШАГ 1:** Скопировать `app/auth/auth.py` на сервер в `/opt/aladdin-backend/app/auth/auth.py`
- [ ] **ШАГ 2:** Создать backup оригинального файла
- [ ] **ШАГ 3:** Проверить синтаксис Python: `python3 -m py_compile /opt/aladdin-backend/app/auth/auth.py`
- [ ] **ШАГ 4:** Перезапустить systemd сервис: `systemctl restart aladdin-backend`
- [ ] **ШАГ 5:** Проверить статус сервиса: `systemctl status aladdin-backend`
- [ ] **ШАГ 6:** Протестировать API: `curl -H "Authorization: Bearer TOKEN" https://aladdin-ai.ru/api/family/stats`
- [ ] **ШАГ 7:** Проверить логи: `journalctl -u aladdin-backend -n 50`
- [ ] **ШАГ 8:** Протестировать в iOS приложении

---

## 📝 ПРИМЕЧАНИЯ

1. **SSH может быть недоступен** - используйте альтернативные методы (веб-интерфейс, Git, SFTP)

2. **Имя systemd сервиса может отличаться** - проверьте:
   ```bash
   systemctl list-units --type=service | grep -i aladdin
   ```

3. **После деплоя подождите 1-2 минуты** перед тестированием - серверу нужно время на перезапуск

4. **Все исправления уже применены локально** - нужно только задеплоить на сервер

---

**Дата:** 16 марта 2026  
**Build:** 121  
**Статус:** ✅ Локально готово, ⏳ Ожидает деплоя на сервер
