#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск усиленного перемещения backup файлов
Полное соответствие согласованному плану

Автор: ALADDIN Security Team
Версия: 2.0
Дата: 2025-01-27
"""

import sys
import os

# Добавляем путь к скриптам
sys.path.append(os.path.dirname(__file__))

from enhanced_fast_backup_mover import EnhancedFastBackupMover

def main():
    """Запуск усиленного перемещения"""
    print("🚀 ЗАПУСК УСИЛЕННОГО ПЕРЕМЕЩЕНИЯ BACKUP ФАЙЛОВ")
    print("📋 ПОЛНОЕ СООТВЕТСТВИЕ СОГЛАСОВАННОМУ ПЛАНУ")
    print("=" * 70)
    
    # Создаем экземпляр и запускаем
    mover = EnhancedFastBackupMover()
    result = mover.run_enhanced_movement()
    
    return result

if __name__ == "__main__":
    main()