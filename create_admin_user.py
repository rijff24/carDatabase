from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def main():
    """Create an admin user for testing the application"""
    app = create_app()
    
    with app.app_context():
        # Check if admin user already exists
        user = User.query.filter_by(username='admin').first()
        if not user:
            # Create admin user
            user = User(
                username='admin',
                full_name='Administrator',
                role='admin'
            )
            # Directly set password hash to bypass validation
            user.password_hash = generate_password_hash('admin')
            db.session.add(user)
            db.session.commit()
            print('Admin user created successfully with username: admin, password: admin')
        else:
            print('Admin user already exists')

if __name__ == "__main__":
    main() 