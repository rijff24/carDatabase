from app import db
from datetime import datetime

class RepairProvider(db.Model):
    """RepairProvider model representing the repair_providers table"""
    __tablename__ = 'repair_providers'

    provider_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    provider_name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    contact_info = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.now, nullable=False)
    rating = db.Column(db.Integer, nullable=True)  # Rating out of 5

    def __repr__(self):
        return f'<RepairProvider {self.provider_name} ({self.service_type})>'
    
    @property
    def total_repairs(self):
        """Get the total number of repairs handled by this provider"""
        return len(self.repairs)
    
    @property
    def total_repair_cost(self):
        """Get the total cost of all repairs done by this provider"""
        return sum(repair.repair_cost for repair in self.repairs) if self.repairs else 0
    
    @property
    def average_repair_duration(self):
        """Calculate the average repair duration in days"""
        completed_repairs = [r for r in self.repairs if r.end_date is not None]
        if not completed_repairs:
            return None
        durations = [(r.end_date - r.start_date).days for r in completed_repairs]
        return sum(durations) / len(durations) if durations else None 