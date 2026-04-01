import os
import sys
import json
import importlib.util

import jwt
from fastapi.testclient import TestClient

# Гарантируем, что в sys.path есть корень проекта с `main.py` и пакетом `app`
# test_gamification_rewards_live.py лежит в docs/server/, поэтому поднимаемся на 3 уровня вверх.
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Явно подгружаем корневой main.py, чтобы не схватить docs/server/main.py
MAIN_PATH = os.path.join(PROJECT_ROOT, "main.py")
spec = importlib.util.spec_from_file_location("aladdin_main_root", MAIN_PATH)
main_module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(main_module)  # type: ignore[arg-type]
app = main_module.app

from app.auth.auth import JWT_SECRET, JWT_ALGORITHM


def show(name, resp):
    print(f"=== {name} ===")
    print("status:", resp.status_code)
    try:
        print("body:", json.dumps(resp.json(), ensure_ascii=False))
    except Exception:
        print("raw:", resp.text)
    print()


def main() -> None:
    client = TestClient(app)

    user_id = "test_user_123"
    parent_id = "parent_123"

    token = jwt.encode({"user_id": user_id}, JWT_SECRET, algorithm=JWT_ALGORITHM)
    headers = {"Authorization": f"Bearer {token}"}

    # 1) Топап баланса
    resp = client.post(
        "/api/gamification/balance",
        headers=headers,
        json={"userId": user_id, "amount": 500, "reason": "test_setup"},
    )
    show("balance_topup", resp)

    # 2) Каталог наград
    resp = client.get(f"/api/gamification/rewards?userId={user_id}", headers=headers)
    show("rewards_catalog", resp)

    # 3) Магазин наград
    resp = client.get(
        f"/api/gamification/rewards/shop?userId={user_id}", headers=headers
    )
    show("rewards_shop", resp)

    # 4) История наград (до операций)
    resp = client.get(
        f"/api/gamification/rewards/history?userId={user_id}&limit=10", headers=headers
    )
    show("rewards_history_before", resp)

    # 5) Claim обычной награды
    resp = client.post(
        "/api/gamification/rewards/claim",
        headers=headers,
        json={"userId": user_id, "rewardId": "reward_1", "deviceId": "dev_ios"},
    )
    show("reward_claim", resp)

    # 6) Purchase товара из магазина
    resp = client.post(
        "/api/gamification/rewards/purchase",
        headers=headers,
        json={"userId": user_id, "rewardId": "shop_1", "deviceId": "dev_ios"},
    )
    show("reward_purchase", resp)

    # 7) Give награды ребёнку
    resp = client.post(
        f"/api/gamification/rewards/give?childId={user_id}&rewardId=reward_2&parentId={parent_id}",
        headers=headers,
    )
    show("reward_give", resp)

    # 8) История наград после операций
    resp = client.get(
        f"/api/gamification/rewards/history?userId={user_id}&limit=10", headers=headers
    )
    show("rewards_history_after", resp)


if __name__ == "__main__":
    main()

