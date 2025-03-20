from app import db

class Dealer(db.Model):
    """Dealer model representing the dealers table"""
    __tablename__ = 'dealers'

    dealer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dealer_name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f'<Dealer {self.dealer_name}>' 