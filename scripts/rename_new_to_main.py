#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Переименование new файлов в основные
Убирает суффикс _new из имен файлов
"""

import os
import shutil
from datetime import datetime

def rename_new_to_main():
    """Переименование new файлов в основные"""
    print("=" * 80)
    print("🔄 ПЕРЕИМЕНОВАНИЕ NEW ФАЙЛОВ В ОСНОВНЫЕ")
    print("=" * 80)
    
    # Файлы для переименования
    files_to_rename = [
        ('security/ai_agents/analytics_manager_new.py', 'security/ai_agents/analytics_manager.py'),
        ('security/ai_agents/dashboard_manager_new.py', 'security/ai_agents/dashboard_manager.py'),
        ('security/ai_agents/monitor_manager_new.py', 'security/ai_agents/monitor_manager.py'),
        ('security/ai_agents/report_manager_new.py', 'security/ai_agents/report_manager.py'),
        ('security/family/child_protection_new.py', 'security/family/child_protection.py'),
        ('security/microservices/api_gateway_new.py', 'security/microservices/api_gateway.py'),
        ('security/preliminary/behavioral_analysis_new.py', 'security/preliminary/behavioral_analysis.py'),
        ('security/preliminary/trust_scoring_new.py', 'security/preliminary/trust_scoring.py'),
        ('security/privacy/universal_privacy_manager_new.py', 'security/privacy/universal_privacy_manager.py')
    ]
    
    # Создаем backup перед переименованием
    backup_dir = f"backup_before_rename_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"📁 Создан backup: {backup_dir}")
    
    renamed_count = 0
    
    for old_path, new_path in files_to_rename:
        old_full_path = f"/Users/sergejhlystov/ALADDIN_NEW/{old_path}"
        new_full_path = f"/Users/sergejhlystov/ALADDIN_NEW/{new_path}"
        
        if os.path.exists(old_full_path):
            # Создаем backup
            backup_path = os.path.join(backup_dir, old_path.replace('/', '_'))
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(old_full_path, backup_path)
            
            # Переименовываем файл
            shutil.move(old_full_path, new_full_path)
            renamed_count += 1
            
            print(f"✅ Переименован: {old_path} → {new_path}")
        else:
            print(f"⚠️ Файл не найден: {old_path}")
    
    print(f"\n📊 РЕЗУЛЬТАТ ПЕРЕИМЕНОВАНИЯ:")
    print(f"   Переименовано файлов: {renamed_count}")
    print(f"   Backup создан: {backup_dir}")
    
    return renamed_count

if __name__ == "__main__":
    rename_new_to_main()