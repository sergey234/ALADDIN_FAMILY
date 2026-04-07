import sys

file_path = '/opt/aladdin-backend/app/config/subscription_limits.py'

with open(file_path, 'r') as f:
    content = f.read()

# Изменяем лимит для free на 6
content = content.replace('"free": 1,', '"free": 6,')
# Дополнительно, если trial = 3, то пусть тоже будет 6 для тестов
content = content.replace('"trial": 3,', '"trial": 6,')

with open(file_path, 'w') as f:
    f.write(content)

print("Limits patched.")
