# OPS-05 — Definition of Done (прогон 2026-05-26)

**Спринт:** OPS-02 + P1-26 + повторный deploy  
**Прод:** `https://aladdin-ai.ru` · VPS `149.154.65.180` · `/opt/aladdin-backend`

---

## §12 Handoff (COMPANION_ML_HANDOFF_FULL.md)

| Пункт | Статус | Примечание |
|-------|--------|------------|
| Прочитать `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` | ✅ | SSH key `~/.ssh/aladdin_server` |
| SSH `root@149.154.65.180` | ✅ | deploy script |
| `PYTHONPATH=. python3 Tests/test_companion_p0_smoke.py` | ✅ | 10/10 |
| `test_companion_persona_not_security_only.py` | ✅ | 4/4 (P1-26) |
| `./scripts/deploy_companion_p0.sh` | ✅ | + `companion_persona.py` |
| `./scripts/verify_companion_p0_prod.sh` | ✅ | OPS-02 full (12 шагов) |
| Устройство: Kids → чат → стрим → resume UI | ☐ | QA вручную |
| Родитель: Family → consent / memory / profile | ☐ | QA вручную |
| Обновить `COMPANION_IMPLEMENTATION_TODOS.md` | ✅ | этот прогон |
| §17 Grok parity gate | ☐ | после CX/P1+ |

---

## Что выкатили в этом прогоне

- `security/services/ai_platform/companion_persona.py` — **life-first** промпты (70/30)
- `security/api/routers/ai_companion_router.py` — `age_band` в system prefix
- `scripts/verify_companion_p0_prod.sh` — stream, threads, memory, profile, feedback, cosmetics, consent

---

## Verify (OPS-02)

Запуск:

```bash
./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru
```

Ожидаемый финал: `=== All checks passed (OPS-02 full verify) ===`

---

## Следующий критический путь (CX)

1. **P1-27** — companion intent router (domains + mood)
2. **P1-28** — персоны по age_band (тон уже в persona; отдельные character hints)
3. **P1-30** — эмоции + humor в BE
4. **GATE-CX** — D01–D03

---

*Авто-часть OPS-05 закрыта; device QA — открыта.*
