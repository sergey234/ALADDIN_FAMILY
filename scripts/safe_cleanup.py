#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Безопасная очистка дублированных файлов
Удаляет старые версии, оставляя новые
"""

import os
import shutil
from datetime import datetime

def safe_cleanup():
    """Безопасная очистка дублированных файлов"""
    print("=" * 80)
    print("🧹 БЕЗОПАСНАЯ ОЧИСТКА ДУБЛИРОВАННЫХ ФАЙЛОВ")
    print("=" * 80)
    
    # Файлы для удаления
    files_to_delete = [
        'scripts/verify_backup_quality.py',
        'security/ai_agents/analytics_manager_old.py',
        'security/ai_agents/dashboard_manager_old.py',
        'security/ai_agents/monitor_manager_old.py',
        'security/ai_agents/report_manager_old.py',
        'security/family/child_protection_old.py',
        'security/microservices/api_gateway_old.py',
        'security/preliminary/behavioral_analysis_old.py',
        'security/preliminary/trust_scoring_old.py',
        'security/privacy/universal_privacy_manager_old.py',
        'security/safe_function_manager_backup_20250909_021153.py',
        'security/safe_function_manager_fixed.py'
    ]
    
    # Создаем backup перед удалением
    backup_dir = f"backup_before_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"📁 Создан backup: {backup_dir}")
    
    deleted_count = 0
    total_size = 0
    
    for file_path in files_to_delete:
        full_path = f"/Users/sergejhlystov/ALADDIN_NEW/{file_path}"
        
        if os.path.exists(full_path):
            # Получаем размер файла
            file_size = os.path.getsize(full_path)
            total_size += file_size
            
            # Создаем backup
            backup_path = os.path.join(backup_dir, file_path.replace('/', '_'))
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(full_path, backup_path)
            
            # Удаляем файл
            os.remove(full_path)
            deleted_count += 1
            
            print(f"✅ Удален: {file_path} ({file_size/1024:.1f}KB)")
        else:
            print(f"⚠️ Файл не найден: {file_path}")
    
    print(f"\n📊 РЕЗУЛЬТАТ ОЧИСТКИ:")
    print(f"   Удалено файлов: {deleted_count}")
    print(f"   Освобождено места: {total_size/1024/1024:.1f}MB")
    print(f"   Backup создан: {backup_dir}")
    
    return deleted_count, total_size

if __name__ == "__main__":
    safe_cleanup()