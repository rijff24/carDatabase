import os
from app import create_app, db
from app.models.car import Car
from app.models.repair import Repair
from app.models.part import Part, RepairPart
from app.models.repair_provider import RepairProvider
from app.models.stand import Stand
from app.models.dealer import Dealer
from app.models.user import User
from flask_migrate import Migrate

# Create app instance
app = create_app(os.getenv('FLASK_ENV') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """Make additional objects available in the shell context"""
    return dict(
        db=db, 
        Car=Car, 
        Repair=Repair, 
        Part=Part, 
        RepairPart=RepairPart,
        RepairProvider=RepairProvider, 
        Stand=Stand, 
        Dealer=Dealer, 
        User=User
    )

@app.cli.command("create-db")
def create_db():
    """Create database tables"""
    db.create_all()
    print("Database tables created")

@app.cli.command("drop-db")
def drop_db():
    """Drop all database tables"""
    db.drop_all()
    print("Database tables dropped")

@app.cli.command("create-admin")
def create_admin():
    """Create admin user"""
    admin = User(
        username='admin',
        full_name='Administrator',
        role='admin'
    )
    admin.password = 'admin123'
    db.session.add(admin)
    db.session.commit()
    print("Admin user created")

if __name__ == '__main__':
    app.run(debug=True) 