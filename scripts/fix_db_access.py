import pymysql

def fix_tables():
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='vehicle_erp_app', password='vehicle_erp_pass_2026', database='Vehicle_Analyzis', autocommit=True)
    cursor = conn.cursor()

    # Drop app_sessions if it exists (it failed to create properly)
    try:
        cursor.execute("DROP TABLE IF EXISTS `app_sessions`;")
        print("Dropped app_sessions table (if it existed).")
    except Exception as e:
        print("Drop error:", e)

    # Check users table column type
    cursor.execute("SHOW CREATE TABLE `users`;")
    create_stmt = cursor.fetchone()[1]
    print("\nCurrent users table definition:")
    print(create_stmt)

    # Create app_sessions with matching column type to users.id
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `app_sessions` (
                `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
                `token_hash` VARCHAR(64) NOT NULL,
                `user_id` BIGINT UNSIGNED NOT NULL,
                `expires_at` DATETIME NOT NULL,
                `last_activity_at` DATETIME NOT NULL,
                `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (`id`),
                UNIQUE KEY `uq_sessions_token` (`token_hash`),
                KEY `idx_sessions_user` (`user_id`),
                KEY `idx_sessions_expires` (`expires_at`),
                CONSTRAINT `fk_sessions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("\nSUCCESS! Created app_sessions table with BIGINT UNSIGNED matching users.id!")
    except Exception as e:
        print("Create app_sessions error:", e)

    # Verify all tables
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    print(f"\nTotal tables in Vehicle_Analyzis: {len(tables)}")
    for t in tables:
        print(f"  - {t[0]}")

    conn.close()

if __name__ == "__main__":
    fix_tables()
