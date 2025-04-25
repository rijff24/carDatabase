import sqlite3
import os

def add_location_column():
    try:
        # Get the directory of the current script
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(basedir, 'data-dev.sqlite')
        
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(parts)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'location' not in column_names:
            # Add the new column
            cursor.execute("ALTER TABLE parts ADD COLUMN location VARCHAR(100)")
            conn.commit()
            print(f"Successfully added 'location' column to the parts table in {db_path}")
        else:
            print(f"The 'location' column already exists in the parts table in {db_path}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_location_column() 