# Trial на тарифах — UX (отдельно от Antifake l10n)

**Дата:** 2026-09-18  
**Статус:** план + TODO `trial-ux-*`. Локализация вердикта Hub (`afl10n-*`) **не меняется**.  
**Симптом:** тап Trial при уже активном trial → `prepareCreateFamilyFlow` / registration (часто после `RESET_ONBOARDING` + пустой локальный family cache).

## Рекомендуемый UX

| Ситуация | Поведение |
|----------|-----------|
| Trial **уже active** | Не registration. Snackbar: «Trial already active until DATE». Опционально: Open Antifake / закрыть тарифы. |
| Trial **только что выдан** и на сервере **нет** семьи | Registration **один раз**. |
| Перед `prepareCreateFamilyFlow` | Только если `needsServerFamilyCreation()` после **свежего** `GET /family/members` (не на пустом локальном кэше после RESET). |
| QA | Не смешивать с `RESET_ONBOARDING` в той же сессии — ломает family context. |

## Варианты

| | Суть | Trade-off |
|---|------|-----------|
| **A (рекомендуем)** | Только Tariffs: если Trial already active → не звать `prepareCreateFamilyFlow` / registration | Маленький diff, закрывает баг сразу |
| B | Перед registration — refresh `GET /family/members`, потом `needsServerFamilyCreation()` | Надёжнее против stale cache; чуть больше сети |
| C | Глубокий рефактор family gate | Не нужен сейчас |

## Cursor TODO

| Todo id | Задача | Статус |
|---------|--------|--------|
| `trial-ux-meta` | Этот документ + TODO | ✅ |
| `trial-ux-a-skip-reg` | A: skip registration если trial already active | ✅ |
| `trial-ux-a-snackbar` | A+: toast «Trial already active until DATE» | ✅ |
| `trial-ux-a-open-antifake` | Опционально: CTA Open Antifake / закрыть тарифы | pending |
| `trial-ux-b-fresh-members` | B: перед prepare — fresh GET /family/members | pending |
| `trial-ux-qa-no-reset` | QA note: не мешать RESET_ONBOARDING с trial family flow | pending (док) |

## Порядок

1. A + snackbar (сделано в Tariffs).  
2. Опциональный CTA / B — отдельные маленькие diff.  
3. Не смешивать коммиты с `afl10n-*`.
