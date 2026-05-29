# ElevenLabs — три голоса для героев (VOICE-PREM-04)

**Порядок работ:** сначала **04** (три voice id) → потом **03** (ключ API + пилот на проде).

---

## 1. В кабинете ElevenLabs

Для каждого героя выберите **отдельный** голос (RU, семейный тон):

| Герой | Характер | Подсказка при выборе |
|-------|----------|----------------------|
| **unicorn** 🦄 | Тёплый, светлый, чуть выше | Женский/нейтральный, мягкий, без «новостного» тембра |
| **genie** 🧞 | Живой, с юмором, энергичный | Чуть быстрее, эмоциональнее (пилот **03** — первый smoke на нём) |
| **aladdin** 🧑 | Спокойный наставник | Ровный мужской/нейтральный, уверенный, не пугающий |

Скопируйте **Voice ID** (UUID) каждого в env — три **разных** id.

---

## 2. Локально → VPS (рекомендуется — без зависаний в чате)

```bash
cp secrets/elevenlabs.env.example secrets/elevenlabs.local.env
# заполнить 4 поля в редакторе

./scripts/apply_elevenlabs_from_local_file.sh
```

Один скрипт: configure + verify + TTS probe + prewarm (~30–60 с).

**Быстрая проверка без ключей** (~4 с):

```bash
./scripts/companion_voice_quick_check.sh
```

Альтернатива через `export` в shell:

```bash
export ELEVENLABS_API_KEY="sk_..."
export ELEVENLABS_VOICE_UNICORN="..." ELEVENLABS_VOICE_GENIE="..." ELEVENLABS_VOICE_ALADDIN="..."
./scripts/configure_companion_neuro_tts_env.sh root 149.154.65.180 ~/.ssh/aladdin_server
```

Скрипт `configure_*` **не примет** конфиг без всех трёх id.

---

## 3. Пилот 03 (после 04)

```bash
export PREMIUM_TOKEN="$(./scripts/mint_premium_companion_jwt.sh)"
curl -sS -X POST https://aladdin-ai.ru/api/ai/companion/tts \
  -H "Authorization: Bearer $PREMIUM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Привет! Я джин.","character_id":"genie","locale":"ru"}' | jq '{provider,cached,audio_len:(.audio_base64|length)}'

./scripts/prewarm_companion_tts_cache.sh https://aladdin-ai.ru
```

Повторите с `character_id`: `unicorn`, `aladdin` — должны звучать **по-разному**.

---

## 4. Free / Trial

Без Premium — только **AVSpeech** (Katya / Yuri / Milena на iOS). Картинки героев одинаковые на всех тарифах.
