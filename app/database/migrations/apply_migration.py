#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для применения миграции компонентов защиты
Применяет SQL файл create_component_tables.sql к базе данных PostgreSQL
"""

import os
import sys
import psycopg2
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def apply_migration():
    """Применить миграцию к базе данных"""
    
    # Получаем параметры подключения из переменных окружения
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://aladdin_user:AladdinSecure2024!@localhost:5432/aladdin_db"
    )
    
    # Парсим DATABASE_URL
    # Формат: postgresql://user:password@host:port/database
    try:
        # Убираем префикс postgresql://
        url_part = database_url.replace("postgresql://", "")
        
        # Разделяем на части
        auth_part, host_db_part = url_part.split("@")
        user, password = auth_part.split(":")
        host_port, database = host_db_part.split("/")
        
        if ":" in host_port:
            host, port = host_port.split(":")
        else:
            host = host_port
            port = "5432"
            
    except Exception as e:
        print(f"❌ Ошибка парсинга DATABASE_URL: {e}")
        print(f"   Используйте формат: postgresql://user:password@host:port/database")
        return False
    
    # Путь к SQL файлу миграции
    migration_file = Path(__file__).parent / "create_component_tables.sql"
    
    if not migration_file.exists():
        print(f"❌ Файл миграции не найден: {migration_file}")
        return False
    
    # Читаем SQL файл
    try:
        with open(migration_file, "r", encoding="utf-8") as f:
            sql_content = f.read()
    except Exception as e:
        print(f"❌ Ошибка чтения файла миграции: {e}")
        return False
    
    # Подключаемся к базе данных
    try:
        print(f"🔌 Подключение к базе данных: {host}:{port}/{database}")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        conn.autocommit = False
        
        cursor = conn.cursor()
        
        print("✅ Подключение установлено")
        print("📝 Применение миграции...")
        
        # Выполняем SQL
        cursor.execute(sql_content)
        
        # Коммитим изменения
        conn.commit()
        
        print("✅ Миграция успешно применена!")
        
        # Проверяем созданные таблицы
        print("\n📊 Проверка созданных таблиц:")
        tables_to_check = [
            "dark_web_leaks",
            "dark_web_scans",
            "identity_theft_attempts",
            "location_requests",
            "data_cleanup_records",
            "tracker_blocks",
            "ai_category_reports"
        ]
        
        for table_name in tables_to_check:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            
            exists = cursor.fetchone()[0]
            status = "✅" if exists else "❌"
            print(f"   {status} {table_name}")
        
        # Проверяем индексы
        print("\n📊 Проверка индексов:")
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename IN (
                'dark_web_leaks', 'dark_web_scans', 'identity_theft_attempts',
                'location_requests', 'data_cleanup_records', 'tracker_blocks',
                'ai_category_reports'
            )
            ORDER BY tablename, indexname;
        """)
        
        indexes = cursor.fetchall()
        if indexes:
            for index in indexes:
                print(f"   ✅ {index[0]}")
        else:
            print("   ⚠️ Индексы не найдены")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Миграция завершена успешно!")
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
    print("=" * 60)
    print("МИГРАЦИЯ БАЗЫ ДАННЫХ: Компоненты защиты")
    print("=" * 60)
    print()
    
    success = apply_migration()
    
    if success:
        print("\n✅ Все готово!")
        sys.exit(0)
    else:
        print("\n❌ Миграция не применена!")
        sys.exit(1)
