# 🇷🇺 РУКОВОДСТВО ПО НАСТРОЙКЕ РОССИЙСКИХ API

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ

### **ШАГ 1: ПОЛУЧЕНИЕ API КЛЮЧА ЯНДЕКС КАРТ**

#### **1.1 Регистрация**
1. Перейдите на https://developer.tech.yandex.ru/
2. Нажмите **"Получить ключ"**
3. Войдите через **Яндекс ID**
4. Создайте новый проект **"ALADDIN Security"**

#### **1.2 Настройка API**
1. Выберите **"Карты"** → **"JavaScript API"**
2. Укажите домен: `localhost` (для разработки)
3. Скопируйте полученный **API ключ**

### **ШАГ 2: АВТОМАТИЧЕСКАЯ НАСТРОЙКА**

```bash
# Запустите скрипт настройки
python3 scripts/setup_russian_apis.py
```

Скрипт автоматически:
- ✅ Запросит ваш API ключ
- ✅ Сохранит его в конфигурацию
- ✅ Протестирует все API
- ✅ Покажет результаты

### **ШАГ 3: РУЧНАЯ НАСТРОЙКА (АЛЬТЕРНАТИВА)**

#### **3.1 Откройте файл конфигурации**
```bash
nano config/russian_apis_config.json
```

#### **3.2 Замените API ключ**
```json
{
  "yandex_maps": {
    "api_key": "ВАШ_РЕАЛЬНЫЙ_API_КЛЮЧ_ЗДЕСЬ",
    "enabled": true
  }
}
```

### **ШАГ 4: ЗАПУСК СИСТЕМЫ**

#### **4.1 Запуск сервера**
```bash
# Автоматический запуск
./start_russian_apis.sh

# Или вручную
python3 russian_apis_server.py
```

#### **4.2 Проверка работы**
```bash
# Проверка здоровья
curl http://localhost:5005/api/russian/health

# Тест геокодирования
curl -X POST http://localhost:5005/api/russian/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "Москва, Красная площадь"}'
```

---

## 🔧 КОНФИГУРАЦИЯ

### **Файл: `config/russian_apis_config.json`**
```json
{
  "yandex_maps": {
    "api_key": "YOUR_YANDEX_API_KEY_HERE",
    "enabled": true,
    "description": "Яндекс Карты API - 25,000 запросов/день бесплатно"
  },
  "glonass_free": {
    "api_key": null,
    "enabled": true,
    "description": "Открытый ГЛОНАСС - 1M+ запросов бесплатно"
  },
  "altox_server": {
    "api_key": null,
    "enabled": true,
    "description": "ALTOX Server - 1 объект бесплатно"
  },
  "settings": {
    "cache_ttl": 300,
    "timeout": 10,
    "retry_attempts": 3,
    "log_level": "INFO"
  }
}
```

---

## 🌐 ДОСТУПНЫЕ API

### **После настройки доступны:**

| API | URL | Описание |
|-----|-----|----------|
| **Health** | `GET /api/russian/health` | Проверка здоровья |
| **Geocode** | `POST /api/russian/geocode` | Геокодирование адресов |
| **Route** | `POST /api/russian/route` | Построение маршрутов |
| **GLONASS** | `POST /api/russian/glonass` | ГЛОНАСС координаты |
| **Statistics** | `GET /api/russian/statistics` | Статистика использования |
| **Status** | `GET /api/russian/status` | Статус всех API |
| **Clear Cache** | `POST /api/russian/clear-cache` | Очистка кэша |
| **Test All** | `POST /api/russian/test-all` | Тестирование всех API |

---

## 🧪 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### **Геокодирование**
```bash
curl -X POST http://localhost:5005/api/russian/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "Москва, Красная площадь"}'
```

### **Построение маршрута**
```bash
curl -X POST http://localhost:5005/api/russian/route \
  -H "Content-Type: application/json" \
  -d '{"from_point": "Москва", "to_point": "Санкт-Петербург"}'
```

### **ГЛОНАСС координаты**
```bash
curl -X POST http://localhost:5005/api/russian/glonass \
  -H "Content-Type: application/json" \
  -d '{"device_id": "device_001"}'
```

---

## 🔍 УСТРАНЕНИЕ ПРОБЛЕМ

### **Проблема: "API ключ недействителен"**
**Решение:**
1. Проверьте правильность API ключа
2. Убедитесь, что ключ активен в Яндекс.Разработке
3. Проверьте домен в настройках ключа

### **Проблема: "Сервер не запускается"**
**Решение:**
1. Проверьте, что порт 5005 свободен
2. Убедитесь, что все зависимости установлены
3. Проверьте логи: `python3 russian_apis_server.py`

### **Проблема: "Геокодирование не работает"**
**Решение:**
1. Проверьте API ключ Яндекс Карт
2. Убедитесь, что ключ имеет права на геокодирование
3. Проверьте лимиты запросов

---

## 📊 МОНИТОРИНГ

### **Проверка статистики**
```bash
curl http://localhost:5005/api/russian/statistics
```

### **Проверка статуса**
```bash
curl http://localhost:5005/api/russian/status
```

---

## 🚀 СЛЕДУЮЩИЕ ШАГИ

1. **Настройте API ключи** - следуйте инструкции выше
2. **Протестируйте API** - используйте примеры
3. **Интегрируйте в приложение** - используйте REST API
4. **Настройте мониторинг** - отслеживайте использование

---

**Дата создания:** 8 сентября 2025  
**Автор:** ALADDIN Security Team  
**Версия:** 1.0