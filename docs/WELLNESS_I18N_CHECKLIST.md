# Wellness — чеклист локализации (i18n)

> **Версия:** 1.0 | **Связанный план:** [WELLNESS_PLATFORM_MASTER_PLAN.md](./WELLNESS_PLATFORM_MASTER_PLAN.md) §18  
> **Репозиторий iOS:** `ALADDIN_NEW/mobile_apps/ALADDIN_iOS`  
> **Launch:** ru + en (P0) | **TODO:** p18-01 … p18-15, p1-14

---

## 1. Правила именования

| Правило | Пример |
|---------|--------|
| Префикс | `wellness_` (UI), `wellness_error_` (ошибки) |
| Child / teen | суффикс `_child`, `_teen` где текст проще |
| Не использовать в UI | psychotherapist, cure, diagnose, лечение |
| Плейсхолдеры | `%@`, `%d` — как в `companion_*` |
| Файл iOS | `Core/Localization/LocalizationManager.swift` (ru + en блоки) |
| Backend | `security/services/ai_platform/wellness_i18n/ru.json`, `en.json` |
| Push | `wellness_i18n/push_ru.json`, `push_en.json` |

**Статус в таблицах:** ☐ — не внедрено | ☑ — готово (отмечать при реализации)

---

## 2. Навигация и вход

| Key | RU (черновик) | EN (черновик) | Фаза | ☐ |
|-----|---------------|---------------|------|---|
| `nav_screen_wellness_hub` | Настроение и поддержка | Mood & support | 1 | ☑ |
| `nav_screen_wellness_checkin` | Как ты? | How are you? | 1 | ☑ |
| `nav_screen_wellness_timeline` | Мой прогресс | My progress | 2 | ☑ |
| `nav_screen_wellness_assessment` | Проверить себя | Check-in with yourself | 2 | ☑ |
| `nav_screen_wellness_dreams` | Дневник снов | Dream journal | 2 | ☑ |
| `nav_screen_wellness_together` | Вместе | Together | 2 | ☑ |
| `nav_screen_wellness_family` | Семья | Family | 2 | ☑ |
| `nav_screen_wellness_trust` | Безопасность и поддержка | Safety & how we work | 1 | ☑ |
| `wellness_chip_mood` | Настроение | Mood | 1 | ☑ |
| `wellness_entry_from_companion` | Открыть поддержку | Open wellness | 1 | ☑ |

---

## 3. Четыре столпа — Wellness Hub

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_hub_title` | Эмоциональная поддержка | Emotional support | 1 | ☑ |
| `wellness_hub_subtitle` | Выбери, с чего начать сегодня | Choose where to start today | 1 | ☑ |
| `wellness_pillar_cognitive_title` | Разобрать мысли | Untangle your thoughts | 1 | ☑ |
| `wellness_pillar_cognitive_subtitle` | Когда крутятся тревожные мысли | When anxious thoughts keep spinning | 1 | ☑ |
| `wellness_pillar_behavioral_title` | Маленькие шаги | Small steps | 1 | ☑ |
| `wellness_pillar_behavioral_subtitle` | Одна привычка или действие сегодня | One habit or action today | 1 | ☑ |
| `wellness_pillar_humanistic_title` | Принять себя | Accept yourself | 1 | ☑ |
| `wellness_pillar_humanistic_subtitle` | Просто побыть рядом, без оценок | Just be here, no judgment | 1 | ☑ |
| `wellness_pillar_jung_title` | Понять себя | Understand yourself | 1 | ☑ |
| `wellness_pillar_jung_subtitle` | Сны, символы, смысл — без ярлыков | Dreams, symbols, meaning — no labels | 1 | ☑ |
| `wellness_pillar_suggested_banner` | Рекомендуем сейчас: %@ | Suggested now: %@ | 2 | ☑ |
| `wellness_hub_child_hint` | Для тебя доступны: принять себя и маленькие шаги | For you: accept yourself & small steps | 1 | ☑ |

---

## 4. Consent и Trust Center

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_consent_title` | Эмоциональная поддержка | Emotional support | 0 | ☑ |
| `wellness_consent_body` | ALADDIN — цифровой друг для самопомощи. Это не медицинский сервис и не заменяет психолога или врача. Опросники — скрининг, не диагноз. | ALADDIN is a digital friend for self-help. Not medical care and not a replacement for a therapist or doctor. Screenings are not a diagnosis. | 0 | ☑ |
| `wellness_consent_jung_note` | «Понять себя» и сны — метафоры для размышления, не предсказания. | «Understand yourself» and dreams are metaphors for reflection, not predictions. | 0 | ☑ |
| `wellness_consent_accept` | Понятно, продолжить | Got it, continue | 0 | ☑ |
| `wellness_consent_decline` | Не сейчас | Not now | 0 | ☑ |
| `wellness_trust_title` | Как мы работаем | How we work | 1 | ☑ |
| `wellness_trust_data_stored` | Что сохраняем | What we save | 1 | ☑ |
| `wellness_trust_data_not_stored` | Что не сохраняем | What we don't save | 1 | ☑ |
| `wellness_trust_escalation_title` | Уровни поддержки | Support levels | 1 | ☑ |
| `wellness_trust_escalation_l0` | Самопомощь — упражнения и чат | Self-help — exercises and chat | 1 | ☑ |
| `wellness_trust_escalation_l1` | Наблюдение — опросники и прогресс | Monitoring — screenings and progress | 1 | ☑ |
| `wellness_trust_escalation_l2` | Рекомендуем специалиста | We suggest a professional | 1 | ☑ |
| `wellness_trust_escalation_l3` | Кризис — 112 и взрослый | Crisis — 112 and a trusted adult | 1 | ☑ |
| `wellness_trust_crisis_no_chat_log` | Родитель не видит текст ваших сообщений | Parents don't see your message text | 1 | ☑ |

---

## 5. Check-in («Как ты?»)

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_checkin_title` | Как ты себя чувствуешь? | How are you feeling? | 1 | ☑ |
| `wellness_checkin_subtitle` | Это займёт несколько секунд | Takes a few seconds | 1 | ☑ |
| `wellness_mood_great` | Хорошо | Great | 1 | ☑ |
| `wellness_mood_ok` | Нормально | OK | 1 | ☑ |
| `wellness_mood_sad` | Грустно | Sad | 1 | ☑ |
| `wellness_mood_anxious` | Тревожно | Anxious | 1 | ☑ |
| `wellness_mood_tired` | Устал(а) | Tired | 1 | ☑ |
| `wellness_sleep_label` | Как спал(а)? | How did you sleep? | 1 | ☑ |
| `wellness_sleep_hours` | %@ ч | %@ h | 1 | ☑ |
| `wellness_stress_label` | Уровень стресса | Stress level | 1 | ☑ |
| `wellness_stress_low` | Низкий | Low | 1 | ☑ |
| `wellness_stress_high` | Высокий | High | 1 | ☑ |
| `wellness_checkin_save` | Сохранить | Save | 1 | ☑ |
| `wellness_checkin_talk_after` | Поговорить с другом | Talk to your friend | 1 | ☑ |
| `wellness_checkin_offline_saved` | Сохранено offline — отправим позже | Saved offline — will sync later | 2 | ☑ |

---

## 6. Опросники (UI + backend JSON)

### 6.1 UI (LocalizationManager)

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_assessment_hub_title` | Проверить себя | Check in with yourself | 2 | ☐ |
| `wellness_assessment_phq_lite_title` | Короткий опрос (5 вопросов) | Short check (5 questions) | 1 | ☐ |
| `wellness_assessment_phq9_title` | Настроение (PHQ-9) | Mood (PHQ-9) | 2 | ☐ |
| `wellness_assessment_gad7_title` | Тревога (GAD-7) | Anxiety (GAD-7) | 2 | ☐ |
| `wellness_assessment_burnout_title` | Выгорание (короткий) | Burnout (short) | 2 | ☐ |
| `wellness_assessment_disclaimer` | Это скрининг, не диагноз. | This is a screening, not a diagnosis. | 1 | ☐ |
| `wellness_assessment_result_mild` | Лёгкие признаки — можно продолжить самопомощь | Mild signs — self-help may help | 2 | ☐ |
| `wellness_assessment_result_moderate` | Рекомендуем поговорить со специалистом | Consider talking to a professional | 2 | ☐ |
| `wellness_assessment_result_severe` | Важно обратиться к специалисту | Please reach out to a professional | 2 | ☐ |
| `wellness_assessment_answer_never` | Совсем нет | Not at all | 1 | ☐ |
| `wellness_assessment_answer_severaldays` | Несколько дней | Several days | 1 | ☐ |
| `wellness_assessment_answer_morehalf` | Больше половины дней | More than half the days | 1 | ☐ |
| `wellness_assessment_answer_daily` | Почти каждый день | Nearly every day | 1 | ☐ |
| `wellness_assessment_next` | Далее | Next | 1 | ☐ |
| `wellness_assessment_finish` | Готово | Done | 1 | ☐ |
| `wellness_assessment_blocked_child` | Этот опросник доступен с 13 лет | This screening is for age 13+ | 1 | ☐ |

### 6.2 Backend JSON (`wellness_i18n/{locale}/assessments.json`)

| JSON id | Описание | Фаза | ☐ |
|---------|----------|------|---|
| `phq9_lite.q1` … `q5` | 5 вопросов PHQ-lite | 1 | ☑ |
| `phq9.q1` … `q9` | Полный PHQ-9 (валидированный перевод) | 2 | ☐ |
| `gad7.q1` … `q7` | GAD-7 | 2 | ☐ |
| `mbi_burnout.q1` … `q5` | MBI-lite burnout | 2 | ☐ |

---

## 7. Упражнения (UI + backend steps)

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_exercise_title` | Упражнение | Exercise | 2 | ☐ |
| `wellness_exercise_thought_record_title` | Разобрать мысль | Examine a thought | 2 | ☐ |
| `wellness_exercise_step_situation` | Что произошло? | What happened? | 2 | ☐ |
| `wellness_exercise_step_thought` | Какая мысль? | What thought came up? | 2 | ☐ |
| `wellness_exercise_step_emotion` | Что почувствовал(а)? | What did you feel? | 2 | ☐ |
| `wellness_exercise_step_evidence_for` | Факты «за» | Facts «for» | 2 | ☐ |
| `wellness_exercise_step_evidence_against` | Факты «против» | Facts «against» | 2 | ☐ |
| `wellness_exercise_step_reframe` | Более сбалансированный взгляд | A more balanced view | 2 | ☐ |
| `wellness_exercise_step_action` | Один маленький шаг | One small step | 2 | ☐ |
| `wellness_exercise_grounding_title` | Заземление 5-4-3-2-1 | Grounding 5-4-3-2-1 | 2 | ☐ |
| `wellness_exercise_breathing_title` | Спокойное дыхание | Calm breathing | 2 | ☐ |
| `wellness_exercise_stop_title` | Пауза STOP | STOP pause | 2 | ☐ |
| `wellness_exercise_complete` | Молодец, шаг сделан | Nice — step done | 2 | ☐ |

Backend: `exercises.json` — полные тексты шагов по `exercise_type`. ☑ `wellness_i18n/exercises/*_v1.json` (p18-08)

---

## 8. «Понять себя» — reflective sub-modes

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_deep_explore_title` | Глубокое исследование | Deep exploration | 2 | ☑ |
| `wellness_deep_explore_subtitle` | Важнее понять, чем исправить | Understanding matters more than fixing | 2 | ☑ |
| `wellness_mode_presence` | Просто побудь рядом | Just stay with me | 2 | ☑ |
| `wellness_mode_deep` | Разбери глубоко | Explore deeply | 2 | ☑ |
| `wellness_mode_structured` | Взгляд со стороны | Outside view | 2 | ☑ |
| `wellness_mode_blind_spots` | Слепые зоны | Blind spots | 2 | ☑ |
| `wellness_mode_one_question` | Только вопрос | One question only | 2 | ☑ |
| `wellness_insight_understood` | Что я понял(а) | What I understood | 2 | ☑ |
| `wellness_insight_observe` | Что понаблюдать | What to watch | 2 | ☑ |
| `wellness_insight_step` | Следующий шаг | Next step | 2 | ☑ |
| `wellness_recap_prefix` | В прошлый раз: %@ | Last time: %@ | 2 | ☑ |

---

## 9. Дневник снов (Jung)

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_dream_title` | Дневник снов | Dream journal | 2 | ☑ |
| `wellness_dream_prompt` | Опиши сон своими словами | Describe your dream in your words | 2 | ☑ |
| `wellness_dream_reflect_hint` | Символы — только как метафоры, не «приговор» | Symbols are metaphors only, not verdicts | 2 | ☑ |
| `wellness_dream_save` | Сохранить | Save | 2 | ☑ |
| `wellness_dream_blocked_child` | Дневник снов — с 13 лет | Dream journal — age 13+ | 2 | ☑ |
| `wellness_archetype_card_title` | Образ дня | Image of the day | 2 | ☑ |

---

## 10. Timeline и прогресс

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_timeline_title` | Мой прогресс | My progress | 2 | ☑ |
| `wellness_timeline_mood_chart` | Настроение | Mood | 2 | ☑ |
| `wellness_timeline_insights` | Инсайты | Insights | 2 | ☑ |
| `wellness_streak_days` | %d дней подряд | %d days in a row | 2 | ☑ |
| `wellness_badge_first_insight` | Первый инсайт | First insight | 2 | ☑ |
| `wellness_weekly_meaning_title` | 10 минут понять себя | 10 minutes to understand yourself | 2 | ☑ |
| `wellness_weekly_meaning_body` | Раз в неделю — время для смысла | Once a week — time for meaning | 2 | ☑ |

---

## 11. Outcome 24h и Referral

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_outcome_title` | Стало легче? | Feeling any better? | 2 | ☑ |
| `wellness_outcome_better` | Легче | Better | 2 | ☑ |
| `wellness_outcome_same` | Так же | Same | 2 | ☑ |
| `wellness_outcome_worse` | Тяжелее | Worse | 2 | ☑ |
| `wellness_outcome_thanks` | Спасибо, учтём | Thanks, we'll adjust | 2 | ☑ |
| `wellness_referral_title` | Помощь рядом | Help nearby | 2 | ☑ |
| `wellness_referral_112` | Экстренная помощь: 112 | Emergency: 112 | 1 | ☑ |
| `wellness_referral_helpline_ru` | Телефон доверия: 8-800-2000-122 | Helpline: 8-800-2000-122 | 0 | ☑ |
| `wellness_referral_specialist` | Рекомендуем очного специалиста | We recommend an in-person professional | 2 | ☑ |
| `wellness_referral_call` | Позвонить | Call | 2 | ☑ |

Backend: `referral_v1.json ☑` — номера и описания по региону.

---

## 12. Together Mode и Family

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_together_title` | Вместе | Together | 2 | ☑ |
| `wellness_together_parent_intro` | 3 минуты спокойного дыхания с ребёнком | 3 minutes of calm breathing with your child | 2 | ☑ |
| `wellness_together_child_intro` | Дышим вместе с взрослым | Breathing together with an adult | 2 | ☑ |
| `wellness_together_start` | Начать | Start | 2 | ☑ |
| `wellness_together_done` | Готово | Done | 2 | ☑ |
| `wellness_family_dashboard_title` | Семья | Family | 2 | ☑ |
| `wellness_family_mood_trend_down` | Настроение ↓ %d дн. | Mood ↓ %d days | 2 | ☑ |
| `wellness_family_theme_school` | Школа | School | 2 | ☑ |
| `wellness_family_theme_friends` | Друзья | Friends | 2 | ☑ |
| `wellness_family_theme_anxiety` | Тревога | Anxiety | 2 | ☑ |
| `wellness_family_no_transcript` | Без текста сообщений | No message text shown | 2 | ☑ |
| `wellness_teen_privacy_title` | Что видит родитель | What parent sees | 1 | ☑ |
| `wellness_teen_privacy_crisis_only` | Только кризис | Crisis only | 1 | ☑ |
| `wellness_teen_privacy_summary` | Сводка настроения | Mood summary | 1 | ☑ |
| `wellness_teen_privacy_none` | Ничего | Nothing | 1 | ☑ |
| `wellness_parent_playbook_title` | Как поговорить | How to talk | 3 | ☑ |
| `wellness_parent_playbook_subtitle` | Мягкие фразы — без чтения чата | Gentle phrases — without reading chat | 3 | ☑ |

---

## 13. Настройки и Premium

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_settings_title` | Настройки поддержки | Support settings | 1 | ☑ |
| `wellness_settings_reminder` | Напоминание вечером | Evening reminder | 2 | ☑ |
| `wellness_settings_reminder_time` | В %@ | At %@ | 2 | ☑ |
| `wellness_settings_export` | Выгрузить мой прогресс | Export my progress | 3 | ☑ |
| `wellness_settings_delete_data` | Удалить данные поддержки | Delete wellness data | 3 | ☑ |
| `wellness_premium_title` | Расширенная поддержка | Extended support | 3 | ☑ |
| `wellness_premium_body` | Полный timeline, все опросники, пакеты упражнений | Full timeline, all screenings, exercise packs | 3 | ☑ |

---

## 14. Чат Companion — suggested_actions

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_action_start_thought_record` | Разобрать мысль | Examine a thought | 2 | ☐ |
| `wellness_action_start_breathing` | Подышать | Breathe | 2 | ☐ |
| `wellness_action_start_grounding` | Заземление | Grounding | 2 | ☐ |
| `wellness_action_open_checkin` | Отметить настроение | Log mood | 1 | ☑ |
| `wellness_action_open_assessment` | Короткий опрос | Short screening | 1 | ☑ |
| `wellness_action_open_deep` | Глубокое исследование | Deep exploration | 2 | ☐ |
| `wellness_action_switch_pillar` | Попробовать: %@ | Try: %@ | 2 | ☐ |
| `wellness_fatigue_suggest` | Давай попробуем другой способ | Let's try another way | 2 | ☐ |

---

## 15. Push-уведомления (`wellness_i18n/push_*.json`)

| JSON id | RU | EN | Фаза | ☐ |
|---------|----|----|------|---|
| `push.checkin_evening` | Как прошёл день? | How was your day? | 2 | ☑ |
| `push.nudge_idle_2d` | Давно не заходил(а) — всё ок? | Haven't checked in — all OK? | 2 | ☑ |
| `push.outcome_24h` | Стало ли легче после вчерашнего разговора? | Feeling better after yesterday? | 2 | ☑ |
| `push.weekly_meaning` | 10 минут понять себя — когда удобно | 10 min for yourself — when ready | 2 | ☑ |
| `push.parent_digest` | Сводка по семье за неделю | Weekly family summary | 2 | ☑ |
| `push.phq_suggest` | Можем коротко проверить настроение | Quick mood check available | 1 | ☑ |

---

## 16. Widget

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_widget_title` | Как ты? | How are you? | 3 | ☑ |
| `wellness_widget_tap` | Нажми, чтобы отметить | Tap to log | 3 | ☑ |

---

## 17. Ошибки (`wellness_error_*`)

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_error_disabled` | Поддержка выключена родителем | Support turned off by parent | 1 | ☑ |
| `wellness_error_consent_required` | Нужно принять правила | Please accept the terms first | 1 | ☑ |
| `wellness_error_age_blocked` | Недоступно для твоего возраста | Not available for your age | 1 | ☑ |
| `wellness_error_network` | Нет сети — сохраним позже | Offline — saved for later | 2 | ☑ |
| `wellness_error_generic` | Не получилось — попробуй ещё раз | Something went wrong — try again | 1 | ☑ |

---

## 18. Кризис (sync с `companion_ethics`)

| Key | RU | EN | Фаза | ☐ |
|-----|----|----|------|---|
| `wellness_crisis_message` | Мне жаль, что тебе так тяжело. Ты не один(одна). Расскажи взрослому, которому доверяешь, или позвони 112. | I'm sorry it's so hard. You're not alone. Tell a trusted adult or call 112. | 1 | ☑ |
| `wellness_crisis_deep_blocked` | Сейчас важнее поддержка живого человека | A real person matters most right now | 2 | ☑ |

> Текст кризиса должен совпадать по смыслу с `companion_ethics.py` L3.

---

## 19. Глоссарий (запрещённые / предпочтительные термины)

| ❌ Не в UI | ✅ В UI |
|-----------|---------|
| психотерапевт | цифровой друг / emotional support |
| лечит депрессию | поддержка / self-help |
| диагноз | скрининг |
| EMDR / проработка травмы | обратиться к специалисту |
| предсказание сна | метафора / размышление |

Файл: `docs/WELLNESS_I18N_GLOSSARY.md` (создать в p18-01).

---

## 20. QA перед релизом

```bash
# После внедрения ключей (p18-12): ☑
python3 scripts/check_wellness_l10n.py
```

- [x] Все ключи §2–§17 есть в ru **и** en — `check_wellness_l10n.py` 297 keys (2026-06-01)
- [x] Нет ключей из §19 в пользовательских строках — glossary gate + pytest i18n
- [ ] Hub cards: EN не обрезает subtitle (iPhone SE) — **PO visual QA на устройстве**
- [ ] PHQ/GAD: сверка с валидированным переводом — **PO/clinical sign-off**
- [x] Child strings проще adult (§18.3 `_child`) — p18-14 `WellnessAgeL10n` + `check_wellness_l10n.py` age gate

---

## 21. Связь с TODO

| Задача | Этот документ |
|--------|----------------|
| p18-01 | §19 этого файла → отдельный `WELLNESS_I18N_GLOSSARY.md` (термины) |
| p18-02 | §4 |
| p18-03 | §2–§13 (LocalizationManager) |
| p18-04 | §6.2, §7 backend |
| p18-05 | API locale (все endpoints) |
| p18-06 | §14, §18 |
| p18-07–15 | соответствующие § |

**Итого ключей iOS (план):** ~**120** `wellness_*` + backend JSON + push.

---

*Чеклист v1.0 — отмечайте ☑ по мере внедрения в LocalizationManager.swift*
