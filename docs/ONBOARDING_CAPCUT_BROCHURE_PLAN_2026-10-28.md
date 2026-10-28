# Онбординг — план CapCut: фольга, лак, место героя

**Дата:** 2026-10-28  
**Для кого:** владелец и следующая ML-система, которая ведёт CapCut по одной странице.  
**Экран:** iPhone, холст **393×852** pt. Картинка на весь экран. Текст и кнопки рисует приложение поверх картинки.  
**Значок App Store в этот план не входит.** Его промпт уже готовый, менять его не нужно.

Майский файл `docs/ALADDIN_Onboarding_Prompts.md` (12 мая 2026) описывает **другую** историю: лампа, маленький пастельный единорог, постепенное появление. Живые файлы в приложении другие. Для этого прохода CapCut берёт **только этот документ** и файл, который указан у страницы.

---

## 0. Как пользоваться

1. Одна страница за сессию. Порядок внизу, раздел «Порядок работы».
2. В CapCut режим **Image**, не Video.
3. Соотношение **9:16**, качество максимальное.
4. Прикрепить указанный PNG через **+** и дождаться миниатюры. Без миниатюры CapCut нарисует новую картинку.
5. Вставить **только английский блок** этой страницы. Прикреплять **русский** скрин этой страницы. Английский скрин не прикреплять: слова рисует приложение.
6. Если на результате водяной знак CapCut, сдвинутое лицо, новые буквы, сдвинутый или переписанный текст, или пластиковый блеск — кадр не принимается.
7. В приложение файлы кладутся после того, как владелец принял кадр. Сборку Xcode этот план не запускает.

---

## 1. Как устроен экран

| Полоса | Где на холсте 852 | Что там |
|---|---|---|
| Верх | 0–52 | «Пропустить» |
| Середина | 52–698 на карточках 1–6 | герой и текст |
| Низ карточек 1–6 | 698–852 | точки и кнопка, высота 154 |
| Финал | с 556 до низа | описание уже выше, ниже согласие и кнопки |

Координаты текста ниже — это **Y от верха экрана**. Герой должен быть **выше** этой линии. Ниже линии картинка остаётся тёмной и живой, чтобы белый текст читался.

Картинки 2–7 на телефоне увеличиваются на **1.09** от верхнего края. Низ чуть обрезается. Поэтому важный предмет не ставить в самый низ.

Файлы «Язык», «Семья», «Агент», «Родители», «Финал» сейчас **393×852**. На телефоне они растягиваются примерно втрое и выглядят мягко. Файлы «Аналитика», «Дети», «Antifake» сейчас **горизонтальные 1536×1024**. Телефон оставляет центр и срезает бока. Новый кадр нужен вертикальный **9:16**, герой в центральной колонке.

---

## 2. Что такое «глянец» в промпте

На значке это уже получилось. В промпте это **фольга и тонкий лак**, как на обложке дорогого буклета:

- светлая кромка на золоте;
- в тени золото глубже, античное;
- одна искра на камне и в глазах, как камень у ювелира под лампой;
- небо резкое и в фокусе: много звёзд, полоса Млечного Пути, галактика, планеты с тонким бликом фольги;
- лицо детальное и резкое, кожа без лака.

Три плана на каждой картинке, все резкие:

1. Первый план — герой: лицо, руки, фольга. Яркий и живой.
2. Второй план — предмет этой страницы: шар, лампа, куб, кольцо. Нарисован целиком.
3. Третий план — небо за героем: звёзды, Млечный Путь, галактика, планеты. Не закрывают лицо.

Слово `glossy` в промпт не писать. CapCut от него делает пластик и белую дымку. Блик планет называется `thin polished highlight, like foil, not plastic`. В каждом промпте уже стоит запрет: no halo, no neon, no plastic, no HDR, no fog, no gaussian blur.

Буквы в картинки карточек не рисовать. Логотип на «Семье» и на «Финал» приложение кладёт само.

---

## 3. Общий хвост качества

Он уже вшит в каждый промпт ниже, с своим списком золотых предметов. Отдельно дописывать абзац не нужно. Если ML-система собирает промпт заново, хвост такой, а в скобках подставляются предметы этой страницы:

```
Finish this like a luxury print brochure and a top App Store screen at the same time. Gold reads as polished foil: a thin bright edge on OBJECTS, with deeper antique gold in the shadows. GLINT carries one clean glint, like a jeweler’s stone under a soft lamp. The face stays detailed and sharp, with no lacquer on the skin. The sky stays matte and in focus: separated cloud edges, clean indigo, clean amber and gold where the scene is warm, bright and clear at a small size and rich at a large size. The frame looks varnished and press-ready. No halo, no neon, no plastic, no HDR, no fog, no gaussian blur. If the face moves, the result is wrong.
```

---

## 4. Страницы

### 4.0 Язык — первый экран

| | |
|---|---|
| Файл | `Resources/HeroAssets/OnboardingHero_00.png` |
| Сейчас | 393×852. Мальчик слева, высокий светящийся единорог справа, решётчатый шар между ними, золотая дорожка внизу |
| Текст приложения | заголовок «Язык приложения» и четыре кнопки языка по центру экрана. Кнопка «Продолжить» внизу |
| Куда сесть героям | головы мальчика и единорога в верхней трети. Шар поднять туда же, выше кнопок. Середина глубже и спокойнее. Дорожка внизу тише |
| Фольга | рог, решётка шара, золотая дорожка |
| Кожа | лицо мальчика без лака, только чёткое |
| В картинку не класть | кнопки, слово «Язык», логотип |

Кнопки закрывают середину. Если шар останется в центре, его не будет видно.

```
This is the language screen of the ALADDIN AI iPhone app. Portrait 9:16. It is not a poster, not an app icon, and not an ad. The app draws the title “App language” and four language buttons over the middle of this picture, and a continue button at the bottom. Do not draw any text, letters, logo, URL, or button. Erase every word, letter, button, and logo already visible in this photo. Do not keep them, do not move them, do not translate them, and do not replace any word. Leave only the illustration.

Keep this exact scene. Keep this boy on the left and this tall luminous unicorn on the right. Do not redraw their faces. Do not replace the unicorn with a small pastel pony. Do not swap their sides.

Place both heads in the top third of the frame. Lift the glowing wireframe globe into that same upper third, above the middle, so the buttons will not cover it. Keep the middle band deep, calm, and dark enough for white buttons. Keep a quiet gold path along the bottom.

Draw three sharp planes, all in focus. First plane: the boy and the unicorn, bright and alive. Second plane: the wireframe globe and the gold path, fully drawn. Third plane, behind them: many sharp stars, a clear Milky Way band, one bright galaxy, and two or three planets. Each planet has a thin polished highlight, like foil, not plastic. Do not cover their faces with a planet. The sky stays in focus, not a haze.

The horn, the wireframe globe, and the gold path read as polished foil: a thin bright edge, deeper antique gold in the shadows. The horn carries one clean glint, like a jeweler’s stone under a soft lamp. The boy’s face stays detailed and sharp, with no lacquer on the skin. The night sky stays in focus: separated cloud edges, clean indigo, the stars and the Milky Way still sharp, bright and clear at a small size and rich at a large size. The frame looks varnished and press-ready. No halo, no neon, no plastic, no HDR, no fog, no gaussian blur. If the boy or the unicorn changes face, the result is wrong.
```

**Принять кадр, если:** те же двое, шар выше середины, середина спокойная, рог с одной искрой, букв нет.

---

### 4.1 Семья — «Защита всей семьи в кармане»

| | |
|---|---|
| Файл | `Resources/HeroAssets/OnboardingHero_01.png` |
| Сейчас | 393×852. Крупный портрет молодого человека в тёмном худи, золотые звёзды и маленькая лампа на рукаве, тёплые окна сзади. Увеличение на телефоне 1.0 |
| Текст приложения | логотип ALADDIN с Y=271, высота 121. Заголовок с Y=450. Описание с Y=546. Затемнение с Y=528 |
| Куда сесть герою | глаза в верхней трети, выше Y=250. Худи может заходить под логотип. Ниже Y=450 темнее |
| Фольга | лампа на рукаве и золотые звёзды на худи |
| Кожа | лицо без лака |
| В картинку не класть | слово ALADDIN, заголовок, телефон в кармане (на маленьком размере он становится пятном) |

```
This is a full-screen story image on an iPhone onboarding page, portrait 9:16. It is not a poster and not an app icon. The app draws its own ALADDIN logo from about 30% down the screen and a white title across the lower half. Do not draw any text, letters, or logo. Erase every word, letter, button, and logo already visible in this photo. Do not keep them, do not move them, do not translate them, and do not replace any word. Leave only the illustration.

Keep this exact young man: his face, his dark indigo hoodie, the small gold stars, and the small gold lamp on the sleeve. Do not redraw his face. Place his eyes in the top third, above the upper-middle of the frame. The hoodie may continue downward. From the middle of the frame downward, the picture becomes a deeper night, still sharp, still with a living background, darker than his face so white text can sit there.

Draw three sharp planes, all in focus. First plane: this young man, face and hoodie bright and alive. Second plane: the lamp and the small gold stars on the sleeve, and the warm windows, fully drawn. Third plane, behind him and above the roof: many sharp stars, a clear Milky Way band, one bright galaxy, and one planet in the open sky. The planet has a thin polished highlight, like foil, not plastic. Do not cover his face. The sky stays in focus, not a haze.

The lamp and the gold stars read as polished foil: a thin bright edge, deeper antique gold in the shadows. The lamp carries one clean glint, like a jeweler’s stone under a soft lamp. His face stays detailed and sharp, with no lacquer on the skin. Warm window light may stay behind him, softer than his face. The sky stays matte and in focus. The frame looks varnished and press-ready, bright and clear at a small size and rich at a large size. No halo, no neon, no plastic, no HDR, no fog, no gaussian blur. If the face changes, the result is wrong.
```

**Принять кадр, если:** то же лицо, глаза в верхней трети, лампа и звёзды с кромкой фольги, ниже середины темнее, букв нет.

---

### 4.2 Агент — «Ваш персональный агент безопасности»

| | |
|---|---|
| Файл | `Resources/HeroAssets/OnboardingHero_02.png` |
| Сейчас | 393×852. Синий джинн в светящемся шаре, золотой куб внизу рисунка, под рисунком плоский тёмно-синий прямоугольник. На телефоне масштаб 1.09 от верха |
| Текст приложения | заголовок с Y=328, на телефоне ещё на 28 pt выше. Описание с Y=466. Затемнение с Y=448 |
| Куда сесть герою | вся голова целиком, с запасом неба над пламенем: макушка не у верхнего края, иначе масштаб 1.09 срежет её. Камень на груди ниже подбородка, в верхней трети. Куб поднять к рукам, выше середины. Плоский низ заменить тёмным звёздным полом |
| Фольга | ободок шара, камень на груди, куб |
| В картинку не класть | заголовок и звёзды рейтинга. Их пишет приложение |

Заголовок высокий. Если куб оставить внизу рисунка, текст его закроет.

```
This is a full-screen story image on an iPhone onboarding page, portrait 9:16. It is not a poster and not an app icon. A white title covers the lower middle of the screen. The picture is also zoomed slightly from the top, so the bottom edge is cropped. Do not draw any text, letters, stars-as-rating, or logo. Erase every word, letter, button, and logo already visible in this photo. Do not keep them, do not move them, do not translate them, and do not replace any word. Leave only the illustration.

Keep this exact blue genie: flame hair, face, gold chest gem, gold shoulders, the blue sphere, and the hands. Do not redraw the face. Show the entire head, including the full flame of hair. Leave a clear band of night sky above the highest flame so the head does not touch the top edge and is not cut off. The phone zooms this picture from the top, so if the flame touches the top, the head will be cropped. Place the chest gem in the upper third, still below the chin. Move the gold cube up beside the hands, above the middle of the frame.

Draw three sharp planes, all in focus. First plane: the genie, the full head, and the hands, bright and alive. Second plane: the blue sphere and the gold cube, fully drawn, not cut off. Third plane, behind him: many sharp stars, a clear Milky Way band, one bright galaxy, and two or three planets with a thin polished highlight, like foil, not plastic. Do not cover his face or the flame. The sky stays in focus, not a haze.

Replace the flat empty navy block at the bottom with a dark sharp star floor, quieter than the genie. The same stars, Milky Way, galaxy, and planets continue into that floor, still sharp. The rim of the sphere, the chest gem, and the cube read as polished foil: a thin bright edge, deeper antique gold in the shadows. The chest gem and the eyes carry one clean glint, like a jeweler’s stone under a soft lamp. The face stays detailed and sharp, with no lacquer on the skin. The sky stays matte and in focus: clean indigo, separated edges, bright and clear at a small size and rich at a large size. The frame looks varnished and press-ready. No halo, no neon, no plastic, no HDR, no fog, no gaussian blur. If the face changes or the top of the head is cut off, the result is wrong.
```

**Принять кадр, если:** тот же джинн, вся голова с небом над пламенем, куб выше середины, вместо пустого прямоугольника тёмный звёздный пол, одна искра на камне, букв нет.

---

### 4.3 Родители — «Родительский контроль»

| | |
|---|---|
| Файл | `Resources/HeroAssets/OnboardingHero_03.png` |
| Сейчас | 393×852. Джинн крупно в верхней части, золотой след от поднятой руки, внизу снова плоский тёмно-синий прямоугольник. Масштаб 1.09 от верха |
| Текст приложения | заголовок с Y=552. Описание с Y=594, три строки, низ описания около Y=690, выше точек страниц. Затемнение с Y=500 |
| Куда сесть герою | лицо и камень выше Y=500. Обе руки целиком внутри кадра, с запасом от левого и правого края. Нижняя рука справа не у обреза. Золотой серп на правом крае убрать |
| Фольга | камень на груди, золото на плечах, золото на поднятой руке и искра в ладони |
| В картинку не класть | детей, родителей-фото, заголовок, золотой серп или клюв на правом крае |

На этом скрине голова уже целиком. Обрезана нижняя рука справа, и чуть выше неё из правого края торчит золотой серп. Его в кадре быть не должно. Телефон ещё увеличивает картинку от верха, поэтому всё тело должно сидеть внутри, не на кромке.

```
This is a full-screen story image on an iPhone onboarding page, portrait 9:16. It is not a poster and not an app icon. The white title sits in the lower third, starting just below the middle. The picture is zoomed slightly from the top and the side edges are cropped, so keep the whole figure inside the frame with a clear margin. Do not draw any text, letters, logo, or a child. Erase every word, letter, button, and logo already visible in this photo. Do not keep them, do not move them, do not translate them, and do not replace any word. Leave only the illustration.

Keep this exact blue genie, his face, the raised hand with the gold spark trail, the chest gem, and the gold armor on the shoulders. Do not redraw the face. Keep his eyes in the upper half, well above the middle of the frame. Leave night sky above the flame hair so the whole head stays inside the frame.

The lower hand, on the right side of this photo, is cut off at the edge. Draw that entire hand inside the frame, above the white text, with a clear margin from the right edge and from the bottom. Do not leave the wrist or any finger touching the edge. Keep the raised hand on the left fully inside the frame too, spark trail included.

Remove the stray gold crescent on the right edge, just above that lower hand. It is not part of the genie. Do not replace it with a beak, a horn, a blade, or another ornament. Leave only the night sky there. Nothing may stick out of the frame: no hand, no flame, no gold shape, no spark.

Draw three sharp planes, all in focus. First plane: the genie and both hands, bright and alive, fully inside the frame. Second plane: the chest gem, the shoulder gold, and the spark in the raised palm, fully drawn. Third plane, behind him: many sharp stars, a clear Milky Way band, one bright galaxy, and two or three planets with a thin polished highlight, like foil, not plastic. Do not cover his face. Do not put a planet on the right edge. The sky stays in focus, not a haze.

Replace the flat empty navy block at the bottom with a dark living sky, sharp and quiet, darker than the genie, so white text can sit there. Keep the stars, the Milky Way, and the planets visible in that lower sky, still sharp. The chest gem, the shoulder gold, and the gold on the raised hand read as polished foil: a thin bright edge, deeper antique gold in the shadows. The chest gem, the eyes, and the spark in the palm carry one clean glint, like a jeweler’s stone under a soft lamp. The face stays detailed and sharp, with no lacquer on the skin. The sky stays matte and in focus. The frame looks varnished and press-ready, bright and clear at a small size and rich at a large size. No halo, no neon, no plastic, no HDR, no fog, no gaussian blur. If the face changes, or any part of the genie is cut by the frame, the result is wrong.
```

**Принять кадр, если:** тот же джинн, голова целиком, обе руки внутри кадра, золотого серпа на правом крае нет, низ тёмный, букв нет.

---

### 4.4 Аналитика — «Аналитика рисков»

| | |
|---|---|
| Файл | `Resources/HeroAssets/OnboardingHero_04.png` |
| Сейчас | горизонтальный 1536×1024. Джинн, орбиты, золотой куб, галактика, планеты. На вертикальном экране бока срезаются. Масштаб 1.09 от верха |
| Текст приложения | заголовок с Y=440. Описание с Y=522. Затемнение с Y=542 |
| Куда сесть герою | джинн в верхней половине, по центру. Куб выше середины, выше Y=420, целиком виден. Смысл кадра в центральной колонке: бока 9:16 тоже чуть обрежутся |
| Фольга | кольца орбит и золотой куб, плюс камень на груди |
| В картинку не класть | графики из чужого приложения, цифры, слова |

```
This is a full-screen story image on an iPhone onboarding page, portrait 9:16. It is not a poster and not an app icon. A white title covers the lower third. The phone crops the left and right edges and zooms slightly from the top, so keep the story in the center column and out of the bottom edge. Do not draw any text, numbers, charts, or logo. Erase every word, letter, button, and logo already visible in this photo. Do not keep them, do not move them, do not translate them, and do not replace any word. Leave only the illustration.

Keep this exact blue genie, his face, the pointing hand, the chest gem, the gold orbital rings, and the glowing gold cube. Do not redraw the face. Place the genie in the upper half, centered. Place the cube above the middle of the frame, fully visible, not on the bottom edge.

Draw three sharp planes, all in focus. First plane: the genie, bright and alive. Second plane: the pointing hand, the orbital rings, and the gold cube, fully drawn. Third plane, behind him: many sharp stars, a clear Milky Way band, the galaxy made brighter and fully drawn, and the planets large enough to read, each with a thin polished highlight, like foil, not plastic. Do not cover his face. The sky stays in focus, not a haze.

Keep the deep star field, the galaxy, and the planets. The rings, the cube, and the chest gem read as polished foil: a thin bright edge, deeper antique gold in the shadows. The cube and the eyes carry one clean glint, like a jeweler’s stone under a soft lamp. The face stays detailed and sharp, with no lacquer on the skin. The lower third becomes a darker quiet sky for white text, still sharp, not a flat empty block. The sky stays matte and in focus. The frame looks varnished and press-ready, bright and clear at a small size and rich at a large size. No halo, no neon, no plastic, no HDR, no fog, no gaussian blur. If the face moves, the result is wrong.
```

**Принять кадр, если:** вертикальный кадр, тот же джинн, куб выше середины и в центре, кольца с кромкой фольги, букв и цифр нет.

---

### 4.5 Дети — «Защита для детей!»

| | |
|---|---|
| Файл | `Resources/HeroAssets/OnboardingHero_05.png` |
| Сейчас | горизонтальный 1536×1024. Джинн внутри золотой сферы-щита, лампа под ним, красный луч бьёт в сферу слева. Масштаб 1.09 от верха |
| Текст приложения | заголовок с Y=440. Описание длинное, с Y=522, высота 144 (шесть строк). Затемнение с Y=532 |
| Куда сесть герою | лампа, сфера и камень на груди выше Y=420. Красный луч остаётся на сфере, снаружи лампы. Низ темнее под длинный текст |
| Фольга | сфера-щит, лампа, точка удара луча, камень на груди |
| В картинку не класть | ребёнка, сайт, казино, кнопку покупки |

Ребёнка в кадр не добавлять. Защиту показывает щит.

```
This is a full-screen story image on an iPhone onboarding page, portrait 9:16. It is not a poster and not an app icon. A long white title block covers the lower third. The phone crops the sides and zooms slightly from the top. Keep the story in the center column. Do not draw any text, letters, logo, or a child. Erase every word, letter, button, and logo already visible in this photo. Do not keep them, do not move them, do not translate them, and do not replace any word. Leave only the illustration.

Keep this exact blue genie, his face, the gold protective sphere, the small gold lamp under him, and the red beam striking the sphere from the left. Do not redraw the face. Place the lamp, the sphere, and the chest gem above the middle of the frame. The red impact stays on the sphere, outside the lamp.

Draw three sharp planes, all in focus. First plane: the genie and the protective sphere, bright and alive. Second plane: the small gold lamp and the red beam, fully drawn, the impact outside the lamp. Third plane, behind the sphere: many sharp stars, a clear Milky Way band, one bright galaxy, and two or three planets with a thin polished highlight, like foil, not plastic. Do not cover his face or the lamp. The sky stays in focus, not a haze.

The sphere, the lamp, the impact point, and the chest gem read as polished foil: a thin bright edge, deeper antique gold in the shadows. The lamp and the eyes carry one clean glint, like a jeweler’s stone under a soft lamp. The face stays detailed and sharp, with no lacquer on the skin. Keep the star field sharp. The lower third becomes a darker quiet sky for a long block of white text. The sky stays matte and in focus. The frame looks varnished and press-ready, bright and clear at a small size and rich at a large size. No halo, no neon, no plastic, no HDR, no fog, no gaussian blur. If the face changes, the result is wrong.
```

**Принять кадр, если:** вертикальный кадр, щит и лампа выше середины, луч снаружи, ребёнка в кадре нет, букв нет.

---

### 4.6 Antifake — «Antifake для людей 18+»

| | |
|---|---|
| Файл | `Resources/HeroAssets/OnboardingHero_06.png` |
| Сейчас | горизонтальный 1536×1024. Джинн, золотая линия проверки: синяя точка, кольца, золотая галочка, маленький куб ниже линии. Масштаб 1.09 от верха |
| Текст приложения | заголовок с Y=496. Описание с Y=566. Затемнение с Y=552. Места по вертикали больше, чем на аналитике |
| Куда сесть герою | линия, галочка и куб выше Y=480, в центральной колонке. Лицо ещё выше |
| Фольга | линия, кольца, галочка, куб, камень на груди |
| В картинку не класть | слово Antifake, телефон, газету, буквы на галочке |

На экране заголовок именно «Antifake для людей 18+». В старых заметках встречалось «23+». В промпт цифру не писать: CapCut нарисует её на картинке.

```
This is a full-screen story image on an iPhone onboarding page, portrait 9:16. It is not a poster and not an app icon. A white title sits in the lower third, a little below the middle. The phone crops the sides and zooms slightly from the top. Keep the story in the center column. Do not draw any text, letters, numbers, logo, or a checkmark made of letters. Erase every word, letter, button, and logo already visible in this photo. Do not keep them, do not move them, do not translate them, and do not replace any word. Leave only the illustration.

Keep this exact blue genie, his face, the open hands, the gold horizontal line with the blue node, the gold rings, the gold check node, and the small cube below the line. Do not redraw the face. Place the line, the check, and the cube above the middle of the frame, in the center column. The face stays higher than the line.

Draw three sharp planes, all in focus. First plane: the genie and the open hands, bright and alive. Second plane: the gold line, the blue node, the rings, the check node, and the cube, fully drawn in the center. Third plane, behind the line: many sharp stars, a clear Milky Way band, the galaxies brighter and fully drawn, and two or three planets with a thin polished highlight, like foil, not plastic. Do not cover his face. Do not draw a number. The sky stays in focus, not a haze.

The line, the rings, the check node, the cube, and the chest gem read as polished foil: a thin bright edge, deeper antique gold in the shadows. The check node and the eyes carry one clean glint, like a jeweler’s stone under a soft lamp. The face stays detailed and sharp, with no lacquer on the skin. Keep the star field and the galaxies sharp. The lower third stays darker for white text, still a sharp sky, not a flat empty block. The sky stays matte and in focus. The frame looks varnished and press-ready, bright and clear at a small size and rich at a large size. No halo, no neon, no plastic, no HDR, no fog, no gaussian blur. If the face moves, the result is wrong.
```

**Принять кадр, если:** вертикальный кадр, линия и галочка выше середины, на галочке нет букв, фольга на линии и кубе.

---

### 4.7 Финал — «Присоединяйтесь к ALADDIN!»

| | |
|---|---|
| Файл | `Resources/HeroAssets/OnboardingHero_07.png` |
| Сейчас | 393×852. Джинн с раскрытыми руками, золотое кольцо с силуэтами семьи, куб под кольцом. Под рисунком плоский тёмно-синий прямоугольник. Масштаб 1.09 от верха |
| Текст приложения | короткая надпись и маленький логотип у самого верха (около Y=6). Описание с Y=468. Затемнение с Y=400, высота 156. С Y=556 начинается согласие и кнопки |
| Куда сесть герою | запас неба над волосами. Кольцо семьи целиком между верхом и серединой, выше Y=400. Куб сразу под кольцом, тоже выше середины. Ниже середины тёмный звёздный пол |
| Фольга | кольцо с семьёй, куб, камень на груди |
| В картинку не класть | слово ALADDIN, галочки согласия, кнопки «Начать» |

Кольцо — главный смысл кадра. Если оно сядет на Y=468, его закроет описание.

```
This is the last full-screen story image on an iPhone onboarding page, portrait 9:16. It is not a poster and not an app icon. A short title sits at the very top. A paragraph starts at the middle, and buttons cover the lower third. The picture is zoomed slightly from the top. Do not draw any text, letters, logo, checkbox, or button. Erase every word, letter, button, and logo already visible in this photo. Do not keep them, do not move them, do not translate them, and do not replace any word. Leave only the illustration.

Keep this exact blue genie, his face, the open arms, the gold ring with the family silhouettes, and the cube under the ring. Do not redraw the face. Leave a clear margin of night sky above his hair so a small title can sit at the top corner. Place the family ring in the upper-middle, fully above the middle of the frame. Place the cube directly under the ring, still above the middle.

Draw three sharp planes, all in focus. First plane: the genie, bright and alive, with open arms inside the frame. Second plane: the gold family ring and the cube, fully drawn, the ring not split. Third plane, in the sky above his hair and around the ring: many sharp stars, a clear Milky Way band, one bright galaxy, and two or three planets with a thin polished highlight, like foil, not plastic. Do not cover his face or the small title margin at the top. The sky stays in focus, not a haze.

Replace the flat empty navy block with a dark sharp star floor, quieter than the ring. Keep stars, the Milky Way, and a planet visible in that floor, still sharp. The family ring, the cube, and the chest gem read as polished foil: a thin bright edge, deeper antique gold in the shadows. The ring and the eyes carry one clean glint, like a jeweler’s stone under a soft lamp. The face stays detailed and sharp, with no lacquer on the skin. The sky stays matte and in focus. The frame looks varnished and press-ready, bright and clear at a small size and rich at a large size. No halo, no neon, no plastic, no HDR, no fog, no gaussian blur. If the face moves or the family ring splits apart, the result is wrong.
```

**Принять кадр, если:** запас неба над головой, кольцо целиком выше середины, пустой прямоугольник заменён тёмным полом, букв нет.

---

## 5. Порядок работы

| Шаг | Страница | Файл, который прикрепить |
|---|---|---|
| 1 | Язык | `OnboardingHero_00.png` |
| 2 | Семья | `OnboardingHero_01.png` |
| 3 | Агент | `OnboardingHero_02.png` |
| 4 | Родители | `OnboardingHero_03.png` |
| 5 | Аналитика | `OnboardingHero_04.png` |
| 6 | Дети | `OnboardingHero_05.png` |
| 7 | Antifake | `OnboardingHero_06.png` |
| 8 | Финал | `OnboardingHero_07.png` |

На каждом шаге одно и то же:

1. Image, 9:16, файл через **+**, миниатюра на месте.
2. Вставить английский блок только этой страницы.
3. Сверить с пунктом «Принять кадр».
4. Сохранить PNG рядом с исходником, имя `OnboardingHero_0N_capcut.png`. В каталог приложения не класть, пока владелец не скажет, что кадр принят.
5. Водяной знак CapCut в углу — кадр бракуется, как браковали его на значке.

После принятия всех восьми, отдельным шагом и только по слову владельца:

- положить резкие вертикальные PNG в `Resources/HeroAssets/` и в `Assets.xcassets/OnboardingHero_0N.imageset/`;
- целевой размер мастер-файла **1179×2556** (это 393×852 в три раза). Если CapCut отдал 9:16, лицо не растягивать: вписать в этот прямоугольник, лишнее по бокам обрезать равномерно, низ под текст не вытягивать;
- загрузка в Figma и сборка Xcode в этот план не входят.

Значок магазина этим проходом не трогать. Его промпт остаётся прежним: квадрат 1:1, про фольгу там уже сказано словами «quiet metal highlight» и «one living glint».
