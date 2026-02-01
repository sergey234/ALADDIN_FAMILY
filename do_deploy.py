#!/usr/bin/env python3
import os
import sys

# Переходим в директорию проекта
os.chdir("/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS")

print("🚀 Запуск развертывания через expect скрипт...")
print("")

# Выполняем готовый expect скрипт
exit_code = os.system("/usr/bin/expect deploy_api_gateway_final.exp")

if exit_code == 0:
    print("\n✅ Развертывание завершено успешно!")
    sys.exit(0)
else:
    print(f"\n⚠️ Код выхода: {exit_code}")
    sys.exit(1)



