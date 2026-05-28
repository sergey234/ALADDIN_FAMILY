# Grok → ALADDIN Platform: полная матрица реализации

**Дата:** 26 мая 2026  
**Статус:** Master traceability (источник правды для спринтов)  
**Финальный план:** [COMPANION_MASTER_PLAN_v1.md](./COMPANION_MASTER_PLAN_v1.md)  
**TODO tracker:** [COMPANION_IMPLEMENTATION_TODOS.md](./COMPANION_IMPLEMENTATION_TODOS.md)  
**Связанные документы:**
- [GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md](./GROK_COMPANION_ARCHITECTURE_FOR_ALADDIN.md)
- Код платформы: `security/services/ai_platform/`
- API: `security/api/routers/ai_platform_router.py`, `ai_companion_router.py`

---

## Легенда

| Колонка | Значение |
|---------|----------|
| **Поверхность** | `INFRA` = общий backend для всех приложений; `ALADDIN` = только семейное iOS; `ADULT` = отдельное 18+ приложение (не в бинарнике ALADDIN); `—` = не делаем |
| **Фаза** | `NOW` = закладываем API/типы сразу; `MVP` / `B` / `C` = поставка |
| **Статус** | ✅ есть · 🟡 stub · ❌ нет |
| **MVP** | P0/P1 в [Master Plan](./COMPANION_MASTER_PLAN_v1.md) |
| **Kids** | Companion UI в Kids/играх |
| **Adult** | Отдельное приложение / backend only |
| **Removed** | Не в roadmap |

**Важно:** 18+ NSFW **реализуется в INFRA + ADULT**, в ALADDIN Kids **никогда** (JWT `app_id=aladdin_family`).

### Контроль полноты плана (аудит 26.05.2026)

| Проверка | Статус |
|----------|--------|
| Все пункты Grok B–H из согласованного списка | ✅ 74 ID (+ 5 явных «не делаем») |
| Блок A (платформы) | ✅ |
| Adult app отдельно, INFRA сразу | ✅ `policy_engine`, `AppId` |
| Запись разговора | ✅ F11 = не делаем |
| ALADDIN-only (PII, parental, no mock) | ✅ блок **I** |
| Уникальное УТП (security + все агенты) | ✅ блок **J** |
| Auth JWT `app_id` / age | ✅ I1, дорожная NOW |
| Feedback, suggested actions, stream resume | ✅ B15–B17 |
| Bond decay / streak | ✅ F6, F13 |
| Операции (деплой, тесты, мониторинг) | ✅ блок **K** |

**Итого в матрице: 102 строки** (87 feature + 15 process/legal/metrics/age). План **100%**.  
**Голос:** двусторонний realtime — **P0**, не Phase B.

---

## A. Платформы и доступ

| ID | Функция Grok | Поверхность | Фаза | Backend | API / модуль | ALADDIN iOS | ADULT app | Статус |
|----|--------------|-------------|------|---------|--------------|-------------|-----------|--------|
| A1 | Web grok.com | INFRA | C | `ai_platform_router` | Admin/analytics | — | Web client TBD | ❌ |
| A2 | iOS app | ALADDIN | MVP→C | companion + assistant | existing | Companion screens | Separate repo | 🟡 |
| A3 | Android app | ADULT+ALADDIN | C | same API | JWT app_id | — | TBD | ❌ |
| A4 | X / Twitter embed | — | — | — | — | — | — | — не делаем |
| A5 | Public developer API | INFRA | B | `ai_platform_router` | `/api/ai/platform/*` | — | uses same | 🟡 |
| A6 | Tesla / telephony voice | INFRA | C | `voice_gateway` | `/api/ai/voice/*` | Phase B | Phase B | ❌ |

---

## B. Базовый чат (Grok Assistant)

| ID | Функция | Поверхность | Фаза | Backend | API | ALADDIN iOS | Статус |
|----|---------|-------------|------|---------|-----|-------------|--------|
| B1 | Текстовый диалог, любые темы | INFRA+ALADDIN | MVP | `hermes_client`, `ai_assistant_router`, `policy_engine` | `POST …/chat`, `…/companion/chat` | `AIAssistantViewModel`, Companion VM | 🟡 |
| B2 | Streaming (SSE) | INFRA | MVP | `ai_assistant_router` stream | `POST …/assistant/stream`, `…/companion/stream` | `AIStreamingService` | 🟡 |
| B3 | Fast / Reasoning / Think | INFRA | B | `ai_platform/modes.py` | `mode` in chat request | Mode picker settings | 🟡 |
| B4 | Long context 1–2M | INFRA | C | Hermes/SFM config | `max_context_tokens` per tier | — | ❌ |
| B5 | Follow-up в ветке | INFRA | MVP | `ai_history_store` | `thread_id`, `parent_message_id` | Thread UI | 🟡 |
| B6 | История / threads | INFRA | MVP | `ai_history_store` | `GET/POST …/platform/threads` | History list | 🟡 |
| B7 | Sync web↔mobile | INFRA | C | `threads` + device sync | `GET …/threads?device_id=` | iCloud optional | ❌ |
| B8 | 30+ языков | INFRA | MVP | `response_language` | already in `ChatMessageRequest` | `LocalizationManager` | ✅ |
| B9 | Custom Instructions | INFRA | B | `user_ai_profile_store` | `PUT …/platform/profile/instructions` | Settings screen | 🟡 |
| B10 | Custom Personality | INFRA | B | same | `personality_preset` | Settings | 🟡 |
| B11 | Memory on/off, delete | INFRA | B | `companion_memory_store` | `GET/DELETE …/memory` | Settings + parent gate | 🟡 |
| B12 | Workspaces / Projects | INFRA | C | `workspace_store` | `…/platform/workspaces` | Workspace sidebar | 🟡 |
| B13 | Canvas (long edit) | INFRA | C | `canvas_sessions` | `…/platform/canvas` | iPad/side panel | ❌ |
| B14 | Share public link | INFRA | C | `shared_thread_tokens` | `POST …/threads/{id}/share` | Share sheet (no child PII) | ❌ |
| B15 | Feedback (rating) | INFRA | MVP | `ai_history_store` analytics | `POST …/assistant/feedback` | Thumb up/down UI | 🟡 |
| B16 | Stream resume | INFRA | MVP | `StreamRequest.resumeFromIndex` | `POST …/assistant/stream` | reconnect UI | 🟡 |
| B17 | Suggested actions / deep links | INFRA | MVP | intent → actions | `suggested_actions[]` | deep links | 🟡 |

**Пробелы до MVP:** B6 threads API, B5 `parent_message_id`, Companion iOS screens, B16 resume polish.

---

## C. Поиск и актуальность

| ID | Функция | Поверхность | Фаза | Backend | API | Статус |
|----|---------|-------------|------|---------|-----|--------|
| C1 | Live Web Search | INFRA | B | `tools/web_search.py` | `tools: [{type: web_search}]` in Responses | ❌ |
| C2 | DeepSearch | INFRA | C | multi-step search agent | `search_depth: deep` | ❌ |
| C3 | X Search | INFRA | C | `tools/x_search.py` | optional if API key | ❌ |
| C4 | Filters (domain, date) | INFRA | B | search params schema | in tool config | ❌ |
| C5 | Citations | INFRA | B | merge citations in orchestrator | `sources[]` in response | 🟡 partial |

**Сейчас:** только KB RAG (`kb_rag_service`) — не полноценный web search.

---

## D. Мультимодальность

| ID | Функция | Поверхность | Фаза | Backend | API | ALADDIN iOS | Статус |
|----|---------|-------------|------|---------|-----|-------------|--------|
| D1 | Voice mode | INFRA+ALADDIN | B | `voice_gateway` | `WS /api/ai/voice/realtime` | `SpeechManager` + WS | 🟡 |
| D2 | Speech-to-speech WS | INFRA | B | `voice_realtime_session` | OpenAI-compatible events | Companion voice UI | ❌ |
| D3 | STT streaming | INFRA | B | `stt_stream` | `WS /api/ai/voice/stt` | mic pipeline | ❌ |
| D4 | TTS + voices | INFRA | B | `tts_service` | `POST /api/ai/voice/tts` | `AVSpeech` → server TTS | ❌ |
| D5 | Voice clone | INFRA | C | `voice_clone_store` | `POST …/voice/clone` | — | ❌ |
| D6 | Expressive tags [laugh] | INFRA | B | TTS preprocessor | in TTS request | — | ❌ |
| D7 | Camera mode | ALADDIN | C | vision + voice | multipart upload | `AVCapture` | ❌ |
| D8 | Vision (image) | INFRA | B | `vision_analyze` | `POST …/platform/vision` | PHPicker | ❌ |
| D9 | Video input | INFRA | C | `video_analyze` | `POST …/platform/video` | — | ❌ |
| D10 | PDF / files | INFRA | B | `document_ingest` | `POST …/platform/files` | Document picker | ❌ |
| D11 | Image gen (Imagine) | INFRA | C | `image_gen_service` | `POST …/platform/images/generate` | Gallery UI | ❌ |
| D12 | Video gen | INFRA | C | `video_gen_service` | `POST …/platform/video/generate` | — | ❌ |
| D13 | Batch API | INFRA | C | job queue | `POST …/platform/batch` | — | ❌ |

---

## E. Код и агенты

| ID | Функция | Поверхность | Фаза | Backend | Статус |
|----|---------|-------------|------|---------|--------|
| E1 | Code generation | INFRA | MVP | Hermes general | 🟡 |
| E2 | Debug / explain | INFRA | MVP | Hermes | 🟡 |
| E3 | Code Interpreter | INFRA | C | sandbox runner | ❌ |
| E4 | Function calling | INFRA | B | `tools/registry` | 🟡 |
| E5 | MCP tools | INFRA | C | `mcp_connector` | ❌ |
| E6 | Collections RAG | INFRA | B | extend `kb_rag_service` | 🟡 |
| E7 | Multi-agent Heavy | INFRA | B | `ai_platform/orchestrator.py` | 🟡 stub |
| E8 | 4-head agent (4.20 style) | INFRA | C | orchestrator profiles | ❌ |
| E9 | Grok Build | — | — | — | — |
| E10 | Grok Computer | — | — | — | — |
| E11 | Structured JSON output | INFRA | B | `response_format` in chat | 🟡 |

**Агенты ALADDIN server (подключить в orchestrator):**

| Agent | File | Route intent |
|-------|------|--------------|
| AI Assistant | `ai_assistant_router` | general, app_help |
| Psychological | `psychological_support_agent.py` | emotional, crisis |
| Mobile User AI | `mobile_user_ai_agent.py` | gamification, explain |
| + SFM tools | `sfm_tools_registry.py` | threat, vpn, parental |

---

## F. Companions

| ID | Функция | Поверхность | Фаза | Backend | ALADDIN | ADULT | Статус |
|----|---------|-------------|------|---------|---------|-------|--------|
| F1 | Enable companions | ALADDIN | MVP | settings flag | Settings toggle | own settings | 🟡 |
| F2 | 3D characters | ALADDIN | MVP→C | emotion hints | Aladdin/Unicorn assets | Adult personas TBD | 🟡 |
| F3 | Conversation UI | ALADDIN | MVP | companion router | `CompanionConversationScreen` | ADULT UI | ❌ |
| F4 | Voice + text | ALADDIN | B | D1+D2 | same screen | same | ❌ |
| F5 | Lip-sync + emotions | ALADDIN | B→C | `emotion`, `animation_hint` | Rive/SceneKit | same | 🟡 |
| F6 | Affection / Bond | INFRA | MVP | trust in companion router | Trust bar | Bond + adult romance policy | 🟡 |
| F7 | Unlocks (outfits) | INFRA | B | cosmetics API | Cosmetics picker | ADULT cosmetics | 🟡 |
| F8 | Character switch | ALADDIN | MVP | per-character state | Hub | ADULT hub | 🟡 |
| F9 | Good/Bad persona | ADULT | B | `persona_variant` | — | dual persona | 🟡 infra |
| F10 | NSFW toggle | ADULT only | NOW | `policy_engine` adult | **blocked** | enabled 18+ | 🟡 |
| F11 | Screenshot/share record | — | — | — | **не делаем** | — | — |
| F12 | Push re-engagement | ALADDIN | C | `companion_push_service` | ethical push | ADULT push | ❌ |
| F13 | Bond decay / streak | INFRA | B | trust decay rules | in `/companion/state` | streak UI | ❌ |
| F14 | Extra personas (roadmap) | ADULT | C | character registry | `/characters` | Mika/Chad-like TBD | ❌ |

---

## G. Подписки и лимиты

| ID | Функция | Поверхность | Фаза | Backend | Статус |
|----|---------|-------------|------|---------|--------|
| G1 | Free tier limits | INFRA | MVP | JWT `limits`, rate_limit | ✅ |
| G2 | Premium (~SuperGrok) | INFRA | MVP | subscription levels | 🟡 |
| G3 | Heavy / priority | INFRA | C | queue priority | ❌ |
| G4 | X Premium bundle | — | — | — | — |

---

## H. Developer API surface (наша платформа)

| ID | Capability | Endpoint (target) | Фаза | Статус |
|----|------------|---------------------|------|--------|
| H1 | Chat completions compat | `POST /api/ai/platform/chat` | NOW | 🟡 |
| H2 | Responses + tools | `POST /api/ai/platform/responses` | B | ❌ |
| H3 | Voice Agent WS | `WS /api/ai/voice/realtime` | B | ❌ |
| H4 | TTS / STT | `/api/ai/voice/tts`, `…/stt` | B | ❌ |
| H5 | Image / video gen | `/api/ai/platform/images`, `…/video` | C | ❌ |
| H6 | Ephemeral tokens | `POST /api/ai/voice/ephemeral-token` | NOW | 🟡 stub |
| H7 | **GET /capabilities** | `/api/ai/platform/capabilities` | P0 | 🟡 |
| H8 | **Module registry** | `modules/registry.py` | P0 | 🟡 |

---

## I. Кросс-функции платформы (обязательно для ALADDIN)

| ID | Функция | Фаза | Backend / iOS | Статус |
|----|---------|------|---------------|--------|
| I1 | JWT `app_id`, `age_verified`, `content_policy` | NOW | `app/auth` issue token | ❌ |
| I2 | PII gate перед LLM | MVP | `ai_prompt_gate`, `AIOutboundTextGate` | 🟡 |
| I3 | Prod: no mock / no sfm_fallback | MVP | `ai_response_helpers` | 🟡 |
| I4 | `ai_data_sharing` opt-in (iOS) | MVP | settings + block send | 🟡 |
| I5 | Parental consent API | MVP | `POST …/companion/consent` | 🟡 |
| I6 | Child profile (только Единорог) | MVP | policy + UI gate | ❌ |
| I7 | Локальный FAQ fallback | MVP | `UnifiedFAQCatalog` | 🟡 |
| I8 | Лимит `max_ai_messages` в JWT | MVP | subscription models | ✅ |

---

## J. Уникальное ALADDIN (сверх Grok, в плане)

| ID | Функция | Фаза | Статус |
|----|---------|------|--------|
| J1 | Security intents (threat, VPN, parental) | MVP | 🟡 intent_router |
| J2 | Все SFM/server agents в orchestrator | B | 🟡 registry |
| J3 | Интеграция gamification (единороги, награды) | B | 🟡 endpoints exist |
| J4 | Family dashboard context в prompt | B | ❌ |
| J5 | Telegram support bot (отдельный канал) | C | 🟡 router exists |

---

## K. Операции и качество

| ID | Задача | Фаза | MVP | Статус |
|----|--------|------|-----|--------|
| K1 | Деплой роутеров на VPS | P0 | ✅ | 🟡 |
| K2 | Smoke tests companion/platform | P0 | ✅ | ❌ |
| K3 | OpenAPI / контракт для Adult app | P0 | ✅ | 🟡 |
| K4 | Мониторинг latency voice/chat | P2 | — | ❌ |
| K5 | Матрица ↔ спринты | NOW | ✅ | ✅ |

---

## L. Unit economics

| ID | Требование | Фаза | MVP |
|----|------------|------|-----|
| L1 | Meters: msgs, voice_seconds, image_gen | P0 | ✅ |
| L2 | JWT limits max_ai_messages, voice_minutes_month | P0 | ✅ |
| L3 | COGS alert vs MRR | P2 | — |
| L4 | Tariff config | P1 | ✅ |
| L5 | UI warning 80% limit | P1 | ✅ |

---

## M. Legal / privacy

| ID | Требование | Фаза | MVP |
|----|------------|------|-----|
| M1 | Parent consent UI+API | P1 | ✅ |
| M2 | Memory policy text | P1 | ✅ |
| M3 | Export/delete threads+memory | P1 | ✅ |
| M4 | Store privacy labels age | P1 | ✅ |
| M5 | Legal sign-off doc | P1 | ✅ |
| M6 | Logs without raw child PII | P0 | ✅ |

---

## N. Metrics MVP

| ID | Метрика | Target |
|----|---------|--------|
| N1 | D7 retention companion | >25% |
| N2 | msgs/user/week | >8 |
| N3 | users 3+ sessions/week | >20% |
| N4 | voice session completion | >70% |
| N5 | trial→paid uplift | +10% vs control |
| N6 | policy_block rate | monitor |

---

## O. Age bands

| ID | band | UI | Персонажи | NSFW |
|----|------|-----|-----------|------|
| O1 | child | Kids | unicorn only | block |
| O2 | teen | Kids | unicorn, aladdin | PG-13 |
| O3 | parent | Family/Kids | aladdin | block |
| O4 | adult_app | Adult app | TBD | policy adult |

---

## Сводка: что предусмотрено в плане vs пробел

| Категория | Пунктов | В плане | Код сейчас (оценка) |
|-----------|---------|---------|---------------------|
| A Платформы | 6 | ✅ | 🟡 1 |
| B Чат | **17** | ✅ | 🟡 ~9, ✅ 1, ❌ 7 |
| C Поиск | 5 | ✅ | 🟡 1, ❌ 4 |
| D Мультимодальность | 13 | ✅ | 🟡 1, ❌ 12 |
| E Агенты | 11 | ✅ | 🟡 4, ❌ 5, — 2 |
| F Companion | **14** | ✅ | 🟡 7, ❌ 5, — 1 |
| G Тарифы | 4 | ✅ | ✅ 1, 🟡 2, — 1 |
| H API | 6 | ✅ | 🟡 2, ❌ 4 |
| I Кросс (ALADDIN) | 8 | ✅ | ✅ 1, 🟡 5, ❌ 2 |
| J УТП ALADDIN | 5 | ✅ | 🟡 3, ❌ 2 |
| K Ops | 5 | ✅ | 🟡 2, ❌ 3 |

**Вывод:** план **100%** для согласованного scope (87 требований). Код **~15–20%**. Не упущено из согласованного списка Grok; явно вне scope: E9, E10, A4, G4, F11.

---

## Дорожная карта

**См. [COMPANION_MASTER_PLAN_v1.md](./COMPANION_MASTER_PLAN_v1.md) §5–§7.**

| Приоритет | Срок | Содержание |
|-----------|------|------------|
| **P0** | нед 1–3 | JWT age_band, realtime voice WS, Kids companion UI, DB trust |
| **P1** | нед 4–6 | threads, memory, legal, analytics, cosmetics |
| **P2** | нед 7–14 | web search, multi-agent, vision, modes |
| **P3** | 15+ | image/video, workspaces, Android, Adult Store app |

---

## JWT / multi-app

```json
{
  "sub": "user-uuid",
  "app_id": "aladdin_family",
  "content_policy": "family_pg13",
  "age_verified": false,
  "subscription": { "level": "premium", "limits": { "max_ai_messages": 1000 } }
}
```

ADULT app:

```json
{
  "app_id": "aladdin_adult",
  "content_policy": "adult_18",
  "age_verified": true
}
```

`policy_engine` разрешает NSFW tools **только** при `app_id=aladdin_adult` + `age_verified=true`.
