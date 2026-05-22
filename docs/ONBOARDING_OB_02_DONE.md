# OB_02 — принято (что сделано)

**Figma:** `103:53` · **iOS:** `currentPage` = 2 · `contentIndex` = 1 · asset `OnboardingHero_02`

## Герой (почему так виден)

1. **Не full-bleed crop** из master 1536×1024 — при cover обрезались **обе руки** по бокам.
2. Взята готовая зона **`OnboardingHero_02_figma_zone_361x460.png`** (весь силуэт + ладони + лампа).
3. Зона **увеличена до ~94% ширины** (369×470), вставлена **по центру** на фон **`#0a1128`** (10, 17, 40).
4. Итоговый PNG для макета/приложения: **`OB02_center_zone94_393x852.png`** (бэкап: `docs/backup/onboarding_ob02_20260522_164358/crop_variants/`).

Отклонено: `left25` (сдвиг влево — видна одна рука, дух уехал).

## Текст (читаемость)

| Элемент | Figma Y | Код `OnboardingFigmaAnchor` case 1 |
|---------|---------|-------------------------------------|
| Заголовок | 533, x=12 | `CGRect(x: 12, y: 533, …)` |
| Описание | 607, x=12 | `CGRect(x: 12, y: 607, …)` |
| Scrim | y=552, h=300 | opacity **0.42** |
| Шрифт | SF Pro Bold 24 / Regular 16 | белый body, center |
| Градиент низа | `HeroBottomReadableGradient(strong: true)` | для `currentPage` 1…6 |

## SYNC (после «принято»)

1. Скопировать финальный PNG в `Assets.xcassets/OnboardingHero_02.imageset/`.
2. При необходимости upload в Figma `103:54` (тот же файл).
3. **SYNC-D:** симулятор SE + Pro Max ≈ макет.

## Открыть в симуляторе

```bash
xcrun simctl launch booted family.aladdin.ios -RESET_ONBOARDING -OnboardingPage2
```
