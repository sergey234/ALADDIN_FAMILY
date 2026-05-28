# Companion — App Store pack (P1-19, без Rive-скриншотов)

**Обновлено:** 2026-05-29  
**Build reference:** iOS 214+ (local)  
**Отложено после Rive:** 3 marketing-скриншота Hub с живой анимацией (см. P1-19b в master plan)

## 1. Privacy Nutrition (App Store Connect)

| Data type | Linked to user | Purpose | Notes |
|-----------|----------------|---------|-------|
| User content (chat with hero) | Yes | App functionality | Cloud AI when consent ON |
| Audio (mic) | Yes | App functionality | On-device STT; transcript to server |
| Identifiers (device/user id) | Yes | App functionality | JWT auth |
| Usage data (companion analytics) | Yes | Analytics | No PII in event payloads |

**Privacy policy URLs:** in-app `CompanionLegalScreen` → Privacy / Terms.

## 2. AI disclosure (Review Notes)

> ALADDIN Family includes optional **AI Companion** («Мир героев»): three fictional heroes (Unicorn, Aladdin, Genie) powered by cloud LLM.  
> Responses are not human. Parental consent controls access for child/teen profiles.  
> Post-LLM moderation and pre-send policy filters are enabled. No NSFW in Family app.

## 3. Parental gate

- Child/teen: `companion_access_allowed` + parental consent in Family settings  
- Legal sheet on first companion open (`CompanionLegalScreen`, ack version stored)  
- Heroes available to all age bands (PG copy); witty preset blocked for child

## 4. Screenshots checklist (no Rive required for this pack)

- [ ] Child Interface — button **«Друзья»** visible  
- [ ] Companion Home — 3 tabs (Главное / Герои / Моё)  
- [ ] Conversation — hero stage + subtitle strip + mic  
- [ ] Mine tab — trust + TTS toggle + rules  
- [ ] Child Rewards — «Мир героев» card (🦄🧑🧞)

Capture on **iPhone 6.7"** and **6.1"** simulators; RU + EN locales.

## 5. TestFlight / Review smoke

- [ ] Kids path: Child Interface → Друзья → send text message  
- [ ] Voice hold (device): mic permission → hero reply or friendly error  
- [ ] Airplane mode: cached thread + draft (P1-21)  
- [ ] Rate limit: 429 shows localized banner (P1-18)  
- [ ] No mock responses in production API (`503` instead of mock)

## 6. Metadata strings (RU primary)

**Subtitle:** Мир героев — голос и чат  
**Keywords:** дети, безопасность, AI друг, единорог, семья  
**Description bullet:** Три героя-companion с голосом и текстом; родительский контроль и правила AI.

## 7. Sign-off

| Role | Check | Date |
|------|-------|------|
| iOS | XCUITest P1-14 ✅ (CI/device ⏳) | 2026-05-29 |
| BE | pytest companion + VPS deploy | |
| PO | Copy 3 heroes all users | 2026-05-29 |
| Legal | COPPA / 152-FZ sheet in app | |
