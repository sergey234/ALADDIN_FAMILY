# Задание для AI-агента Rive (Cadet) — Единорог ALADDIN

> **Куда вставить:** editor.rive.app → ваш файл `ALADDIN_unicorn` (или untitled/2319314) → **AI Agent / Chat** в Rive.  
> **Язык:** скопируйте блок **«ПРОМПТ ДЛЯ АГЕНТА»** целиком в чат агента.

---

## ПРОМПТ ДЛЯ АГЕНТА (копировать отсюда)

```
Ты — Rive-аниматор для iOS-приложения ALADDIN (детское, PG, family-safe).

Файл: единорог companion hero. На artboard уже лежит PNG unicorn_master_crop_360x480.
НЕ векторизуй и НЕ удаляй весь PNG. Тело и шерсть остаются картинкой.
Работай только с ЛИЦОМ (верхние 45% кадра): добавь векторные слои поверх PNG.

=== ЦЕЛЬ ===
Сделать 13 разных «лиц» (эмоций) + рот при разговоре.
Без 13 отдельных PNG — только слои и State Machine в Rive.
Artboard: 360×480. Export to RIV включён на raster asset.

=== ШАГ 1. ПРОВЕРЬ ХОЛСТ ===
1. Artboard ровно 360 ширина × 480 высота.
2. PNG единорога по центру, лицо в верхней половине.
3. Переименуй artboard: Hero360.
4. Переименуй файл проекта: ALADDIN_unicorn.

=== ШАГ 2. СЛОИ ЛИЦА (Design) ===
Создай группу Face поверх PNG (не трогай тело ниже шеи):

5. brow_left, brow_right — простые дуги (вектор).
6. eye_left, eye_right — белок + зрачок + веко (можно упрощённо).
7. mouth_shape — рот (линия / дуга / овал).
8. cheek_blush — опционально, opacity 0…0.35.
9. extras — для sad (слеза PG), celebrate (✨), без крови/ужаса.

10. Сгруппируй: Face → brows, eyes, mouth, cheeks, extras.
11. Origin рта — центр губ (для speaking).

=== ШАГ 3. STATE MACHINE HeroSM (Animate) ===
12. Создай State Machine с именем точно: HeroSM
13. Добавь 13 Trigger inputs (имена МАЛЕНЬКИМИ буквами, БЕЗ опечаток):

idle
listening
thinking
speaking
happy
playful
sad
comfort
celebrate
curious
nostalgic
excited
alert

14. Добавь Number input: mouth_open (min 0, max 1).

15. Создай 13 States с теми же именами.
16. Связь: каждый Trigger → переход в свой State (200–300 ms blend).

=== ШАГ 4. 13 ЛИЦ — ЧТО НАРИСОВАТЬ В КАЖДОМ STATE ===

idle — спокойное лицо, рот M0 нейтральная линия, глаза 90% открыты.
listening — брови чуть выше, лёгкая улыбка M1, глаза смотрят на зрителя.
thinking — одна бровь выше, глаза вверх-вбок, рот M7 «hm».
speaking — рот M4 овал; привяжи Scale Y рта к input mouth_open (0=закрыт, 1=открыт).
happy — улыбка M2, брови дугой вверх, щёки blush 0.2.
playful — широкая улыбка M3, один глаз прищур 50%, щёки 0.25; лёгкий bob головы.
sad — брови внутрь, рот M6 уголки вниз, веки 60%, БЕЗ «праздника».
comfort — мягкие брови, тёплый взгляд, рот M1, щёки 0.15.
celebrate — глаза wide, рот M3, щёки 0.35, extras ✨.
curious — одна бровь выше, глаза wide, рот M5 «о».
nostalgic — расслабленные брови, полуприкрытые глаза 80%, рот M1.
excited — брови высоко, глаза 110% wide, рот M3, щёки 0.3.
alert — брови сближены (не злость), серьёзный взгляд, рот M0.

17. idle: лёгкое «дыхание» loop 2 сек (микро scale body или head).
18. unicorn: уши/грива слегка вперёд на listening; без жёстких прыжков на sad.

=== ШАГ 5. ПРОВЕРКА (Play) ===
19. Нажми Play. В Inputs по очереди жми все 13 triggers.
20. Каждая эмоция должна ВИЗУАЛЬНО отличаться от idle без подписи.
21. На speaking двигай mouth_open 0→1 — рот открывается.
22. Если happy = idle — исправь state happy.

=== ШАГ 6. EXPORT ===
23. Убедись Export to RIV включён на PNG asset.
24. Export → For runtime → скачай unicorn.riv (ожидаем >25 KB, <500 KB).
25. Export → .rev for backup → ALADDIN_unicorn.rev

=== ЗАПРЕЩЕНО ===
- Переименовывать triggers (Happy, IDLE и т.д.)
- Удалять HeroSM
- Vectorize весь персонаж целиком
- Кровь, страх, 18+, сарказм
- Дым/искры (это только для genie, не unicorn)

=== ГОТОВО КОГДА ===
Preview проходит цепочку:
idle → listening → thinking → speaking (mouth_open) → happy → sad → alert → idle
и файл .riv скачан.

Сначала сделай только unicorn. Не переходи к aladdin/genie пока я не скажу.
```

---

## После единорога — промпт для aladdin (когда unicorn OK)

```
Duplicate project ALADDIN_unicorn → ALADDIN_aladdin.
Replace body PNG with aladdin_master_OB01 360×480 (наставник-человек, не джинн).
HeroSM и все 13 trigger names — НЕ МЕНЯТЬ.
Подстрой Face layers под aladdin: сдержаннее, без прыжка на playful.
Export runtime → aladdin.riv и backup .rev.
```

## После aladdin — промпт для genie

```
Duplicate ALADDIN_aladdin → ALADDIN_genie.
Replace PNG with genie OB03 360×480.
HeroSM имена те же.
Дым/искры extras ТОЛЬКО на playful, excited, speaking — ВЫКЛ на sad и comfort.
Export → genie.riv + .rev backup.
```

---

## Куда положить .riv на Mac

```
/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/Resources/Companion/
  unicorn.riv
  aladdin.riv
  genie.riv
```

Напишите в Cursor: **unicorn export готов** — ML прогонит gate.

---

## Если агент Rive «не понимает»

Скажите агенту коротко:

> «Сделай только шаг 12–16: State Machine HeroSM с 13 triggers и states по списку. PNG body не трогай.»

Потом отдельно:

> «Сделай шаг 4 для states happy, sad, speaking с mouth_open.»

---

## Честно: что агент может / не может

| Может | Не может |
|-------|----------|
| SM, triggers, mouth_open | Заменить Cadet export без вашего Download |
| Вектор рта/бровей поверх PNG | 12 Disney-лиц без вашего Preview |
| Loop idle, transitions | Открыть файл на iPhone — это ML после export |

**12 лиц без 12 PNG** = **слои лица + 13 states** в одном файле. Это правильный путь по плану §2.3.
