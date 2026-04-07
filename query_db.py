import sys
import os
sys.path.append('/opt/aladdin-backend/backend')
sys.path.append('/opt/aladdin-backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Assuming postgres DB is on localhost or accessible via standard env
try:
    from app.database.database import engine
except Exception as e:
    print(f"Error importing engine: {e}")
    sys.exit(1)

Session = sessionmaker(bind=engine)
db = Session()

device_id = "8993C837-3B23-41A5-B4D3-E4C346606AE7"
result = db.execute(text("SELECT id, user_id, device_id, level, trial_end_date FROM subscriptions WHERE device_id = :d"), {"d": device_id}).fetchone()
print(f"DB Result: {result}")
db.close()
