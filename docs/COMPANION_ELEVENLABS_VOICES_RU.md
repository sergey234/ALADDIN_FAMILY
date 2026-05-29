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

## 2. Автоматически (рекомендуется)

```bash
# 1) Положите API key (не коммитить):
echo 'sk_ВАШ_КЛЮЧ' > secrets/elevenlabs.api_key
chmod 600 secrets/elevenlabs.api_key

# 2) Один скрипт: bootstrap 3 voice id → VPS → probe → prewarm
./scripts/voice_prem_04_03.sh
```

Скрипт `bootstrap_elevenlabs_voices.py`:
- читает библиотеку `GET /v1/voices`
- подбирает 3 разных голоса под 🦄🧞🧑 (fallback: `secrets/elevenlabs.recommended-voices.env`)
- проверяет RU TTS probe на ElevenLabs
- пишет `secrets/elevenlabs.local.env` → `apply_elevenlabs_from_local_file.sh`

**Рекомендованные premade id** (можно заменить после прослушивания):

| Герой | Voice | ID |
|-------|-------|-----|
| 🦄 unicorn | Sarah | `EXAVITQu4vr4xnSDxMaL` |
| 🧞 genie | Antoni | `ErXwobaYiN019PkySvjV` |
| 🧑 aladdin | Daniel | `onwK4e9ZLuTAKqWW03F9` |

## 2b. Вручную (локальный env)

```bash
cp secrets/elevenlabs.env.example secrets/elevenlabs.local.env
# заполнить ELEVENLABS_API_KEY + при необходимости voice id

./scripts/apply_elevenlabs_from_local_file.sh
```

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
