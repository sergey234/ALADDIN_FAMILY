import unittest
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal
from app.repositories import SubscriptionRepository
from app.models import Subscription, UsageTracking, AuditLog

class TestSubscriptionSystem(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.repo = SubscriptionRepository(self.db)
        self.test_user_id = "test_user_999"
        self.test_device_id = "test_device_999"
        
        # Cleanup previous tests
        self.db.query(Subscription).filter(Subscription.user_id == self.test_user_id).delete()
        self.db.commit()

    def tearDown(self):
        self.db.query(Subscription).filter(Subscription.user_id == self.test_user_id).delete()
        self.db.commit()
        self.db.close()

    def test_subscription_lifecycle(self):
        print("\n🧪 Testing Subscription Lifecycle...")
        
        # 1. Create
        sub_data = {
            "user_id": self.test_user_id,
            "device_id": self.test_device_id,
            "level": "free",
            "status": "active",
            "start_date": datetime.now()
        }
        sub = self.repo.create_subscription(sub_data)
        self.assertIsNotNone(sub.id)
        self.assertEqual(sub.level, "free")
        print("✅ Subscription created")

        # 2. Get
        fetched = self.repo.get_subscription_by_user_device(self.test_user_id, self.test_device_id)
        self.assertEqual(fetched.id, sub.id)
        print("✅ Subscription fetched")

        # 3. Update (Upgrade to Premium)
        updates = {
            "level": "premium",
            "end_date": datetime.now() + timedelta(days=30)
        }
        updated = self.repo.update_subscription(sub.id, updates)
        self.assertEqual(updated.level, "premium")
        self.assertEqual(updated.version, 2)
        print("✅ Subscription upgraded")

        # 4. Usage Tracking
        usage = self.repo.increment_usage(sub.id, "ai_messages", 5)
        self.assertEqual(usage.amount, 5)
        
        usage_again = self.repo.increment_usage(sub.id, "ai_messages", 3)
        self.assertEqual(usage_again.amount, 8)
        print("✅ Usage tracking works")

if __name__ == "__main__":
    unittest.main()
