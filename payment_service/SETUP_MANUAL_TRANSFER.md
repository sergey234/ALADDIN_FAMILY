# 💳 Настройка Manual Transfer (Оплата на карту через СБП)

## ⚠️ Проблема

Если на странице оплаты вы видите:
- "⚠️ Номер карты не настроен. Обратитесь в поддержку."
- "Получатель: не указан"

Это означает, что переменные окружения `PAYMENT_CARD_NUMBER` и `PAYMENT_CARD_HOLDER_NAME` не установлены.

## ✅ Решение

### Вариант 1: Установка переменных окружения (рекомендуется)

**Для macOS/Linux:**
```bash
export PAYMENT_CARD_NUMBER="2202 2083 0881 3410"
# Оставьте пустым, чтобы не показывать ФИО
export PAYMENT_CARD_HOLDER_NAME=""
```

**Для Windows (PowerShell):**
```powershell
$env:PAYMENT_CARD_NUMBER="2202 2083 0881 3410"
$env:PAYMENT_CARD_HOLDER_NAME=""
```

**Затем запустите backend:**
```bash
cd payment_service
python3 -m uvicorn main:app --reload --port 8000 --host 0.0.0.0
```

### Вариант 2: Создание .env файла

1. Создайте файл `.env` в папке `payment_service/`:
```bash
cd payment_service
touch .env
```

2. Добавьте в файл `.env`:
```env
PAYMENT_CARD_NUMBER=2202 2083 0881 3410
# Оставьте пустым, если не хотите отображать ФИО на лендинге
PAYMENT_CARD_HOLDER_NAME=
```

3. Установите `python-dotenv` (если ещё не установлен):
```bash
pip3 install python-dotenv
```

4. Обновите `app/config.py` для загрузки `.env`:
```python
from dotenv import load_dotenv
load_dotenv()  # Загружает переменные из .env
```

5. Перезапустите backend.

### Вариант 3: Прямое редактирование config.py (для тестирования)

**⚠️ НЕ рекомендуется для продакшена!**

Отредактируйте `payment_service/app/config.py`:
```python
card_number: str = Field("2202 2083 0881 3410", description="Card number for manual transfers")
card_holder_name: str = Field("", description="Card holder name for manual transfers")
```

## 📝 Формат данных

- **Номер карты:** `2202 2083 0881 3410` (16 цифр, с пробелами или без)
- **Имя держателя:** можно оставить пустым, если не требуется показывать ФИО

## ✅ Проверка

После настройки:
1. Перезапустите backend
2. Создайте новый платёж с методом "Оплата на карту через СБП"
3. На странице `success.html` должны отображаться:
   - Номер карты (крупно, с кнопкой копирования)
   - Имя получателя
   - Инструкции по переводу

## 🔒 Безопасность

⚠️ **ВАЖНО:** 
- НЕ коммитьте `.env` файл в git (добавьте в `.gitignore`)
- НЕ храните реальные данные карты в коде
- Используйте переменные окружения или секреты в продакшене

