import sqlite3
import os

# Check for production database
prod_db = 'data.sqlite'

if not os.path.exists(prod_db):
    print(f"Production database {prod_db} not found.")
    exit(1)

try:
    print(f"Processing production database {prod_db}...")
    
    # Connect to the database
    conn = sqlite3.connect(prod_db)
    cursor = conn.cursor()
    
    # Check if the parts table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parts'")
    if not cursor.fetchone():
        print(f"The 'parts' table does not exist in {prod_db}")
        conn.close()
        exit(1)
    
    # Check if the stock_quantity column already exists
    cursor.execute("PRAGMA table_info(parts)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"Current columns in parts table: {', '.join(column_names)}")
    
    if 'stock_quantity' in column_names:
        print("The 'stock_quantity' column already exists")
    else:
        # Add the stock_quantity column
        cursor.execute("ALTER TABLE parts ADD COLUMN stock_quantity INTEGER NOT NULL DEFAULT 0")
        conn.commit()
        print("Added 'stock_quantity' column successfully")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(parts)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"Updated columns in parts table: {', '.join(column_names)}")
    
    conn.close()
    
except Exception as e:
    print(f"Error processing {prod_db}: {str(e)}")

print("\nScript completed.") 