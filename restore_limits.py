import sys

file_path = '/opt/aladdin-backend/app/config/subscription_limits.py'

with open(file_path, 'r') as f:
    content = f.read()

# Возвращаем оригинальные лимиты
content = content.replace('"free": 6,', '"free": 1,')
content = content.replace('"trial": 6,', '"trial": 3,')

with open(file_path, 'w') as f:
    f.write(content)

print("Limits restored.")
