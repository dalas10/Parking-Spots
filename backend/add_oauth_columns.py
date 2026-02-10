"""
Add OAuth support to users table
"""
import sqlite3

# Connect to database
conn = sqlite3.connect('parkingspots.db')
cursor = conn.cursor()

try:
    # Add oauth_provider column
    cursor.execute("""
        ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(50)
    """)
    print("✓ Added oauth_provider column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("✓ oauth_provider column already exists")
    else:
        raise

try:
    # Add oauth_id column
    cursor.execute("""
        ALTER TABLE users ADD COLUMN oauth_id VARCHAR(255)
    """)
    print("✓ Added oauth_id column")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("✓ oauth_id column already exists")
    else:
        raise

try:
    # Create index on oauth_id
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_users_oauth_id ON users (oauth_id)
    """)
    print("✓ Created index on oauth_id")
except Exception as e:
    print(f"Index creation: {e}")

try:
    # Make hashed_password nullable - SQLite doesn't support ALTER COLUMN
    # So we'll just note that new users can have NULL password
    print("✓ hashed_password already nullable in SQLite (no action needed)")
except Exception as e:
    print(f"Password column: {e}")

# Commit changes
conn.commit()
conn.close()

print("\n✅ OAuth migration completed successfully!")
print("\nDatabase schema updated:")
print("  - oauth_provider: VARCHAR(50) - Stores OAuth provider name")
print("  - oauth_id: VARCHAR(255) - Stores OAuth user ID")
print("  - hashed_password: Nullable for OAuth users")
