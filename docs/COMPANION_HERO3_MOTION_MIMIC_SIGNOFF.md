# HERO-3-17 — Motion + Mimic Spec (sign-off для Figma)

**Статус:** ✅ подписано владельцем продукта **2026-05-26**  
**Figma:** https://www.figma.com/design/vwKcGPUUEZjgayEHNn0BJM — страница `00_Spec`, фрейм `Sign-off_HERO-3-17`  
**Разблокировало:** **HERO-3-02** (3×12 wireframe grid на `01`–`03`)  
**План:** [COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md](./COMPANION_HEROES_3_FIGMA_RIVE_PLAN.md) §2.2 · §2.3

**ADR (в Figma):** 12 макетов CX.4; `speaking` + `mouth_open` — Motion/Rive only, не 13-й постер в 02.

---

## Deliverables в Figma

| Путь | Содержание |
|------|------------|
| `Companion/Heroes/00_Spec/Motion` | Таймлайн listening → thinking → speaking → content; bob; `mouth_open` |
| `Companion/Heroes/00_Spec/Mimic` | L1–L5 брови/глаза/рот/щёки; **12 карточек** × 3 героя |
| `Companion/Heroes/01_Unicorn` … `03_Genie` | После sign-off — **02** |

---

## Sign-off чеклист (дизайнер)

- [x] **13 state** согласованы с §3.1 ADR (9 контент + 3 фазы + idle в Hub)
- [x] **MIMIC-Q1:** 12 контент-эмоции попарно различимы на 96pt (каждый герой)
- [x] **MOTION-Q1:** listening / thinking / speaking различимы без текста
- [x] **MOTION-Q2:** `mouth_open` 0…1 при speaking (референс для Rive input)
- [x] Genie: дым/искры только playful/speaking, **не** на sad/comfort
- [x] Aladdin-human: без дыма джина; лицо OB_01
- [x] Child policy: genie не в child-макетах Hub

**Подпись:** PO (product owner) **Дата:** 2026-05-26

---

## После sign-off

1. ~~**HERO-3-02**~~ — wireframe grid 3×12 ✅ (final faces в Rive)  
2. **HERO-3-07** — export `.riv` ×3 + `python3 scripts/companion_riv_size_gate.py`  
3. **MIMIC-Q1** скриншот-сетка на device после каждого `.riv`
