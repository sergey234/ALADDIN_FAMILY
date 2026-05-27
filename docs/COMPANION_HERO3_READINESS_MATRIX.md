# HERO-3 — матрица готовности (spec / BE / iOS / .riv / QA)

**Обновлено:** 2026-05-27 · Handoff: [COMPANION_ML_HANDOFF_2026-05-27.md](./COMPANION_ML_HANDOFF_2026-05-27.md)  
**Задача:** [HERO-3-21](./COMPANION_IMPLEMENTATION_TODOS.md) · **ADR имён:** [HERO-3-20](./COMPANION_IMPLEMENTATION_TODOS.md)  
**Трекер:** [COMPANION_PROGRESS_TRACKER.md](./COMPANION_PROGRESS_TRACKER.md)

Легенда: ✅ готово · 🟡 частично · ⏳ ожидает · — не применимо

| ID | Spec (Figma/§) | BE | iOS | `.riv` | QA / test |
|----|----------------|----|-----|--------|-----------|
| **HERO-3-01** | ✅ §1–11 | — | — | — | ADR утверждён |
| **HERO-3-17** | ✅ [Motion+Mimic sign-off](./COMPANION_HERO3_MOTION_MIMIC_SIGNOFF.md) PO 26.05 | — | — | — | — |
| **HERO-3-02** | 🟡 3×12 wireframe grid (`01`–`03`) | — | — | — | final art → **07** |
| **HERO-3-03** | — | ✅ genie + age | — | — | pytest age_policy |
| **HERO-3-04** | — | ✅ Pydantic + cosmetics | — | — | verify API |
| **HERO-3-05** | ✅ §2.1 черновики | ✅ 3 persona | — | — | persona tests |
| **HERO-3-06** | — | ✅ GET /characters | ✅ Hub 3 + emoji | — | child без genie |
| **HERO-3-07** | ✅ [checklist](./COMPANION_RIVE_EXPORT_CHECKLIST.md) | — | ✅ Grok-stage UI | 🟡 3× placeholder `.riv` | art ⏳ |
| **HERO-3-08** | ✅ [unblock](./COMPANION_RIVE_UNBLOCK.md) | — | 🟡 08a compile+bundle ✅ · 08b UI ⏳ (**`CompanionHome` → `Главное`**) | 🟡 placeholder | `verify_companion_rive_ios_bundle.sh` + [08b checklist](./COMPANION_08B_DEVICE_CHECKLIST.md) |
| **HERO-3-09** | ✅ Bible §4 | — | — | — | [ALADDIN_Character_Bible](./ALADDIN_Character_Bible.md) |
| **HERO-3-10** | — | ✅ deploy 27.05 | — | — | verify PASS child=unicorn |
| **HERO-3-11** | ✅ D10 script | — | — | ⏳ | SPEECH/MOTION/MIMIC-Q |
| **HERO-3-12** | ✅ witty | ✅ preset | — | — | witty≠child |
| **HERO-3-13** | ✅ defaults | ✅ CHARACTER_DEFAULT | — | — | unit |
| **HERO-3-14** | ✅ humor | ✅ intent router | — | — | genie hint |
| **HERO-3-15** | ✅ §2.1 UI | ✅ available_presets | ✅ witty TTS | — | Family UI |
| **HERO-3-16** | — | ✅ | — | — | `test_companion_persona_speech` |
| **HERO-3-18** | ✅ §2.2 | — | ✅ timeline+debounce | — | **HERO-3-26** unit |
| **HERO-3-19** | ✅ mouth_open | — | ✅ procedural+Rive input | ⏳ SM | MOTION-Q2 |
| **HERO-3-20** | ✅ ADR §3.1 | ✅ `companion_emotions` | ✅ enum 13 | ⏳ 13 states | **HERO-3-25** sync |
| **HERO-3-21** | ✅ этот файл | — | — | — | поддерживать при каждом PR |
| **HERO-3-22** | ✅ §3.2 &lt;500KB | — | — | ✅ 3/3 gate | CI companion-gate.yml ✅ |
| **HERO-3-23** | ✅ §2.2 фазы | — | ✅ meta-on-done | — | MOTION-Q + stream |
| **HERO-3-24** | ✅ §2.3 L3 | — | ✅ suppressesPlayful | — | MIMIC-Q6 |
| **HERO-3-25** | — | ✅ | ✅ | — | pytest sync 13↔13 ✅ |
| **HERO-3-26** | — | — | ✅ debouncer | — | XCTest ✅ |

**GATE без отдельного ID:** [GATE-HERO-3-IOS-α](./COMPANION_FINAL_PLAN_AND_VERIFICATION.md) · [GATE-EMO-EMPATHY](./COMPANION_FINAL_PLAN_AND_VERIFICATION.md)
