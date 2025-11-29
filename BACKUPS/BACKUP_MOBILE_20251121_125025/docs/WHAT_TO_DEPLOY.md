# 📦 ЧТО НУЖНО ЗАГРУЗИТЬ НА СЕРВЕР ДЛЯ ОПЛАТЫ

## ✅ ОТВЕТЫ НА ВОПРОСЫ

### 1. `main.py` - он же у нас есть?

**Да, теперь есть!** ✅
- Файл был пустой (2 строки)
- Создан полный `main.py` с FastAPI приложением
- Включает все эндпоинты для оплаты
- Сохраняет согласие на обработку ПДн (152-ФЗ)

### 2. Что значит "весь backend"? Что нужно для оплаты?

**"Весь backend"** = все файлы из папки `payment_service/`, которые нужны для работы:

---

## 📋 СПИСОК ФАЙЛОВ ДЛЯ ЗАГРУЗКИ

### ✅ ОБЯЗАТЕЛЬНЫЕ файлы:

```
payment_service/
├── main.py                    ✅ ГЛАВНЫЙ ФАЙЛ - FastAPI приложение
├── requirements.txt           ✅ Зависимости Python
├── .env                       ✅ Настройки (или .env.example)
│
├── app/                       ✅ ВСЯ ПАПКА app/
│   ├── __init__.py
│   ├── config.py              ✅ Настройки и конфигурация
│   ├── database.py            ✅ Подключение к БД
│   ├── models.py              ✅ Модели БД (Payment, ActivationCode)
│   ├── schemas.py             ✅ Pydantic схемы (PaymentCreateRequest)
│   ├── payment_methods.py     ✅ Список методов оплаты
│   ├── utils.py               ✅ Утилиты (hash_pin, generate_code)
│   ├── rate_limit.py          ✅ Rate limiting
│   └── providers/
│       └── mock_psp.py        ✅ Провайдер платежей (заглушка)
│
└── migrations/                ✅ Миграции БД
    └── add_consent_fields.sql ✅ Добавление полей согласия ПДн
```

### ❌ НЕ нужно загружать:

```
payment_service/
├── .venv/                     ❌ Виртуальное окружение (создастся на сервере)
├── __pycache__/               ❌ Кэш Python
├── *.pyc                      ❌ Скомпилированные файлы
├── payments.db                 ❌ База данных (создастся автоматически)
└── *.backup*                  ❌ Backup файлы
```

---

## 🎯 МИНИМАЛЬНЫЙ НАБОР ДЛЯ ОПЛАТЫ

Для работы оплаты нужно:

1. **`main.py`** - FastAPI приложение с эндпоинтами
2. **`app/`** - все модули (models, schemas, utils и т.д.)
3. **`requirements.txt`** - зависимости Python
4. **`.env`** - настройки (API ключи, номер карты и т.д.)

**Остальное создастся автоматически:**
- База данных `payments.db` создастся при первом запуске
- Виртуальное окружение `.venv` создастся на сервере

---

## 📝 ЧТО ДЕЛАЕТ КАЖДЫЙ ФАЙЛ

### `main.py` (ГЛАВНЫЙ)
- FastAPI приложение
- Эндпоинты:
  - `POST /api/payments/create` - создание платежа
  - `GET /api/payment-methods` - список методов оплаты
  - `POST /api/activation/retrieve` - получение кода активации
  - И другие...

### `app/models.py`
- Модели БД: `Payment`, `ActivationCode`
- Поля для согласия на обработку ПДн

### `app/schemas.py`
- Pydantic схемы для валидации запросов
- `PaymentCreateRequest` с полями согласия

### `app/config.py`
- Настройки из переменных окружения
- API ключи, секреты, номер карты

### `app/database.py`
- Подключение к SQLite базе данных
- Создание сессий

### `app/utils.py`
- Хеширование PIN
- Генерация кодов активации
- Работа с датами

### `app/payment_methods.py`
- Список всех методов оплаты
- QR/СБП, карты банков, ручной перевод

### `app/providers/mock_psp.py`
- Заглушка платежного провайдера
- Для тестирования (можно заменить на реальный)

---

## 🚀 КАК ЗАГРУЗИТЬ

### Вариант 1: Автоматически (скрипт)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./deploy_backend_to_server.sh
```

**Что делает скрипт:**
1. Загружает все файлы на сервер (кроме .venv, __pycache__)
2. Создает виртуальное окружение на сервере
3. Устанавливает зависимости
4. Создает .env файл (если нет)

### Вариант 2: Вручную (rsync)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

rsync -avz --progress \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude 'payments.db' \
  payment_service/ \
  root@149.154.65.180:/opt/aladdin-backend/
```

---

## ✅ ПОСЛЕ ЗАГРУЗКИ НА СЕРВЕРЕ

1. **Установить зависимости:**
   ```bash
   cd /opt/aladdin-backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Настроить .env:**
   ```bash
   nano .env
   # Добавить PAYMENT_CARD_NUMBER и другие настройки
   ```

3. **Запустить backend:**
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8000
   ```

4. **Настроить Nginx** (см. `docs/BACKEND_SETUP_COMPLETE.md`)

---

## 📊 РАЗМЕР ФАЙЛОВ

```
payment_service/
├── main.py              ~8 KB   ✅
├── requirements.txt     ~200 B  ✅
├── .env                 ~100 B  ✅
├── app/                 ~50 KB  ✅
└── migrations/          ~1 KB   ✅
─────────────────────────────────
ИТОГО:                   ~60 KB  ✅
```

**Очень маленький размер!** Легко загрузить даже на медленном соединении.

---

## 🎯 ИТОГО

**Для работы оплаты нужно загрузить:**
1. ✅ `main.py` - теперь создан и готов
2. ✅ Всю папку `app/` - все модули
3. ✅ `requirements.txt` - зависимости
4. ✅ `.env` - настройки (или создать на сервере)
5. ✅ `migrations/` - миграции БД

**Все остальное создастся автоматически на сервере!**

---

**Дата:** 19 ноября 2025  
**Версия:** 1.0

