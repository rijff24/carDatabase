import os
from app import create_app, db
from app.models.user import User

# Create app with the development configuration
app = create_app('development')

# Push an application context
with app.app_context():
    # Create all database tables
    db.create_all()
    print("Database tables created")
    
    # Check if admin user already exists
    admin = User.query.filter_by(username='admin').first()
    if admin is None:
        # Create admin user
        admin = User(
            username='admin',
            full_name='Administrator',
            role='admin'
        )
        admin.password = 'admin123'
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with username: admin and password: admin123")
    else:
        print("Admin user already exists") 