# Localization Batch Gate — RU/EN для всех 129+ batch

**Версия:** 1.0 · **2026-06-10**  
**Правило:** любой batch с **пользовательскими строками в iOS** закрывается только при паритете **RU + EN** в `LocalizationManager.swift` и использовании `localizationManager.localized("key")` (без хардкода в View).

**Связано:** `.cursor/IMPLEMENTATION_BATCHES_TODO.md` (BATCH LOC), `af-6-09`, `B-QA-06`.

---

## Критерии PASS

| # | Проверка |
|---|----------|
| 1 | Каждый новый UI key есть в **обоих** словарях RU и EN |
| 2 | Views/ViewModels не содержат user-facing литералов (кроме `reasons[]` с backend) |
| 3 | `NavigationManager` / nav bar keys через `nav_screen_*` где экран в quick-nav |
| 4 | Placeholder / error / button / tab — все через keys |
| 5 | При закрытии batch — grep: `rg 'Text\("[А-Яа-я]' Screens/<Hub>` → 0 в новом коде |

---

## Матрица batch → локализация

| Batch / группа | LOC gate ID | UI scope | Статус |
|----------------|-------------|----------|--------|
| SFM-WIRE (10) | B-LOC-01 | backend only — N/A iOS | ✅ N/A |
| OPS (22) | B-LOC-01 | скрипты/логи — N/A | ✅ N/A |
| BATCH SYNC (5) | B-LOC-01 | docs only | ✅ N/A |
| BATCH 0 SEC-INFRA (8) | B-LOC-01 | server errors only | ✅ N/A |
| BATCH 1 API (12) | B-LOC-01 | backend OpenAPI | ✅ N/A |
| B-PRE iOS (6) | B-LOC-02 | AppConfig/tests — минимум UI | ✅ N/A (no user strings) |
| **BATCH 2 Antifake (12)** | **B-LOC-02** | **AntifakeHub + components** | **✅** |
| BATCH 3 Privacy (8) | B-LOC-03 | Privacy Hub + DW modals | ✅ |
| BATCH 4 Identity (6) | B-LOC-04 | Identity Hub + modal | ✅ |
| BATCH 5 Device (9) | B-LOC-05 | Device Hub + scans | ✅ |
| BATCH 6 Family (5) | B-LOC-06 | parental modals | ✅ |
| BATCH 7 Extras (4) | B-LOC-07 | crash/roadside/elderly | ✅ |
| SEC-P2 (5) | B-LOC-01 | backend migration | ⬜ |
| BATCH COPY (4) | B-LOC-08 | FAQ, tariffs, App Store | ✅ `family_roles_help_*` |
| BATCH QA (6) | B-LOC-09 + **B-QA-06** | полный regression 143 items | ✅ static |
| Navigation shared | B-LOC-10 | `nav_screen_*` для новых Hub | ✅ B2–B7 hubs |
| Antifake af-6-09 | B-LOC-11 | все `antifake_*` keys | ✅ |

---

## Antifake keys (B-LOC-11 PASS evidence)

**43 keys** `antifake_*` + `nav_screen_antifake_hub` — паритет RU/EN (2026-06-10).

Проверка:
```bash
rg '"antifake_' Core/Localization/LocalizationManager.swift | wc -l
# ожидаем: чётное число (×2 языка)
```

---

## Чеклист при закрытии любого Hub batch (B3…B7)

1. Добавить keys в RU и EN секции `LocalizationManager.swift`
2. Все `Text("…")` / `title:` / `placeholder:` → `localized("…")`
3. Обновить эту таблицу → статус ✅
4. Отметить `B-LOC-0N` в `IMPLEMENTATION_BATCHES_TODO.md`
5. При GATE-FINAL — `B-QA-06` полный прогон

---

*LOC gate v1.1 · B-LOC-08…10 ✅ · Evidence: `docs/release/QA_06_LOC_REGRESSION.md`*
