import sqlite3
from datetime import datetime

def upgrade_repair_providers_table():
    """Add new fields to the repair_providers table"""
    conn = sqlite3.connect('app/data-dev.sqlite')
    cursor = conn.cursor()
    
    # Check if notes column exists
    cursor.execute("PRAGMA table_info(repair_providers)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    if 'notes' not in column_names:
        print("Adding 'notes' column...")
        cursor.execute("ALTER TABLE repair_providers ADD COLUMN notes TEXT")
    
    if 'date_added' not in column_names:
        print("Adding 'date_added' column...")
        cursor.execute("ALTER TABLE repair_providers ADD COLUMN date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        # Update existing records to have a date_added value
        cursor.execute("UPDATE repair_providers SET date_added = ? WHERE date_added IS NULL", 
                      (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
    
    if 'rating' not in column_names:
        print("Adding 'rating' column...")
        cursor.execute("ALTER TABLE repair_providers ADD COLUMN rating INTEGER")
    
    conn.commit()
    conn.close()
    print("Repair providers table upgraded successfully!")

if __name__ == '__main__':
    print("Running repair providers table migration...")
    upgrade_repair_providers_table() 