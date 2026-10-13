# План: Privacy / Terms — память звонков и запись (RU+EN)

**Дата:** 2026-10-13  
**Статус:** тексты готовы · вставка в app + landing в том же коммите/сессии  
**Связь:** `PLAN_CALLS_MEMORY_HUB_2026-10-13.md` · spike отдельно на устройстве

---

## 1. Ответ: нужна ли ещё «политика» перед записью?

Пользователь на OB_07 уже принял **Политику** и **Условия** (`onboarding_privacy_policy_accepted` / `onboarding_terms_of_service_accepted`).

| Что | Нужно перед записью? | Почему |
|-----|----------------------|--------|
| Ещё раз читать **всю** Политику | **Нет** | Уже принята при входе; повтор каждый раз = шум |
| Push «обновилась политика» перед **каждой** записью | **Нет** | Не UX и не требование Apple |
| Короткий дисклеймер + чекбокс в **Подготовить звонок** | **Да** | Это согласие на **действие** (мик, запись, предупредить собеседника), не повтор политики |
| Разрешение микрофона iOS | **Да** (системный диалог) | Apple |
| Если Политика **существенно** обновлена (п. про запись) | **Один раз** мягкий баннер «Политика обновлена» со ссылкой на новый раздел | Не блокер; версия → `2.3` |

**Итог:** доп. «уведомления по политике» перед записью **не нужны**. Нужны: пункт в Privacy/Terms + короткий UI-дисклеймер (уже есть `calls_disclaimer_*` / `calls_consent_checkbox`).

---

## 2. Куда вносить изменения (карта экранов)

### A. Приложение — Политика (`PrivacyPolicyScreen`)

| Место | Действие |
|-------|----------|
| Новый аккордеон **«Память звонков и запись»** (`PrivacyMainSection.callsMemory`) | **После** Antifake, **перед** «Заключительные» |
| Версия в шапке | `2.2` → **`2.3 \| 13 октября 2026`** |
| Ключи LocManager + `Localizable.strings` RU/EN | title, subtitle, content_1…8 |
| Раздел Antifake | **Не смешивать** — там проверка после звонка, не «пишем во время» |

### B. Приложение — Условия (`TermsOfServiceScreen`)

| Место | Действие |
|-------|----------|
| Раздел **«Ответственность»** (`liability`) | Добавить пункты **6–10** про запись / мошенников / собеседника / качество записи |

### C. Сайт — `landing/legal/`

| Файл | Действие |
|------|----------|
| `privacy.ru.html` / `privacy.en.html` | Новый блок **«Память звонков и запись»** (после Wellness / перед финалом — удобно как §19) |
| `terms.ru.html` / `terms.en.html` | В § «Ответственность» те же пункты, что в app |

### D. UI продукта (уже есть — не убирать)

| Где | Что показывает |
|-----|----------------|
| Settings → Звонки / хаб | `calls_disclaimer_short` |
| Подготовить звонок | `calls_disclaimer_full` + чекбокс `calls_consent_checkbox` |
| After-call «спокойно / деньги» | Не запись — отдельный toggle; в Terms уже «не 100% защита» |

### E. Не трогать сейчас

- Companion / wellness legal  
- Antifake «во время звонка не слушаем» (это про серверный antifake, не про локальный Диктофон) — при FAQ уточнить разницу  
- Re-onboarding всех юзеров

---

## 3. Канон текста (вставка)

### 3.1 Privacy — RU

**Заголовок:** Память звонков и запись  
**Подзаголовок:** Микрофон, локальное хранение, ваша ответственность  

1. ALADDIN **не записывает линию оператора** (не как у сотового оператора). Запись возможна только через **микрофон телефона**, если **вы сами** включили запись и обычно **громкую связь**.  
2. Запись **не начинается сама**. Нужны ваши действия в разделе «Звонки» / Диктофон.  
3. Аудио и выжимка по умолчанию хранятся **на устройстве**. На сервер — только если **вы** отправите (например, проверка antifake).  
4. Вы сами решаете, **предупреждать ли собеседника**, и соблюдаете законы своей страны о записи разговоров.  
5. Качество записи **не гарантируется**: iOS может прервать микрофон во время звонка; часть речи может не попасть в файл.  
6. Красная/зелёная кнопка после звонка — **ваш ручной сигнал семье**, не автоматическое доказательство мошенничества.  
7. ALADDIN **не несёт ответственности** за ущерб от мошенников, пропущенных угроз, сбоев записи, неправильного использования или претензий собеседника из‑за записи.  
8. Удалить записи можно в приложении или удалив приложение; срок хранения — пока вы их не удалите (локально).

### 3.2 Privacy — EN

**Title:** Call memory and recording  
**Subtitle:** Microphone, on-device storage, your responsibility  

1. ALADDIN does **not** record the carrier phone line. Capture is only via the **phone microphone** if **you** start recording (usually with speakerphone).  
2. Recording never starts by itself. You must start it in Calls / Voice Notes.  
3. Audio and summaries stay **on device** by default. Upload only if **you** send them (e.g. antifake check).  
4. You decide whether to **tell the other party** and must follow local call-recording laws.  
5. Quality is **not guaranteed**: iOS may interrupt the mic during a call.  
6. Post-call calm / money buttons are **your manual family signal**, not automatic fraud proof.  
7. ALADDIN is **not liable** for scam losses, missed threats, failed recordings, misuse, or claims from the other party about recording.  
8. Delete recordings in the app or by deleting the app; kept until you delete them (local).

### 3.3 Terms liability — доп. пункты RU

6. Запись звонков — только по вашей инициативе; вы отвечаете за согласие собеседника и законность.  
7. Мы не гарантируем полноту/качество записи и распознавания речи.  
8. Мы не несём ответственности за убытки от телефонного мошенничества и за решения, принятые по выжимке или кнопкам после звонка.  
9. Раздел «Звонки» — вспомогательный инструмент, не юридическая/банковская консультация и не услуга оператора связи.  
10. Используя запись и память звонков, вы принимаете эти ограничения.

### 3.4 Terms liability — EN

6. Call recording is only by your action; you are responsible for the other party’s consent and legality.  
7. We do not guarantee completeness or quality of recordings or speech recognition.  
8. We are not liable for phone-scam losses or decisions based on summaries or post-call safety buttons.  
9. Calls is a helper tool, not legal/banking advice or a carrier recording service.  
10. By using call recording/memory you accept these limits.

---

## 4. Что далее по плану продукта (после legal)

1. **Legal вставка** (этот документ + код/landing) — сейчас.  
2. **Переименование toggle** — владелец выбирает 1–5 («Проверка после звонка» и т.д.).  
3. **Spike на реальном iPhone** — позже; симуляторные логи не засчитываются.  
4. По spike: **green/yellow** → Фаза 3 (реальная запись в сессию); **red** → без «записи во время», только Prep + after.  
5. Унификация post-call UX (safety → memory → antifake).  
6. Мелочи UI: SF Symbol для iOS 15, `tel://` только с номером / на устройстве.  
7. Commit / push — только по GO владельца.

---

## 5. Disclaimer (не юрконсультация)

Тексты — продуктовый канон для ALADDIN. Финальный sign-off по закону РФ/юрисдикций — за владельцем / юристом при необходимости. «Не несём никакой ответственности» в UI/Terms усиливает позицию, но **не заменяет** законные пределы дисклеймера.
