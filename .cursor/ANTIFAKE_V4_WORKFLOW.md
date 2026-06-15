# Antifake v4 — правила работы (обязательно для всех агентов)

**Дата:** 2026-06-15  
**Единая точка входа:** [ANTIFAKE_UNIFIED_MASTER.md](./ANTIFAKE_UNIFIED_MASTER.md)  
**SSOT задач:** [ANTIFAKE_V4_TASK_REGISTRY.md](./ANTIFAKE_V4_TASK_REGISTRY.md)  
**Индекс:** [ANTIFAKE_V4_DOC_INDEX.md](./ANTIFAKE_V4_DOC_INDEX.md)

---

## 1. Cursor TODO — 134 задачи (~156 строк)

- **Все 134** атомарных пункта (`af-A-01` … `af-O-03`) **остаются в панели** + meta + заголовки батчей `hdr-*`.
- **Не удалять** и **не пересоздавать** список — только `merge: true`.
- **Прогресс SSOT (2026-06-15):** **111 ✅ · 7 ⬜ · 13 ⏸ · 3 ❌**

---

## 2. Device / Xcode / TestFlight — **ПОСЛЕДНИЙ ШАГ**

| Cursor ID | ID | Статус |
|-----------|-----|--------|
| `af-D-01` … `af-D-04` | D-01…D-04 | ⬜ iPhone |
| `af-D-09` | D-09 | ⬜ iPhone |
| `af-E-06` | E-06 | ⬜ iPhone |
| `af-R-02` | R-02 | ⬜ sign-off |

**Код + static gates:** ✅ `bash scripts/verify_antifake_all_static.sh`

---

## 3. Порядок (выполнен → осталось)

```
✅ C → A → F → J → B → E → N → R → Ф2 (I,L,M,P,G,Q) → G-03/Q-01
⬜ DEVICE (D-01…04, D-09, E-06, R-02)
⏸ v2: H (PIR), K (on-device ML)
```

---

## 4. Синхронизация при закрытии задачи

1. REGISTRY ✅  
2. TOP_TIER_PLAN ✅  
3. UNIFIED (при смене сводки)  
4. Cursor todo `merge: true`  
5. Runbook/smoke при необходимости  

---

## 5. Не смешивать нумерацию

| Документ | ID |
|----------|-----|
| **v4 SSOT** | A-01, F-01, D-04, … |
| Legacy | af-2-01, af-11, B2-09 |

**Карта:** [ANTIFAKE_UNIFIED_MASTER.md](./ANTIFAKE_UNIFIED_MASTER.md)
