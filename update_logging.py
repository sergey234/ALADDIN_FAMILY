#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для обновления логирования в smart_notification_manager_extra.py
"""

import re

def update_logging():
    """Обновляет логирование на структурированное"""
    
    file_path = 'security/ai_agents/smart_notification_manager_extra.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Паттерны для замены
    patterns = [
        # self.logger.error(f"Ошибка ...: {e}")
        (r'self\.logger\.error\(f"([^"]+): \{e\}"\)', 
         r'self.logger.error(\n                "\1",\n                error=str(e)\n            )'),
        
        # self.logger.error(f"Ошибка ...")
        (r'self\.logger\.error\(f"([^"]+)"\)', 
         r'self.logger.error("\1")'),
        
        # self.logger.info(f"...")
        (r'self\.logger\.info\(f"([^"]+)"\)', 
         r'self.logger.info("\1")'),
    ]
    
    # Применяем замены
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Записываем обновленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Логирование обновлено на структурированное!")

if __name__ == '__main__':
    update_logging()