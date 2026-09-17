# Antifake Hub — единый план (без дублей)

**Дата:** 2026-09-17 · **SSOT**  
**Вердикт:** хаб = каркас; Text сейчас «мягкий детектор новостей», не детектор мошенничества → один soft-score ~27% + green authentic. Нужно восстановить цепочку: сленг ↔ lexicon ↔ mode ↔ пороги ↔ UI (RU+EN).

**Cursor TODO:** `afhub-*` (merge-only). Не смешивать с Antifake v4 REGISTRY / bot / dirty tree.  
**Деплой MAIN FirstVDS (`…180`):** только по **GO**.

**Инвариант языка:** каждый пункт ниже — строки **RU + EN** сразу (KZ — п.18).

---

## Честный ответ: будет ли «идеальный хаб на 100%»?

**Нет — и никто в мире не даёт 100%.**  
Norton / Kaspersky / Truecaller / Hive / Reality Defender тоже ошибаются: новые схемы социнженерии, deepfake SOTA, zero-day фишинг. Обещать «идеально 100%» = ложь родителю и риск App Review.

| Уровень | Что означает | Этот план (п.1–18) |
|---------|--------------|---------------------|
| **P0 Done** | На телефоне снова «есть анализ»: скам ≠ green 27% | ✅ цель P0 |
| **P0–P1 Done** | Надёжный **семейный scam/phishing hub** RU+EN (текст, ссылки, звонок UX) | ✅ достижимо |
| **P0–P3 Done** | Сильный **продуктовый** хаб: медиа, intel, feedback, l10n, red-team | ✅ «топ для family-safety», не lab-SOTA |
| **Мировой lab-SOTA** | Live VT/GSB, CNAM-класс, face-swap SOTA, watermark/C2PA, continuous ML | ❌ **не** в п.1–18 → см. **P4 ниже** |

**После реализации п.1–18 у нас будет:**
- рабочий детектор **мошенничества** (не «мягкие новости») на Text/SMS;
- полный **двуязычный** UI + lexicon RU/EN (+ KZ pack);
- читаемые Reasons, action tips, share, калибровка на прод;
- Voice/Video/Call на уровне **честного ensemble**, не «магия 100%».

**Что ещё улучшить / дополнить (P4 — вне текущего TODO, опционально):**

| # | Дополнение | Зачем |
|---|------------|--------|
| 19 | Live Safe Browsing / VirusTotal (ключи в secret manager) | ссылки как у топ-AV |
| 20 | Мультиязычный transformer (scam) на GPU/edge | обобщение вне словаря |
| 21 | CNAM / carrier spam API (где легально) | звонки Truecaller-class |
| 22 | Face-swap / lip-sync SOTA model + C2PA | video lab-grade |
| 23 | Watermark / provenance для медиа | доказательность |
| 24 | Online learning с human review (не авто) | скорость к новым схемам |
| 25 | Юр. дисклеймер + метрики false± в Settings | доверие и App Store |

**Критерий «готово для семьи» (не 100% вселенной):** golden SMS/URL ≥ **95%**; 0 green authentic на явный money+urgency; 0 сырых `rules:` в UI на RU и EN.

---

## Карта «причина → пункт плана» (без дыр)

| Причина | Пункт |
|---------|--------|
| A mode=`news` | **1** |
| B узкий lexicon | **2** |
| C soft ML 0.27 | **3** |
| D ensemble без SMS-veto | **1** + **3** |
| E сырые Reasons | **4** |
| F simulator try_later | **6** |
| Доверие UX «что делать» | **5** |
| Отдельно от fake-news | **7** |
| Ссылки | **8** |
| Call spoof | **9** |
| Прод + калибровка | **10** |
| Voice | **11** |
| Video | **12** |
| Threat intel freshness | **13** |
| Share family | **14** |
| Feedback lexicon | **15** |
| Полный l10n хаба | **16** |
| Red-team | **17** |
| KZ packs | **18** |

---

# Общий план: что делаем и для чего

## P0 — за 1–2 дня (вернуть «есть анализ» на телефоне)

### 1. Mode sms / auto · `afhub-p0-01-mode-sms`
**Что:** Text + Contact → `sms` (или auto: короткий/скам-паттерн → sms, длинный → news).  
**Зачем:** включить SMS-защиты (scam-hit → 0.72, veto SFM). Сейчас всё как «новость».  
**Без дубля:** один helper выбора mode в iOS; сервер уже умеет `sms`.

### 2. Lexicon RU+EN · `afhub-p0-02-lexicon`
**Что:** один shared pack → heuristic + agent. **Обязательно:** и **отдельные слова**, и **словосочетания** (RU+EN).  
**Зачем:** закрыть B — комбо financial + urgency; ловить и «срочно», и «на карту».  
**Без дубля:** один модуль `antifake_scam_lexicon.py` (не копипаст в 3 файла).

**Целевой объём (family optimum):**

| Метрика | Цель | Сейчас (`lexicon_v2`) |
|---------|------|------------------------|
| Lexicon unique | **150–250** | **214** (`lexicon_stats`) |
| — single words | ≥40 | **75** |
| — multiword phrases | ≥60 | **139** |
| Intent entries | 50–120 | **112** (words 38 + phrases 74) |
| Формат | слово **и** фраза | оба |
| Языки | RU + EN | оба в одном pack |

**Слабые одиночные слова** (`WEAK_SCAM_SINGLES`: деньги/карта/код/банк/сбер…): матчятся, но **не** дают hard `likely_fake` без партнёра (urgency / 2-й intent / сильная фраза).

**Словари (примеры):**

| Тег | Слова | Словосочетания |
|-----|-------|----------------|
| urgency | срочно, urgently, asap | через час, act now, limited time |
| money | переведи, money, wire | переведи мне деньги, send me money |
| card | карта, cvv, card | на карту, card number |
| otp | otp, смс | код из смс, verification code |
| sbp | сбп | сбп перевод, faster payments |
| banks/ops | сбер, втб, мтс, paypal | служба безопасности банка, bank security |
| prize | приз, prize | выиграли приз, claim your prize |

Полный pack versioned: `LEXICON_VERSION = lexicon_v2`. Дальше расширение — п.15 feedback / п.17 red-team.

### 3. Scoring + anti-green · `afhub-p0-03-scoring`
**Что:** urgency + money → `likely_fake` ≥ 0.85; при manipulation-reasons и score &lt; 0.65 → минимум `uncertain`, никогда green authentic.  
**Зачем:** убрать вечный 27% authentic (причина C/D).  
**Без дубля:** пороги в одном месте (`_analyze_text_heuristic` + normalize), не в UI.

### 4. Human Reasons RU+EN · `afhub-p0-04-reasons-i18n`
**Что:** strip `rules:`/`sfm:`; `reasons_human` по app lang; ключи LocalizationManager.  
**Зачем:** закрыть E — родитель видит смысл, не machine codes.  
**Без дубля:** SSOT human на сервере; iOS только safety net.

### 5. Action card «Что делать» · `afhub-p0-05-action-card`
**Что:** после fake/uncertain — не переводить / банк / доверенный человек (RU+EN).  
**Зачем:** доверие и безопасность, не только %.  
**Без дубля:** одна карточка в `AntifakeVerdictCard`; share-family — отдельно п.14.

### 6. Golden QA + simulator · `afhub-p0-06-golden-sms`
**Что:** golden SMS RU+EN (scam/benign); симулятор: auth/сеть без silent fail.  
**Зачем:** DoD P0 + закрыть F.  
**Без дубля:** один golden pack; prod alert — в п.10.

**DoD P0:** «Переведи мне срочно деньги на карту» → `likely_fake` + читаемые Reasons на EN и RU.

---

## P1 — неделя (намерение + ссылки + звонок + прод)

### 7. Scam-intent слой · `afhub-p1-01-intent`
**Что:** классификатор money/card/OTP/SBP/authority отдельно от fake-news.  
**Зачем:** не путать сенсационные новости с мошенничеством.  
**Без дубля:** новый модуль intent → теги; scoring п.3 только потребляет теги.

### 8. URL redirect + lookalike · `afhub-p1-02-url`
**Что:** follow redirects (лимит) + brand lookalike; reasons RU+EN.  
**Зачем:** дыра Link vs топ. SSRF-guard сохранить.  
**Без дубля:** только `check_url` pipeline; VT/GSB не здесь (опционально позже в п.13).

### 9. Call/Contact spoof UI · `afhub-p1-03-call-spoof`
**Что:** усилить directory + spoof hints в UI (RU+EN).  
**Зачем:** согласовано в roadmap P1; Contact уже на sms (п.1).  
**Без дубля:** UI + существующий directory store; не обещать Truecaller-class.

### 10. Калибровка + деплой MAIN · `afhub-p1-04-calib-prod`
**Что:** golden pass-rate ≥ 95% + alert если ниже; GO → выкат только antifake scoring файлов на `…180`.  
**Зачем:** прод = то, что видит телефон.  
**Без дубля:** один deploy checklist; не весь dirty tree.

---

## P2 — месяц (медиа + intel + share)

### 11. Voice · `afhub-p2-01-voice`
**Что:** обязательный STT → text scam (п.1–3); сильнее deepfake encoder.  
**Зачем:** vishing. Copy RU+EN.  
**Без дубля:** STT результат → тот же text pipeline, не второй lexicon.

**Статус:** ✅ `antifake_audio_v2` — канал `stt_text` (RU+EN) → `check_text(mode=sms)` + veto; deepfake + clipping/narrowband; i18n + iOS hint.

### 12. Video · `afhub-p2-02-video`
**Что:** ONNX on + face quality gates + AV1 fallback UX RU+EN.  
**Зачем:** не green при decode fail.  
**Без дубля:** один video ensemble path.

**Статус:** ✅ `antifake_video_v2` — ONNX/frame **ON by default** (`ANTIFAKE_VIDEO_ONNX=0` выкл.); face-gates блокируют hard fake на blur/no-face; AV1/decode → `insufficient_data` + RU/EN UX; iOS hint обновлён.

### 13. Threat intel freshness · `afhub-p2-03-threat-intel`
**Что:** мониторинг cron URLHaus/OpenPhish freshness + alert.  
**Зачем:** ссылки не на протухшем feed.  
**Без дубля:** health поверх существующих import-скриптов.

**Статус:** ✅ код — `antifake_threat_intel_freshness.py` + gate `scripts/antifake_phishing_feed_gate.py` + `capabilities.threat_intel.freshness`. Cron на MAIN `…180` — только после **GO**.

### 14. Share with family · `afhub-p2-04-share-family`
**Что:** one-tap «поделиться с семьёй» после вердикта (RU+EN).  
**Зачем:** roadmap UX; дополняет п.5, не дублирует action tips.  
**Без дубля:** reuse family reports / share payload если уже есть.

---

## P3 — зрелость

### 15. Feedback → lexicon · `afhub-p3-01-feedback`
**Что:** «это был скам» → очередь на расширение lexicon (ручной/полуавто).  
**Зачем:** живой язык меняется.  
**Без дубля:** не авто-retrain ML вслепую; только pack updates + review.

### 16. Полный l10n-аудит хаба · `afhub-p3-02-hub-l10n-audit`
**Что:** все табы, errors, empty, premium, history — 0 сырых ключей, 0 RU на EN.  
**Зачем:** весь антихаб на 2 языках end-to-end.

### 17. Red-team monthly · `afhub-p3-03-redteam`
**Что:** корпус социнженерии RU+EN ежемесячно + регресс golden.  
**Зачем:** ловить регресс 27%-класса.

### 18. Locale packs RU/EN/**KZ** · `afhub-p3-04-locale-kz`
**Что:** per-locale packs (сначала RU/EN стабильны, затем KZ).  
**Зачем:** roadmap зрелости; не блокирует P0.

---

## Что делаем сейчас (минимальный пакет)

Только **п.1–4** (+ п.5–6 для DoD):  
`mode=sms` + lexicon + anti-green + human Reasons (+ action + golden).

Код без деплоя dirty tree → потом **GO** на п.10 (MAIN `…180`).

---

## Cursor TODO (канон, 1:1 с пунктами)

| # | Id | Статус |
|---|-----|--------|
| — | `afhub-meta` | ✅ план SSOT |
| 1 | `afhub-p0-01-mode-sms` | ✅ код (iOS resolver + contact/text→sms) |
| 2 | `afhub-p0-02-lexicon` | ✅ `lexicon_v2` — 214 фраз (75 слов + 139 словосочетаний) RU+EN |
| 3 | `afhub-p0-03-scoring` | ✅ floors + anti-green + ensemble SMS veto |
| 4 | `afhub-p0-04-reasons-i18n` | ✅ strip `rules:`/`sfm:` + `reasons_human` |
| 5 | `afhub-p0-05-action-card` | ✅ next-steps card RU/EN |
| 6 | `afhub-p0-06-golden-sms` | ✅ RU 24 + EN 10; unittest PASS |
| 7 | `afhub-p1-01-intent` | ✅ `antifake_scam_intent.py` + floors + i18n |
| 8 | `afhub-p1-02-url` | ✅ redirect + lookalike + SSRF + i18n |
| 9 | `afhub-p1-03-call-spoof` | ✅ spoof hints UI + authority labels + tests |
| 10 | `afhub-p1-04-calib-prod` | ✅ calib 100% + GO deploy MAIN `…180` (tar scoring pack) |
| 11 | `afhub-p2-01-voice` | ✅ audio_v2 STT→SMS scam RU+EN + deepfake strengthen |
| 12 | `afhub-p2-02-video` | ✅ ONNX default + face gates + AV1/decode no-green |
| 13 | `afhub-p2-03-threat-intel` | ✅ код freshness gate; cron MAIN — ждать GO |
| 14 | `afhub-p2-04-share-family` | pending |
| 15 | `afhub-p3-01-feedback` | pending |
| 16 | `afhub-p3-02-hub-l10n-audit` | pending |
| 17 | `afhub-p3-03-redteam` | pending |
| 18 | `afhub-p3-04-locale-kz` | pending |

**Убраны дубли:** Call не в P2 повторно; threat intel не только в P3; «What to do» = п.5, share = п.14; calib alert = п.10 (не второй golden).

---

## Чеклист закрытия любой задачи

- [ ] Один owner-файл / модуль (без копипаста lexicon/scoring)
- [ ] RU + EN строки
- [ ] Тест или smoke
- [ ] Пункт в этом файле ✅
- [ ] `TodoWrite merge: true` на id
