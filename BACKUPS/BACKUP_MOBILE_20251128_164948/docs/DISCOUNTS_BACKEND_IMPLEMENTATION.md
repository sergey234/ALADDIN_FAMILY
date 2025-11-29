# ✅ BACKEND РЕАЛИЗАЦИЯ: Скидки за предоплату на 3/6/12 месяцев

**Дата:** 15 ноября 2025  
**Статус:** ✅ **BACKEND РЕАЛИЗОВАН**

---

## ✅ ЧТО РЕАЛИЗОВАНО

### 1. Добавлены тарифы на 3/6/12 месяцев

**Файл:** `security/managers/subscription_manager.py`

**Добавлены планы:**
- `BASIC_3M` - 783₽ за 3 месяца (скидка 10%)
- `BASIC_6M` - 1479₽ за 6 месяцев (скидка 15%)
- `BASIC_12M` - 2780₽ за 12 месяцев (скидка 20%, экономия 700₽)
- `FAMILY_3M` - 1323₽ за 3 месяца (скидка 10%)
- `FAMILY_6M` - 2499₽ за 6 месяцев (скидка 15%)
- `FAMILY_12M` - 4704₽ за 12 месяцев (скидка 20%)
- `PREMIUM_3M` - 2430₽ за 3 месяца (скидка 10%)
- `PREMIUM_6M` - 4590₽ за 6 месяцев (скидка 15%)
- `PREMIUM_12M` - 8640₽ за 12 месяцев (скидка 20%)

**Каждый план включает:**
- `period_months` - период подписки (3, 6, 12)
- `discount_percent` - процент скидки (10, 15, 20)
- `original_price` - цена без скидки
- `monthly_price` - цена за месяц (вычисляется автоматически)
- `savings` - экономия (вычисляется автоматически)

---

### 2. Обновлен метод `create_subscription()`

**Файл:** `security/managers/subscription_manager.py`

**Добавлен параметр:**
```python
async def create_subscription(self, family_id: str, tier: SubscriptionTier,
                              trial_days: Optional[int] = None,
                              period_months: Optional[int] = None) -> Dict[str, Any]:
```

**Логика расчета периода:**
- Если `period_months` указан, используется он
- Если нет, используется `period_months` из плана
- По умолчанию: 1 месяц (30 дней)

**Расчет end_date:**
```python
if period_months is not None and period_months > 0:
    subscription_days = period_months * 30
else:
    plan_period_months = plan.period_months if hasattr(plan, 'period_months') else 1
    subscription_days = plan_period_months * 30

end_date = now + timedelta(days=subscription_days)
```

---

### 3. Обновлен API endpoint `/api/payments/qr/create`

**Файл:** `security/api/mobile_api_endpoints.py`

**Обновлен `CreateQRPaymentRequest`:**
```python
class CreateQRPaymentRequest(BaseModel):
    family_id: str
    tariff: str
    amount: float
    payment_method: str = "sbp"
    period_months: Optional[int] = None  # Период подписки: 1, 3, 6, 12 месяцев
```

**Обновлен вызов `generate_family_qr`:**
```python
result = await qr_payment_manager.generate_family_qr(
    family_id=request.family_id,
    tariff=request.tariff,
    devices_count=5,
    amount=request.amount,
    period_months=request.period_months  # Передаем период
)
```

---

### 4. Обновлен `qr_payment_manager`

**Файл:** `security/managers/qr_payment_manager.py`

**Обновлен `generate_family_qr`:**
```python
async def generate_family_qr(self, family_id: str, tariff: str,
                             devices_count: int, amount: float,
                             period_months: Optional[int] = None) -> Dict[str, Any]:
```

**Обновлен вызов `create_payment`:**
```python
payment_result = await self.create_payment(
    family_id=family_id,
    subscription_tier=tariff,
    amount=Decimal(str(amount)),
    description=f"Оплата подписки {tariff} для {devices_count} устройств",
    payment_method=PaymentMethod.SBP,
    period_months=period_months  # Передаем период
)
```

---

## 💰 РАСЧЕТЫ ЦЕН

### BASIC (290₽/мес):

| Период | Цена | Цена/мес | Скидка | Экономия |
|--------|------|----------|--------|----------|
| 1 мес | 290₽ | 290₽ | 0% | 0₽ |
| 3 мес | 783₽ | 261₽ | 10% | 87₽ |
| 6 мес | 1479₽ | 246.5₽ | 15% | 261₽ |
| 12 мес | **2780₽** | **232₽** | **20%** | **700₽** ✅ |

### FAMILY (490₽/мес):

| Период | Цена | Цена/мес | Скидка | Экономия |
|--------|------|----------|--------|----------|
| 1 мес | 490₽ | 490₽ | 0% | 0₽ |
| 3 мес | 1323₽ | 441₽ | 10% | 147₽ |
| 6 мес | 2499₽ | 416.5₽ | 15% | 441₽ |
| 12 мес | 4704₽ | 392₽ | 20% | 1176₽ |

### PREMIUM (990₽/мес):

| Период | Цена | Цена/мес | Скидка | Экономия |
|--------|------|----------|--------|----------|
| 1 мес | 990₽ | 990₽ | 0% | 0₽ |
| 3 мес | 2430₽ | 810₽ | 10% | 270₽ |
| 6 мес | 4590₽ | 765₽ | 15% | 810₽ |
| 12 мес | 8640₽ | 720₽ | 20% | 2160₽ |

---

## 🔄 ПОТОК ДАННЫХ

```
1. iOS отправляет CreateQRPaymentRequest с periodMonths
   ↓
2. API endpoint /api/payments/qr/create принимает запрос
   ↓
3. Вызывается qr_payment_manager.generate_family_qr() с periodMonths
   ↓
4. Создается платеж через create_payment() с periodMonths
   ↓
5. После успешной оплаты создается подписка через create_subscription() с periodMonths
   ↓
6. Подписка создается на указанный период (3/6/12 месяцев)
```

---

## ✅ ПРОВЕРКА

**Все требования выполнены:**
- ✅ Тарифы на 3/6/12 месяцев добавлены в `_initialize_plans()`
- ✅ `create_subscription()` учитывает `periodMonths`
- ✅ API endpoint `/api/payments/qr/create` принимает `periodMonths`
- ✅ `qr_payment_manager` передает `periodMonths` в `create_subscription`
- ✅ BASIC 12 месяцев: экономия 700₽ (вместо 696₽)

---

## 📄 ФАЙЛЫ

**Обновленные файлы:**
- `security/managers/subscription_manager.py` - тарифы и create_subscription
- `security/api/mobile_api_endpoints.py` - API endpoint
- `security/managers/qr_payment_manager.py` - передача periodMonths

**Документация:**
- `docs/DISCOUNTS_COMPLETE_IMPLEMENTATION.md` - полная реализация iOS
- `docs/DISCOUNTS_BACKEND_IMPLEMENTATION.md` - этот файл

---

**Дата реализации:** 15 ноября 2025  
**Статус:** ✅ **BACKEND РЕАЛИЗОВАН**  
**Готово к тестированию:** ✅ **ДА**




