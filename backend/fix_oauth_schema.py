"""Fix OAuth schema - make hashed_password nullable"""
import sqlite3

def fix_schema():
    conn = sqlite3.connect('parkingspots.db')
    cursor = conn.cursor()
    
    try:
        print("Creating new users table with nullable hashed_password...")
        
        # Create new table with correct schema
        cursor.execute("""
            CREATE TABLE users_new (
                id VARCHAR(36) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255),
                full_name VARCHAR(255) NOT NULL,
                phone_number VARCHAR(20),
                profile_image TEXT,
                role VARCHAR(50) NOT NULL DEFAULT 'RENTER',
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                oauth_provider VARCHAR(50),
                oauth_id VARCHAR(255),
                stripe_customer_id VARCHAR(255),
                latitude FLOAT,
                longitude FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(oauth_provider, oauth_id)
            )
        """)
        
        print("Copying data from old table...")
        cursor.execute("""
            INSERT INTO users_new 
            SELECT * FROM users
        """)
        
        print("Dropping old table...")
        cursor.execute("DROP TABLE users")
        
        print("Renaming new table...")
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        
        conn.commit()
        print("✓ Schema fixed successfully!")
        print("✓ hashed_password is now nullable for OAuth users")
        
        # Verify
        cursor.execute("PRAGMA table_info(users)")
        for row in cursor.fetchall():
            if row[1] == 'hashed_password':
                print(f"✓ Verified: hashed_password nullable = {row[3] == 0}")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()
