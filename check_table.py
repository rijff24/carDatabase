import sqlite3

try:
    # Connect to the database
    conn = sqlite3.connect('data-dev.sqlite')
    cursor = conn.cursor()
    
    # Check the parts table schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='parts'")
    table_schema = cursor.fetchone()
    
    if table_schema:
        print("Parts table schema:")
        print(table_schema[0])
    else:
        print("Parts table not found")
    
    # Check the parts table columns
    cursor.execute("PRAGMA table_info(parts)")
    columns = cursor.fetchall()
    
    print("\nParts table columns:")
    for col in columns:
        # Format: cid, name, type, notnull, dflt_value, pk
        print(f"Column {col[0]}: {col[1]} ({col[2]}), Not Null: {bool(col[3])}, Default: {col[4]}, PK: {bool(col[5])}")
    
    # Check if there are any records in the parts table
    cursor.execute("SELECT COUNT(*) FROM parts")
    count = cursor.fetchone()[0]
    print(f"\nNumber of records in parts table: {count}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {str(e)}") 