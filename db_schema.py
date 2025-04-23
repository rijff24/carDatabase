import sqlite3

# Connect to the database
conn = sqlite3.connect('data-dev.sqlite')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

# For each table, print its schema
for table in tables:
    table_name = table[0]
    print(f"\n=== Table: {table_name} ===")
    
    try:
        # Get column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for column in columns:
            column_id, name, type, notnull, default, pk = column
            pk_str = "PRIMARY KEY" if pk else ""
            null_str = "NOT NULL" if notnull else ""
            default_str = f"DEFAULT {default}" if default is not None else ""
            print(f"  {name}: {type} {pk_str} {null_str} {default_str}".strip())
        
        # Count rows
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        print(f"  Rows: {row_count}")
        
        # If few rows, show sample data
        if row_count > 0 and row_count <= 5:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            print("  Sample data:")
            for row in rows:
                print(f"    {row}")
    except sqlite3.Error as e:
        print(f"  Error getting info for table {table_name}: {e}")

conn.close() 