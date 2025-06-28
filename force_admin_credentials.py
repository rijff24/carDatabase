from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def force_admin_credentials():
    """Force admin username and password to be 'admin' and 'admin'"""
    app = create_app()
    
    with app.app_context():
        # Check if admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        
        if admin_user:
            # Update existing admin user
            admin_user.password_hash = generate_password_hash('admin')
            admin_user.full_name = 'Administrator'
            admin_user.role = 'admin'
            db.session.commit()
            print('Admin user updated with username: admin, password: admin')
        else:
            # Create new admin user
            admin_user = User(
                username='admin',
                full_name='Administrator',
                role='admin'
            )
            # Directly set the password hash to bypass validation
            admin_user.password_hash = generate_password_hash('admin')
            db.session.add(admin_user)
            db.session.commit()
            print('Admin user created with username: admin, password: admin')
        
        # Verify the user was created/updated correctly
        verify_user = User.query.filter_by(username='admin').first()
        if verify_user and verify_user.verify_password('admin'):
            print('✓ Admin credentials verified successfully')
            print(f'  Username: {verify_user.username}')
            print(f'  Role: {verify_user.role}')
            print(f'  Full Name: {verify_user.full_name}')
        else:
            print('✗ Error: Admin credentials verification failed')

if __name__ == "__main__":
    force_admin_credentials() 