from app import db

class Part(db.Model):
    """Part model representing the parts table"""
    __tablename__ = 'parts'

    part_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    part_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    manufacturer = db.Column(db.String(100), nullable=True)
    standard_price = db.Column(db.Numeric(10, 2), nullable=True)

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
    repair = db.relationship('Repair', backref='repair_parts')
    part = db.relationship('Part', backref='repair_parts')

    def __repr__(self):
        return f'<RepairPart {self.part_id} for Repair {self.repair_id}>' 