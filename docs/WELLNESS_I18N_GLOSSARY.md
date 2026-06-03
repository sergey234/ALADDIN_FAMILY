# Wellness i18n — глоссарий терминов (ru / en)

> Связано: [WELLNESS_I18N_CHECKLIST.md](./WELLNESS_I18N_CHECKLIST.md) §19 | TODO **p18-01** | r100 **r100-2-14**

## Продуктовые термины (единые во всём приложении)

| RU (UI) | EN (UI) | Не использовать |
|---------|---------|-----------------|
| Цифровой друг | Digital friend | AI therapist |
| Эмоциональная поддержка | Emotional support | Therapy app |
| Самопомощь | Self-help | Treatment |
| Глубокое исследование | Deep exploration | Psychoanalysis session |
| Скрининг | Screening | Diagnosis |
| Разобрать мысли | Untangle thoughts | CBT therapy |
| Маленькие шаги | Small steps | Conditioning |
| Принять себя | Accept yourself | Humanistic therapy |
| Понять себя | Understand yourself | Jung analysis |
| Мост к близким | Bridge to people | Parent monitoring |

## Дорожка (UI) vs pillar (код) — r100-2-14

| Где | Термин | Пример |
|-----|--------|--------|
| **UI ru/en** | **дорожка** / track | «Выбери дорожку», `wellness_pillar_active` → «Активная дорожка» |
| **API / Swift / YAML** | `pillar` | `wellness_pillar`, `POST /session/pillar`, `pack.yaml` |
| **Доки внутренние** | можно «pillar (дорожка)» | не писать «столп» в user-facing текстах |
| **Запрещено в UI** | столп, КПТ, Юнг, терапия | см. `companion_ethics`, Knowledge Pack `forbidden_concepts` |

Код и контракты **не переименовываем** (`pillar` остаётся). Меняем только копирайт и l10n.

## 4 дорожки — краткие определения для копирайтеров

| UI (дорожка) | `pillar` | Смысл |
|--------------|----------|--------|
| Разобрать мысли | `cognitive` | CBT-lite: мысли, факты, тревога |
| Маленькие шаги | `behavioral` | одно действие/привычка, не мотивационные речи |
| Принять себя | `humanistic` | эмпатия, дыхание, без анализа |
| Понять себя | `jung` | сны и символы как метафоры; child — ограничения age_policy |

**Child (8–12):** в Hub только **Принять себя** + **Маленькие шаги** (`WellnessPillar.allowed(for: "child")`).

## Child / teen

| Аудитория | Тон |
|-----------|-----|
| child 8–12 | короткие фразы, без «скрининг», «тревога» → «переживаю» |
| teen 13–17 | уважительно, без морали, без «лечения» |
| parent | ясно, без мед. жаргона |
| senior | неторопливо, тёпло |

---

*Glossary v1.1 — r100-2-14 «дорожка»/pillar (2026-06-03). EN market — legal review.*
