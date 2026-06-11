# SFM на проде — форензика (09.06.2026)

**Сервер:** `149.154.65.180` · SSH key `~/.ssh/aladdin_server`

---

## Вы были правы: SFM задеплоен

Файл **есть**. Ошибка в прошлом анализе — искали не в том пути.

| Путь | Строк | Статус |
|------|-------|--------|
| `/opt/aladdin-backend/app/security/safe_function_manager.py` | **4866** | ✅ Полный SFM |
| `/opt/aladdin-backend/safe_function_manager.py` | 43 | ⚠️ Тестовая заглушка `SFM Test Stub` |
| `/opt/aladdin-backend/security/safe_function_manager.py` | — | ❌ Нет (импорт в `start_sfm_core_http.py` битый) |
| Бэкап 30.01.2026 | 4855 | ✅ `.../backend_backup/aladdin-backend/security/safe_function_manager.py` |

**Агенты на диске:** 85 `.py` в `app/security/ai_agents/` (fake_news, deepfake, dark_web, identity…).

**Декабрь 2025 (док):** `function_registry.json` = **1074 функции**, ~1 МБ.

---

## Почему сейчас не «100%», хотя поднимали

### Цепочка поломки (не одна причина)

```
1. deploy_optimized_sfm.sh (фев 2026)
   → залил OptimizedSFM mock (3.0.0-mock-real-protection) в sfm_singleton.py

2. start_sfm_core_http.py
   → import: security.safe_function_manager  (НЕВЕРНЫЙ путь)
   → sys.path без /opt/aladdin-backend/app первым
   → except: sfm = None → fallback {"status":"success"}

3. app/security/reactive/performance_optimizer.py
   → dangling symlink на несуществующий security/performance_optimizer.py
   → SafeFunctionManager не импортируется без фикса

4. function_registry.json
   → был 1074 fn (бэкап 30.01.2026, 1.1 МБ)
   → сейчас 14 fn (12 КБ) — реестр потерян/перезаписан пустым init

5. sfm-healthcheck.service
   → failed 203/EXEC каждые 60s (битый путь к скрипту)

6. main.py wildcard
   → неизвестные API → SFMAdapter → :8003 fallback (не реальный SFM)
```

### Доказательство: SFM **живой** после 2 фиксов (тест на VPS)

```bash
# 1) Починить symlink reactive
rm app/security/reactive/performance_optimizer.py
cp app/security/performance_optimizer.py app/security/reactive/

# 2) PYTHONPATH
sys.path.insert(0, "/opt/aladdin-backend/app")
from security.safe_function_manager import SafeFunctionManager
sfm = SafeFunctionManager()  # INIT OK ~0.5s, Redis OK
len(sfm.functions)  # 14 без полного registry; 1074 после restore backup
```

`fake_news_detection_agent` → handler отвечает (не пустой mock).  
`get_darkweb_stats` → «не найдена» без полного registry (имя API ≠ имя в registry).

---

## Что реально работает на VPS

| Компонент | systemd | Факт |
|-----------|---------|------|
| `aladdin-backend.service` :8002 | active | FastAPI + parental/VPN/reports |
| `aladdin-sfm-core.service` :8003 | active | **Fallback HTTP**, не полный SFM |
| `safe_function_manager` import в :8003 | — | **FAIL** → sfm=None |
| Полный SFM код | на диске | **ДА**, `app/security/` |
| Registry 1074 | бэкап | **ДА**, нужен restore |
| Registry live | data/sfm/ | **14** (сломан) |

---

## Исправление «раз и навсегда» (продуктовое)

**Не отказываться от SFM.** Восстановить boot chain + registry, затем Hub-роутеры для iOS.

### Batch SFM-R (restore) — 1–2 дня

1. Restore `function_registry.json` из `/root/backup_20260130_122000/.../function_registry.json`
2. `start_sfm_core_http.py`: `sys.path.insert(0, APP)` + `from security.safe_function_manager import SafeFunctionManager`
3. Починить `reactive/performance_optimizer.py` (копия, не symlink)
4. `Environment=PYTHONPATH=/opt/aladdin-backend/app:/opt/aladdin-backend` в `aladdin-sfm-core.service`
5. Удалить/переименовать корневую заглушку `safe_function_manager.py` (43 строки)
6. Откатить `sfm_singleton.py` с OptimizedSFM mock → delegate to real SFM или не использовать в prod
7. Починить `sfm-healthcheck.service` (203 EXEC)
8. Smoke: `execute_function('get_darkweb_stats')` → success с registry

### Batch SEC-INFRA — параллельно

protection persist, iOS load, wildcard block (как в Фазе 0).

### Batch HUB — после SFM-R + SEC

Явные `/api/antifake/*`, `/api/darkweb/*` → вызывают SFM handlers по `complete_api_sfm_mapping.py`.

**Не стоит:** снова деплоить OptimizedSFM mock; поднимать второй параллельный «Registry» с нуля; трогать онбординг.

---

## Связь с 138 функциями

| Слой | Без SFM-R | После SFM-R | После HUB+iOS |
|------|-----------|-------------|---------------|
| Код агентов | ✅ на диске | ✅ | ✅ |
| Registry | ❌ 14 | ✅ 1074 | ✅ + new agents |
| HTTP :8003 | mock success | real execute | real execute |
| iOS L3 | ❌ | ⚠️ частично | ✅ |

---

*Отчёт заменяет утверждение «файла нет» — файл в `app/security/`, сломан путь запуска и реестр.*
