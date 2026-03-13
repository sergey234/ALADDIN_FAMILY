# 🔍 АНАЛИЗ СУЩЕСТВУЮЩИХ API ДЛЯ АНТИВИРУСА

**Дата:** 13 марта 2025  
**Статус:** ✅ **АНАЛИЗ ЗАВЕРШЕН**

---

## ✅ ЧТО УЖЕ ЕСТЬ НА СЕРВЕРЕ

### 1. ЭНДПОИНТЫ `/api/malware/` (5 эндпоинтов):

#### ✅ Реализованы:
1. **`GET /api/malware/scan_scheduled`**
   - Получить расписание сканирования
   - SFM функция: `get_malware_scan_scheduled`
   - Статус: ✅ Работает

2. **`PUT /api/malware/scan_scheduled`**
   - Обновить расписание сканирования
   - SFM функция: `update_malware_scan_scheduled`
   - Статус: ✅ Работает

3. **`GET /api/malware/quarantine`**
   - Получить **настройки** карантина (enabled, retention_days)
   - SFM функция: `get_malware_quarantine`
   - Статус: ✅ Работает
   - **ВНИМАНИЕ:** Это настройки, а не список файлов!

4. **`PUT /api/malware/quarantine`**
   - Обновить **настройки** карантина
   - SFM функция: `update_malware_quarantine`
   - Статус: ✅ Работает
   - **ВНИМАНИЕ:** Это настройки, а не действия с файлами!

5. **`POST /api/malware/scan_now`**
   - Запустить сканирование сейчас
   - SFM функция: `scan_malware_now`
   - Статус: ✅ Работает

---

## ❌ ЧТО ОТСУТСТВУЕТ НА СЕРВЕРЕ

### 1. ЭНДПОИНТЫ ДЛЯ РАБОТЫ С УГРОЗАМИ:

#### ❌ Отсутствуют:
1. **`GET /api/malware/threats`** или **`GET /api/protection/threats`**
   - Получить список всех угроз пользователя
   - Фильтрация по статусу (active, quarantined, resolved)
   - **НУЖНО СОЗДАТЬ**

2. **`GET /api/malware/threats/{status}`**
   - Получить угрозы по статусу
   - **НУЖНО СОЗДАТЬ**

### 2. ЭНДПОИНТЫ ДЛЯ ДЕЙСТВИЙ С КАРАНТИНОМ:

#### ❌ Отсутствуют:
1. **`POST /api/malware/quarantine/action`** или **`POST /api/protection/quarantine/action`**
   - Выполнить действие с файлом в карантине
   - Действия: `quarantine`, `restore`, `remove`
   - **НУЖНО СОЗДАТЬ**

2. **`GET /api/malware/quarantine/list`**
   - Получить список файлов в карантине
   - **НУЖНО СОЗДАТЬ** (или использовать `/api/malware/threats?status=quarantined`)

---

## 🔧 SFM ФУНКЦИИ

### ✅ Существующие SFM функции:
- `get_malware_scan_scheduled` ✅
- `update_malware_scan_scheduled` ✅
- `get_malware_quarantine` ✅ (настройки)
- `update_malware_quarantine` ✅ (настройки)
- `scan_malware_now` ✅

### ❌ Отсутствующие SFM функции:
- `get_malware_threats` ❌ (список угроз)
- `get_malware_threats_by_status` ❌ (угрозы по статусу)
- `quarantine_file_action` ❌ (действия с карантином)
- `get_quarantine_list` ❌ (список файлов в карантине)

---

## 📋 ВЫВОДЫ

### ✅ ЧТО РАБОТАЕТ:
1. Настройки карантина (включен/выключен, срок хранения)
2. Расписание сканирования
3. Запуск сканирования

### ❌ ЧТО НЕ РАБОТАЕТ:
1. Получение списка угроз с сервера
2. Действия с файлами в карантине (restore, remove)
3. Синхронизация локального и серверного карантина

---

## 🎯 РЕШЕНИЕ

### ВАРИАНТ 1: СОЗДАТЬ НОВЫЕ ЭНДПОИНТЫ НА СЕРВЕРЕ (РЕКОМЕНДУЕТСЯ)

**Нужно добавить в `api_gateway_server_current.py`:**

```python
# Получить список угроз
@app.get("/api/malware/threats")
async def get_malware_threats(status: str = None):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        params = {}
        if status:
            params["status"] = status
        success, result, message = sfm_adapter.execute_function("get_malware_threats", params)
        return result if success else {"error": message}
    else:
        return {"threats": [], "total": 0, "source": "mock"}

# Действие с карантином
@app.post("/api/malware/quarantine/action")
async def quarantine_action(request: dict):
    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        success, result, message = sfm_adapter.execute_function("quarantine_file_action", request)
        return result if success else {"error": message}
    else:
        return {"success": True, "action": request.get("action"), "source": "mock"}
```

**И добавить SFM функции:**
- `get_malware_threats` - получить список угроз
- `quarantine_file_action` - выполнить действие с карантином

### ВАРИАНТ 2: ИСПОЛЬЗОВАТЬ СУЩЕСТВУЮЩИЕ ЭНДПОИНТЫ (ВРЕМЕННОЕ РЕШЕНИЕ)

**Адаптировать код iOS для работы с существующими эндпоинтами:**
- Использовать `/api/malware/quarantine` для получения настроек
- Хранить список угроз локально (как сейчас)
- Синхронизировать только настройки, а не файлы

---

## 🚨 КРИТИЧНОСТЬ

### 🔴 КРИТИЧНО:
- Без эндпоинтов для получения списка угроз синхронизация не работает
- Без эндпоинтов для действий с карантином нельзя управлять файлами на сервере

### ⚠️ ВАЖНО:
- Локальный карантин работает полностью
- Можно использовать локальный карантин без синхронизации

---

## ✅ РЕКОМЕНДАЦИИ

1. **Создать новые эндпоины на сервере** для полной функциональности
2. **Добавить SFM функции** для работы с угрозами и карантином
3. **Обновить AppConfig.swift** для использования `/api/malware/` вместо `/api/protection/`
4. **Протестировать** синхронизацию после создания эндпоинтов

---

**СТАТУС:** ⚠️ **ТРЕБУЕТСЯ РЕАЛИЗАЦИЯ НА СЕРВЕРЕ**
