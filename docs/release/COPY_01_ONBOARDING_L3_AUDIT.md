# B-COPY-01 — Onboarding vs L3 Reality Audit

**Дата:** 2026-06-11 · **Gate:** GATE-K · **Post-L3 copy:** R-19 COPY-POST-L3 ✅

**Источники:** `Screens/14_OnboardingScreen.swift`, `Core/Localization/LocalizationManager.swift`, `COPY_POST_L3_FULL_AUDIT.md`.

---

## Сводка

| Метрика | Было (audit) | После R-19 |
|---------|--------------|------------|
| OB-страниц | 7 (+ language) | 7 — Figma frames **не менялись** |
| Marketing copy OB_01/04/06 | over-promise | ✅ смягчено RU+EN |
| OB_02 «военные технологии» | keep | ✅ **без изменений** (PO) |
| onboarding_frozen | true → false | false (copy applied) |

---

## Матрица OB → L3 (post R-19)

| OB | Claim RU (после R-19) | L3 экран / API | Статус | Gap |
|----|----------------------|----------------|--------|-----|
| OB_01 | «основных киберугроз» | 9 категорий + 5 Hub | ✅ Copy aligned | Тариф определяет набор функций |
| OB_02 | ИИ 24/7 + **военные технологии шифрования** | Companion + Network Protection | ✅ | VPN B7-04 PASS |
| OB_03 | Родительский контроль | Family + parental API | ✅ GATE-I | — |
| OB_04 | **анализирует, предупреждает** | Privacy Hub + stats | ✅ | «предсказывает» убрано |
| OB_05 | Защита детей | Family chd | ✅ | — |
| OB_06 | AI **проверяет** фейки 23+ | Antifake Hub | ✅ | async job до нескольких минут |
| OB_07 | Согласия, регистрация | L1 legal | ✅ | не security claim |

---

## R-19 правки (выполнено)

| Key | Было | Стало RU |
|-----|------|----------|
| `onboarding_page1_desc` | более 100 видов | основных киберугроз |
| `onboarding_page4_desc` | предсказывает…предотвращает | анализирует…предупреждает |
| `onboarding_page6_desc` | распознает | проверяет |
| `onboarding_page2_desc` EN | без military-grade | Military-grade encryption (sync RU) |

**Файлы:** `LocalizationManager.swift`, `14_OnboardingScreen.swift`, `Localizable.strings`, kb `onboarding_page_onboarding_{ru,en}.json`, `ML_SYSTEM_PACKAGE` mirror.

---

## Over-promise — закрыто / остаток

| Риск | R-19 |
|------|------|
| «100 видов» в OB | ✅ убрано |
| «предсказывает» | ✅ убрано |
| «военное шифрование» | ✅ **оставлено** |
| «невозможно взломать» / «полная анонимность» | ✅ смягчено в Privacy/FAQ |
| Figma OB layout drift | ⏸ pre-existing; verify script case 1 anchors — не блокер copy |

---

## PASS B-COPY-01 + R-19

- [x] Таблица OB → L3 задокументирована
- [x] Post-L3 copy edits применены (R-19)
- [x] OB_02 RU military keep
- [x] RU/EN sync + verify RU strings PASS

*Audit v2.0 · R-19 done · Next: B-QA-02 Archive*
