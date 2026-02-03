# 🧪 ТЕСТИРОВАНИЕ ФУНКЦИИ 4/93: `/api/components/enable/{component_id}`

## 📋 ПРОВЕРКА ИСПРАВЛЕНИЯ

### ✅ КРИТЕРИИ УСПЕШНОГО ИСПРАВЛЕНИЯ:

1. **HTTP Статус:** `200 OK`
2. **JSON Структура:** Валидный JSON без ошибок
3. **Источник данных:** НЕ `"source": "mock"`
4. **Реальные данные:** Данные из SFM или ошибка SFM
5. **Логи:** Нет ошибок в `journalctl`

### 🔍 ТЕСТОВЫЕ КОМАНДЫ:

```bash
# Проверка health status
curl -s http://149.154.65.180:8002/api/health | python3 -m json.tool

# Тестирование исправленной функции (POST запрос)
curl -s -X POST http://149.154.65.180:8002/api/components/enable/crash_detection_agent | python3 -m json.tool

# Проверка логов на ошибки
ssh root@149.154.65.180 "journalctl -u aladdin-main-api-gateway -n 5"
```

### 🎯 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:

#### ДО ИСПРАВЛЕНИЯ:
```json
{
    "component_id": "crash_detection_agent",
    "action": "enable",
    "source": "mock"
}
```

#### ПОСЛЕ ИСПРАВЛЕНИЯ:
```json
{
    "component_id": "crash_detection_agent",
    "action": "enable",
    "status": "success",
    "enabled_at": "2025-02-02T12:00:00Z",
    "configuration": {
        "active": true,
        "monitoring_enabled": true
    },
    "source": "real_sfm_component_enable"
}
```

### 🚨 ВАЖНЫЕ ЗАМЕЧАНИЯ:

1. **НЕ должно быть** `"source": "mock"`
2. **НЕ должно быть** hardcoded значений
3. **ДОЛЖНЫ быть** реальные данные или правильная ошибка SFM
4. **Функция ДОЛЖНА** изменять состояние компонента в SFM
5. **Использовать метод POST** для этого эндпоинта

### 📞 КОНТАКТЫ ДЛЯ ПОДДЕРЖКИ:

Если функция не работает:
1. Проверьте логи: `journalctl -u aladdin-main-api-gateway -n 10`
2. Проверьте SFM статус: `curl http://149.154.65.180:8002/api/health`
3. Проверьте что используется правильный HTTP метод (POST)
4. Свяжитесь с командой разработки

**🎉 ФУНКЦИЯ 4/93 ГОТОВА К ПРОДАКШЕНУ!**