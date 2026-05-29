# Companion — Cursor TODO (Этап 2–3 + VOICE-PREM)

**Обновлено:** 2026-05-29 · **Git:** `f8ca4e1e` build **216** on `origin/master`  
**Трекер 102:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) · **Осталось:** [COMPANION_WHAT_REMAINS.md](./COMPANION_WHAT_REMAINS.md)

**Рабочая папка:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS`

> Не трогать без PO: **HERO-3-07**, **GATE-DIALOG**

---

## ✅ Закрыто (build 216)

- [x] Sprint 4 (4.1–4.6) · Sprint 5 код (5.1–5.14 кроме device)
- [x] Блок G (G.1–G.3) · GATE-OPS · verify 18/18
- [x] Push `f8ca4e1e` · build **216** (Info.plist, pbxproj×8, AppConfig×2)
- [x] Neuro-TTS код · Hermes rotator · companion UX fixes
- [x] **5.6** `tools_used` в «Моё» · **5.9** media stub дока
- [x] VOICE-PREM 01, 02, 05, 06 · verify/deploy scripts в git

---

## 🔴 Активно — делать дальше

### P0 продукт

- [ ] **TestFlight 216** — Archive → App Store Connect
- [ ] **Smoke device 216** — COGS, вложения, trust, social bridge, chips

### VOICE-PREM (порядок PO)

- [ ] **VOICE-PREM-04** — `./scripts/voice_prem_04_03.sh` (нужен `secrets/elevenlabs.api_key`)
- [ ] **VOICE-PREM-03** — включён в `voice_prem_04_03.sh` (prewarm после 04)

### Ops

- [ ] **2-й ключ OpenRouter** — `/opt/aladdin-backend/secrets/hermes_keys.txt` на VPS
- [ ] `./scripts/companion_voice_quick_check.sh` — после ElevenLabs (ожидаем HTTP 200 на `/tts`)

### 102 / PO (не код-агент без разрешения)

- [ ] **HERO-3-07** — production `.riv` ×3
- [ ] **HERO-3-11b / 11c** — device QA
- [ ] **GATE-*** — формальное закрытие

---

## Справка: команды

```bash
./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru
export PREMIUM_TOKEN="$(./scripts/mint_premium_companion_jwt.sh)"
./scripts/companion_voice_quick_check.sh
```

---

## Сессии (кратко)

| Дата | Коммит | Содержание |
|------|--------|------------|
| 2026-05-29 | `f8ca4e1e` | build **216**: Premium TTS, Hermes, UX, docs, ops scripts |
| 2026-05-29 | `351a9b03` | build **215**: Sprint 4–5, stream wiring |
| 2026-05-28 | `771340a3` | build **214**: CODE Sprints 1–3 |
