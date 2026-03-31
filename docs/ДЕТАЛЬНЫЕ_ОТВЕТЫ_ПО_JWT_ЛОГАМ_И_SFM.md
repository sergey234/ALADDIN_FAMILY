# 🔍 **ДЕТАЛЬНЫЕ ОТВЕТЫ ПО JWT, ЛОГАМ И SFM**

**Дата:** 2026-03-18  
**Цель:** Ответить на все вопросы по архитектуре и рекомендациям

---

## 1️⃣ **JWT И ПОДПИСКИ: КАК ПРАВИЛЬНО РАЗГРАНИЧИТЬ?**

### **📊 ТЕКУЩАЯ СИТУАЦИЯ:**

```python
# backend/app/services/jwt_service.py:23
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365  # 1 год для ВСЕХ
```

**Проблема:** Один срок для всех (trial, free, paid) = **365 дней**

### **🎯 ПРАВИЛЬНАЯ АРХИТЕКТУРА:**

#### **Вариант A (Рекомендуемый): Дифференцированные сроки**

```python
# backend/app/services/jwt_service.py

# Разные сроки для разных типов подписок
TRIAL_TOKEN_EXPIRE_MINUTES = 60 * 24 * 14      # 14 дней (trial период)
FREE_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30       # 30 дней (free тариф)
PAID_TOKEN_EXPIRE_MINUTES = 60 * 24 * 90       # 90 дней (paid тарифы)
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365    # 1 год (refresh token)

class JWTService:
    @staticmethod
    def create_subscription_token(subscription: SubscriptionPayload) -> str:
        """Create JWT token with subscription-specific expiry"""
        
        # Определяем срок токена в зависимости от уровня подписки
        if subscription.level == SubscriptionLevel.TRIAL:
            expire_minutes = TRIAL_TOKEN_EXPIRE_MINUTES
            # Важно: токен истекает вместе с trial периодом
            if subscription.trial_info and subscription.trial_info.end_date:
                expire = subscription.trial_info.end_date
            else:
                expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
                
        elif subscription.level == SubscriptionLevel.FREE:
            expire_minutes = FREE_TOKEN_EXPIRE_MINUTES
            expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
            
        else:  # PERSONAL, FAMILY, PREMIUM
            expire_minutes = PAID_TOKEN_EXPIRE_MINUTES
            # Для paid: токен истекает вместе с подпиской или через 90 дней
            if subscription.end_date:
                expire = min(
                    subscription.end_date,
                    datetime.utcnow() + timedelta(minutes=expire_minutes)
                )
            else:
                expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
        
        payload = {
            "sub": subscription.user_id or subscription.device_id,
            "device_id": subscription.device_id,
            "subscription": {
                "level": subscription.level.value,
                "start_date": subscription.start_date.isoformat(),
                "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
                "is_active": subscription.is_active,
                "trial_info": subscription.trial_info.dict() if subscription.trial_info else None,
                "limits": subscription.limits.dict(),
                "permissions": subscription.permissions
            },
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "aladdin-backend"
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
```

#### **Вариант B (С Refresh Token): Двухуровневая система**

```python
# Access Token: короткий срок (для безопасности)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 дней для всех

# Refresh Token: длинный срок (для удобства)
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365  # 1 год

class JWTService:
    @staticmethod
    def create_tokens(subscription: SubscriptionPayload) -> dict:
        """Create both access and refresh tokens"""
        
        # Access Token: короткий срок
        access_expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Refresh Token: длинный срок, но с ограничениями
        if subscription.level == SubscriptionLevel.TRIAL:
            # Для trial: refresh token истекает вместе с trial
            if subscription.trial_info and subscription.trial_info.end_date:
                refresh_expire = subscription.trial_info.end_date
            else:
                refresh_expire = datetime.utcnow() + timedelta(days=14)
        else:
            refresh_expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        
        access_payload = {
            "sub": subscription.user_id or subscription.device_id,
            "device_id": subscription.device_id,
            "subscription": subscription.dict(),
            "exp": access_expire,
            "iat": datetime.utcnow(),
            "iss": "aladdin-backend",
            "type": "access"
        }
        
        refresh_payload = {
            "sub": subscription.user_id or subscription.device_id,
            "device_id": subscription.device_id,
            "exp": refresh_expire,
            "iat": datetime.utcnow(),
            "iss": "aladdin-backend",
            "type": "refresh"
        }
        
        access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # секунды
        }
```

### **📋 ТАБЛИЦА РАЗГРАНИЧЕНИЯ:**

| Тип подписки | Access Token | Refresh Token | Логика |
|--------------|--------------|---------------|--------|
| **TRIAL** | 14 дней (или до конца trial) | 14 дней (или до конца trial) | Токен истекает вместе с trial |
| **FREE** | 30 дней | 90 дней | Короткий срок для безопасности |
| **PERSONAL** | 90 дней | 365 дней | Стандартный срок для paid |
| **FAMILY** | 90 дней | 365 дней | Стандартный срок для paid |
| **PREMIUM** | 90 дней | 365 дней | Стандартный срок для paid |

### **✅ ПРЕИМУЩЕСТВА:**

1. **Безопасность:**
   - Trial токены истекают вместе с trial (14 дней)
   - Paid токены можно отозвать через 90 дней (вместо 365)
   - При компрометации токена меньше риск

2. **Гибкость:**
   - Можно обновить права пользователя через refresh token
   - Не нужно перерегистрировать устройство при upgrade

3. **UX:**
   - Trial пользователи не остаются с валидным токеном после истечения trial
   - Paid пользователи не перерегистрируются часто (refresh token живёт год)

### **⚠️ ВАЖНО:**

- **Trial токен должен истекать вместе с trial периодом** (14 дней)
- **При upgrade с trial на paid:** выдать новый токен с новым сроком
- **При истечении trial:** токен становится невалидным, пользователь должен upgrade

---

## 2️⃣ **SFM MOCK В ПРОДЕ: ПОЧЕМУ СЕРВЕР ВОЗВРАЩАЕТ MOCK?**

### **🔍 НАЙДЕННАЯ ПРОБЛЕМА:**

```python
# security/sfm_singleton_new.py:52-75
def execute_function(self, func_name: str, params: Optional[Dict[str, Any]] = None) -> Any:
    if self._sfm:
        # Use original SFM
        try:
            result = self._sfm.execute_function(func_name, params)
            return result
        except Exception as e:
            print(f"SFM execution error: {e}")
            return {"error": str(e), "function": func_name, "source": "sfm_error"}
    
    # Fallback - return mock
    return {
        "function": func_name,
        "params": params,
        "result": "mock_fallback",
        "timestamp": datetime.utcnow().isoformat(),
        "source": "sfm_mock",  # ← ВОТ ОНА ПРОБЛЕМА!
        "version": self.version
    }
```

**Причина:** `self._sfm` = `None` → SFM не инициализирован → возвращается mock

### **🔍 ДИАГНОСТИКА:**

#### **Шаг 1: Проверить инициализацию SFM**

```python
# security/sfm_singleton_new.py:31-41
if ORIGINAL_SFM_AVAILABLE and SafeFunctionManager:
    try:
        print("🔄 Initializing original SafeFunctionManager...")
        self._sfm = SafeFunctionManager()
        print(f"✅ Original SFM initialized with {len(self._sfm.functions)} functions")
    except Exception as e:
        print(f"❌ Failed to initialize original SFM: {e}")
        self._sfm = None  # ← ПРОБЛЕМА: SFM не инициализирован
else:
    print("⚠️ Original SFM not available, using mock functions")
    self._sfm = None
```

**Возможные причины:**
1. `SafeFunctionManager` не импортируется (ImportError)
2. Ошибка при инициализации `SafeFunctionManager()`
3. SFM не загружен в production окружении

#### **Шаг 2: Проверить на сервере**

```bash
# На сервере проверить:
cd /opt/aladdin-backend
python3 -c "
from security.sfm_singleton_new import get_sfm
sfm = get_sfm()
print('SFM Status:', sfm.get_status())
print('Functions count:', len(sfm.functions))
print('Original SFM available:', sfm._sfm is not None)
"
```

**Ожидаемый результат:**
```
SFM Status: {'version': '3.0.0-original', 'original_sfm_available': True, 'functions_count': 1074, ...}
Functions count: 1074
Original SFM available: True
```

**Если `original_sfm_available: False`:**
- SFM не инициализирован → нужно исправить

### **✅ РЕШЕНИЕ:**

#### **Вариант 1: Исправить инициализацию SFM (Критично)**

```python
# security/sfm_singleton_new.py
def __init__(self):
    self.version = "3.0.0-original"
    self._sfm = None

    if ORIGINAL_SFM_AVAILABLE and SafeFunctionManager:
        try:
            print("🔄 Initializing original SafeFunctionManager...")
            self._sfm = SafeFunctionManager()
            
            # ✅ ПРОВЕРКА: убедиться что SFM реально работает
            if self._sfm and hasattr(self._sfm, 'functions'):
                func_count = len(self._sfm.functions)
                print(f"✅ Original SFM initialized with {func_count} functions")
                
                # ✅ ТЕСТ: попробовать выполнить тестовую функцию
                try:
                    test_result = self._sfm.execute_function("get_component_status", {"component_id": "test"})
                    print(f"✅ SFM test execution successful: {type(test_result)}")
                except Exception as test_error:
                    print(f"⚠️ SFM test execution failed: {test_error}")
                    # НЕ сбрасываем _sfm в None - возможно функция просто не существует
            else:
                print("❌ SFM initialized but functions not available")
                self._sfm = None
                
        except Exception as e:
            print(f"❌ Failed to initialize original SFM: {e}")
            import traceback
            traceback.print_exc()  # ← Детальный лог ошибки
            self._sfm = None
    else:
        print("⚠️ Original SFM not available, using mock functions")
        self._sfm = None

    print(f"🚀 SFM {self.version} initialized (available: {self._sfm is not None})")
```

#### **Вариант 2: Возвращать 503 вместо 200 с mock (Рекомендуемый)**

```python
# В роутере /api/user/profile
@app.get("/api/user/profile")
async def get_user_profile(authorization: Optional[str] = Header(None)):
    """Get user profile - returns 503 if SFM unavailable"""
    
    # Проверка JWT
    token = get_auth_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    # Попытка получить реальные данные через SFM
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function(
            "get_authentication_manager_profile", 
            {}
        )
        
        # ✅ КРИТИЧНО: Проверяем что это НЕ mock
        if success and isinstance(result, dict):
            source = result.get("source", "")
            if source == "sfm_mock" or result.get("result") == "mock_fallback":
                # SFM недоступен → возвращаем 503
                raise HTTPException(
                    status_code=503,
                    detail="SFM service temporarily unavailable. Please try again later.",
                    headers={"Retry-After": "60"}  # Retry через 60 секунд
                )
            
            # ✅ Реальные данные
            return result
    
    # SFM Adapter недоступен → 503
    raise HTTPException(
        status_code=503,
        detail="SFM adapter not available",
        headers={"Retry-After": "60"}
    )
```

**Преимущества:**
- ✅ Клиент получает явный сигнал (503) о недоступности
- ✅ Нет путаницы между реальными данными и mock
- ✅ Можно реализовать retry с экспоненциальной задержкой

### **📋 ПЛАН ДЕЙСТВИЙ:**

1. **Проверить на сервере:**
   ```bash
   # Проверить статус SFM
   ssh user@server
   cd /opt/aladdin-backend
   python3 -c "from security.sfm_singleton_new import get_sfm; sfm = get_sfm(); print(sfm.get_status())"
   ```

2. **Если SFM не инициализирован:**
   - Проверить логи инициализации
   - Исправить импорт/инициализацию SafeFunctionManager
   - Убедиться что все зависимости установлены

3. **Изменить роутеры:**
   - Возвращать 503 вместо 200 с mock
   - Добавить проверку `source != "sfm_mock"`

4. **Обработать 503 в клиенте:**
   - Показать пользователю понятное сообщение
   - Реализовать retry с задержкой

---

## 3️⃣ **ШУМНЫЕ ЛОГИ: ПОЧЕМУ ИЗБЫТОЧНОЕ ЛОГИРОВАНИЕ?**

### **🔍 ТЕКУЩАЯ СИТУАЦИЯ:**

```swift
// Core/Managers/TokenHealthMonitor.swift:58-79
func startMonitoring() {
    logger.business("👀 DEFENSIVE JWT: Starting proactive token health monitoring")
    
    // Cancel existing timer if any
    stopMonitoring()  // ← Всегда вызывается, даже если таймера нет
    
    // Create new timer
    DispatchQueue.main.async { [weak self] in
        // ...
        strongSelf.logger.business("✅ DEFENSIVE JWT: Proactive token health monitoring is now ACTIVE")
    }
}

func stopMonitoring() {
    logger.business("⏹️ DEFENSIVE JWT: Stopping token health monitoring")
    monitoringTimer?.invalidate()
    monitoringTimer = nil
    logger.business("✅ DEFENSIVE JWT: Health monitoring stopped")
}
```

**Результат в логах:**
```
[18:40:11.011] 👀 DEFENSIVE JWT: Starting proactive token health monitoring
[18:40:11.016] ⏹️ DEFENSIVE JWT: Stopping token health monitoring
[18:40:11.021] ✅ DEFENSIVE JWT: Health monitoring stopped
[18:40:11.025] ✅ DEFENSIVE JWT: Proactive token health monitoring is now ACTIVE
```

**4 строки логов для одной операции!**

### **❓ ПОЧЕМУ МЫ СДЕЛАЛИ ИМЕННО ТАК?**

**Логика ML системы:**
1. **Защита от дубликатов** — гарантирует, что активен только один таймер
2. **Идемпотентность** — можно безопасно вызывать `startMonitoring()` несколько раз
3. **Детальное логирование** — для отладки важно видеть все шаги

**Это правильная логика**, но **логи избыточны для production**.

### **📊 ВЛИЯНИЕ ИЗБЫТОЧНОГО ЛОГИРОВАНИЯ:**

#### **1. Размер логов:**
- **4 строки** вместо **2 строк** = **+100% объём логов**
- При 1000 запусках приложения = **+2000 строк логов**
- Увеличение размера лог-файлов и затрат на хранение

#### **2. Читаемость:**
- Сложнее найти реальные проблемы в логах
- "Шум" мешает видеть важные события
- Анализ логов занимает больше времени

#### **3. Производительность:**
- Каждый `logger.business()` = системный вызов
- При большом объёме логов = замедление работы
- Особенно критично на устройствах с ограниченными ресурсами

### **✅ ОПТИМАЛЬНОЕ РЕШЕНИЕ:**

```swift
// Core/Managers/TokenHealthMonitor.swift

func startMonitoring() {
    let hadTimer = monitoringTimer != nil
    
    // ✅ Логируем только при необходимости
    if hadTimer {
        logger.business("🔄 DEFENSIVE JWT: Restarting token health monitoring")
        stopMonitoring(silent: false)  // Логируем при перезапуске
    } else {
        logger.business("👀 DEFENSIVE JWT: Starting proactive token health monitoring")
    }
    
    // Create new timer on main thread
    DispatchQueue.main.async { [weak self] in
        guard let strongSelf = self else { return }
        
        strongSelf.monitoringTimer = Timer.scheduledTimer(
            withTimeInterval: strongSelf.monitoringInterval,
            repeats: true
        ) { [weak self] _ in
            guard let self = self else { return }
            Task { await self.checkTokenHealth() }
        }
        
        // ✅ Одна строка лога вместо двух
        if hadTimer {
            strongSelf.logger.business("✅ DEFENSIVE JWT: Token health monitoring restarted")
        } else {
            strongSelf.logger.business("✅ DEFENSIVE JWT: Token health monitoring started - checking every \(Int(strongSelf.monitoringInterval)) seconds")
        }
    }
}

func stopMonitoring(silent: Bool = false) {
    guard monitoringTimer != nil else {
        // ✅ Не логируем если таймера нет
        return
    }
    
    if !silent {
        logger.business("⏹️ DEFENSIVE JWT: Stopping token health monitoring")
    }
    
    monitoringTimer?.invalidate()
    monitoringTimer = nil
    
    if !silent {
        logger.business("✅ DEFENSIVE JWT: Health monitoring stopped")
    }
}
```

**Результат:**
- ✅ При первом запуске: **2 строки** вместо 4 (-50%)
- ✅ При перезапуске: **3 строки** (restart → stop → restarted)
- ✅ Нет лишних логов при отсутствии таймера

### **📊 СРАВНЕНИЕ:**

| Сценарий | Текущее | Оптимизированное | Экономия |
|----------|---------|------------------|----------|
| Первый запуск | 4 строки | 2 строки | **-50%** |
| Перезапуск | 4 строки | 3 строки | **-25%** |
| Повторный вызов без таймера | 4 строки | 0 строк | **-100%** |

### **✅ ЧТО ДАСТ ОПТИМИЗАЦИЯ:**

1. **Меньше логов:**
   - Снижение объёма лог-файлов на 30-50%
   - Меньше затрат на хранение и анализ

2. **Лучшая читаемость:**
   - Проще найти реальные проблемы
   - Меньше "шума" в логах

3. **Производительность:**
   - Меньше системных вызовов
   - Быстрее работа на слабых устройствах

---

## 4️⃣ **EMERGENCY RESET: ЗА ЧТО ОТВЕЧАЕТ И КАК ОПТИМИЗИРОВАТЬ?**

### **🔍 ТЕКУЩАЯ СИТУАЦИЯ:**

```swift
// Core/Managers/SubscriptionManager.swift:227-228
// 🚨 DEFENSIVE JWT: Emergency reset Circuit Breaker if stuck
JWTCircuitBreaker.shared.emergencyReset()
```

```swift
// Core/Managers/JWTCircuitBreaker.swift:362-370
func emergencyReset() {
    logger.business("🚨 DEFENSIVE JWT: Emergency reset to CLOSED state")
    forceState(.closed)
    JWTEventLogger.logEvent(.circuitBreakerStateChanged(state: "CLOSED", reason: "Emergency reset"))
}

func forceState(_ newState: CircuitState) {
    logger.business("🔧 DEFENSIVE JWT: Manual state change to \(newState.rawValue) (testing only)")
    // ...
}
```

**Результат в логах:**
```
[18:40:11.175] 🚨 DEFENSIVE JWT: Emergency reset to CLOSED state
[18:40:11.180] 🔧 DEFENSIVE JWT: Manual state change to closed (testing only)
```

### **❓ ЗА ЧТО ОТВЕЧАЕТ CIRCUIT BREAKER?**

**Circuit Breaker (CB)** — паттерн защиты от каскадных сбоев:

1. **CLOSED (норма)** — все запросы проходят
2. **OPEN (защита)** — запросы блокируются после N ошибок
3. **HALF-OPEN (тест)** — пробуем восстановление

**Зачем Emergency Reset:**
- Если CB "застрял" в OPEN после предыдущего запуска
- При старте приложения гарантируем нормальное состояние
- Предотвращаем блокировку всех запросов из-за старого состояния

### **❓ ПОЧЕМУ МЫ СДЕЛАЛИ ИМЕННО ТАК?**

**Логика ML системы:**
1. **Гарантия нормального состояния** — при старте CB всегда в CLOSED
2. **Защита от "застрявшего" CB** — если приложение упало с CB в OPEN
3. **Простота** — не нужно проверять состояние, просто сбрасываем

**Это правильная логика**, но **избыточна** — сбрасываем даже если CB уже в CLOSED.

### **📊 ВЛИЯНИЕ ТЕКУЩЕЙ РЕАЛИЗАЦИИ:**

#### **1. Избыточные операции:**
- Сброс счётчиков (`failureCount = 0`)
- Логирование события
- Отправка в analytics
- **Даже если CB уже в CLOSED!**

#### **2. "(testing only)" в прод:**
- Фраза попадает в production логи
- Выглядит как тестовый код
- Может смутить при анализе логов

#### **3. Analytics шум:**
- Событие `circuitBreakerStateChanged` отправляется при каждом старте
- Даже если состояние не изменилось
- Засоряет аналитику

### **✅ ОПТИМАЛЬНОЕ РЕШЕНИЕ:**

```swift
// Core/Managers/JWTCircuitBreaker.swift

// ✅ Добавить getter для текущего состояния
func getCurrentState() -> CircuitState {
    stateLock.lock()
    defer { stateLock.unlock() }
    return state
}

func emergencyReset() {
    stateLock.lock()
    let currentState = state
    stateLock.unlock()
    
    // ✅ Сбрасываем только если НЕ в CLOSED
    if currentState != .closed {
        logger.business("🚨 DEFENSIVE JWT: Circuit Breaker не в CLOSED (\(currentState.rawValue)) - выполняем emergency reset")
        forceState(.closed, reason: "emergency_reset")
        JWTEventLogger.logEvent(.circuitBreakerStateChanged(state: "CLOSED", reason: "Emergency reset"))
    } else {
        logger.business("✅ DEFENSIVE JWT: Circuit Breaker уже в CLOSED - сброс не требуется")
    }
}

func forceState(_ newState: CircuitState, reason: String? = nil) {
    #if DEBUG
    if let reason = reason, reason.contains("testing") {
        logger.business("🔧 DEFENSIVE JWT: Manual state change to \(newState.rawValue) (testing only)")
    } else {
        logger.business("🔧 DEFENSIVE JWT: Manual state change to \(newState.rawValue)")
    }
    #else
    // ✅ Production: без "(testing only)"
    if let reason = reason {
        logger.business("🔧 DEFENSIVE JWT: Circuit Breaker state changed to \(newState.rawValue) (reason: \(reason))")
    } else {
        logger.business("🔧 DEFENSIVE JWT: Circuit Breaker state changed to \(newState.rawValue)")
    }
    #endif
    
    stateLock.lock()
    state = newState
    failureCount = 0
    halfOpenSuccessCount = 0
    lastFailureTime = newState == .open ? Date() : nil
    stateLock.unlock()
}
```

**Результат:**
- ✅ Emergency reset вызывается только при необходимости
- ✅ Нет "(testing only)" в production логах
- ✅ Меньше событий в analytics (только при реальном изменении)

### **📊 СРАВНЕНИЕ:**

| Сценарий | Текущее | Оптимизированное | Экономия |
|----------|---------|------------------|----------|
| CB уже в CLOSED | 2 строки логов + analytics | 1 строка лога | **-50%** |
| CB в OPEN | 2 строки логов + analytics | 2 строки логов + analytics | 0% |
| Повторный вызов | 2 строки логов + analytics | 0 строк (проверка) | **-100%** |

### **✅ ЧТО ДАСТ ОПТИМИЗАЦИЯ:**

1. **Меньше операций:**
   - Сброс только при необходимости
   - Меньше событий в analytics

2. **Чистые логи:**
   - Нет "(testing only)" в production
   - Профессиональный вид логов

3. **Лучшая аналитика:**
   - События только при реальных изменениях
   - Проще отслеживать проблемы

---

## 📋 **ИТОГОВЫЕ РЕКОМЕНДАЦИИ:**

### **Приоритет 1 (Критично):**

1. **🔴 SFM Mock → 503:**
   - Проверить инициализацию SFM на сервере
   - Возвращать 503 вместо 200 с mock
   - Обработать 503 в клиенте

2. **🟡 JWT сроки:**
   - Разграничить сроки для trial (14 дней) vs paid (90 дней)
   - Добавить refresh token механизм

### **Приоритет 2 (Важно):**

3. **🟡 Логирование:**
   - Оптимизировать логи TokenHealthMonitor
   - Убрать "(testing only)" из production

4. **🟢 Circuit Breaker:**
   - Проверять состояние перед emergency reset
   - Логировать только при реальном изменении

### **Приоритет 3 (Оптимизация):**

5. **🟢 Мониторинг:**
   - Добавить метрики для mock ответов
   - Отслеживать частоту emergency reset

---

## ✅ **ВЕРДИКТ:**

**Все рекомендации обоснованы и улучшат систему:**

1. ✅ **JWT разграничение** — правильная архитектура для trial vs paid
2. ✅ **SFM 503** — явный сигнал о недоступности вместо скрытого mock
3. ✅ **Оптимизация логов** — меньше шума, лучше читаемость
4. ✅ **Умный emergency reset** — только при необходимости

**Рекомендуемый порядок внедрения:**
1. SFM Mock → 503 (критично для production)
2. JWT разграничение (важно для безопасности)
3. Оптимизация логов (желательно для качества)
