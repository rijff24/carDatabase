from app import db

class RepairProvider(db.Model):
    """RepairProvider model representing the repair_providers table"""
    __tablename__ = 'repair_providers'

    provider_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    provider_name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    contact_info = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<RepairProvider {self.provider_name} ({self.service_type})>' 