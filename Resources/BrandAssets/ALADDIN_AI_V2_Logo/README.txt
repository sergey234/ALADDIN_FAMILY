ALADDIN AI — Wordmark V2 (прозрачный, без космоса)
=================================================

Канон для онбординга OB_01 и OB_07: только золотые буквы «ALADDIN AI», PNG с альфой.

ФАЙЛЫ (источник для Figma + Xcode)
----------------------------------
WORDMARK_V2_transparent_master.png      — 361×104, прозрачный фон
WORDMARK_V2_transparent_figma_1x.png    — то же, заливка в Figma FIT
WORDMARK_V2_transparent_figma_1x@2x.png
WORDMARK_V2_transparent_figma_1x@3x.png

Справочно (с фоном, не в app):
ALADDIN_AI_logo_V2_master.png           — cinematic board 670×340
REFERENCE_V1_V2_board.png
BLOCK_aladdin_logo_V2_*.png             — устаревшие opaque-экспорты

FIGMA (KvkUdyb5Ll31Z9FSzCbpNl)
------------------------------
| Слой | Node ID | Размер | Режим |
|------|---------|--------|-------|
| EXPORT_WORDMARK_V2_transparent | 185:53 | 361×104 | экспорт-канон |
| WORDMARK_V2_raster | 185:54 | 361×104 | FIT |
| WORDMARK_V2 (OB_01) | 88:53 | 361×104 @ (16,484) | FIT |
| WORDMARK_V2 (OB_07) | 168:53 | 361×104 | FIT |

Загрузка: WORDMARK_V2_transparent_figma_1x.png через MCP upload_assets, scaleMode=FIT.

XCODE
-----
Assets.xcassets/OnboardingLogo_V2_Cinematic.imageset
Синхронизация: python3 scripts/sync_wordmark_v2_transparent.py

SWIFT
-----
Screens/14_OnboardingScreen.swift → OnboardingLogoV2View (contentIndex 0 и 6)

Обновлено: 2026-05-21
