# B-COPY-04 — App Store Review Notes (per domain)

**Дата:** 2026-06-11 · **Для:** App Store Connect → Review Notes · **Test account:** предоставить demo family + JWT device.

---

## Reviewer quick path (L3 demo)

1. Register device → JWT via `POST /api/auth/register-device`
2. **Antifake Hub** (Premium): text check «переведите деньги срочно» → verdict card
3. **Privacy Hub**: dark web scan CTA → real API (not mock)
4. **Identity Hub**: SNILS detect tab → `SecurityVerdict` card
5. **Device Hub**: malware quick scan → EICAR optional in DEBUG only
6. **Family**: parental monitoring modal → export PDF (B6)
7. **Network Protection → Emergency**: Roadside sheet + Crash settings (B7)
8. **Elderly** (Family+ role): blood pressure empty state → API sync

---

## Domain notes for Apple reviewer

### Parental / Family
- Family data uses anonymous labels; parental bypass has **no mock** in production (`prod-no-mock-bypass` policy).
- Screen Time / Family Controls integration documented in app help.

### Anti-fake / Deepfakes
- Premium feature; free tier gets 403 with `premium_required`.
- **Async processing (R-19 copy aligned):** audio/video checks run as background jobs — polling may take **up to several minutes** (not instant). Reviewer path: submit sample → wait for verdict card. Terms: `terms_section_network_protection_content_6` RU/EN.
- Text/URL checks are typically faster (seconds).
- FAQ `faq_deepfake` / `faq_fake_voices` — no «blocks calls» claim; warns and analyzes.

### VPN / Network Protection
- Optional component; integrated in app Network Protection hub.
- **B7-04 VPN prod smoke 10/10 PASS** (2026-06-11). Privacy copy: **5+ servers** (not exact pool count until VPS audit).
- Emergency: Crash detection + Roadside — **not a substitute for 112**; false positives possible (`terms_section_network_protection_content_7`).

### Health (Elderly)
- Blood pressure is user-entered wellness data, not medical device claim.
- Disclaimer: not a substitute for professional medical advice.

### AI Assistant
- FAQ fallback local; cloud AI optional. No medical/legal advice.

---

## Backend for review

- API: `https://aladdin-ai.ru` (not raw :8002 from outside)
- Health: `GET /api/health`
- Security smokes: `test_security_prod_smoke.py` pass on VPS

---

## Known limitations (honest)

| Item | Status |
|------|--------|
| 138/138 TestFlight L3 | B-QA-02 pending (after R-19 ✅) |
| VPN prod smoke 10/10 | ✅ B7-04 PASS |
| R-19 marketing copy RU/EN | ✅ COPY-POST-L3 |
| af-3 async workers Redis | video may take several minutes |
| eld-03 voice wellness | deferred |

---

## PASS B-COPY-04 + R-19

- [x] Review notes draft ready for paste into App Store Connect
- [x] Async antifake + emergency disclaimers (R-19)
- [ ] Final paste at Archive time (B-QA-02)
