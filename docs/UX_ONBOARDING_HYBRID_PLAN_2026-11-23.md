# Онбординг · отдельный план (2026-11-23)

**Рабочий план онбординга.** Основной файл тот же по смыслу: `docs/UX_SIMPLIFY_PLAN_2026-11-21.md`, этап 4, §9.8. Если числа расходятся, верны §8 этого файла и §9.8 основного: они описывают одну и ту же сборку. Старые кадры Figma не удаляем.

**Статус (2026-11-23, вечер):** в ленте шесть экранов: язык и пять страниц на кругах. Агент, отдельный родительский контроль и аналитика скрыты, не удалены. На «Финале» политики, ссылки и обе галочки остаются. Сборку не запускать без «GO на сборку».

---

## 1. Что уже решено раньше (не открывать заново)

Шесть экранов, в этом порядке:

1. Язык
2. Семья
3. Дети
4. Где семья
5. Проверка на обман
6. Финал

Из показа убраны три старых экрана: «агент», отдельный «родительский контроль», «аналитика». Файлы картинок и ключи не удалены. В коде они в `archivedStoryPages()`.

Старые кадры Figma (`OB_00…OB_07`, файл `KvkUdyb5Ll31Z9FSzCbpNl`) только читаем. Новая страница `Onboarding_V2` — только после «GO на Figma».

Пробный период, согласия и кнопка старта работают как сейчас. Одна вибрация на первом экране. Шторм остаётся, белый экран не рисуем. Букв на рисунке нет. «Aladdin start!» на главной не меняем.

Тексты варианта A лежат в основном плане §9.4. В этот черновик их не переносим, пока не выбран вид картинки: слова должны сесть в новую колонку под кругом, а не в старые точки Figma.

---

## 2. Как устроена страница «Aladdin start!» (эталон красоты)

Фон — Шторм.

**Центр.** Круг 254 точки. Тёмная подложка. Мультфильм с прозрачным фоном, обрезка кругом. Кадры сменяются примерно раз в 6,5 секунды. Стекла на самом герое нет.

Уже есть такие кадры:

| Файл | Что нарисовано |
|---|---|
| `SimpleHome_Hero_R02_FamilyWalk` | Семья идёт: мама, папа, девочка, мальчик, собака |
| `SimpleHome_Hero_5811` | Бабушка, мама, папа, девочка и дедушка держат золотой щит |
| `SimpleHome_Hero_R03_ShieldFirewall` | Щит |
| `SimpleHome_Hero_R04_FamilyMapPhone` | Телефон с картой |
| `SimpleHome_Hero_R05_ShieldVerify` | Проверка щитом |
| `SimpleHome_Hero_R06_GlobePin` | Глобус и метка |

**Три стеклянных круга** «Проверить», «Ребёнок», «Где семья». Каждый 88 точек:

1. Картинка внутри (`SimpleHome_Door_Check`, `SimpleHome_Door_Child`, `SimpleHome_Door_Where`).
2. Матовое стекло iOS и белая плёнка 10%.
3. Внешний ободок: белый на 28%, толщина 1,5.
4. Мягкая тень.
5. Под кругом одна белая строка. Она не нарисована на картинке. Длинное слово сжимается и не уезжает за край.

**Большое золотое кольцо** вокруг группы — только линия `#F59E0B` на 28%, стекла нет. При первом открытии три круга один раз проезжают по кольцу. Если включено «Уменьшение движения», кольцо тонкое белое и поездка не играет.

Слова живут в обычной колонке под картинкой. Поэтому их легко сдвинуть. На старом онбординге слова прибиты к рисунку по точкам, на другом телефоне строка наезжает на героя. Новый онбординг повторяет способ старта: картинка в круге, текст под ним.

---

## 3. Какой Аладдин

**Старый** — фотореалистичный парень в худи на ночном городе (`OnboardingHero_01`) и джинны на остальных старых экранах. Это другой рисунок, не мультфильм семьи.

**Новый** — один маленький портрет в том же мультфильме, что семья на прогулке: тёмные волосы, мягкий свет, золотая лампа или маленький щит, по грудь, прозрачный фон. Одна и та же поза на всех экранах. Такого файла ещё нет.

Решение черновика: на новых экранах старого парня и старых джиннов не показываем. Файлы остаются в архиве. Новый портрет рисуем только после выбора варианта и «GO на Figma».

---

## 4. Пять способов собрать гибрид

Каркас у всех один. Фон Шторм. Круг как на старте. Букв на рисунке нет. Под кругом заголовок и две строки, белые. На узком телефоне колонка ниже. Крупный шрифт растит строки, круг не ломает. CapCut отдаёт PNG с прозрачным фоном. Figma — новая страница, чтобы увидеть круг и блок текста.

Шесть смыслов:

| Экран | Сцена |
|---|---|
| Язык | Аладдин один, без семьи |
| Семья | Семья идёт вместе. Картинка прогулки уже есть |
| Дети | Ребёнок с телефоном, вечер, лампа |
| Где семья | Дорожка от дома к школе, золотая метка |
| Проверка на обман | Взрослый смотрит на странный звонок, рядом щит |
| Финал | Семья держит золотой щит. Картинка уже есть |

### 1. Аладдин большой, семья маленькая

В центре новый Аладдин. Семейная сцена — в маленьком стеклянном круге сбоку. Талисман узнаётся сразу. Семью видно плохо, а экран про семью.

### 2. Семья большая, Аладдин маленький — рекомендация

В центре сцена этого экрана, круг около 254 точек. Новый Аладдин — стеклянный круг 88 точек на краю большого круга, всегда в одном месте. Сначала читается смысл экрана, талисман не закрывает лица.

Берём готовое: прогулку на «Семью», щит на «Финал». В CapCut три новые сцены: ребёнок, дорога дом–школа, звонок. Плюс один портрет Аладдина.

### 3. Все в одном круге

Аладдин нарисован внутри семейной сцены. Второго круга нет. Кадр цельный. CapCut делает шесть рисунков, Аладдин каждый раз в новой позе. Дороже, легче получить шесть разных лиц.

### 4. Старый Аладдин, новая семья

В центре новые семейные сцены. Маленький значок — вырезка парня в худи или старого джинна. Нового лица нет. Фото рядом с мультфильмом выглядит как два приложения.

### 5. Два одинаковых стеклянных круга

Слева Аладдин, справа сцена экрана, оба примерно 88–120 точек. Под ними текст на всю ширину. Места для слов больше всего. Большого центра, как на старте, нет.

---

## 5. Как делать, когда будет номер и «GO на Figma»

1. Владелец называет номер 1–5. Если молчит, не подставлять номер 2 молча в код.
2. Одна пробная страница «Семья», не все шесть.
3. Figma: новая страница `Onboarding_V2`, один кадр. Старые `OB_*` не двигать и не удалять.
4. CapCut: только то, чего нет в выбранном номере. Буквы в PNG не писать. Фон прозрачный. Свет и лица как у семьи на прогулке.
5. В приложении текст — колонка под кругом, не точки из старой Figma. Крупный шрифт проверяем на узком iPhone после отдельного «GO на сборку». Сборку делает владелец.
6. Короткий отчёт: какой файл картинки, где текст, что осталось в архиве.
7. Только после «так оставляем» — остальные пять экранов.
8. Потом этот файл соединяем с этапом 4 основного плана.

Пока номера нет: не открывать Figma, не рисовать, не менять `14_OnboardingScreen.swift`.

---

## 6. Уточнение владельца (2026-11-23) · джинн и сюжет в круге

Картинки в этот день **не перерисовывать**. Сначала промпт. Потом CapCut.

Лампы, фески, чалмы и «мальчик Аладдин» из прошлого промпта **сняты**. В маленьком круге джинн.

### Что уже сказано

- **Язык** остаётся прежним экраном приложения: «Язык приложения», «Русский», «English», «Продолжить». Макет `onboarding-01-yazyk.jpg` не используем.
- **Большой круг** на каждом экране со сценой — это место и дело, как на макете «Дети»: ребёнок сидит в комнате за столом и смотрит в телефон, рядом тёплая лампа. Не люди на пустом фоне.
- **Внутри круга** нет молний, грозы, дождя и тёмных туч. Свет ясный или тихий тёплый вечер.
- **Снаружи круга** на некоторых картинках может быть грозовое небо. Молнии не обязательны и не на каждой картинке. На остальных снаружи спокойная ночь.
- Край большого круга **отдаёт золотом**, как набросок `assets/onboarding-family-phone.jpg`: тонкое золотое кольцо и мягкий золотой свет.
- **Маленький круг** — сказочный джинн приложения, не человек. Добрый, лёгкая улыбка. Без лампы и без других предметов из сказки про лампу.
- Букв на рисунке нет. Текст под кругом берём из приложения как есть.

### Пять образов джинна

Одна и та же поза на все экраны: по грудь, смотрит на нас, лёгкая улыбка. Тот же объёмный мультфильм, что семья. Прозрачный фон. В круге 88 точек читаются лицо и цвет.

| № | Образ | Как выглядит |
|---|---|---|
| 1 | Домашний | Круглое лицо, тёплая золотистая кожа, короткие мягкие волосы, бирюзовая жилетка. Руки не нужны. Рекомендация: самый спокойный рядом с семьёй |
| 2 | Молодой | Крупные добрые глаза, румянец, тёмно-синий шёлк на плечах, маленькая золотая серьга. Без бороды |
| 3 | Старший | Короткая седая борода, морщинки у глаз, кремовая накидка, та же лёгкая улыбка. Не строгий |
| 4 | Дымка | Тело ниже плеч растворяется в мягком золотом облачке. Лицо обычное, человеческое, не страшное |
| 5 | Свет | Над головой тихое золотое сияние, как тёплый ореол. Одежда простая, тёмно-синяя. Это не корона и не лампа |

Старого джинна с прошлых экранов онбординга не копируем. Парень в худи в маленький круг не идёт.

### Кто что делает

CapCut рисует только картинки. Букв на рисунке нет. Знак CapCut с двух выбранных джиннов владелец уже убрал.

Слова, «Пропустить» и кнопка — текст приложения под кругом. Их можно сдвинуть, не трогая картинку. В старом онбординге слова были прибиты к точкам Figma, поэтому на другом телефоне наезжали на героя. Так больше не делаем. Figma для этой вёрстки не нужна.

### Круг не режет картинку

Круг — это сцена, не ножницы. Голова, ноги, руки, телефон, щит, собака и мебель целые. Никто не обрезан кругом.

Персонажи и крупные предметы могут чуть выходить за золотое кольцо, как объёмная картинка, которая выступает вперёд. За краем виден кусок плеча, локоть, лапа или край стола. Лицо и предмет при этом целые.

Картинка яркая и живая: тёплый свет, ясные цвета, персонажи ближе к нам, не плоский значок внутри рамки.

То же у джинна: голова и плечи могут чуть выступить из маленького круга. Лицо не срезано.

### Промпт для CapCut

Английский текст ниже вставляется в генератор. Номер джинна подставляем, когда владелец его назовёт. Сцены большого круга меняются по строке SCENE.

**Маленький круг, джинн.**

```text
3D cartoon friendly genie bust, not a human man, same soft family-animation style as a mother father children and puppy. Chest up, looking at the viewer, light kind smile, calm eyes. The genie stands in front of a round gold frame and slightly steps out of it, like a 3D picture popping forward. Head, hair, shoulders and smile stay fully visible, never cropped by the circle. No lamp, no smoke spout, no carpet, no jewelry pile, no scary face, no beard unless the chosen look says so. Bright, lively, warm clear light inside the circle. No lightning, no storm, no rain and no dark clouds inside the circle. Outside the gold ring only, a storm sky is allowed on some pictures and is not required; do not put lightning on every picture. Thin gold ring with a soft warm gold glow. Transparent background beyond the character and the ring. No text, no letters, no logo.

1: round face, warm gold skin, short soft hair, teal vest, no hands.
2: young genie, large kind eyes, rosy cheeks, dark-blue silk on the shoulders, one small gold earring, no beard.
3: older genie, short grey beard, smile lines, cream cape, still gentle, not stern.
4: body below the shoulders fades into a soft gold cloud, face stays human and friendly.
5: a quiet gold glow above the head like a warm halo, simple dark-blue clothes, not a crown.
```

Пять готовых промптов. Каждый вставляется в CapCut целиком. Молния есть только снаружи у 4 и 5, внутри круга её нет.

**1. Домашний.** Снаружи тихая ночь, без молнии.

```text
3D cartoon friendly genie bust, not a human man, same soft family-animation style as a mother father children and puppy. Round face, warm gold skin, short soft hair, teal vest, no hands. Chest up, looking at the viewer, light kind smile, calm eyes. He stands in front of a round gold frame and slightly steps out of it, like a 3D picture popping forward. Head, hair and shoulders stay fully visible, never cropped. No lamp, no carpet, no scary face. Inside the circle the light is bright, warm and clear: no lightning, no storm, no rain, no dark clouds. Outside the gold ring: a quiet deep-navy night, no lightning. Thin gold ring with a soft warm gold glow. No text, no letters, no logo.
```

**2. Молодой.** Снаружи тихая ночь, без молнии.

```text
3D cartoon young friendly genie bust, not a human man, same soft family-animation style. Large kind eyes, rosy cheeks, dark-blue silk on the shoulders, one small gold earring, no beard. Chest up, looking at the viewer, light kind smile. He slightly steps out of a round gold frame, like a 3D picture popping forward. Head, hair, earring and shoulders stay fully visible, never cropped. No lamp, no carpet, no scary face. Inside the circle the light is bright, warm and clear: no lightning, no storm, no rain, no dark clouds. Outside the gold ring: a quiet deep-navy night, no lightning. Thin gold ring with a soft warm gold glow. No text, no letters, no logo.
```

**3. Старший.** Снаружи тихие тучи, без молнии.

```text
3D cartoon older friendly genie bust, not a human man, same soft family-animation style. Short grey beard, smile lines, cream cape, gentle, not stern. Chest up, looking at the viewer, light kind smile. He slightly steps out of a round gold frame, like a 3D picture popping forward. Head, beard and shoulders stay fully visible, never cropped. No lamp, no carpet, no scary face. Inside the circle the light is bright, warm and clear: no lightning, no storm, no rain, no dark clouds. Outside the gold ring: soft grey-blue clouds, no lightning bolt. Thin gold ring with a soft warm gold glow. No text, no letters, no logo.
```

**4. Дымка.** Снаружи грозовое небо, одна дальняя молния, не в круге.

```text
3D cartoon friendly genie bust, not a human man, same soft family-animation style. Face stays human and kind. Body below the shoulders fades into a soft gold cloud. Chest up, looking at the viewer, light kind smile. He slightly steps out of a round gold frame, like a 3D picture popping forward. Head and smile stay fully visible, never cropped. No lamp, no carpet, no scary face. Inside the circle the light is bright, warm and clear: no lightning, no storm, no rain, no dark clouds. Outside the gold ring only: a storm sky with one distant lightning flash, not touching the genie. Thin gold ring with a soft warm gold glow. No text, no letters, no logo.
```

**5. Свет.** Снаружи грозовое небо без молнии.

```text
3D cartoon friendly genie bust, not a human man, same soft family-animation style. A quiet gold glow above the head like a warm halo, not a crown. Simple dark-blue clothes. Chest up, looking at the viewer, light kind smile, calm eyes. He slightly steps out of a round gold frame, like a 3D picture popping forward. Head, halo and shoulders stay fully visible, never cropped. No lamp, no carpet, no scary face. Inside the circle the light is bright, warm and clear: no lightning, no storm, no rain, no dark clouds. Outside the gold ring only: storm clouds, no lightning bolt. Thin gold ring with a soft warm gold glow. No text, no letters, no logo.
```

**Большой круг, сюжет.** Внутри круга есть комната или двор и дело, как ребёнок за столом на экране «Дети».

```text
3D cartoon story in front of one gold circle, same soft family-animation style. Show a real place and what people are doing, bright and alive, characters close to the camera. The circle is a stage, not a crop. Do not cut off heads, faces, hands, legs, feet, phones, shields, the puppy, tables or other objects. People and large objects may stick out a little past the gold ring, like a 3D picture popping out of the circle, while every head and object stays whole. Inside the circle: clear pleasant light, warm evening or bright day. No lightning, no storm, no rain, no dark clouds and no bad weather inside the circle. Outside the gold ring only, a storm sky may appear on some scenes and is not required; do not add lightning to every picture. Thin gold ring and a soft warm gold glow. Transparent background outside the scene. No text, no letters, no logo, no genie in this picture.

SCENE Family: a sunny garden path in front of a house, mother father daughter son and a golden puppy walking together, full bodies visible.
SCENE Kids: a child's room, one child sitting at a wooden table looking at a phone, a warm table lamp beside them, the child and the phone fully visible.
SCENE Where: a clear day, a path from a house door to a school, a gold map pin, a parent and child walking, a puppy, full figures visible.
SCENE Check: a calm kitchen, a parent sitting at the table looking at an incoming call on a phone, a small gold shield on the table, phone and shield fully visible.
SCENE Final: a warm living room, grandmother mother father girl and grandfather standing together and holding one gold shield, every face and the shield fully visible.
```

Джинн уже выбран. Новые портреты джинна в CapCut не генерировать.

---

## 7. Порядок по страницам

Картинки делает CapCut. Страницу собирает приложение по §8: Шторм, два круга, текст внизу. Буквы в рисунок не писать. Figma для этой вёрстки не нужна. Язык не перерисовывать.

Сборка идёт по очереди. Промпты ниже — как рисовать картинку, если файла ещё нет. Готовый файл заново не генерировать.

| Страница | В приложении |
|---|---|
| Язык | Прежний экран. Не рисуем |
| Семья | Собрана. Образец |
| Дети | Собрана следом за «Семьёй» |
| Где семья | Собрана. Шар справа сверху, на небе |
| Проверка на обман | Собрана. Щит снизу слева, на столе |
| Финал | Собрана. Джинн снаружи справа сверху. Политики и галочки на месте |

Общее для каждой новой картинки: объёмный мультфильм, золотое кольцо, люди и предметы целые и могут чуть выйти за край. Внутри круга ясный тёплый свет, без молнии, дождя и туч. Снаружи кольца гроза не обязательна. Фон за кольцом лучше прозрачный, чтобы молния не приезжала на экран.

### 0. Язык

Ничего не рисуем. Экран остаётся как сейчас: «Язык приложения», «Русский», «English», «Продолжить». Джинна нет.

### 1. Семья

Страница уже собрана в приложении. Джинна и сад заново не генерировать. Промпт ниже оставлен как запись, чем рисовали большой круг.

```text
3D cartoon family on a sunny garden path in front of a house, mother father daughter son and a golden puppy walking together, full bodies visible, bright and alive. The circle is a stage, not a crop. Do not cut off heads, hands, legs or the puppy. They may stick out a little past a thin gold ring. Inside the circle: clear warm daylight, no lightning, no storm, no rain, no dark clouds. Transparent background outside the ring. No text, no letters, no logo, no genie.
```

Текст под кругом уже в приложении, не менять: «Защита всей семьи в кармане». Кнопка «Продолжить». Справа сверху «Пропустить».

### 2. Дети

Страница собрана в приложении тем же способом, что «Семья». Джинна нет. На экране телефона остались лишние щит и галочка: файл не перерисовывали, белый холст и знак с угла сняты. Промпт:

```text
One 3D cartoon smartphone, front view, simple and large, no people, no icons around it, no weapons. It sits in front of a thin gold ring and may stick out a little. The phone is fully visible, not cropped. Bright clear light inside the circle, no lightning, no storm, no rain. Transparent background outside the ring. No text, no letters, no logo.
```

Большой круг — ребёнок в комнате. Промпт:

```text
3D cartoon child's room, one child sitting at a wooden table looking at a phone, a warm table lamp beside them. The child, the phone and the lamp are fully visible and may stick out a little past a thin gold ring. Bright warm evening inside the circle, no lightning, no storm, no rain, no dark clouds. Transparent background outside the ring. No text, no letters, no logo, no genie, no guns, no extra warning icons.
```

Текст не менять: «Защита для детей!». Кнопка «Продолжить». «Пропустить» сверху.

### 3. Где семья

Страница собрана в приложении. Джинна нет. Шар стоит на небе справа сверху. Промпт:

```text
3D cartoon planet Earth seen from space, simple and readable, blue oceans and green land, one gold map pin on it, no photograph of a person, no face inside the pin. The globe is fully visible in front of a thin gold ring and may stick out a little. Bright clear light, no lightning, no storm on the globe. Transparent background outside the ring. No text, no letters, no logo.
```

Большой круг — дорога от дома к школе. Промпт:

```text
3D cartoon clear day, a path from a house door to a school, a parent and a child walking, a golden puppy, full figures visible. They may stick out a little past a thin gold ring. No faces cropped. Bright daylight inside the circle, no lightning, no storm, no rain, no dark clouds. Transparent background outside the ring. No text, no letters, no logo, no genie.
```

Текст не менять: «Где семья». Кнопка «Продолжить». «Пропустить» сверху.

### 4. Проверка на обман

Страница собрана в приложении. Щит не перерисовывали. Маленький круг стоит на столе снизу слева, лицо и руки свободны. Знак в углу файла за кругом. Промпт:

```text
3D cartoon calm kitchen, one parent sitting at a table and looking at an incoming call on a phone, a small gold shield on the table. The parent, the phone and the shield are fully visible and may stick out a little past a thin gold ring. Bright warm light inside the circle, no lightning, no storm, no rain, no dark clouds. Transparent background outside the ring. No text, no letters, no logo, no genie, no guns, no extra warning icons.
```

Текст не менять: «Antifake для людей 18+». Кнопка «Продолжить». «Пропустить» сверху.

### 5. Финал

Страница собрана в приложении. Джинн с подмигиванием стоит снаружи круга справа сверху, пять лиц и щит не закрывает. Кнопка «Начать». «Пропустить» нет.

Политики не трогали. Под кнопкой по-прежнему: строка о данных, ссылка «Политика конфиденциальности», галочка «Я согласен с обработкой данных», ссылка на пользовательское соглашение, галочка «Я принимаю пользовательское соглашение». Пока обе галочки не стоят, «Начать» серая и не нажимается. Промпт:

```text
3D cartoon warm living room, grandmother mother father a girl and grandfather standing together and holding one gold shield. Every face and the shield are fully visible and may stick out a little past a thin gold ring. Bright warm light inside the circle, no lightning, no storm, no rain, no dark clouds. Transparent background outside the ring. No text, no letters, no logo, no genie.
```

Текст не менять: «Присоединяйтесь к ALADDIN!». Кнопка «Начать». «Пропустить» на финале нет. Две строки согласия остаются текстом приложения.

### Когда картинки готовы

Сначала только страница «Семья» в приложении. Остальные пять не собирать, пока эта не понравится. Слова остаются текстом под кругом.

### Выбор по готовым картинкам CapCut (2026-11-23)

Владельцу нравятся две картинки одного синего джинна: подмигивание и тихая улыбка со взглядом вверх. Разных героев не делаем.

- Джинн только на двух экранах. «Семья» — тихая улыбка. Финал — тот же джинн подмигивает.
- «Дети», «Где семья», «Проверка на обман» — во втором круге не джинн, а один предмет: телефон, земной шар из космоса, золотой щит. Не золотая метка и не сцена с несколькими лицами. Большой круг остаётся сюжетом.
- Стекло и матовость — ободок круга, как на «Aladdin start!». Лица и предметы внутри не затираем.
- Знак CapCut с этих двух файлов владелец уже убрал.
- Грозу за кольцом в файл маленького круга не кладём, чтобы молния не приезжала на каждый экран. Гроза может остаться фоном самой страницы, снаружи круга.

---

## 8. Эталон страницы «Семья» (владелец принял круги, 2026-11-23)

Эту страницу повторяем на «Дети», «Где семья», «Проверка на обман» и «Финал». Меняются только картинки и место маленького круга. Слова не переписываем.

### Круги

Оба круга одинаково устроены. Стекло только ободок. Лица и предметы внутри резкие.

| | Большой | Маленький |
|---|---|---|
| Наружный размер | 270 | 96 |
| Картинка внутри | 254 | 80 |
| Стекло | `ultraThinMaterial` + белая плёнка 10% | то же |
| Белая кромка | 28%, толщина 1,5 | то же |
| Золото снаружи | `#F59E0B`, толщина 1,5 | то же |
| Если включено «Уменьшение движения» | тонкое белое кольцо, толщина 1 | то же |
| Тень | чёрная 28%, радиус 8, сдвиг вниз 4 | то же |

Увеличение прячет белый холст. Его смотрим по каждой картинке, одно число на все страницы не ставим.

| Картинка | Увеличение | Зачем |
|---|---|---|
| Семья, большой круг | 1.08 | Белый холст слева заходил внутрь круга. После 1.08 на краю белых точек нет |
| Семья, джинн | 1 | На краю белого нет |
| Дети, большой круг | 1.18 | Холст шире, чем у «Семьи». При 1.18 край — комната, лампа на месте |
| Дети, телефон | 1 | Белый холст снят с файла, в круге его нет. Знак CapCut с угла снят |
| Где семья, большой круг | 1 | Белый холст снят (прозрачный). Голова мамы и щенок внутри круга, белого края нет |
| Где семья, шар | 1.08 | Край — золотое кольцо, не холст. Лёд и облака на шаре не стираем |
| Проверка, большой круг | 1.28 | Край без белого холста. Лицо, телефон и стол в кадре |
| Проверка, щит | 1.12 | Край — обод щита. Знак CapCut в углу, за кругом, его не видно. Щит не перерисовывали |
| Финал, большой круг | 1.14 | Край без белого холста. Пять лиц и щит в кадре |
| Финал, джинн | 1.06 | Тёмное небо за кольцом не попадает в круг |

Файлы: `OnboardingCircle_Family`, `OnboardingCircle_FamilyGenie`, `OnboardingCircle_Kids`, `OnboardingCircle_KidsPhone`, `OnboardingCircle_Where`, `OnboardingCircle_WhereGlobe`, `OnboardingCircle_Check`, `OnboardingCircle_CheckShield`, `OnboardingCircle_Final`, `OnboardingCircle_FinalGenie`.

### Где стоит маленький круг

Он едет по краю большого и не закрывает головы, лица, руки и другие части тела.

На «Семье» место уже выбрано: сдвиг **вправо 96, вниз 122** от центра большого круга. Это забор справа снизу. Головы мамы, папы и мальчика свободны.

На следующих страницах круг сдвигаем по той же окружности, каждый раз глядя на лица:

| Страница | Маленький круг | Куда ставить |
|---|---|---|
| Семья | джинн, тихая улыбка | забор справа снизу: вправо 96, вниз 122 |
| Дети | один телефон | слева снизу: влево 96, вниз 122. Лицо и лампа справа свободны |
| Где семья | шар без лица, одна золотая метка | небо справа сверху: вправо 130, вверх 78 |
| Проверка на обман | готовый щит, знак за кругом не виден | стол снизу слева: влево 36, вниз 140 |
| Финал | тот же джинн, подмигивает | выше и правее, на золотом ободе: вправо 156, вверх 84, фото семьи не задевает |

Новые портреты джинна не генерировать. Щит не перерисовывать.

### Текст

Одна нижняя колонка на всех страницах истории, сразу над точками. На языке колонки нет: там прежний выбор языка.

| | Шрифт | Размер | Цвет |
|---|---|---|---|
| Заголовок | New York, жирный | 24; если ширина меньше 375 — 22 | белый `textPrimary` |
| Описание | обычный, без засечек | **18** | `textSecondary` |
| «Пропустить» | как в приложении | как сейчас | пока серый; в основном плане он белый, это отдельная правка |
| «Продолжить» / «Начать» | как сейчас | как сейчас | синяя кнопка пока не золотая |

Живые фразы не менять. Вариант A из основного плана §9.4 на эти страницы не ставить.

На финале, если круг и заголовок выше свободного места, они прокручиваются. Круг остаётся 270, шрифт 24 и 18 не уменьшается. Точки, «Начать» и правовая информация остаются на экране.

### Что ещё не в приложении

Все шесть экранов в ленте: язык и пять страниц истории. Агент, отдельный родительский контроль и аналитика скрыты переключателем `useShortOnboarding`. Их страницы остаются в `archivedStoryPages()`, картинки и ключи не удалены. Вернуть показ: поставить переключатель в `false`. На «Финале» блок политик и обе галочки на месте.
