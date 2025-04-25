from app import db
from sqlalchemy.schema import CheckConstraint

class Part(db.Model):
    """Part model representing the parts table"""
    __tablename__ = 'parts'

    part_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    part_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    manufacturer = db.Column(db.String(100), nullable=True)
    standard_price = db.Column(db.Numeric(10, 2), nullable=True)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    # Note: The database has 'location' column, but we access it as storage_location
    storage_location = db.Column('location', db.String(100), nullable=True)
    # Commenting out weight as it's not needed according to documentation
    # weight = db.Column(db.Numeric(10, 3), nullable=True)
    
    # Note: These columns don't exist in the current database schema
    # Uncomment and run migrations if you want to add them
    # make = db.Column(db.String(100), nullable=True)
    # model = db.Column(db.String(100), nullable=True)
    
    # Add check constraint to prevent negative stock values
    __table_args__ = (
        CheckConstraint('stock_quantity >= 0', name='check_stock_quantity_non_negative'),
    )
    
    # Relationships
    repairs = db.relationship('Repair', secondary='repair_parts', back_populates='parts', overlaps="repair_parts")
    repair_parts = db.relationship('RepairPart', back_populates='part', overlaps="repairs")

    def __repr__(self):
        return f'<Part {self.part_name}>'
    
    def is_duplicate(self, name, make=None, model=None):
        """
        Check if a part with the same name, make, and model already exists
        
        Args:
            name (str): Part name to check
            make (str, optional): Vehicle make
            model (str, optional): Vehicle model
            
        Returns:
            bool: True if a duplicate exists, False otherwise
        """
        # Convert values for case-insensitive comparison
        name = name.lower().strip() if name else None
        
        # Check for parts with the same name (case-insensitive)
        query = Part.query.filter(db.func.lower(Part.part_name).strip() == name)
        
        # Note: make and model columns don't exist in current database schema
        # Keeping parameters for API compatibility, but not using them in query
        
        # Check if any parts match the criteria (excluding self)
        existing_parts = query.filter(Part.part_id != self.part_id).all()
        
        return len(existing_parts) > 0


# Junction table for many-to-many relationship between repairs and parts
class RepairPart(db.Model):
    """RepairPart model representing the repair_parts junction table"""
    __tablename__ = 'repair_parts'

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    repair_id = db.Column(db.Integer, db.ForeignKey('repairs.repair_id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.part_id'), nullable=False)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    vendor = db.Column(db.String(100), nullable=False)

    # Relationships
    repair = db.relationship('Repair', foreign_keys=[repair_id], back_populates='repair_parts', overlaps="parts,repairs")
    part = db.relationship('Part', back_populates='repair_parts', overlaps="repairs")

    def __repr__(self):
        return f'<RepairPart {self.part_id} for Repair {self.repair_id}>' 