# 😴 ПЛАН УСЫПЛЕНИЯ СЕРВЕРНЫХ ФУНКЦИЙ (SLEEP MODE)

**Дата:** 2025-11-26  
**Цель:** исключить дублирование между iOS-клиентом и сервером (SFM), переведя определённые функции в спящий режим, когда мобильное приложение выполняет ту же логику локально.

---

## 1. Контекст

- Документация по развёртыванию: `docs/COMPLETE_SERVER_MIGRATION_PLAN.md`, `docs/FINAL_MIGRATION_GUIDE.md`.
- Оптимизированный список переноса (~220 файлов): `docs/OPTIMIZED_SERVER_MIGRATION_LIST.md`, `docs/MEMORY_SERVER_MIGRATION_KEY_INFO.md`.
- Анализ миграции: `docs/REAL_SERVER_MIGRATION_ANALYSIS.md`, `docs/SFM_MIGRATION_PLAN.md`.
- Sleep Mode реализуется через `sleep_mode_manager.py`, `check_and_sleep_bots.py`, `safe_sleep_mode_implementation.py` и записи в `function_registry.json`.

---

## 2. Перечень функций для Sleep Mode

### 2.1 AI Agents (серверные копии, дублирующие клиента)
| Файл | Действие |
|------|----------|
| `security/ai_agents/mobile_security_agent.py` | Усыпить, если iOS выполняет локальный мониторинг root/jailbreak. |
| `security/ai_agents/mobile_security_agent_enhanced.py` | Усыпить при активном клиентском анализе поведения и сети. |
| `security/ai_agents/mobile_user_ai_agent.py` | Усыпить: советы и подсказки генерируются на устройстве. |
| `security/ai_agents/child_interface_manager.py` | Усыпить: UI/поведенческие сценарии детского интерфейса выполняются на iOS. |
| `security/ai_agents/parent_control_panel.py` | Усыпить: родитель управляет правилами напрямую в приложении. |

### 2.2 Bots (серверные версии, дублирующие UI)
| Файл | Действие |
|------|----------|
| `security/bots/mobile_navigation_bot.py` | Усыпить: навигацию ведёт мобильный UI. |
| `security/bots/website_navigation_bot.py` | Усыпить: безопасные маршруты формирует клиент. |
| `security/bots/parental_control_bot.py` | Усыпить, когда ограничения управляются на устройстве. |
| `security/bots/parental_control_bot_v2_enhanced.py` | Аналогично — серверный бот спит, клиент выполняет логику. |

### 2.3 Managers
| Файл | Действие |
|------|----------|
| `security/managers/voice_control_manager.py` | Усыпить, если голосовые команды обрабатываются в iOS. |

---

## 3. Шаги реализации Sleep Mode

### 3.1 Обновление `function_registry.json`
1. Для каждого файла из раздела 2 добавить поля:
   ```json
   {
     "function": "mobile_security_agent",
     "mode": "sleep",
     "trigger": "client_active"
   }
   ```
2. Для агентов/ботов/менеджеров, у которых есть локальная реализация, сохраняем ссылку на соответствующий клиентский модуль.

### 3.2 Автоматизация
1. В `sleep_mode_manager.py` и `check_and_sleep_bots.py` добавить логику:
   - Если клиент отправил POST `/sfm/function-status` с `client_active = true`, то серверная функция → Sleep.
   - Если клиент офлайн > N минут, серверная функция просыпается.
2. Обновить `safe_sleep_mode_implementation.py`, чтобы он учитывал новые флаги `trigger: client_active`.
3. Добавлен вспомогательный скрипт `scripts/put_function_to_sleep.py`, позволяющий усыплять каждую из 9 функций по отдельности (fallback, когда общий скрипт не подходит).

### 3.3 Документация и мониторинг
1. В `docs/OPTIMIZED_SERVER_MIGRATION_LIST.md` добавить колонку `MODE` для визуального контроля (SERVER_ACTIVE / SLEEP / MANUAL).
2. `monitor_manager.py` + `performance_optimization_agent.py` проверяют, что sleep-функции не потребляют ресурс.
3. `report_manager.py` формирует отчёт о состоянии Sleep Mode (кто спит, кто активен).

### 3.4 API‑сигналы от мобильного приложения
1. Добавить эндпоинт `POST /sfm/function-status` (или расширить существующий), чтобы iOS посылало события «эта функция выполняется локально». **Готово:** реализован в `security/microservices/api_gateway.py`, сохраняет статус и вызывает `SleepModeManager`.
2. Формат:
   ```json
   {
     "function": "mobile_security_agent",
     "client_active": true,
     "expires_in_sec": 600
   }
   ```
3. На сервере `monitor_manager.py` и `sleep_mode_manager.py` используют это событие для изменения статуса.

---

## 4. Проверка и включение
1. Запустить валидатор (`scripts/sfm_structure_validator.py`) после обновления реестра.
2. На сервере (см. `docs/FINAL_MIGRATION_GUIDE.md`) выполнить:
   ```bash
   cd /opt/aladdin-backend
   source venv/bin/activate
   python scripts/safe_sleep_mode_implementation.py --apply
   ```
3. Если общий скрипт не подходит, пройтись по списку функций:
   ```bash
   python scripts/put_function_to_sleep.py mobile_security_agent
   ```
   (повторить для всех 9 имён).
4. Проверить файлы `sleep_state_<function>.json` и лог `monitor_manager` на отсутствие проснувшихся функций, когда клиент активен.

---

## 5. Ответственные компоненты
- Конфигурация Sleep: `function_registry.json`
- Логика: `sleep_mode_manager.py`, `check_and_sleep_bots.py`, `safe_sleep_mode_implementation.py`
- Мониторинг: `monitor_manager.py`, `performance_optimization_agent.py`, `report_manager.py`
- API приём сигналов: `api_gateway.py` + `external_api_manager.py`
- Документация: обновить `docs/OPTIMIZED_SERVER_MIGRATION_LIST.md`, `docs/MEMORY_SERVER_MIGRATION_KEY_INFO.md`

---

**Результат:** мобильное приложение выполняет локальные функции, серверные дубликаты находятся в спящем режиме и не потребляют ресурсы. Все остальные серверные компоненты (ML, bots, managers, microservices, VPN, compliance и т.д.) остаются активными, как описано в миграционных документах.
