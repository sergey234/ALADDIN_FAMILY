# 🔍 ИНСТРУКЦИЯ ПО ПРОВЕРКЕ МИГРАЦИИ

## ✅ Как проверить, что миграция применилась и все работает

### 📋 **БЫСТРАЯ ПРОВЕРКА (БЕЗ HTTP ЗАПРОСОВ)**

Проверка кода на наличие SFM интеграции:

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
python3 test_all_101_endpoints.py
```

Этот скрипт:
- ✅ Проверит все endpoints в коде
- ✅ Убедится, что все используют SFM интеграцию
- ✅ Покажет статистику по группам
- ✅ Создаст отчет

---

### 🌐 **ПОЛНАЯ ПРОВЕРКА (С HTTP ЗАПРОСАМИ)**

Для проверки работоспособности endpoints нужен запущенный API Gateway:

```bash
# 1. Установите Base URL (если не localhost:8002)
export API_BASE_URL="http://localhost:8002"
# или
export API_BASE_URL="https://aladdin-ai.ru"

# 2. Запустите полное тестирование
python3 test_all_101_endpoints.py --verbose

# 3. Просмотрите отчет
ls -lt migration_test_report_*.md | head -1
```

---

### 🔍 **РУЧНАЯ ПРОВЕРКА КОДА**

#### 1. Проверка Группы 3 (Мониторинг)

```bash
grep -A 5 "ГРУППА 3" api_gateway_complete.py | head -10
```

Должно быть:
- ✅ `# ГРУППА 3: МОНИТОРИНГ (20 endpoints)` (БЕЗ "ЗАГЛУШКИ")
- ✅ `if SFM_ADAPTER_AVAILABLE and sfm_adapter:`
- ✅ `sfm_adapter.execute_function(...)`

#### 2. Проверка Группы 4 (Защита)

```bash
grep -A 5 "ГРУППА 4" api_gateway_complete.py | head -10
```

Должно быть:
- ✅ `# ГРУППА 4: ЗАЩИТА (25 endpoints)` (БЕЗ "ЗАГЛУШКИ")
- ✅ SFM интеграция во всех endpoints

#### 3. Проверка Группы 5 (Система)

```bash
grep -A 5 "ГРУППА 5" api_gateway_complete.py | head -10
```

Должно быть:
- ✅ `# ГРУППА 5: СИСТЕМА (31 endpoint)` (БЕЗ "ЗАГЛУШКИ")
- ✅ SFM интеграция во всех endpoints

#### 4. Проверка отсутствия заглушек

```bash
grep -i "заглушки\|mock only" api_gateway_complete.py
```

Должно быть пусто (нет результатов) или только в fallback блоках.

---

### 📊 **ПРОВЕРКА ЧЕРЕЗ КОД**

#### Быстрая проверка миграции:

```python
import re

with open('api_gateway_complete.py', 'r') as f:
    content = f.read()

# Проверяем наличие заглушек
if 'ЗАГЛУШКИ' in content:
    print("❌ Найдены заглушки!")
    for line in content.split('\n'):
        if 'ЗАГЛУШКИ' in line:
            print(f"  - {line.strip()}")
else:
    print("✅ Заглушек не найдено!")

# Проверяем SFM интеграцию
endpoints = re.findall(r'@app\.(get|post|put|delete)\("([^"]+)"\)', content)
sfm_endpoints = len(re.findall(r'sfm_adapter\.execute_function', content))

print(f"\nВсего endpoints: {len(endpoints)}")
print(f"Endpoints с SFM: {sfm_endpoints}")
print(f"Процент миграции: {sfm_endpoints/len(endpoints)*100:.1f}%")
```

---

### 🧪 **ТЕСТИРОВАНИЕ ОТДЕЛЬНЫХ ENDPOINTS**

#### Тест через curl:

```bash
# Группа 1: Компоненты
curl http://localhost:8002/api/components/status/test_component

# Группа 2: Настройки
curl http://localhost:8002/api/phishing/sensitivity

# Группа 3: Мониторинг
curl http://localhost:8002/api/ai/categories/stats
curl http://localhost:8002/api/darkweb/stats

# Группа 4: Защита
curl http://localhost:8002/api/identity/theft/stats
curl http://localhost:8002/api/antitracker/stats

# Группа 5: Система
curl http://localhost:8002/api/notifications/unread_count
curl http://localhost:8002/api/subscription/status
```

**Ожидаемый результат:**
```json
{
  "status": "...",
  "source": "mock"  // или "sfm" если SFM работает
}
```

---

### 📈 **ПРОВЕРКА СТАТИСТИКИ**

#### Подсчет endpoints по группам:

```bash
# Группа 1
grep -c "@app\." api_gateway_complete.py | grep -A 50 "ГРУППА 1" | grep -c "@app\."

# Или проще - через Python скрипт
python3 -c "
import re
with open('api_gateway_complete.py') as f:
    content = f.read()
    
groups = {
    'Группа 1': len(re.findall(r'ГРУППА 1.*?ГРУППА 2', content, re.DOTALL)[0].split('@app.')) - 1),
    'Группа 2': len(re.findall(r'ГРУППА 2.*?ГРУППА 3', content, re.DOTALL)[0].split('@app.')) - 1),
    'Группа 3': len(re.findall(r'ГРУППА 3.*?ГРУППА 4', content, re.DOTALL)[0].split('@app.')) - 1),
    'Группа 4': len(re.findall(r'ГРУППА 4.*?ГРУППА 5', content, re.DOTALL)[0].split('@app.')) - 1),
    'Группа 5': len(re.findall(r'ГРУППА 5.*?if __name__', content, re.DOTALL)[0].split('@app.')) - 1),
}
for g, c in groups.items():
    print(f'{g}: {c} endpoints')
"
```

---

### ✅ **КРИТЕРИИ УСПЕШНОЙ МИГРАЦИИ**

1. ✅ **Все 101 endpoint** присутствуют в коде
2. ✅ **Все endpoints** используют `SFM_ADAPTER_AVAILABLE` и `sfm_adapter.execute_function()`
3. ✅ **Все endpoints** имеют fallback на `"source": "mock"`
4. ✅ **Нет заглушек** (нет строк "ЗАГЛУШКИ" в комментариях групп)
5. ✅ **HTTP тесты** проходят (если API Gateway запущен)
6. ✅ **Производительность** < 1 секунда на endpoint

---

### 🚀 **БЫСТРЫЙ СТАРТ**

```bash
# 1. Проверка кода (без HTTP)
python3 test_all_101_endpoints.py

# 2. Если нужно проверить HTTP (требует запущенный API Gateway)
export API_BASE_URL="http://localhost:8002"
python3 test_all_101_endpoints.py --verbose

# 3. Просмотр отчета
cat migration_test_report_*.md | tail -50
```

---

### 📝 **ЧТО ДЕЛАТЬ ЕСЛИ НАЙДЕНЫ ПРОБЛЕМЫ**

1. **Не мигрированы endpoints:**
   - Запустите `migrate_group4.py --apply` или `migrate_group5.py --apply`
   - Или вручную замените заглушки на SFM код

2. **HTTP ошибки:**
   - Проверьте, что API Gateway запущен: `systemctl status aladdin-api-gateway`
   - Проверьте порт: `netstat -tlnp | grep 8002`
   - Проверьте логи: `journalctl -u aladdin-api-gateway -n 50`

3. **SFM не работает:**
   - Проверьте импорт: `python3 -c "from sfm_adapter import sfm_adapter; print('OK')"`
   - Проверьте доступность SFM сервиса

---

**Дата создания:** 30 января 2026  
**Версия:** 1.0



