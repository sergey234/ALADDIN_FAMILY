#!/usr/bin/env python3
# Скрипт для исправления роутинга /privacy и /terms

import re

config_file = '/etc/nginx/sites-available/aladdin-ai.ru'

# Читаем конфиг
with open(config_file, 'r') as f:
    content = f.read()

# Заменяем location блок для privacy - вместо редиректа показываем файл напрямую
old_privacy = r'location = /privacy \{[^}]*return 301 /privacy\.html;[^}]*\}'
new_privacy = '''location = /privacy {
        try_files /privacy.html =404;
    }'''

content = re.sub(old_privacy, new_privacy, content, flags=re.DOTALL)

# Заменяем location блок для terms
old_terms = r'location = /terms \{[^}]*return 301 /terms\.html;[^}]*\}'
new_terms = '''location = /terms {
        try_files /terms.html =404;
    }'''

content = re.sub(old_terms, new_terms, content, flags=re.DOTALL)

# Сохраняем
with open(config_file, 'w') as f:
    f.write(content)

print('✅ Location блоки обновлены: вместо редиректа показываем файлы напрямую')
