# ALADDIN — канон цвета «Шьям» (сайт + iOS)

**Статус:** канон продукта · 2026-10-10  
**Источник настроения:** референсы «цвет Шьям» (сапфиры · лотосы · грозовые облака · павлин · золото) + уже живые токены `landing/styles.css` и `Shared/Styles/Colors.swift`.  
**Не путать с религиозным текстом референса** — в продукте это **бренд-палитра**: ночное небо + свет + золото семьи.

---

## 1. Триада Шьям (база)

Одновременно три опоры (как в референсе «чёрный · белый(золотой) · синий»):

| Роль | Имя токена | HEX | Где |
|------|------------|-----|-----|
| Тьма / ночь | `shyamNight` | `#07112A` | фон сайта `--shyam-night`, storm base |
| Свет / золото | `shyamGold` | `#F59E0B` | = `secondaryGold` / `goldPrimary` · **семейный тариф** |
| Синева неба | `shyamSapphire` | `#4C6FFF` | = сайт `--sapphire` · личный тариф |

Дополнения из референса (акценты карточек и hero):

| Роль | Имя | HEX | Метафора |
|------|-----|-----|----------|
| Грозовые облака | `shyamStorm` | `#5B8DEF` | спокойный вход / free |
| Павлин | `shyamPeacock` | `#36D6AE` | = сайт `--peacock` · trial |
| Лотос (violet-blue) | `shyamLotus` | `#8B5CF6` | зеркальный акцент · premium |
| Тушь / ink | `shyamInk` | `#07080D` | глубокая тень |
| Лунный свет | `shyamMoon` | `#F3F3F3` | блик / текст на тёмном |

**Правило золота:** золото (`shyamGold`) — **только семейный тариф** на цветной карточке тарифа/семьи. Не красить free в жёлтый.

---

## 2. Карточка тарифа (главная + профиль)

Единый helper: `TariffAccentPalette.color(for:)`.

| `SubscriptionLevel` | Токен | HEX | Было раньше |
|---------------------|-------|-----|-------------|
| `free` | `shyamStorm` | `#5B8DEF` | secondaryGold (жёлтый) |
| `trial` | `shyamPeacock` | `#36D6AE` | teal rgb(0.22,0.78,0.72) |
| `personal` | `shyamSapphire` | `#4C6FFF` | системный `.blue` |
| **`family`** | **`shyamGold`** | **`#F59E0B`** | было purple → **золото по решению владельца** |
| `premium` | `shyamLotus` | `#8B5CF6` | системный `.orange` |

UI: `LinearGradient` от цвета к `opacity(0.85)`, обводка/тень от того же цвета (как сейчас на главной).

---

## 3. Связь с сайтом (`landing/styles.css`)

| CSS var | HEX | Соответствие iOS |
|---------|-----|------------------|
| `--shyam-night` | `#07112a` | `shyamNight` |
| `--sapphire` | `#4c6fff` | `shyamSapphire` |
| `--peacock` | `#36d6ae` | `shyamPeacock` |
| `--gold` / CTA gold | `#f5c86e` / `#F59E0B` | сайт soft-gold vs app `shyamGold` для тарифа |
| `--lotus-mist` | `rgba(91,74,138,0.06)` | мягкий mist; насыщенный акцент = `shyamLotus` |
| `--shyam-storm-card` | `#5B8DEF` | free card |
| `--shyam-lotus` | `#8B5CF6` | premium |

Сайт **не** уходит в neon purple-секции: лотос — акцент карточек/CTA premium, не заливка страницы.

---

## 4. Файлы-источники правды

| Слой | Файл |
|------|------|
| Этот канон | `docs/ALADDIN_SHYAM_COLOR_CANON.md` |
| iOS tokens | `Shared/Styles/Colors.swift` (`shyam*`) |
| iOS mapping | `Shared/Styles/TariffAccentPalette.swift` |
| Главная | `Screens/01_MainScreen.swift` → `currentTariffColor` |
| Профиль | `Screens/11_ProfileScreen.swift` → та же палитра |
| Сайт | `landing/styles.css` `:root` |
| Старый handoff тарифа | `docs/REGISTRATION_AND_MAIN_TARIFF_CARD.md` §6.2 (обновить ссылкой сюда) |
| Storm Mesh | `docs/STORM_MESH_PREMIUM_DESIGN_HANDOFF.md` (navy+gold остаётся фоном) |
| Персонажи | `docs/ALADDIN_Character_Bible.md` (индиго+золото — согласовано) |

---

## 5. Что не меняем этим каноном

- Storm Mesh фоны экранов (hub/family/…) — как в Storm handoff.
- Онбординг hero wash по слайдам (`HeroAmbientPresentation`) — сюжетные washes, не тариф.
- Danger/success semantic colors — отдельно от тарифа.

---

## 6. Чеклист проверки

1. free → голубая «гроза», не жёлтая.  
2. family → золотая.  
3. trial → павлин/бирюза.  
4. personal → сапфир.  
5. premium → лотос violet-blue.  
6. Сайт и app: одинаковые HEX из §1–2.
