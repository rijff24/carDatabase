import sqlite3
import os
import sys

def add_weight_column(db_path):
    """Add weight column to parts table in SQLite database"""
    try:
        if not os.path.exists(db_path):
            print(f"Error: Database file {db_path} does not exist")
            return False
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the weight column already exists
        cursor.execute("PRAGMA table_info(parts)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'weight' in column_names:
            print(f"Column 'weight' already exists in parts table in {db_path}")
            conn.close()
            return False
        
        # Add the weight column
        cursor.execute("ALTER TABLE parts ADD COLUMN weight NUMERIC(10, 3)")
        conn.commit()
        
        print(f"Successfully added 'weight' column to the parts table in {db_path}")
        conn.close()
        return True
    
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Find all SQLite database files in the current directory
    db_files = [f for f in os.listdir() if f.startswith('data') and f.endswith('.sqlite')]
    
    if not db_files:
        print("No database files found")
        sys.exit(1)
    
    print(f"Found SQLite database files: {', '.join(db_files)}")
    print()
    
    for db_file in db_files:
        print(f"Processing {db_file}...")
        add_weight_column(db_file)
        print()
    
    print("Script completed.")
    
    # Check if production database exists in instance folder
    if os.path.exists('instance'):
        prod_db = os.path.join('instance', 'data.sqlite')
        if os.path.exists(prod_db):
            print(f"Processing production database {prod_db}...")
            add_weight_column(prod_db)
        else:
            print(f"Production database {prod_db} not found.")
    else:
        print("Production database not found.") 