#!/bin/bash

# 🎯 Скрипт для открытия Xcode с настройками для Widgets

echo "🎯 Открытие Xcode для настройки Widgets..."

# Открываем Xcode
open ALADDIN.xcodeproj

echo "✅ Xcode открыт!"
echo ""
echo "📋 Следующие шаги в Xcode:"
echo "1. File → New → Target → Widget Extension"
echo "2. Product Name: ALADDINWidgets"
echo "3. Bundle Identifier: family.aladdin.ios.widgets"
echo "4. Настройте App Groups для обоих targets"
echo "5. Добавьте файлы из папки ALADDINWidgets/"
echo ""
echo "📖 Подробная инструкция: MANUAL_WIDGET_SETUP.md"
echo "🎯 Готовые файлы виджетов находятся в папке ALADDINWidgets/"
