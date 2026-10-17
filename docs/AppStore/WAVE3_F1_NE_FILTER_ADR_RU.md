# WAVE3 · F1 — ADR: Content Filter vs DNS Proxy (без VPN)

**ID:** `cap-F1` · **Статус:** Accepted (пилот 2026-10-17)  
**Связка:** форма [`WAVE3_C3_NE_CONTENT_FILTER_FORM_DRAFT_RU.md`](WAVE3_C3_NE_CONTENT_FILTER_FORM_DRAFT_RU.md) · MASTER §7

---

## Решение

1. **Primary:** Network Extension **Content Filter** (`NEFilterDataProvider` + Control).  
2. **Secondary (optional):** DNS Proxy — отдельный App ID, только если Filter не проходит Review/технику.  
3. **Keep:** Safari Content Blocker (уже есть) — честный UI «только Safari».  
4. **Forbidden in WAVE3:** `NEPacketTunnelProvider` / `packet-tunnel-provider` / in-app VPN.

---

## Сравнение

| Вариант | Плюс | Минус | WAVE3 |
|---------|------|-------|-------|
| A. Content Filter | Блок URL/host per flow; claim «вне Safari» | Сложнее Review + profiles | **GO primary** |
| B. DNS Proxy | Проще семантика доменов | DoH/DoT edge; не весь трафик | опция |
| C. Safari CB only | Без заявки NE | Только Safari | already ship |

---

## Архитектура (после C3 Assigned)

```text
Parent UI (Parental)
  → rules JSON (allow/block hosts) → MAIN :8002 parental API
  → child App Group (ai.aladdin.*)
NEFilterDataProvider
  → read App Group rules → verdict allow/drop
UI honesty (cap-F3)
  → «Safari» vs «Все приложения (системный фильтр)»
```

**App Group:** тот же family group, что Screen Time / Shield.  
**Flag:** `AppStoreBuildPolicy.allowsSystemContentFilter` — false до Assigned+GO.  
**CI:** profiles как ST (`cap-F4`) — не начинать до Assigned.

---

## DoD F1

| Критерий | Статус |
|----------|--------|
| ADR записан | ✅ |
| Packet Tunnel запрещён в плане + verify | ✅ (script) |
| Target Filter ещё не создан | ⏳ после C3 Assigned (`cap-F2`) |
