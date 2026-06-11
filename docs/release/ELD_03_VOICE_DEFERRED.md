# eld-03 — Elderly voice wellness (deferred post-L3)

**Дата:** 2026-06-11 · **Статус:** ⏸ post-L3 · **Не блокирует** GATE-J / Archive

## Scope

| Item | Fact |
|------|------|
| `09_ElderlyInterfaceScreen.swift` | Нет voice UI stub; meds/appts/BP wired B7-03 |
| EX-VOICE (138 row 136) | Отдельный контур: `voice_control_manager` / Family+ |
| Критерий eld-03 | UI stub removed **или** documented endpoint |

## Endpoint (prod)

- `GET /api/components/configuration/voice_control_manager` — smoke в EXTENDED_138
- Elderly-specific voice wellness — **не отдельный router**; при post-L3: wire через components API или wellness hub

## Post-L3 work (когда B-QA-02 PASS)

1. Product decision: voice в Elderly screen vs global voice control
2. Если Elderly: добавить CTA + `AppConfig` path + APIService (no mock)
3. LOC keys RU/EN
4. Smoke script row в emergency или components domain

**До Archive:** документировано, код не меняем.
