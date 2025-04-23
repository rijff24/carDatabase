import sqlite3

# Connect to the database
conn = sqlite3.connect('data-dev.sqlite')
cursor = conn.cursor()

# Check cars table
print("=== Table: cars ===")

# Get column information
cursor.execute("PRAGMA table_info(cars)")
columns = cursor.fetchall()
print("Columns:")
for column in columns:
    column_id, name, type, notnull, default, pk = column
    pk_str = "PRIMARY KEY" if pk else ""
    null_str = "NOT NULL" if notnull else ""
    default_str = f"DEFAULT {default}" if default is not None else ""
    print(f"  {name}: {type} {pk_str} {null_str} {default_str}".strip())

# Count rows
cursor.execute("SELECT COUNT(*) FROM cars")
row_count = cursor.fetchone()[0]
print(f"Rows: {row_count}")

# Show first row
if row_count > 0:
    cursor.execute("SELECT * FROM cars LIMIT 1")
    row = cursor.fetchone()
    if row:
        column_names = [description[0] for description in cursor.description]
        print("First row:")
        for i, col_name in enumerate(column_names):
            print(f"  {col_name}: {row[i]}")
else:
    print("No rows in cars table")

# Also check sales table for profit calculation
print("\n=== Table: sales ===")
cursor.execute("PRAGMA table_info(sales)")
columns = cursor.fetchall()
print("Columns:")
for column in columns:
    column_id, name, type, notnull, default, pk = column
    pk_str = "PRIMARY KEY" if pk else ""
    null_str = "NOT NULL" if notnull else ""
    default_str = f"DEFAULT {default}" if default is not None else ""
    print(f"  {name}: {type} {pk_str} {null_str} {default_str}".strip())

# Count rows
cursor.execute("SELECT COUNT(*) FROM sales")
row_count = cursor.fetchone()[0]
print(f"Rows: {row_count}")

# Also check repairs table
print("\n=== Table: repairs ===")
cursor.execute("PRAGMA table_info(repairs)")
columns = cursor.fetchall()
print("Columns:")
for column in columns:
    column_id, name, type, notnull, default, pk = column
    pk_str = "PRIMARY KEY" if pk else ""
    null_str = "NOT NULL" if notnull else ""
    default_str = f"DEFAULT {default}" if default is not None else ""
    print(f"  {name}: {type} {pk_str} {null_str} {default_str}".strip())

conn.close() 