import sqlite3

# Connect to the database
conn = sqlite3.connect('data-dev.sqlite')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables in the database:")
for table in tables:
    print(f"  - {table[0]}")

conn.close() 