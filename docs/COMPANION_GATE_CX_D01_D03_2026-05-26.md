# GATE-CX — D01–D03 (авто-прогон 2026-05-26)

**Скоуп:** классификация domain/mood + emotion на BE (без устройства).  
**Ручной UI / TestFlight:** ☐ в конце спринта.

---

## Команды

```bash
cd ALADDIN_NEW/mobile_apps/ALADDIN_iOS
PYTHONPATH=. python3 Tests/test_companion_intent_emotion_cx.py -v
PYTHONPATH=. python3 Tests/test_companion_persona_not_security_only.py -v
```

---

## D01 — Ребёнок шутит

| Поле | Ожидание | Авто |
|------|----------|------|
| Фраза | «Расскажи смешную историю про единорога!» | ✅ fixture |
| `mood` | `playful` | ✅ |
| `intent_id` | `companion_humor` | ✅ |
| `emotion` | `playful` | ✅ |
| Текст LLM с юмором | PG-шутка, не VPN | ☐ device / prod eyeball |

---

## D02 — Подросток одинок

| Поле | Ожидание | Авто |
|------|----------|------|
| Фраза | «Мне 14, в классе никто не разговаривает, одиноко» | ✅ |
| `domain` | `loneliness` | ✅ |
| `domain` ≠ `safety` | да | ✅ |
| `emotion` | `comfort` или `sad` | ✅ |
| Эмпатия в тексте | без лекции VPN | ☐ device |

---

## D03 — 60+ скучает

| Поле | Ожидание | Авто |
|------|----------|------|
| Фраза | «Мне 68, дома одна, скучно, некому поговорить» | ✅ |
| `domain` | `loneliness` | ✅ |
| `mood` | `lonely` / `nostalgic` | ✅ |
| `emotion` | `comfort` / `nostalgic` | ✅ |
| Тёплый тон в ответе | ☐ device (senior JWT) |

---

## Prod API (после deploy)

`POST /api/ai/companion/chat` → в JSON:

- `companion_domain`
- `companion_mood`
- `emotion` (расширенный enum)

---

## Вердикт

**GATE-CX (авто): PASS** — D01–D03 routing/emotion.  
**GATE-CX (полный):** открыт до device QA + D04–D10.
