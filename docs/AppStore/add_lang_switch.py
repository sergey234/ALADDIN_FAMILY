#!/usr/bin/env python3
# Скрипт для добавления переключателя языка на страницы privacy.html и terms.html

import re
import sys

def add_language_switch(file_path):
    """Добавляет переключатель языка RU/EN на страницу"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Переключатель языка (HTML)
    language_switch = '''
      <div style="text-align: right; margin-bottom: 16px; display: flex; gap: 8px; justify-content: flex-end; align-items: center;">
        <span style="font-size: 14px; color: #666; margin-right: 8px;">Language:</span>
        <button onclick="switchLanguage('ru')" id="lang-ru" style="padding: 6px 12px; border: 1px solid #3B82F6; background: #3B82F6; color: #fff; cursor: pointer; border-radius: 4px; font-size: 14px; font-weight: 500;">RU</button>
        <button onclick="switchLanguage('en')" id="lang-en" style="padding: 6px 12px; border: 1px solid #ccc; background: #fff; color: #000; cursor: pointer; border-radius: 4px; font-size: 14px;">EN</button>
      </div>
'''
    
    # JavaScript для переключения
    js_code = '''
<script>
let currentLang = localStorage.getItem('preferredLanguage') || 'ru';

function switchLanguage(lang) {
  currentLang = lang;
  document.documentElement.lang = lang;
  localStorage.setItem('preferredLanguage', lang);
  
  // Обновление кнопок
  const ruBtn = document.getElementById('lang-ru');
  const enBtn = document.getElementById('lang-en');
  
  if (ruBtn && enBtn) {
    if (lang === 'ru') {
      ruBtn.style.background = '#3B82F6';
      ruBtn.style.color = '#fff';
      ruBtn.style.borderColor = '#3B82F6';
      enBtn.style.background = '#fff';
      enBtn.style.color = '#000';
      enBtn.style.borderColor = '#ccc';
    } else {
      enBtn.style.background = '#3B82F6';
      enBtn.style.color = '#fff';
      enBtn.style.borderColor = '#3B82F6';
      ruBtn.style.background = '#fff';
      ruBtn.style.color = '#000';
      ruBtn.style.borderColor = '#ccc';
    }
  }
  
  // Здесь можно добавить переключение контента
  // Пока просто меняем lang атрибут
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
  switchLanguage(currentLang);
});
</script>
'''
    
    # Вставляем переключатель после ссылки "Назад на главную"
    content = re.sub(
        r'(<a href="index.html"[^>]*>.*?</a>)',
        r'\1' + language_switch,
        content,
        flags=re.DOTALL
    )
    
    # Вставляем JavaScript перед </head>
    content = re.sub(r'</head>', js_code + '\n</head>', content)
    
    # Сохраняем
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Language switch added to {file_path}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 add_lang_switch.py <file1> [file2] ...")
        sys.exit(1)
    
    for file_path in sys.argv[1:]:
        try:
            add_language_switch(file_path)
        except Exception as e:
            print(f"❌ Error: {e}")
