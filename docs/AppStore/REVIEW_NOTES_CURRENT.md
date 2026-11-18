# Review Notes — текущий канон (ALADDIN AI)

**Обновлено:** 2026-11-10  
**App:** `ai.aladdin` · Team **B3WGHSWL79** · Version **1.0.2** · Build **20**  
**Статус:** candidate **20** (локально, push по GO) · train ASC **1.0.2**.

## Что в build 20 (код)

| Тема | Факт |
|------|------|
| Device QA | Удобный режим subtitle · map FAB hit · speed spike filter · trips card tap · CapCut heroes 01–04 |
| MAP-95 | CLIP sheet + peek · violet trip polyline |
| Loc | Privacy/AI Categories RU/EN + PrivacyReportsModal title |

## Resolution Center

Notes билда: см. архив `ALADDIN_AI_Review_Notes_*`. Не пересылать полное старое Guideline 2.1 без запроса Apple.

## Архив

| Документ | Зачем |
|----------|--------|
| `ALADDIN_AI_Review_Notes_1.0.1_build15_RU.txt` | ITMS / HealthKit / OB_07 |
| `APPLE_GUIDELINE_2_1_*` | архив 2.1 |
| `WAVE3_H2_REVIEW_NOTES_ASC_PACK_RU.md` | справочно |

## L360 — Notes для следующей сборки (2026-11-18)

План: `docs/business/PLAN_LIFE360_GROWTH_TARIFFS_2026-11-18.md`. Сервер уже выкачен на MAIN.

**Notes (EN, вставить в App Review Information → Notes):**

> What changed in this build:
> 1. Plans. Free now includes a family of up to 4 people and the live family map. Personal (individual subscription) is anti-fraud checks for yourself: calls, SMS, links and payments without a monthly limit; voice and video checks — 30 per month. Family and Premium have no such limit and share anti-fraud with every family member.
> 2. Place history. Family members who allowed location for ALADDIN can see each other's place history inside the family: 24 hours on Free and Personal, 7 days on Trial and Family, 30 days on Premium. Points are stored on our server only for this period and are deleted automatically; deleting the account removes all of them at once. A child sees only themselves and their parents. Location data is never sold or used for ads. Where to see it: Where's family → tap a person → Place history.
> 3. Reminders. If a family has fewer than 3 people, the creator may get two local reminders (day 2 and day 3) to invite relatives. No new permission is requested.
> The Privacy Policy (in the app: Settings → Privacy Policy, and https://aladdin-ai.ru/privacy.html) describes these retention periods.

**То же по-русски (для себя / Resolution Center):**

> 1. Тарифы. Бесплатный: семья до 4 человек и живая карта. Личный — антифрод для себя: звонки, SMS, ссылки и переводы без лимита; проверки голоса и видео — 30 в месяц. Семейный и Премиум — без лимита, антифрод для всех в семье.
> 2. История мест. Участники семьи с включённой геолокацией видят историю мест друг друга внутри семьи: 24 часа (Бесплатный, Личный), 7 дней (Пробный, Семейный), 30 дней (Премиум). Точки хранятся на сервере только этот срок и удаляются автоматически; при удалении аккаунта — сразу все. Ребёнок видит себя и родителей. Не продаём, не используем для рекламы. Где: «Где семья» → человек → «История мест».
> 3. Напоминания. Если в семье меньше 3 человек, создатель может получить два локальных напоминания (2-й и 3-й день) пригласить близких. Новых разрешений не запрашиваем.

**App Store Connect → App Privacy (проверить владельцу):** Location → Precise Location: **Collected**, **Linked to the user**, purpose **App Functionality**, **not** used for tracking. Если сейчас отмечено «не собираем» или «не связано с пользователем» — исправить до отправки сборки, иначе расхождение с политикой.
