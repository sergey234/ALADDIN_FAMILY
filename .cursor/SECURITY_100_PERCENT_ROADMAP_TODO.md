# Security 100% — Roadmap Todo (L1 + L2 + L3)

**Создано:** 2026-06-09  
**Цель:** все 138 функций + маркетинг на **L1 + L2 + L3**.  
**Позже объединить с:** `SECURITY_138_MASTER_TODO.md` + `ANTIFAKE_PRODUCTION_TODO.md` → один implementation plan.

**Техспек:** `docs/SECURITY_100_PERCENT_MASTER_PLAN.md`  
**Единый план:** `docs/SECURITY_UNIFIED_100_PERCENT_PLAN.md`  
**Онбординг:** **не меняем** до Фазы 7 (только audit `copy-01-audit`)  
**Счёт фаз:** 0 / 8 фаз ✅ · **9 / 53** gate-задач ✅ (SEC-INFRA + GATE-D backend)

---

## Как читать

| Поле | Значение |
|------|----------|
| **L1** | UI + copy готовы |
| **L2** | API sync + persist |
| **L3** | Пользователь видит результат |
| **Gate** | Не переходить к следующей фазе без ✅ |

---

# ФАЗА 0 — SEC-INFRA «крыша» (1–2 нед) · P0

**Зачем:** без этого все 9 переключателей = обман L2.

| ID | Gate | L | Задача | MASTER | Статус |
|----|------|---|--------|--------|--------|
| `R0-G1` | ✅ | L2 | `protection.py` logger + enable 200 | sec-01, af-0-01 | ✅ |
| `R0-G2` | ✅ | L2 | DB `user_protection_settings` UPSERT | sec-02, af-0-02 | ✅ |
| `R0-G3` | ✅ | L2 | Category IDs канон (док + код) | sec-03, af-0-04 | ✅ |
| `R0-G4` | ✅ | L2 | iOS schema adapter + loadSettingsFromServer | sync-01, af-5-01/02 | ✅ |
| `R0-G5` | ✅ | L2 | Block wildcard security paths | sec-04/05, B0-05 | ✅ |
| `R0-G6` | ✅ | L2 | Reject mock-real-protection in gateway | sec-05 | ✅ |
| `R0-G7` | ✅ | L2 | Smoke: toggle deepfakes → reload → true | af-11-01 | ✅ |
| `R0-G8` | ✅ | L2 | Smoke: все 9 categories round-trip | NEW | ✅ |
| `R0-G9` | ⬜ | L2 | SFM: `sfm-01` fix circular import `security/types` | sfm-01 | ⬜ |
| `R0-G10` | ✅ | L2 | SFM: Agent Registry, unknown → 503 | sfm-02…05 | ✅ |
| `R0-G11` | ✅ | L2 | SFM: category → agent activation map | sfm-06 | ✅ |
| `R0-G12` | ✅ | L2 | Prod: zero `status:success` on unregistered SFM fn | sfm-04 | ✅ |

**Gate 0 выход:** 9/9 категорий L2 ✅ на TestFlight + SFM Registry без fake success.

---

# ФАЗА 1 — Antifake Hub (3–4 нед) · P0

**Покрывает:** deepfakes 8 угроз · **Детали:** `ANTIFAKE_PRODUCTION_TODO.md` (72 задачи)

| ID | Gate | L | Задача | Статус |
|----|------|---|--------|--------|
| `R1-G1` | ⬜ | L3 | `/api/antifake/check/text` real verdict | ⬜ |
| `R1-G2` | ⬜ | L3 | `/check/url` + Share Extension | ⬜ |
| `R1-G3` | ⬜ | L3 | audio/video/document async jobs | ⬜ |
| `R1-G4` | ⬜ | L3 | call/analyze + CallKit post-call | ⬜ |
| `R1-G5` | ⬜ | L1 | `AntifakeHubScreen` 4 вкладки | ⬜ |
| `R1-G6` | ⬜ | L1 | deepfakes → Hub navigation | ⬜ |
| `R1-G7` | ⬜ | L3 | Premium 403 free user on check API | ⬜ |
| `R1-G8` | ⬜ | L3 | 8/8 угроз matrix `af-9-*` | ⬜ |
| `R1-G9` | ⬜ | L1 | FAQ/onboarding antifake = L3 only | ⬜ |
| `R1-G10` | ⬜ | ALL | TestFlight: новость/голос/видео демо | ⬜ |

**Gate 1 выход:** Premium user проходит все 4 вкладки Hub с вердиктом.

---

# ФАЗА 2 — Privacy Hub (3 нед) · P0

**Покрывает:** dataLeaks 12 (DW + DC + LOC + privacy stats)

| ID | Gate | L | Задача | MASTER | Статус |
|----|------|---|--------|--------|--------|
| `R2-G1` | ⬜ | L3 | Dark Web scan → breaches list | dw-01…08 | ⬜ |
| `R2-G2` | ⬜ | L3 | Data cleanup start → report | dc-01…06 | ⬜ |
| `R2-G3` | ⬜ | L3 | Location bubble generate | loc-01…06 | ⬜ |
| `R2-G4` | ⬜ | L1 | Privacy Hub screen (3 входа) | NEW | ⬜ |
| `R2-G5` | ⬜ | L1 | Analytics modals → Privacy Hub | NEW | ⬜ |
| `R2-G6` | ⬜ | L2 | Advanced toggles → API agents | comp + dc | ⬜ |
| `R2-G7` | ⬜ | L3 | EXIF/tracker stats в UI | comp-08 | ⬜ |
| `R2-G8` | ⬜ | ALL | TestFlight Privacy Hub демо | ⬜ |

**Gate 2 выход:** email breach check + cleanup scan с результатом.

---

# ФАЗА 3 — Identity Hub (2–3 нед) · P0

**Покрывает:** fraud 12

| ID | Gate | L | Задача | MASTER | Статус |
|----|------|---|--------|--------|--------|
| `R3-G1` | ⬜ | L3 | SNILS/credit/fraud detect API | id-01…03 | ⬜ |
| `R3-G2` | ⬜ | L3 | attempts list + block/allow | id-05 | ⬜ |
| `R3-G3` | ⬜ | L1 | Identity Hub (не только modal) | NEW | ⬜ |
| `R3-G4` | ⬜ | L2 | fraud toggle → agent on | id-06 | ⬜ |
| `R3-G5` | ⬜ | L3 | vishing/smishing → antifake text link | mob-04 | ⬜ |
| `R3-G6` | ⬜ | ALL | TestFlight identity flow | id-08 | ⬜ |

**Gate 3 выход:** detect identity attempt с вердиктом.

---

# ФАЗА 4 — Device Hub (4–5 нед) · P1

**Покрывает:** cyber 10 + mobile 10 + iot 10 = 30 угроз

| ID | Gate | L | Задача | MASTER | Статус |
|----|------|---|--------|--------|--------|
| `R4-G1` | ⬜ | L3 | Antivirus scan → threats → quarantine | av-01…08 | ⬜ |
| `R4-G2` | ⬜ | L3 | Phishing/Network/Mobile/Incident scan buttons | comp-01…04 | ⬜ |
| `R4-G3` | ⬜ | L3 | IoT home scan + fix threat | iot-01…07 | ⬜ |
| `R4-G4` | ⬜ | L3 | Mobile security agent | mob-01…06 | ⬜ |
| `R4-G5` | ⬜ | L1 | Device Hub screen (scan center) | NEW | ⬜ |
| `R4-G6` | ⬜ | L2 | cyber/mobile/iot toggles → agents | NEW | ⬜ |
| `R4-G7` | ⬜ | L3 | AI categories 404 → real routers | comp-07 | ⬜ |
| `R4-G8` | ⬜ | L3 | Protection stats real numbers | av-05 | ⬜ |
| `R4-G9` | ⬜ | ALL | TestFlight full device scan | ⬜ |

**Gate 4 выход:** EICAR или test threat → quarantine UI.

---

# ФАЗА 5 — Family polish (1–2 нед) · P1

**Покрывает:** child 17 + family 15 — **добивка до 100%**

| ID | Gate | L | Задача | MASTER | Статус |
|----|------|---|--------|--------|--------|
| `R5-G1` | ⬜ | L3 | monitoring/detail real data | pc-01…02 | ⬜ |
| `R5-G2` | ⬜ | L3 | FamilyModals messages/calls API | pc-03 | ⬜ |
| `R5-G3` | ⬜ | L3 | Parental PDF/CSV reports | pc-04…05 | ⬜ |
| `R5-G4` | ⬜ | L2 | Geocode geofences | loc-04 | ⬜ |
| `R5-G5` | ⬜ | ALL | TestFlight parent monitoring | pc-06 | ⬜ |

**Gate 5 выход:** parent видит реальные messages count ≠ 0 на тестовом ребёнке.

---

# ФАЗА 6 — Extras (2 нед) · P2

| ID | Gate | L | Задача | MASTER | Статус |
|----|------|---|--------|--------|--------|
| `R6-G1` | ⬜ | L3 | Crash detection API + settings modal | em-01…03 | ⬜ |
| `R6-G2` | ⬜ | L3 | Roadside assistance API | em-04…05 | ⬜ |
| `R6-G3` | ⬜ | L3 | Elderly remove mockData | eld-01…04 | ⬜ |
| `R6-G4` | ⬜ | L2 | Voice control component | EX-VOICE | ⬜ |
| `R6-G5` | ⬜ | L2 | VPN regression smoke | maintain | ⬜ |

---

# ФАЗА 7 — COPY + Legal (1 нед) · P1

| ID | Gate | L | Задача | MASTER | Статус |
|----|------|---|--------|--------|--------|
| `R7-G1` | ⬜ | L1 | Audit onboarding vs L3 — **no UI edits** | copy-01-audit | ⬜ |
| `R7-G2` | ⬜ | L1 | FAQ только L3-ready | copy-02, af-8 | ⬜ |
| `R7-G3` | ⬜ | L1 | Tariffs bullets ↔ Hub map | copy-03 | ⬜ |
| `R7-G4` | ⬜ | L1 | App Store review notes + screenshots | copy-05 | ⬜ |
| `R7-G5` | ⬜ | L1 | `SECURITY_138_USER_CLAIMS.md` signed off | copy-04 | ⬜ |

---

# ФАЗА 8 — 138 Checklist + Final QA (3 дня + 1 нед)

| ID | Gate | L | Задача | Статус |
|----|------|---|--------|--------|
| `R8-G1` | ⬜ | ALL | Regen EXTENDED_138 verify=L3 criterion | ⬜ |
| `R8-G2` | ⬜ | ALL | 138/138 manual sign-off TestFlight | ⬜ |
| `R8-G3` | ⬜ | ALL | Prod grep 24h: zero mock-real-protection | ⬜ |
| `R8-G4` | ⬜ | ALL | Merge → `SECURITY_UNIFIED_IMPLEMENTATION.md` | ⬜ |

---

## Сводка: что уже ~100% (не блокирует план)

| Сегмент | L1 | L2 | L3 | Действие |
|---------|----|----|-----|----------|
| Parental 32 | ✅ | ✅ | ⚠️ 85% | Фаза 5 |
| VPN / internet 6 | ✅ | ✅ | ✅ | regression |
| Family core | ✅ | ✅ | ✅ | — |
| AI Assistant | ✅ | ✅ | ✅ | tools в фазах 1–3 |
| Gamification | ✅ | ✅ | ✅ | — |

---

## Порядок слияния планов (когда начнёте реализацию)

1. Завершить **Фазу 0** (SEC) — блокер всего.
2. Параллельно вести **ANTIFAKE** детальный трекер = Фаза 1.
3. После Gate 0 — открыть Фазы 2–4 по приоритету Premium.
4. Слить 3 MD в один `SECURITY_UNIFIED_IMPLEMENTATION.md` с единым счётчиком задач.

---

## Обновление статусов

- Gate ✅ → можно начинать следующую фазу.
- Внутри фазы закрывайте MASTER task IDs (`sec-*`, `dw-*`, `af-*`).
- **L1 copy** править только после **L3** готов (Фаза 7), кроме antifake (встроено в R1-G9).
