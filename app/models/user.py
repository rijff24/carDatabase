from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    """User model representing the users table"""
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def password(self):
        """Password property getter raises an error"""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Password property setter creates password hash"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Verify if password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.now()
        db.session.commit()

    def get_id(self):
        """Override get_id method from UserMixin"""
        return str(self.user_id)


@login_manager.user_loader
def load_user(user_id):
    """User loader function for Flask-Login"""
    return User.query.get_or_404(int(user_id)) if user_id else None 