import sqlite3
import os

# Get all SQLite database files in the current directory
db_files = [f for f in os.listdir('.') if f.endswith('.sqlite')]

if not db_files:
    print("No SQLite database files found in the current directory.")
    exit(1)

print(f"Found SQLite database files: {', '.join(db_files)}")

# Try to add the column to all database files
for db_file in db_files:
    try:
        print(f"\nProcessing {db_file}...")
        
        # Connect to the database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if the parts table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parts'")
        if not cursor.fetchone():
            print(f"The 'parts' table does not exist in {db_file}")
            conn.close()
            continue
        
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
        print(f"Error processing {db_file}: {str(e)}")

print("\nScript completed.") 