# Companion — neuro-TTS (ElevenLabs) env на VPS

**Связано:** [COMPANION_PREMIUM_VOICE_PLAN.md](./COMPANION_PREMIUM_VOICE_PLAN.md) · **Сравнение цен:** [COMPANION_TTS_PRICING_COMPARE.md](./COMPANION_TTS_PRICING_COMPARE.md)

---

## Включение (только Premium озвучка)

В `/opt/aladdin-backend/.env`:

```bash
FEATURE_NEURO_TTS_ENABLED=1
ELEVENLABS_API_KEY=sk_...          # не коммитить
ELEVENLABS_MODEL=eleven_flash_v2_5
COMPANION_TTS_CACHE_MAX=30

# VOICE-PREM-04 (сначала — все три, разные UUID):
ELEVENLABS_VOICE_UNICORN=<voice_id>
ELEVENLABS_VOICE_GENIE=<voice_id>
ELEVENLABS_VOICE_ALADDIN=<voice_id>
# VOICE-PREM-03 (потом): smoke / prewarm с genie — см. COMPANION_ELEVENLABS_VOICES_RU.md
```

Перезапуск:

```bash
sudo systemctl restart aladdin-backend.service
```

---

## Где взять voice_id

1. [ElevenLabs](https://elevenlabs.io) → Voices → выбрать голос для RU семейного тона  
2. Скопировать **Voice ID** (UUID) в env  
3. Пилот: один узнаваемый «джин» (живой, тёплый, без пугающего тембра)

---

## Проверка capabilities

JWT с `subscription.level=premium`:

```bash
curl -sS -H "Authorization: Bearer $PREMIUM_TOKEN" \
  https://aladdin-ai.ru/api/ai/companion/capabilities | jq '.features.companion_neuro_tts'
```

Ожидание:

```json
{
  "enabled": true,
  "ui": {
    "neuro_tts_premium": true,
    "hero_visual_tier": "all",
    "tts_provider": "elevenlabs"
  }
}
```

Free/trial: `neuro_tts_premium: false`, `tts_provider: "avspeech"`.

---

## Проверка TTS

```bash
curl -sS -X POST https://aladdin-ai.ru/api/ai/companion/tts \
  -H "Authorization: Bearer $PREMIUM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Привет! Я джин.","character_id":"genie","locale":"ru"}' \
  | jq '{provider,cached,content_type,audio_len:(.audio_base64|length)}'
```

- **403** `neuro_tts_requires_premium` — не Premium  
- **424** `neuro_tts_unconfigured` — нет ключа или voice id (не 503 — gateway иначе маскирует в 404)  
- **200** — base64 audio, iOS `CompanionNeuroTTSPlayer` проиграет

---

## Прогрев кэша (20–30 фраз)

После deploy и env:

```bash
export PREMIUM_TOKEN="..."
./scripts/prewarm_companion_tts_cache.sh https://aladdin-ai.ru
```

Фразы: `security/services/ai_platform/companion_tts_greetings.py`

---

## Deploy

```bash
./scripts/deploy_companion_p0.sh root 149.154.65.180 ~/.ssh/aladdin_server
./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru
```
