# Companion / герои-помощники — что осталось (102 задачи)

**Обновлено:** 2026-05-29 (после push build **216** `f8ca4e1e`)  
**Источник правды по `[x]`:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md)  
**Cursor TODO:** [COMPANION_CURSOR_TODO_STAGE2_3.md](./COMPANION_CURSOR_TODO_STAGE2_3.md)  
**Premium озвучка:** [COMPANION_PREMIUM_VOICE_PLAN.md](./COMPANION_PREMIUM_VOICE_PLAN.md)

---

## Сводка одной таблицей

| Категория | Готово | Осталось | Комментарий |
|-----------|--------|----------|-------------|
| **102 спринтовые задачи** | **90** | **12** | Rive + GATE + P1-12/P2-17 |
| **CODE v2 (без Rive)** | 49/49 | 0 | В репо + push 216 |
| **Sprint 4–5 (runbook)** | код+VPS | **TF216 smoke** | Verify 18/18 ✅ |
| **VOICE-PREM** | 4/6 | **04, 03** | Trial=Premium для neuro-TTS (testing `FEATURE_NEURO_TTS_TRIAL=1`) · ключи ElevenLabs ⏳ |
| **HERO-3** | 24/26 | **07, 11b/11c** | PO / Rive |

---

## ✅ Закрыто в build 216 (`f8ca4e1e`) — не переделывать

- Neuro-TTS API + iOS player + Premium gate · AVSpeech 3 голоса (Free)
- Hermes key rotator + watchdog · companion SFM без шаблона угроз
- Navigation companion, PNG fallback Rive, verify **18/18**, deploy scripts
- Sprint 5.6 `tools_used` в «Моё» · 5.9 media stub дока
- Git push `origin/master` · build **216** в Info.plist / pbxproj / AppConfig

---

## 🔴 Осталось — приоритет (что делать дальше)

### A. Продукт / TestFlight (сейчас)

| # | Задача | Кто |
|---|--------|-----|
| 1 | **Archive TestFlight build 216** | PO / Xcode |
| 2 | **Smoke device 216:** COGS, workspaces, вложения, trust «+N», social bridge | PO |
| 3 | **VOICE-PREM-04+03** — `echo sk_... > secrets/elevenlabs.api_key` → `./scripts/voice_prem_04_03.sh` | PO + API key |
| 4 | **2-й OpenRouter ключ** в `hermes_keys.txt` на VPS | ops |

### B. 102 задачи — 12 открытых ID

| ID | Задача |
|----|--------|
| **HERO-3-07** | Production `.riv` ×3 — **только PO** |
| **HERO-3-11b** | Device QA MOTION/MIMIC/D10/STT-TTS — build **216+** |
| **HERO-3-11c** | MIMIC-Q после production Rive |
| **P2-09** | Figma↔Rive pipeline |
| **UX-14b** | Эмоции только Rive-анимацией |
| **P1-19** | App Store скриншоты Hub с Rive |
| **P1-12** | Postgres (не блокер MVP) |
| **P2-17** | A/B humor_density — по PO |
| **GATE-P0, EMO, DIALOG, CX, P1–P3, PROD** | Формальные ворота — без PO не закрывать |

### C. VOICE-PREM (вне 12, но в плане)

| ID | Статус |
|----|--------|
| 01–02, 05–06 | ✅ |
| **04** | ⏳ 3 voice id |
| **03** | ⏳ после 04 |

### D. Опционально (не блокер)

- Реальный Web Search API (`FEATURE_WEB_SEARCH_ENABLED=0`)
- Vision для фото (metadata в промпт)
- OpenRouter без Hermes CLI · Realtime voice 2027+

---

## Быстрые ссылки

| Документ | Зачем |
|----------|--------|
| [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md) | Все 102 ID |
| [COMPANION_CURSOR_TODO_STAGE2_3.md](./COMPANION_CURSOR_TODO_STAGE2_3.md) | Активный TODO |
| [COMPANION_ELEVENLABS_VOICES_RU.md](./COMPANION_ELEVENLABS_VOICES_RU.md) | VOICE-PREM-04 |
| [COMPANION_NEURO_TTS_ENV.md](./COMPANION_NEURO_TTS_ENV.md) | Env VPS |
