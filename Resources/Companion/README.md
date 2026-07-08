# Companion hero assets (HERO-3-07 / Variant B)

## `.riv` vs `.rev`

| | `.riv` | `.rev` |
|---|--------|--------|
| Для | **iOS runtime** | **Rive Editor** |
| Magic | `RIVE` | `RIVE` (editor backup) |
| Unicorn | `unicorn.riv` ✅ | `unicorn_golden_amp.rev` = **ART, не открывается** ❌ |

**Unicorn Editor:** облако https://editor.rive.app/file/unicorn_golden_amprev/2319314  
**Unicorn iOS:** `unicorn.riv` (strict verify PASS)

Подробно: `docs/COMPANION_UNICORN_RIVE_ML_HANDOFF_2026-06-22.md`

## Runtime (iOS bundle)

| File | Role |
|------|------|
| `unicorn.riv` | Prod runtime — Hero360, HeroSM, 13 triggers |
| `{hero}_master.png` | PNG fallback 360×480 |

## Editor (unicorn)

| File | Role |
|------|------|
| Облако 2319314 | **Единственное место для правок unicorn** |
| `aladdin_golden.rev` | Эталон формата RIVE `.rev` (открывается) |
| `unicorn_golden_amp.rev` | ART/MCP — **не Import в Rive** |

## Pipeline (unicorn prod)

1. Body PNG → `docs/assets/unicorn_body_360x480.png`
2. **Rive облако:** body PNG, Face, HeroSM, Gate A/B
3. **Export runtime** → `unicorn.riv`
4. `./scripts/companion_07_install_unicorn_export.sh`
5. `python3 scripts/companion_07_verify_unicorn_riv.py unicorn --strict-variant-b`
6. iPhone Gate D → «unicorn prod OK» → duplicate aladdin/genie

Interim (без Editor Export): `python3 scripts/companion_07_build_prod_unicorn.py` — не заменяет Gate A/B.

## Verify

```bash
cd mobile_apps/ALADDIN_iOS
python3 scripts/companion_07_verify_unicorn_riv.py unicorn --strict-variant-b
./scripts/companion_07_verify_all_riv.sh --strict-variant-b
```

## iOS

- `CompanionHeroRiveHost.swift` — Hero360, HeroSM
- Sim iOS 15: PNG fallback; QA Rive: iOS 16+
