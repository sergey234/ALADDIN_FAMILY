# WAVE3 · C3 — черновик заявки Apple NE Content Filter / DNS Proxy

**ID:** `cap-C3` · **Дата:** 2026-10-17  
**Account Holder** · team **B3WGHSWL79** · app **ai.aladdin**  
**ADR:** [`WAVE3_F1_NE_FILTER_ADR_RU.md`](WAVE3_F1_NE_FILTER_ADR_RU.md) · MASTER §7 / §9

---

## Канон продукта

| Да | Нет |
|----|-----|
| Parental **Content Filter** (system-wide blocklist/allow) | **Packet Tunnel VPN** |
| Опционально DNS Proxy как второй App ID | In-app VPN / Happ clone в iOS |
| Честный UI: Safari Content Blocker vs «все приложения» | Обещание VPN в ASO |

Обычный Safari Content Blocker **уже можно** без этой формы. C3 нужен только для **системного** фильтра вне Safari.

---

## Suggested answers (EN)

| Field | Draft |
|-------|--------|
| App / Bundle | ALADDIN / `ai.aladdin` (+ future appex e.g. `ai.aladdin.ContentFilter`) |
| Extension type | **Content Filter** (NEFilterDataProvider / Control) — primary |
| Optional second | DNS Proxy — only if Filter path blocked by Apple/tech |
| Purpose | Parent-configured web/domain rules for family safety on the child’s supervised device |
| Explicit exclusion | We do **not** request Packet Tunnel. VPN connectivity stays with the user’s existing client (Happ). |
| Data | Rules from parental API / App Group; no traffic interception for ads or analytics |
| User control | Parent enables; child device shows system filter permission; can disable in Settings |

### Short paragraph for form

```text
ALADDIN is a family safety app. We request a Network Extension Content Filter
so parents can apply domain/app web rules beyond Safari (system-wide parental
filtering). We explicitly do not request Packet Tunnel VPN. VPN remains via
the user’s existing client. Filter rules come from parent settings only and
are not used for advertising or tracking.
```

---

## После Assigned → `cap-C4` → `cap-F2`…`F4`

До Assigned: `AppStoreBuildPolicy.allowsSystemContentFilter = false` (уже).

## Чеклист владельца

- [ ] Форма Content Filter отправлена  
- [ ] DNS Proxy — только если решите вариант B из F1  
- [ ] В форме явно: **not Packet Tunnel**  
