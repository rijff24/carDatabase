from app import db

class Stand(db.Model):
    """Stand model representing the stands table"""
    __tablename__ = 'stands'

    stand_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stand_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    additional_info = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Stand {self.stand_name}>' 