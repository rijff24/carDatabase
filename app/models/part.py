from app import db

class Part(db.Model):
    """Part model representing the parts table"""
    __tablename__ = 'parts'

    part_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    part_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    manufacturer = db.Column(db.String(100), nullable=True)
    standard_price = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Relationships
    repairs = db.relationship('Repair', secondary='repair_parts', back_populates='parts', overlaps="repair_parts")
    repair_parts = db.relationship('RepairPart', back_populates='part', overlaps="repairs")

    def __repr__(self):
        return f'<Part {self.part_name}>'


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