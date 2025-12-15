# 🚀 ИНСТРУКЦИЯ: Деплой AI Categories Agent

**Для пользователя:** Sergio675  
**Сервер:** 149.154.65.180

---

## 📋 БЫСТРЫЙ ДЕПЛОЙ

### Вариант 1: С паролем как аргументом

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./deploy_ai_categories_final.sh <ваш_пароль>
```

### Вариант 2: С паролем через переменную окружения

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
export ALADDIN_PASSWORD=<ваш_пароль>
./deploy_ai_categories_final.sh
```

### Вариант 3: Интерактивный (запросит пароль)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./deploy_ai_categories_interactive.sh
# Введите пароль когда запросит
```

---

## 📝 РУЧНОЙ ДЕПЛОЙ (если автоматический не работает)

### Шаг 1: Копирование файлов

```bash
# Агент
scp security/ai_agents/ai_categories_agent.py \
    Sergio675@149.154.65.180:/opt/aladdin-backend/security/ai_agents/

# Router
scp security/api/routers/ai_categories_router.py \
    Sergio675@149.154.65.180:/opt/aladdin-backend/security/api/routers/

# Registry entry
scp security/ai_agents/function_registry_entry_ai_categories.json \
    Sergio675@149.154.65.180:/tmp/

# Скрипты
scp register_ai_categories_in_sfm.py Sergio675@149.154.65.180:/tmp/
scp add_ai_categories_to_main.py Sergio675@149.154.65.180:/tmp/
```

### Шаг 2: Подключение к серверу

```bash
ssh Sergio675@149.154.65.180
```

### Шаг 3: Регистрация в SFM

```bash
cd /tmp
python3 register_ai_categories_in_sfm.py
# Введите 'y' если спросит об обновлении
```

### Шаг 4: Интеграция в main.py

```bash
cd /tmp
python3 add_ai_categories_to_main.py
```

### Шаг 5: Перезапуск сервиса

```bash
systemctl restart aladdin-backend
# или
supervisorctl restart aladdin-backend
```

### Шаг 6: Проверка

```bash
curl http://localhost:8000/api/ai-categories/health
```

---

## ✅ ПРОВЕРКА ПОСЛЕ ДЕПЛОЯ

1. **Проверка файлов:**
   ```bash
   ssh Sergio675@149.154.65.180
   ls -lh /opt/aladdin-backend/security/ai_agents/ai_categories_agent.py
   ls -lh /opt/aladdin-backend/security/api/routers/ai_categories_router.py
   ```

2. **Проверка SFM:**
   ```bash
   grep "ai_categories_agent" /opt/aladdin-backend/data/sfm/function_registry.json
   ```

3. **Проверка main.py:**
   ```bash
   grep "ai_categories_router" /opt/aladdin-backend/main.py
   # или
   grep "ai_categories_router" /opt/aladdin-backend/api/main.py
   ```

4. **Проверка API:**
   ```bash
   curl http://149.154.65.180:8000/api/ai-categories/health
   ```

---

**Готово! 🚀**
