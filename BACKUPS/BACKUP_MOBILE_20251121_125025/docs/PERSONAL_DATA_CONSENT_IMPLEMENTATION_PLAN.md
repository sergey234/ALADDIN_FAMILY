# 📋 ПЛАН ВНЕДРЕНИЯ: Согласие на обработку персональных данных (152-ФЗ)

**Дата создания:** 19 ноября 2025  
**Срок реализации:** До 1 сентября 2025  
**Статус:** ⚠️ Частично реализовано (требуется доработка)

---

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ

### ✅ ЧТО УЖЕ ЕСТЬ:

1. **iOS приложение:**
   - ✅ `ConsentModal.swift` — модальное окно согласия для регистрации
   - ✅ Сохранение согласия в `UserDefaults` (`consentAccepted`, `consentDate`, `consentVersion`)
   - ✅ Контактная информация в `AppConfig.Support` (телефон, Telegram)

2. **Лендинг:**
   - ✅ `consent_variant_1_final.html` — HTML версия согласия
   - ✅ `privacy.html` — политика конфиденциальности (доступна на https://aladdin-ai.ru/privacy.html)
   - ✅ `terms.html` — условия использования (доступны на https://aladdin-ai.ru/terms.html)

3. **Backend:**
   - ⚠️ Структура для сохранения согласия отсутствует

---

### ❌ ЧТО ОТСУТСТВУЕТ:

1. **Лендинг (форма оплаты):**
   - ❌ Отдельный чек-бокс "Согласие на обработку ПДн" (отдельно от оферты)
   - ❌ Ссылка на `consent.html` рядом с чек-боксом
   - ❌ Валидация: форма не отправляется без согласия
   - ❌ Сохранение факта согласия (alias, timestamp, IP) в backend

2. **Backend:**
   - ❌ Поле `personalDataConsent: Bool` в `PaymentCreateRequest`
   - ❌ Поле `consentTimestamp: datetime` в модели `Payment`
   - ❌ Логирование согласия
   - ❌ Эндпоинт для выгрузки согласий (для проверок)

3. **iOS приложение:**
   - ❌ Блок согласия перед активацией кода
   - ❌ Раздел в Profile → "Согласие на обработку данных" (просмотр и отзыв)
   - ❌ Ссылка на `consent.html` через SafariViewController

4. **Лендинг (контактная информация):**
   - ❌ Контактная информация в футере/шапке
   - ❌ Телефон: `+7 (927) 005-15-77`
   - ❌ Telegram: `@aladdin_support_bot` или ссылка `https://t.me/aladdin_support_bot`
   - ❌ Email (опционально): `sergey21-02-84@list.ru`

5. **iOS приложение (контактная информация):**
   - ⚠️ Контакты есть в `AppConfig`, но нужно проверить отображение в UI

---

## 🎯 ПЛАН ВНЕДРЕНИЯ

### ЭТАП 1: Подготовка документов (30 минут)

#### 1.1. Создать финальный документ согласия

**Файл:** `docs/legal/personal_data_consent.md`

**Содержание:**
- Данные оператора (ООО "АЛАДДИН" или ваше юридическое лицо)
- Список ПД (alias, IP, email (если указан), телефон (если указан))
- Цели обработки (оплата, активация подписки, работа сервиса)
- Действия (сбор, хранение, передача, удаление)
- Срок обработки (до отзыва согласия или прекращения использования)
- Порядок отзыва согласия
- Ссылка на Политику конфиденциальности

**Пример структуры:**
```markdown
# СОГЛАСИЕ НА ОБРАБОТКУ ПЕРСОНАЛЬНЫХ ДАННЫХ

**Оператор:** ООО "АЛАДДИН"  
**ИНН:** [ваш ИНН]  
**Адрес:** [ваш адрес]

**1. Персональные данные:**
- Alias (псевдоним пользователя)
- IP-адрес
- Email (если указан при регистрации)
- Телефон (если указан)
- Данные об оплате (сумма, тариф, период)

**2. Цели обработки:**
- Обработка платежей
- Активация подписки
- Обеспечение работы сервиса
- Связь с пользователем

**3. Способы обработки:**
- Автоматизированная обработка
- Хранение в базе данных
- Передача платежным системам (только для обработки платежа)

**4. Срок обработки:**
До отзыва согласия пользователем или до прекращения использования сервиса.

**5. Права пользователя:**
- Право на доступ к данным
- Право на исправление данных
- Право на удаление данных
- Право на отзыв согласия

**6. Отзыв согласия:**
Для отзыва согласия напишите на email: [email] или через Telegram: [ссылка]

**Дата:** [дата]  
**Версия:** 1.0
```

#### 1.2. Создать HTML версию согласия

**Файл:** `landing/consent.html`

**Требования:**
- Адаптивный дизайн (как `privacy.html` и `terms.html`)
- Ссылки на `privacy.html` и `terms.html`
- Кнопка "Назад" или ссылка на главную
- Версионирование (версия 1.0, дата)

#### 1.3. Разместить на сервере

```bash
# На локальной машине
rsync -avz \
  /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/consent.html \
  root@149.154.65.180:/var/www/aladdin-ai.ru/

# Проверка
curl -I https://aladdin-ai.ru/consent.html
```

**Ожидаемый результат:** `HTTP/2 200`

---

### ЭТАП 2: Лендинг — форма оплаты (1-2 часа)

#### 2.1. Добавить чек-бокс согласия в форму оплаты

**Файл:** `landing/index.html`

**Местоположение:** После чек-бокса оферты, перед кнопкой "Перейти к оплате"

**HTML структура:**
```html
<!-- Согласие на обработку ПДн -->
<div class="consent-wrapper" style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">
    <label style="display: flex; align-items: flex-start; cursor: pointer;">
        <input 
            type="checkbox" 
            id="personalDataConsent" 
            name="personalDataConsent" 
            required
            style="margin-right: 10px; margin-top: 3px; width: 18px; height: 18px; cursor: pointer;"
        >
        <span style="font-size: 14px; line-height: 1.5; color: #333;">
            Я даю согласие на обработку персональных данных в соответствии с 
            <a href="/consent.html" target="_blank" style="color: #007bff; text-decoration: underline;">
                Согласием на обработку персональных данных
            </a>
            и 
            <a href="/privacy.html" target="_blank" style="color: #007bff; text-decoration: underline;">
                Политикой конфиденциальности
            </a>
        </span>
    </label>
</div>
```

#### 2.2. Добавить валидацию в JavaScript

**Файл:** `landing/index.html` (функция `handleFormSubmit`)

**Добавить проверку:**
```javascript
// Проверка согласия на обработку ПДн
const consentCheckbox = document.getElementById('personalDataConsent');
if (!consentCheckbox || !consentCheckbox.checked) {
    alert('⚠️ Для продолжения необходимо дать согласие на обработку персональных данных.');
    consentCheckbox?.focus();
    return;
}
```

#### 2.3. Отправка согласия в backend

**Файл:** `landing/index.html` (функция `handleFormSubmit`)

**Добавить в requestBody:**
```javascript
const requestBody = {
    tariffId: selectedTariff,
    userAlias: alias,
    pin: pin,
    paymentMethod: paymentMethod,
    periodMonths: parseInt(selectedPeriod),
    amount: calculatedAmount,
    personalDataConsent: true,  // ✅ НОВОЕ
    consentTimestamp: new Date().toISOString(),  // ✅ НОВОЕ
    consentIP: await getClientIP()  // ✅ НОВОЕ (опционально)
};
```

**Функция получения IP (опционально):**
```javascript
async function getClientIP() {
    try {
        const response = await fetch('https://api.ipify.org?format=json');
        const data = await response.json();
        return data.ip;
    } catch (error) {
        return 'unknown';
    }
}
```

#### 2.4. Добавить контактную информацию в футер

**Файл:** `landing/index.html` (секция footer)

**Добавить:**
```html
<footer style="background: #2c3e50; color: #ecf0f1; padding: 40px 20px; margin-top: 60px;">
    <div class="container" style="max-width: 1200px; margin: 0 auto;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px;">
            <!-- Контакты -->
            <div>
                <h3 style="color: #fff; margin-bottom: 15px; font-size: 18px;">Контакты</h3>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Телефон:</strong><br>
                    <a href="tel:+79270051577" style="color: #3498db; text-decoration: none;">
                        +7 (927) 005-15-77
                    </a>
                </p>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Telegram:</strong><br>
                    <a href="https://t.me/aladdin_support_bot" target="_blank" style="color: #3498db; text-decoration: none;">
                        @aladdin_support_bot
                    </a>
                </p>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Email:</strong><br>
                    <a href="mailto:sergey21-02-84@list.ru" style="color: #3498db; text-decoration: none;">
                        sergey21-02-84@list.ru
                    </a>
                </p>
            </div>
            
            <!-- Документы -->
            <div>
                <h3 style="color: #fff; margin-bottom: 15px; font-size: 18px;">Документы</h3>
                <ul style="list-style: none; padding: 0;">
                    <li style="margin: 8px 0;">
                        <a href="/privacy.html" style="color: #3498db; text-decoration: none; font-size: 14px;">
                            Политика конфиденциальности
                        </a>
                    </li>
                    <li style="margin: 8px 0;">
                        <a href="/terms.html" style="color: #3498db; text-decoration: none; font-size: 14px;">
                            Условия использования
                        </a>
                    </li>
                    <li style="margin: 8px 0;">
                        <a href="/consent.html" style="color: #3498db; text-decoration: none; font-size: 14px;">
                            Согласие на обработку ПДн
                        </a>
                    </li>
                </ul>
            </div>
        </div>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #34495e; text-align: center; font-size: 12px; color: #95a5a6;">
            © 2025 ALADDIN AI. Все права защищены.
        </div>
    </div>
</footer>
```

---

### ЭТАП 3: Backend — сохранение согласия (1 час)

#### 3.1. Обновить схему PaymentCreateRequest

**Файл:** `payment_service/app/schemas.py`

**Добавить поля:**
```python
class PaymentCreateRequest(BaseModel):
    tariff_id: str
    user_alias: str
    pin: str
    payment_method: str
    period_months: int
    amount: float
    personal_data_consent: bool  # ✅ НОВОЕ
    consent_timestamp: Optional[str] = None  # ✅ НОВОЕ (ISO format)
    consent_ip: Optional[str] = None  # ✅ НОВОЕ
```

#### 3.2. Обновить модель Payment

**Файл:** `payment_service/app/models.py`

**Добавить колонки:**
```python
class Payment(Base):
    __tablename__ = "payments"
    
    # ... существующие поля ...
    
    personal_data_consent: bool = Column(Boolean, default=False, nullable=False)  # ✅ НОВОЕ
    consent_timestamp: Optional[datetime] = Column(DateTime, nullable=True)  # ✅ НОВОЕ
    consent_ip: Optional[str] = Column(String(45), nullable=True)  # ✅ НОВОЕ (IPv6 support)
```

#### 3.3. Обновить эндпоинт create_payment

**Файл:** `payment_service/main.py`

**Добавить сохранение:**
```python
@router.post("/api/payments/create")
async def create_payment(payload: PaymentCreateRequest):
    # ... существующий код ...
    
    # Сохранение согласия
    payment.personal_data_consent = payload.personal_data_consent
    if payload.consent_timestamp:
        payment.consent_timestamp = datetime.fromisoformat(payload.consent_timestamp.replace('Z', '+00:00'))
    payment.consent_ip = payload.consent_ip
    
    # Логирование
    if payload.personal_data_consent:
        logger.info(f"✅ Согласие на обработку ПДн получено: alias={payload.user_alias}, IP={payload.consent_ip}, timestamp={payload.consent_timestamp}")
    else:
        logger.warning(f"⚠️ Согласие на обработку ПДн НЕ получено: alias={payload.user_alias}")
    
    # ... остальной код ...
```

#### 3.4. Создать миграцию базы данных

**Файл:** `payment_service/migrations/add_consent_fields.sql`

```sql
ALTER TABLE payments 
ADD COLUMN personal_data_consent BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN consent_timestamp DATETIME,
ADD COLUMN consent_ip VARCHAR(45);
```

**Применить миграцию:**
```bash
cd payment_service
sqlite3 app.db < migrations/add_consent_fields.sql
```

#### 3.5. Создать эндпоинт для выгрузки согласий (опционально)

**Файл:** `payment_service/main.py`

```python
@router.get("/api/admin/consents/export")
async def export_consents(
    admin_key: str = Header(..., alias="X-Admin-Key"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    # Проверка admin key
    if admin_key != settings.admin_key:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    
    # Запрос согласий
    query = select(Payment).where(Payment.personal_data_consent == True)
    
    if start_date:
        query = query.where(Payment.consent_timestamp >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.where(Payment.consent_timestamp <= datetime.fromisoformat(end_date))
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(query)
        payments = result.scalars().all()
        
        consents = [
            {
                "alias": p.alias,
                "consent_timestamp": p.consent_timestamp.isoformat() if p.consent_timestamp else None,
                "consent_ip": p.consent_ip,
                "payment_id": p.id
            }
            for p in payments
        ]
        
        return {"consents": consents, "total": len(consents)}
```

---

### ЭТАП 4: iOS приложение — согласие перед активацией (1-2 часа)

#### 4.1. Добавить блок согласия на экране активации

**Файл:** `Screens/26_ActivationCodeScreen.swift`

**Добавить:**
```swift
@State private var consentAccepted: Bool = false

// В body, перед кнопкой "Активировать":
VStack(alignment: .leading, spacing: 12) {
    HStack(alignment: .top, spacing: 12) {
        Toggle("", isOn: $consentAccepted)
            .toggleStyle(SwitchToggleStyle(tint: .blue))
            .frame(width: 50)
        
        VStack(alignment: .leading, spacing: 4) {
            Text("Я даю согласие на обработку персональных данных")
                .font(.system(size: 14, weight: .medium))
            
            HStack(spacing: 4) {
                Text("в соответствии с")
                    .font(.system(size: 12))
                    .foregroundColor(.secondary)
                
                Button(action: {
                    if let url = URL(string: "https://aladdin-ai.ru/consent.html") {
                        UIApplication.shared.open(url)
                    }
                }) {
                    Text("Согласием на обработку ПДн")
                        .font(.system(size: 12))
                        .foregroundColor(.blue)
                        .underline()
                }
                
                Text("и")
                    .font(.system(size: 12))
                    .foregroundColor(.secondary)
                
                Button(action: {
                    if let url = URL(string: "https://aladdin-ai.ru/privacy.html") {
                        UIApplication.shared.open(url)
                    }
                }) {
                    Text("Политикой конфиденциальности")
                        .font(.system(size: 12))
                        .foregroundColor(.blue)
                        .underline()
                }
            }
        }
    }
    .padding()
    .background(Color.blue.opacity(0.05))
    .cornerRadius(12)
}
```

**Обновить кнопку "Активировать":**
```swift
Button(action: {
    if !consentAccepted {
        // Показать алерт
        return
    }
    // ... существующий код активации ...
}) {
    Text("Активировать")
        .frame(maxWidth: .infinity)
        .frame(height: 50)
        .background(consentAccepted ? Color.blue : Color.gray)
        .foregroundColor(.white)
        .cornerRadius(12)
}
.disabled(!consentAccepted)
```

#### 4.2. Добавить раздел в Profile

**Файл:** `Screens/05_ProfileScreen.swift`

**Добавить секцию:**
```swift
Section(header: Text("Согласие на обработку данных")) {
    HStack {
        VStack(alignment: .leading, spacing: 4) {
            Text("Согласие на обработку ПДн")
                .font(.system(size: 16, weight: .medium))
            
            if let consentDate = UserDefaults.standard.object(forKey: AppConfig.UserDefaultsKeys.consentDate) as? Date {
                Text("Дано: \(consentDate.formatted(date: .abbreviated, time: .shortened))")
                    .font(.system(size: 12))
                    .foregroundColor(.secondary)
            }
        }
        
        Spacer()
        
        Button(action: {
            // Открыть consent.html в SafariViewController
            if let url = URL(string: "https://aladdin-ai.ru/consent.html") {
                UIApplication.shared.open(url)
            }
        }) {
            Text("Просмотреть")
                .font(.system(size: 14))
                .foregroundColor(.blue)
        }
    }
    
    Button(action: {
        // Показать алерт с подтверждением отзыва
        // После подтверждения: очистить UserDefaults, показать экран регистрации
    }) {
        Text("Отозвать согласие")
            .font(.system(size: 14))
            .foregroundColor(.red)
    }
}
```

---

### ЭТАП 5: Обновление документации (30 минут)

#### 5.1. Обновить PAYMENT_FULL_IMPLEMENTATION_PLAN.md

**Добавить раздел:**
```markdown
## 24. Согласие на обработку ПДн (152-ФЗ)

**Статус:** ✅ Реализовано  
**Дата:** 19 ноября 2025

**Реализовано:**
- ✅ Отдельный чек-бокс в форме оплаты на лендинге
- ✅ Сохранение согласия в backend (personalDataConsent, consentTimestamp, consentIP)
- ✅ Блок согласия перед активацией кода в iOS
- ✅ Раздел в Profile для просмотра и отзыва согласия
- ✅ Контактная информация на лендинге и в приложении

**URL:**
- Согласие: https://aladdin-ai.ru/consent.html
- Политика: https://aladdin-ai.ru/privacy.html
- Условия: https://aladdin-ai.ru/terms.html
```

#### 5.2. Обновить FAQ

**Файл:** `landing/cms/faq.json`

**Добавить вопрос:**
```json
{
  "question": "Требуется ли согласие на обработку персональных данных?",
  "answer": "Да, для оформления подписки требуется ваше согласие на обработку персональных данных в соответствии с Федеральным законом № 152-ФЗ. Согласие оформляется отдельным документом и может быть отозвано в любой момент через приложение или обратившись в поддержку."
}
```

#### 5.3. Обновить Review Notes

**Файл:** `docs/REVIEW_NOTES_TEMPLATE.md`

**Добавить раздел:**
```markdown
## 🔒 СОГЛАСИЕ НА ОБРАБОТКУ ПЕРСОНАЛЬНЫХ ДАННЫХ

Приложение соответствует требованиям российского законодательства (152-ФЗ):
- ✅ Отдельное согласие на обработку ПДн оформляется на сайте и в приложении
- ✅ Пользователь может просмотреть текст согласия и отозвать его в любой момент
- ✅ Все согласия логируются и могут быть предоставлены по запросу контролирующих органов
```

---

## 📋 ЧЕКЛИСТ ВНЕДРЕНИЯ

### Документы:
- [ ] Создать `docs/legal/personal_data_consent.md`
- [ ] Создать `landing/consent.html`
- [ ] Загрузить `consent.html` на сервер
- [ ] Проверить доступность `https://aladdin-ai.ru/consent.html`

### Лендинг:
- [ ] Добавить чек-бокс согласия в форму оплаты
- [ ] Добавить валидацию (форма не отправляется без согласия)
- [ ] Добавить отправку `personalDataConsent`, `consentTimestamp`, `consentIP` в backend
- [ ] Добавить контактную информацию в футер
- [ ] Обновить FAQ

### Backend:
- [ ] Обновить `PaymentCreateRequest` (добавить поля согласия)
- [ ] Обновить модель `Payment` (добавить колонки)
- [ ] Создать и применить миграцию БД
- [ ] Обновить эндпоинт `create_payment` (сохранение согласия)
- [ ] Добавить логирование согласий
- [ ] (Опционально) Создать эндпоинт `/api/admin/consents/export`

### iOS приложение:
- [ ] Добавить блок согласия на экране активации
- [ ] Добавить раздел в Profile (просмотр и отзыв согласия)
- [ ] Проверить отображение контактной информации
- [ ] Обновить `ConsentModal` (если нужно)

### Документация:
- [ ] Обновить `PAYMENT_FULL_IMPLEMENTATION_PLAN.md`
- [ ] Обновить `REVIEW_NOTES_TEMPLATE.md`
- [ ] Обновить FAQ на лендинге

---

## ⏱️ ОЦЕНКА ВРЕМЕНИ

- **Этап 1 (Документы):** 30 минут
- **Этап 2 (Лендинг):** 1-2 часа
- **Этап 3 (Backend):** 1 час
- **Этап 4 (iOS):** 1-2 часа
- **Этап 5 (Документация):** 30 минут

**Общее время:** ~4-6 часов

---

## 🎯 ПРИОРИТЕТЫ

### 🔴 Критическое (блокирует запуск):
1. Чек-бокс согласия в форме оплаты на лендинге
2. Валидация согласия (форма не отправляется без галочки)
3. Сохранение согласия в backend
4. Контактная информация на лендинге

### 🟡 Важное (рекомендуется):
1. Блок согласия перед активацией в iOS
2. Раздел в Profile для просмотра и отзыва
3. Эндпоинт для выгрузки согласий
4. Обновление документации

---

## 📝 ЗАМЕТКИ

- **Срок реализации:** До 1 сентября 2025 (требование 152-ФЗ)
- **Версионирование:** Согласие должно иметь версию и дату
- **Логирование:** Все согласия должны логироваться для аудита
- **Отзыв согласия:** Пользователь должен иметь возможность отозвать согласие в любой момент

---

**Документ создан:** 19 ноября 2025  
**Последнее обновление:** 19 ноября 2025  
**Статус:** ✅ План готов к реализации

