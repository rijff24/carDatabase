from datetime import datetime
from app import db

class Repair(db.Model):
    """Repair model representing the repairs table"""
    __tablename__ = 'repairs'

    repair_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.car_id'), nullable=False)
    repair_type = db.Column(db.String(50), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('repair_providers.provider_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=datetime.now().date)
    end_date = db.Column(db.Date, nullable=True)
    repair_cost = db.Column(db.Numeric(10, 2), nullable=False)
    additional_notes = db.Column(db.Text, nullable=True)

    # Relationships
    provider = db.relationship('RepairProvider', backref='repairs')
    parts = db.relationship('Part', secondary='repair_parts', backref='repairs')
    repair_parts = db.relationship('RepairPart', backref='repair_ref', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Repair {self.repair_type} for Car ID {self.car_id}>'
    
    @property
    def duration(self):
        """Calculate repair duration in days"""
        if not self.end_date:
            return None
        return (self.end_date - self.start_date).days
        
    @property
    def total_cost(self):
        """Calculate total repair cost (labor + parts)"""
        # Get the sum of all parts costs
        parts_cost = sum(float(part.purchase_price) for part in self.repair_parts)
        # Add labor cost (repair_cost)
        return float(self.repair_cost) + parts_cost 