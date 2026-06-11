# SFM — единый источник правды (для всех ML-систем)

**Версия:** 1.0 · **2026-06-09**  
**Цель:** любая ML-система за **30 секунд** видит реальный SFM — без путаницы «файла нет / неполный / 1074 не работает».

---

## 1. В чём была проблема (корень путаницы)

| # | Симптом, который видела ML | Реальность | Почему врали данные |
|---|---------------------------|------------|---------------------|
| 1 | «`safe_function_manager.py` нет на сервере» | Файл **есть**: `/opt/aladdin-backend/app/security/safe_function_manager.py` (4866 строк) | Искали `security/safe_function_manager.py` — **другой путь** |
| 2 | «SFM неполный / 14 функций» | Код полный; **registry** на диске был 14 вместо 1000+ | `function_registry.json` перезаписан; init без backup |
| 3 | «SFM работает, 1074 функции» | :8003 отвечает 200, health пишет 1074 | **Hardcoded** `functions_count`; `sfm=None` → fallback `status:success` |
| 4 | «Подняли SFM 100%» | HTTP transport OK, не L3 | Тест = curl 200, не `sfm_loaded` + execute real agent |
| 5 | Декабрьский отчёт vs июнь | Оба «правы» в разное время | Registry был 1074, потом сломали deploy path |
| 6 | Два `safe_function_manager.py` | 43-строчная **заглушка** в корне `/opt/aladdin-backend/` | Import path выбирал stub |

**Итог:** путаница не в отсутствии SFM, а в **отсутствии честного статуса** и **единого пути проверки**.

---

## 2. Канонические пути (запомнить раз и навсегда)

| Что | Единственный правильный путь на VPS |
|-----|-------------------------------------|
| **Код SFM** | `/opt/aladdin-backend/app/security/safe_function_manager.py` |
| **Агенты** | `/opt/aladdin-backend/app/security/ai_agents/` (85+ файлов) |
| **Registry** | `/opt/aladdin-backend/data/sfm/function_registry.json` |
| **HTTP SFM** | `http://127.0.0.1:8003` (systemd `aladdin-sfm-core.service`) |
| **PYTHONPATH** | `/opt/aladdin-backend/app` **первым** |
| **НЕ использовать** | `/opt/aladdin-backend/safe_function_manager.py` (stub) |
| **НЕ использовать** | `security/safe_function_manager` import без `app` в path |
| **НЕ доверять** | health `functions_count` без поля `registry_source` |

---

## 3. Единая команда проверки (первая для любой ML)

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180 \
  'curl -s http://127.0.0.1:8003/api/sfm/status | python3 -m json.tool'
```

**После внедрения B-OPS-13** ответ **обязан** содержать:

```json
{
  "sfm_loaded": true,
  "sfm_class": "SafeFunctionManager",
  "code_path": "/opt/aladdin-backend/app/security/safe_function_manager.py",
  "code_lines": 4866,
  "registry_path": "/opt/aladdin-backend/data/sfm/function_registry.json",
  "registry_count": 1074,
  "runtime_functions_count": 1074,
  "fallback_mode": false,
  "optimized_sfm_mock": false,
  "agents_on_disk": 85,
  "status": "healthy",
  "truth_version": "1.0"
}
```

**Если `sfm_loaded: false` или `fallback_mode: true` — SFM НЕ готов.** Не писать «работает».

### До внедрения `/api/sfm/status` (временно)

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180 'bash /opt/aladdin-backend/docs/server/sfm_truth_check.sh'
```

Скрипт создаётся задачей `B-OPS-13`.

---

## 4. Что внедрить, чтобы больше не путались (задачи плана)

| ID | Задача | Эффект |
|----|--------|--------|
| `B-OPS-13` | Endpoint `GET /api/sfm/status` — честный JSON (§3) | ML одна curl — вся правда |
| `B-OPS-14` | `docs/server/sfm_truth_check.sh` + symlink в ML guide | Copy-paste для ML |
| `B-OPS-15` | `docs/SFM_ML_QUICKSTART.md` (1 страница) | «Не читай 50 файлов — начни здесь» |
| `B-OPS-16` | `AGENTS.md` + handoff: **первый шаг = sfm/status** | Cursor agents |
| `B-OPS-17` | Rename stub `safe_function_manager.py` → `.STUB_DO_NOT_IMPORT` | Нет ложного import |
| `B-OPS-18` | README в `/opt/aladdin-backend/app/security/README_SFM.md` on server | Путь на диске |
| `B-OPS-19` | CI: `sfm_truth_check.sh` fail → block deploy | Не сломать снова |
| `B-OPS-20` | `function_registry.manifest.json` в репо (count + sha256) | Сверка с prod |

Связь с SFM-WIRE: `B-SFM-W03`…`W08` подключают runtime; OPS-13…20 делают статус **видимым**.

---

## 5. Правила для всех ML-систем (обязательные)

### Перед любым отчётом «SFM готов / неполный»

1. Выполнить `sfm_truth_check.sh` или `GET /api/sfm/status`
2. Сверить `registry_count` ≥ 1000 и `sfm_loaded: true`
3. Выполнить probe: `fake_news_detection_agent` — ответ **не** `{"status":"success"}` alone
4. Записать вывод в `security-l3-report.json` → block `SFM-TRUTH`

### Запрещённые формулировки без evidence

- «SFM файла нет» — без `ls` обоих путей
- «SFM неполный» — без `registry_count` из status API
- «SFM 100%» — без `sfm_loaded` + registry + agent probe
- «1074 функции» — только если `runtime_functions_count` совпадает

### Разрешённые формулировки

- «SFM код на диске: 4866 строк, путь app/security/ — **подтверждено**»
- «SFM runtime: **не подключён** (`sfm_loaded: false`) — нужен SFM-WIRE»
- «Registry: **N** функций (требуется ≥1000) — нужен W06 rebuild»

---

## 6. Диаграмма: как ML должна думать о SFM

```
                    ┌─────────────────────────────┐
                    │  GET /api/sfm/status        │
                    │  (единственная точка правды)  │
                    └──────────────┬──────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
        sfm_loaded?         registry_count?      fallback_mode?
              │                    │                    │
         false → WIRE          <1000 → W06          true → FAIL
              │                    │                    │
              └────────────────────┴────────────────────┘
                                   │
                            all OK → SFM runtime ready
                                   │
                            дальше: API routers + iOS Hub
```

**Код на диске ≠ runtime готов.** ML всегда проверяет **оба** через status API.

---

## 7. Связанные документы

| Документ | Роль |
|----------|------|
| `docs/SFM_SERVER_FORENSIC_REPORT.md` | История инцидента июнь 2026 |
| `docs/OPS_ANTI_REGRESSION_GATES.md` | Gates + monitoring |
| `docs/server/L3_SMOKE_CONTRACT.md` | PASS/FAIL критерии |
| `ML_SYSTEM_HANDOFF_SECURITY_100_PERCENT.md` | Полный handoff |
| `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` | SSH + § SFM TRUTH (добавить) |

---

## 8. Критерий «проблема решена навсегда»

- [ ] Любая ML за 1 команду видит `sfm_loaded`, `registry_count`, `fallback_mode`
- [ ] Stub переименован, import path задокументирован на сервере
- [ ] Deploy без PASS `sfm_truth_check.sh` невозможен
- [ ] Ни один документ не ссылается на `security/safe_function_manager.py` без `app/`
- [ ] `security-l3-report.json` содержит блок `SFM-TRUTH` с timestamp
