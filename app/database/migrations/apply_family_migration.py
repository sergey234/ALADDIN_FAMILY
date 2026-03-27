#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для применения миграции Family (families + family_members)
Применяет SQL файл create_family_tables.sql к базе данных PostgreSQL
"""

import os
import sys
import psycopg2
from pathlib import Path


def _parse_database_url(database_url: str):
    # Формат: postgresql://user:password@host:port/database
    url_part = database_url.replace("postgresql://", "")
    auth_part, host_db_part = url_part.split("@")
    user, password = auth_part.split(":")
    host_port, database = host_db_part.split("/")
    if ":" in host_port:
        host, port = host_port.split(":")
    else:
        host, port = host_port, "5432"
    return host, port, database, user, password


def apply_migration() -> bool:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://aladdin_user:AladdinSecure2024!@localhost:5432/aladdin_db",
    )

    try:
        host, port, database, user, password = _parse_database_url(database_url)
    except Exception as e:
        print(f"❌ Ошибка парсинга DATABASE_URL: {e}")
        return False

    migration_file = Path(__file__).parent / "create_family_tables.sql"
    if not migration_file.exists():
        print(f"❌ Файл миграции не найден: {migration_file}")
        return False

    sql_content = migration_file.read_text(encoding="utf-8")

    conn = None
    try:
        print(f"🔌 Подключение к базе данных: {host}:{port}/{database}")
        conn = psycopg2.connect(host=host, port=port, database=database, user=user, password=password)
        conn.autocommit = False
        cursor = conn.cursor()

        print("📝 Применение миграции Family...")
        cursor.execute(sql_content)
        conn.commit()
        print("✅ Миграция Family успешно применена!")

        print("\n📊 Проверка созданных таблиц:")
        for table_name in ["families", "family_members"]:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_name = %s
                );
                """,
                (table_name,),
            )
            exists = cursor.fetchone()[0]
            status = "✅" if exists else "❌"
            print(f"   {status} {table_name}")

        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"❌ Ошибка базы данных: {e}")
        return False
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Неожиданная ошибка: {e}")
        return False


if __name__ == "__main__":
    ok = apply_migration()
    sys.exit(0 if ok else 1)

