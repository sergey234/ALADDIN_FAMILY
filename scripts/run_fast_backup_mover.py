#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск быстрого перемещения backup файлов
Простой скрипт для запуска FastBackupMover

Автор: ALADDIN Security Team
Версия: 1.0
Дата: 2025-01-27
"""

import sys
import os

# Добавляем путь к скриптам
sys.path.append(os.path.dirname(__file__))

from fast_backup_mover import FastBackupMover

def main():
    """Запуск быстрого перемещения"""
    print("🚀 ЗАПУСК БЫСТРОГО ПЕРЕМЕЩЕНИЯ BACKUP ФАЙЛОВ")
    print("=" * 60)
    
    # Создаем экземпляр и запускаем
    mover = FastBackupMover()
    result = mover.run_fast_movement()
    
    return result

if __name__ == "__main__":
    main()