#!/usr/bin/env python3
import json
import os
import time
from datetime import datetime

def monitor_registry():
    registry_path = "data/sfm/function_registry.json"
    expected_functions = 327
    
    while True:
        try:
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            
            current_functions = len(registry.get('functions', {}))
            
            if current_functions < expected_functions:
                print(f"🚨 ALERT: Registry was overwritten! Expected {expected_functions}, got {current_functions}")
                # Здесь можно добавить логику восстановления
                
        except Exception as e:
            print(f"❌ Error monitoring registry: {e}")
        
        time.sleep(60)  # Проверяем каждую минуту

if __name__ == "__main__":
    monitor_registry()
