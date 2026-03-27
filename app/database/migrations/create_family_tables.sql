-- ═══════════════════════════════════════════════════════════════
-- МИГРАЦИЯ: Family (families + family_members)
-- Дата: 2026-03-25
-- Описание: Создает таблицы для семей и участников семьи (источник правды для /api/family/*)
-- ═══════════════════════════════════════════════════════════════

-- Таблица семей
CREATE TABLE IF NOT EXISTS families (
    id TEXT PRIMARY KEY,                       -- "FAM_XXXXXXXXXXXX"
    owner_user_id INTEGER NOT NULL,            -- users.id
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_families_owner_user_id ON families(owner_user_id);

-- Таблица участников семьи
CREATE TABLE IF NOT EXISTS family_members (
    id TEXT PRIMARY KEY,                       -- "MEM_XXXXXXXX"
    family_id TEXT NOT NULL,
    user_id INTEGER NULL,                      -- users.id (может быть NULL для приглашённых/неактивированных)
    name TEXT NOT NULL,                        -- анонимное имя/лейбл, без персональных данных
    role TEXT NOT NULL,                        -- parent|child|teenager|elderly|other
    status TEXT NOT NULL DEFAULT 'protected',  -- protected|warning|danger|offline
    threats_blocked INTEGER NOT NULL DEFAULT 0,
    devices INTEGER NOT NULL DEFAULT 0,
    last_active TEXT NOT NULL DEFAULT '',      -- "HH:mm" или пусто
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_family_members_family_id
        FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_family_members_family_id ON family_members(family_id);
CREATE INDEX IF NOT EXISTS idx_family_members_user_id ON family_members(user_id);
CREATE INDEX IF NOT EXISTS idx_family_members_role ON family_members(role);

