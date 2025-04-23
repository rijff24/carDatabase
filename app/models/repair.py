from datetime import datetime
from app import db

class Repair(db.Model):
    """Model for storing repair information"""
    __tablename__ = 'repairs'
    
    repair_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.car_id'), nullable=False)
    repair_type = db.Column(db.String(50), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('repair_providers.provider_id'), nullable=False)
    additional_notes = db.Column(db.Text, nullable=True)
    repair_cost = db.Column(db.Numeric(10, 2), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=datetime.now().date)
    end_date = db.Column(db.Date, nullable=True)
    
    # Relationships
    car = db.relationship('Car', back_populates='repairs')
    provider = db.relationship('RepairProvider', back_populates='repairs')
    parts = db.relationship('Part', secondary='repair_parts', back_populates='repairs', overlaps="repair_parts")
    repair_parts = db.relationship('RepairPart', back_populates='repair', overlaps="parts,repairs")
    
    def __repr__(self):
        return f'<Repair {self.repair_id}: {self.repair_type} for Car {self.car_id}>'
    
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
        parts_cost = sum(float(part.purchase_price) for part in self.parts)
        # Add labor cost
        return float(self.repair_cost) + parts_cost 