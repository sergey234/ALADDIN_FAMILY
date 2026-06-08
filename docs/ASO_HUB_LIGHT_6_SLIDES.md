# Batch 8 — ASO 6 slides (hub light palette)

**Статус:** ✅ build 227  
**Claim:** «Защита семьи. Умный родконтроль. Обучение без страха.»  
**Палитра:** Storm Mesh `.hub` light premium — те же tokens, что `01_MainScreen` (≤ Main brightness)

## Экспорт

1. Xcode → `StormMeshBackground.swift` → Preview **「Batch 8 — ASO 6 slides hub light」**
2. Screenshot каждого slide (393×852) для App Store Connect
3. Сверка side-by-side с Main simulator — indigo / gold / scrim 28%

## 6 slides

| # | Заголовок | Mesh variant | Экран-референс |
|---|-----------|--------------|----------------|
| 1 | Защита семьи 24/7 | `.hub` | Main |
| 2 | Умный родконтроль | `.grow` | Parental |
| 3 | Обучение без страха | `.growWarm` | Child |
| 4 | AI для родителей | `.ai` | AI Assistant |
| 5 | Все устройства — одна панель | `.shield` | Devices |
| 6 | Попробуйте бесплатно | `.premium` | Tariffs |

Код превью: `ASOHubLightSlideView` / `ASOHubLightSlides_Previews` в `Shared/Components/StormMeshBackground.swift` (#if DEBUG).
