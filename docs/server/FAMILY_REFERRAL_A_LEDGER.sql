-- Family Invite Pro (Вариант A) — ledger
-- Apply on MAIN :8002 after GO DEPLOY (py_compile + migrate)

CREATE TABLE IF NOT EXISTS family_referral_ledger (
    id SERIAL PRIMARY KEY,
    referrer_user_id INTEGER NOT NULL,
    friend_user_id INTEGER NOT NULL,
    referrer_family_id VARCHAR(64) NOT NULL,
    friend_family_id VARCHAR(64) NOT NULL,
    referral_code VARCHAR(32),
    status VARCHAR(24) NOT NULL DEFAULT 'granted',
    reason VARCHAR(64) NOT NULL,
    friend_discount_percent INTEGER NOT NULL DEFAULT 20,
    referrer_protection_days INTEGER NOT NULL DEFAULT 0,
    tier VARCHAR(24),
    device_soft_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT family_referral_ledger_pair UNIQUE (referrer_family_id, friend_family_id)
);

CREATE INDEX IF NOT EXISTS idx_frl_referrer ON family_referral_ledger(referrer_user_id);
CREATE INDEX IF NOT EXISTS idx_frl_friend ON family_referral_ledger(friend_user_id);
CREATE INDEX IF NOT EXISTS idx_frl_created ON family_referral_ledger(created_at);
