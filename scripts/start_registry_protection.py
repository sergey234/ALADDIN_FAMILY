#!/usr/bin/env python3
# Автоматический запуск системы защиты реестра
import sys
sys.path.append('/Users/sergejhlystov/ALADDIN_NEW')
from scripts.registry_security_manager import RegistrySecurityManager

if __name__ == "__main__":
    manager = RegistrySecurityManager()
    manager.start_full_protection()
    print("🛡️ Система защиты реестра запущена")
