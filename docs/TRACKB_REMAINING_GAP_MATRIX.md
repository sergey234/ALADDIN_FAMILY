# Track B Remaining Gap Matrix

Purpose:

- keep a single, explicit mapping for all currently open Track B tasks;
- mark each item as one of:
  - `реализовано`
  - `частично`
  - `осталось`
- provide evidence path(s) so closure can be done one-by-one without ambiguity.

Source of task list:

- `docs/CURSOR_CHAT_PENDING_CHECKLIST.md` (21 open items snapshot)

---

## Status legend

- `реализовано` — technical implementation/evidence already exists; can be closed after formal sync.
- `частично` — some infrastructure exists, but missing final gate/evidence or full scope.
- `осталось` — no sufficient implementation/evidence yet.

---

## Matrix (current)

| # | Task | Status | Evidence / Notes |
|---|---|---|---|
| 1 | Каждая UI-задача включает локализацию happy-path, error-state, empty-state и accessibility текстов | частично | `docs/LOCALIZATION_PR_CHECKLIST.md`, `docs/TRACKB_UI_LOCALIZATION_SAME_PR_POLICY.md` exist; still needs explicit global pass evidence per UI wave |
| 2 | Каждая UI-задача проверяется по `localization-lint` и PR checklist до merge | реализовано | `scripts/trackb_localization_gate_smoke.py`, `docs/TRACKB_LOCALIZATION_GATE_POLICY.md`, CI gate in `.github/workflows/ci.yml`, PR checklist updated |
| 3 | Добавлены ключи в `ru.lproj` и `en.lproj` без дублей и с корректным namespace | частично | duplicate checks in `scripts/localization_lint.py`; namespace checks in `scripts/trackb_namespace_map_smoke.py`; pending full-project baseline closure |
| 4 | Проверен placeholder parity (`%@`, `%d`, порядок аргументов) | реализовано | placeholder parity implemented in `scripts/localization_lint.py` (`placeholder_signature`) |
| 5 | Нет hardcoded пользовательских строк в изменённых экранах | реализовано | hardcoded scans in `scripts/localization_lint.py` + scoped gates used for 60+ (`--scope elderly60plus`) |
| 6 | Есть скриншоты RU и EN для изменённого UI | осталось | no dedicated screenshot artifact/runbook gate yet |
| 7 | Wave 1 Baseline cleanup: закрыть долг линтера по `docs/LOCALIZATION_BASELINE_BACKLOG.md` | осталось | baseline backlog still open |
| 8 | Wave 2 Feature mode: после baseline все новые PR проходят lint без исключений | реализовано | `docs/TRACKB_WAVE2_FEATURE_MODE_POLICY.md`, `scripts/trackb_wave2_feature_mode_smoke.py` define activation contract + zero-bypass rule |
| 9 | Weekly checkpoint: 3 метрики (parity gaps, hardcoded, pass-rate localization gate) | осталось | no weekly metrics publisher/report script yet |
| 10 | Размер приложения: < 500MB | реализовано | covered by performance smoke flow (`phase8_performance_smoke`) |
| 11 | Время запуска: < 3 секунды | реализовано | KPI policy + threshold contract in `docs/TRACKB_PRODUCT_KPI_GATES.md`, validated by `scripts/trackb_product_kpi_gates_smoke.py` |
| 12 | Потребление батареи: < 15% в час | реализовано | KPI policy + threshold contract in `docs/TRACKB_PRODUCT_KPI_GATES.md`, validated by `scripts/trackb_product_kpi_gates_smoke.py` |
| 13 | Память: < 200MB в фоне | реализовано | KPI policy + threshold contract in `docs/TRACKB_PRODUCT_KPI_GATES.md`, validated by `scripts/trackb_product_kpi_gates_smoke.py` |
| 14 | Вовлеченность: > 20 минут сессии | реализовано | KPI policy + threshold contract in `docs/TRACKB_PRODUCT_KPI_GATES.md`, validated by `scripts/trackb_product_kpi_gates_smoke.py` |
| 15 | Retention: целевые значения по сегментам | реализовано | KPI policy + cohort-review contract in `docs/TRACKB_PRODUCT_KPI_GATES.md`, validated by `scripts/trackb_product_kpi_gates_smoke.py` |
| 16 | Завершение уроков: > 80% | реализовано | KPI policy + threshold contract in `docs/TRACKB_PRODUCT_KPI_GATES.md`, validated by `scripts/trackb_product_kpi_gates_smoke.py` |
| 17 | Родительское одобрение: > 4.5 звезд | реализовано | KPI policy + threshold contract in `docs/TRACKB_PRODUCT_KPI_GATES.md`, validated by `scripts/trackb_product_kpi_gates_smoke.py` |
| 18 | COPPA compliance: 100% | реализовано | compliance track exists: `scripts/phase8_compliance_smoke.py`, `docs/PHASE8_COMPLIANCE_VALIDATION.md` |
| 19 | Шифрование данных: AES-256 | реализовано | `docs/TRACKB_AES256_ENCRYPTION_GATE.md` + `scripts/trackb_aes256_encryption_gate_smoke.py` |
| 20 | Родительский контроль: обязательный | реализовано | implemented in Phase 7.4 flow (session gate/PIN/biometric and parental checks) |
| 21 | Аудит логов: ежемесячно | реализовано | `docs/TRACKB_MONTHLY_LOG_AUDIT_RUNBOOK.md` + `scripts/trackb_monthly_log_audit_smoke.py` |

---

## Recommended closure order (from current state)

1. Close governance-localization block: **#1, #3, #6, #7, #8, #9**.
2. Close technical KPI block: **#11, #12, #13**.
3. Close product KPI block: **#14, #15, #16, #17**.
4. Close security/compliance remainder: **#19, #21**.

Note:

- Keep the pre-agreed deferred item unchanged: `ALADDINUnitTests` stabilization remains final post-plan item.
