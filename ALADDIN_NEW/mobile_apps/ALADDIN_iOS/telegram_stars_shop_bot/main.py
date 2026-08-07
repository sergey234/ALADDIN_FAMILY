"""
Точка входа: запуск из корня пакета.

  cd telegram_stars_shop_bot
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  cp env.example .env   # заполните BOT_TOKEN и ADMIN_IDS
  python main.py
"""

from bot.main import main

if __name__ == "__main__":
    main()
