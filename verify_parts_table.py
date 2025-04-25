import sqlite3

try:
    # Connect to the database
    conn = sqlite3.connect('data-dev.sqlite')
    cursor = conn.cursor()
    
    # Get table schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='parts'")
    schema = cursor.fetchone()[0]
    print("Parts table schema:")
    print(schema)
    print()
    
    # Get column information
    cursor.execute("PRAGMA table_info(parts)")
    columns = cursor.fetchall()
    print("Parts table columns:")
    for i, col in enumerate(columns):
        cid, name, type_, notnull, dflt_value, pk = col
        print(f"Column {cid}: {name} ({type_}), Not Null: {bool(notnull)}, Default: {dflt_value}, PK: {bool(pk)}")
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM parts")
    count = cursor.fetchone()[0]
    print(f"Number of records in parts table: {count}")
    
    conn.close()
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
except Exception as e:
    print(f"Error: {e}") 