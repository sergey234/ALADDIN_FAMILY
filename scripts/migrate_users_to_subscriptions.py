import sys
import os
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models import Subscription
from sqlalchemy import text

def migrate_users():
    db = SessionLocal()
    try:
        print("🚀 Starting user migration to subscription system...")
        
        # Using raw SQL to fetch users as we might not have a SQLAlchemy model for 'users' table in app/models.py
        # Based on my previous check, users table exists in the database.
        result = db.execute(text("SELECT id, email, device_id, subscription_level, trial_used, trial_end_date FROM users"))
        users = result.fetchall()
        
        count = 0
        for user in users:
            user_id = str(user.id)
            device_id = user.device_id or f"migrated_device_{user_id}"
            level = user.subscription_level or "free"
            
            # Check if subscription already exists
            existing = db.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.device_id == device_id
            ).first()
            
            if not existing:
                # Create new subscription
                status = "active"
                if user.trial_used and user.trial_end_date:
                    if user.trial_end_date > datetime.now():
                        status = "trial"
                        level = "trial"
                    else:
                        level = "free"
                
                new_sub = Subscription(
                    user_id=user_id,
                    device_id=device_id,
                    level=level,
                    status=status,
                    start_date=datetime.now(),
                    trial_end_date=user.trial_end_date,
                    limits={
                        "devices": 1 if level == "free" else (3 if level == "trial" else 10),
                        "scans_per_day": 10 if level == "free" else 100,
                        "ai_messages_per_day": 0 if level == "free" else 50,
                        "reports_per_month": 3 if level == "free" else 30,
                        "storage_gb": 1 if level == "free" else 10
                    }
                )
                db.add(new_sub)
                count += 1
        
        db.commit()
        print(f"✅ Migration completed! {count} subscriptions created.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_users()
