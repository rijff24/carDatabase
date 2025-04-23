from app import create_app, db
import sqlalchemy as sa
from sqlalchemy import inspect

def show_schema():
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Get all table names
        table_names = inspector.get_table_names()
        print(f"Database contains {len(table_names)} tables:\n")
        
        # For each table, print its structure
        for table_name in sorted(table_names):
            print(f"Table: {table_name}")
            
            # Get columns
            columns = inspector.get_columns(table_name)
            print("  Columns:")
            for column in columns:
                # Format column info
                col_type = str(column['type'])
                col_nullable = "NULL" if column.get('nullable', True) else "NOT NULL"
                col_default = f"DEFAULT {column.get('default')}" if column.get('default') is not None else ""
                col_primary_key = "PRIMARY KEY" if column.get('primary_key', False) else ""
                
                attrs = " ".join(filter(None, [col_nullable, col_default, col_primary_key]))
                if attrs:
                    print(f"    {column['name']} ({col_type}) {attrs}")
                else:
                    print(f"    {column['name']} ({col_type})")
            
            # Get primary keys
            pk = inspector.get_pk_constraint(table_name)
            if pk['constrained_columns']:
                print(f"  Primary Key: {', '.join(pk['constrained_columns'])}")
            
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            if foreign_keys:
                print("  Foreign Keys:")
                for fk in foreign_keys:
                    ref_table = fk['referred_table']
                    ref_cols = fk['referred_columns']
                    constrained_cols = fk['constrained_columns']
                    print(f"    {', '.join(constrained_cols)} -> {ref_table}({', '.join(ref_cols)})")
            
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print("  Indexes:")
                for index in indexes:
                    print(f"    {index['name']}: {', '.join(index['column_names'])}")
            
            print()

if __name__ == "__main__":
    show_schema() 