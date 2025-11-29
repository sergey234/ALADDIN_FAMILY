# 💳 РУКОВОДСТВО: УПРАВЛЕНИЕ ВИДИМОСТЬЮ МЕТОДОВ ОПЛАТЫ

**Дата:** 27 ноября 2025  
**Статус:** ✅ Реализовано

---

## ✅ ЧТО СДЕЛАНО

Реализована система управления видимостью методов оплаты через флаги в настройках.

### Изменения:

1. **`app/config.py`** - добавлена настройка `visible_payment_methods`
2. **`app/payment_methods.py`** - добавлена функция фильтрации методов
3. **`main.py`** - обновлен endpoint `/api/payment-methods` и добавлены админские endpoints

---

## 🎯 ТЕКУЩИЕ НАСТРОЙКИ (ТОП-5 методов)

По умолчанию видимы только ТОП-5 методов:

1. ✅ **СБП** (`qr_sbp`) - QR / Система быстрых платежей
2. ✅ **SberPay** (`sberpay`) - SberPay
3. ✅ **Банковские карты** (`card_*`) - все карты (Сбербанк, Тинькофф, Альфа-Банк, ВТБ и др.)
4. ✅ **Tinkoff Pay** (`tinkoff_pay`) - Tinkoff Pay
5. ✅ **Ручной перевод** (`manual_transfer`) - Оплата на карту через СБП

**Скрыты (но не удалены):**
- Все методы остаются в коде, просто не отображаются на сайте

---

## 📋 API ENDPOINTS

### 1. Получить видимые методы оплаты (для сайта)

```http
GET /api/payment-methods
```

**Ответ:**
```json
{
  "methods": [
    {
      "id": "qr_sbp",
      "label": "QR / Система быстрых платежей",
      "type": "qr",
      "banks": [...]
    },
    ...
  ],
  "total": 5,
  "visible_only": true
}
```

**Параметры:**
- `show_all=false` (по умолчанию) - возвращает только видимые методы
- `show_all=true` - возвращает все методы (включая скрытые)

**Пример:**
```bash
# Только видимые методы
curl http://localhost:8000/api/payment-methods

# Все методы (включая скрытые)
curl "http://localhost:8000/api/payment-methods?show_all=true"
```

---

### 2. Получить настройки видимости (админ)

```http
GET /api/admin/payment-methods/visibility
Headers:
  X-Admin-Key: YOUR_ADMIN_KEY
```

**Ответ:**
```json
{
  "visible_methods": ["qr_sbp", "sberpay", "card_sber", ...],
  "all_methods": [
    {
      "id": "qr_sbp",
      "label": "QR / Система быстрых платежей",
      "type": "qr",
      "visible": true
    },
    {
      "id": "card_alfa",
      "label": "Карта Альфа-Банк",
      "type": "card",
      "visible": false
    },
    ...
  ]
}
```

**Пример:**
```bash
curl -H "X-Admin-Key: YOUR_ADMIN_KEY" \
  http://localhost:8000/api/admin/payment-methods/visibility
```

---

### 3. Обновить настройки видимости (админ)

```http
POST /api/admin/payment-methods/visibility
Headers:
  X-Admin-Key: YOUR_ADMIN_KEY
  Content-Type: application/json
Body:
{
  "visible_methods": "qr_sbp,sberpay,card_sber,card_tinkoff,tinkoff_pay,manual_transfer"
}
```

**Ответ:**
```json
{
  "status": "updated",
  "visible_methods": ["qr_sbp", "sberpay", ...],
  "message": "Payment methods visibility updated..."
}
```

**Пример:**
```bash
curl -X POST \
  -H "X-Admin-Key: YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"visible_methods": "qr_sbp,sberpay,card_sber,tinkoff_pay,manual_transfer"}' \
  http://localhost:8000/api/admin/payment-methods/visibility
```

---

## ⚙️ НАСТРОЙКА ЧЕРЕЗ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ

### Способ 1: Файл `.env`

Создайте файл `.env` в корне `payment_service/`:

```env
PAYMENT_VISIBLE_PAYMENT_METHODS=qr_sbp,sberpay,card_sber,card_tinkoff,card_alfa,card_vtb,card_gpb,card_psb,card_rosselkhoz,card_uralsib,card_mkb,card_rosbank,card_homecredit,card_mts,card_otkritie,card_rencredit,card_rsb,card_sinara,card_trust,tinkoff_pay,manual_transfer
```

### Способ 2: Переменные окружения системы

```bash
export PAYMENT_VISIBLE_PAYMENT_METHODS="qr_sbp,sberpay,card_sber,tinkoff_pay,manual_transfer"
```

### Способ 3: Docker Compose

```yaml
services:
  payment_service:
    environment:
      - PAYMENT_VISIBLE_PAYMENT_METHODS=qr_sbp,sberpay,card_sber,tinkoff_pay,manual_transfer
```

---

## 🔧 БЫСТРОЕ РАЗВЕРТЫВАНИЕ СКРЫТЫХ МЕТОДОВ

### Вариант 1: Через API (рекомендуется)

```bash
# Показать все методы
curl -X POST \
  -H "X-Admin-Key: YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{"visible_methods": "qr_sbp,sberpay,card_sber,card_tinkoff,card_alfa,card_vtb,card_gpb,card_psb,card_rosselkhoz,card_uralsib,card_mkb,card_rosbank,card_homecredit,card_mts,card_otkritie,card_rencredit,card_rsb,card_sinara,card_trust,tinkoff_pay,manual_transfer"}' \
  http://localhost:8000/api/admin/payment-methods/visibility
```

**Примечание:** После изменения через API нужно перезапустить сервис для применения изменений (или использовать переменные окружения для постоянных изменений).

### Вариант 2: Через переменные окружения (постоянно)

1. Обновить `.env` файл или переменные окружения
2. Перезапустить сервис

---

## 📊 СПИСОК ВСЕХ МЕТОДОВ ОПЛАТЫ

### Видимые (ТОП-5):

| ID | Название | Тип |
|---|----------|-----|
| `qr_sbp` | QR / Система быстрых платежей | qr |
| `sberpay` | SberPay | pay_button |
| `card_sber` | Карта Сбербанк | card |
| `card_tinkoff` | Карта Тинькофф | card |
| `card_alfa` | Карта Альфа-Банк | card |
| `card_vtb` | Карта ВТБ | card |
| `card_gpb` | Карта Газпромбанк | card |
| `card_psb` | Карта Промсвязьбанк | card |
| `card_rosselkhoz` | Карта Россельхозбанк | card |
| `card_uralsib` | Карта Уралсиб | card |
| `card_mkb` | Карта МКБ | card |
| `card_rosbank` | Карта Росбанк | card |
| `card_homecredit` | Карта Хоум Кредит | card |
| `card_mts` | Карта МТС Банк | card |
| `card_otkritie` | Карта Банк Открытие | card |
| `card_rencredit` | Карта Ренессанс Кредит | card |
| `card_rsb` | Карта Русский Стандарт | card |
| `card_sinara` | Карта Синара | card |
| `card_trust` | Карта Траст | card |
| `tinkoff_pay` | Tinkoff Pay | pay_button |
| `manual_transfer` | Оплата на карту через СБП | manual |

### Скрытые (можно развернуть):

Все методы уже включены в список выше. Если нужно скрыть какие-то методы, просто уберите их ID из `visible_payment_methods`.

---

## ✅ ПРОВЕРКА РАБОТЫ

### 1. Проверить видимые методы:

```bash
curl http://localhost:8000/api/payment-methods
```

Должны вернуться только ТОП-5 методов.

### 2. Проверить все методы:

```bash
curl "http://localhost:8000/api/payment-methods?show_all=true"
```

Должны вернуться все методы.

### 3. Проверить настройки (админ):

```bash
curl -H "X-Admin-Key: YOUR_ADMIN_KEY" \
  http://localhost:8000/api/admin/payment-methods/visibility
```

---

## 🎯 ИСПОЛЬЗОВАНИЕ НА САЙТЕ

### JavaScript пример:

```javascript
// Получить видимые методы оплаты
async function loadPaymentMethods() {
  const response = await fetch('/api/payment-methods');
  const data = await response.json();
  
  // data.methods содержит только видимые методы
  data.methods.forEach(method => {
    // Отобразить метод на странице
    console.log(method.label);
  });
}
```

### React пример:

```jsx
import { useEffect, useState } from 'react';

function PaymentMethods() {
  const [methods, setMethods] = useState([]);
  
  useEffect(() => {
    fetch('/api/payment-methods')
      .then(res => res.json())
      .then(data => setMethods(data.methods));
  }, []);
  
  return (
    <div>
      {methods.map(method => (
        <button key={method.id}>
          {method.label}
        </button>
      ))}
    </div>
  );
}
```

---

## 📝 ПРИМЕЧАНИЯ

1. **Изменения через API** - временные, применяются до перезапуска сервиса
2. **Изменения через переменные окружения** - постоянные, применяются после перезапуска
3. **Скрытые методы не удалены** - они остаются в коде и могут быть быстро развернуты
4. **Безопасность** - админские endpoints требуют `X-Admin-Key` заголовок

---

## ✅ ГОТОВО К ИСПОЛЬЗОВАНИЮ

Система полностью реализована и готова к использованию!

**Следующие шаги:**
1. Обновить сайт, чтобы использовать `/api/payment-methods` вместо статического списка
2. Настроить админ-панель для управления видимостью методов (опционально)
3. Протестировать работу на продакшене

---

**Документ создан:** 27 ноября 2025  
**Статус:** ✅ Реализовано и готово к использованию

