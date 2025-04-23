from datetime import datetime
from app import db
from sqlalchemy import event

class Car(db.Model):
    """Model for storing car information"""
    __tablename__ = 'cars'

    car_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vehicle_name = db.Column(db.String(100), nullable=False)
    vehicle_make = db.Column(db.String(50), nullable=False)
    vehicle_model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    colour = db.Column(db.String(50), nullable=False)
    dekra_condition = db.Column(db.String(20), nullable=False)
    licence_number = db.Column(db.String(20), nullable=False)
    registration_number = db.Column(db.String(20), nullable=False)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    recon_cost = db.Column(db.Numeric(10, 2), nullable=True)
    final_cost_price = db.Column(db.Numeric(10, 2), nullable=True)
    source = db.Column(db.String(50), nullable=False)
    date_bought = db.Column(db.Date, nullable=False, default=datetime.now().date)
    date_added_to_stand = db.Column(db.Date, nullable=True)
    date_sold = db.Column(db.Date, nullable=True)
    refuel_cost = db.Column(db.Numeric(10, 2), default=0.00)
    current_location = db.Column(db.String(100), nullable=False)
    repair_status = db.Column(db.String(30), nullable=False)
    stand_id = db.Column(db.Integer, db.ForeignKey('stands.stand_id'), nullable=True)
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealers.dealer_id'), nullable=True)
    sale_price = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Relationships
    repairs = db.relationship('Repair', back_populates='car', cascade='all, delete-orphan')
    stand = db.relationship('Stand', foreign_keys=[stand_id], back_populates='cars')
    dealer = db.relationship('Dealer', back_populates='cars')
    sale = db.relationship('Sale', back_populates='car', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Car {self.year} {self.vehicle_make} {self.vehicle_model}>'

    @property
    def full_name(self):
        """Get the full name of the car (year make model)"""
        return f'{self.year} {self.vehicle_make} {self.vehicle_model}'

    @property
    def is_available(self):
        """Check if the car is available for sale"""
        return self.date_sold is None

    @property
    def days_in_recon(self):
        """Calculate days in reconditioning"""
        if not self.date_added_to_stand or not self.date_bought:
            return None
        return (self.date_added_to_stand - self.date_bought).days

    @property
    def days_on_stand(self):
        """Calculate days on stand"""
        if not self.date_sold or not self.date_added_to_stand:
            return None
        return (self.date_sold - self.date_added_to_stand).days

    @property
    def total_repair_cost(self):
        """Calculate total repair costs for this car"""
        return sum(float(repair.repair_cost) for repair in self.repairs)

    @property
    def total_investment(self):
        """Calculate total investment in the car"""
        repair_cost = self.total_repair_cost or 0
        refuel = float(self.refuel_cost) if self.refuel_cost else 0
        purchase = float(self.purchase_price) if self.purchase_price else 0
        return purchase + repair_cost + refuel

    @property
    def profit(self):
        """Calculate profit (sale price - total investment)"""
        if not self.sale_price or not self.date_sold:
            return None
        return float(self.sale_price) - float(self.total_investment)

# Add event listeners to maintain data consistency between Car and Sale
@event.listens_for(Car, 'load')
def check_car_sale_consistency(target, context):
    """Ensure car.date_sold is consistent with the associated sale record"""
    # This event is fired when a Car object is loaded from the database
    # We'll defer actual validation until the object is accessed
    target._needs_consistency_check = True

@event.listens_for(Car, 'refresh')
def on_car_refresh(target, context, attrs):
    """Flag car for consistency check after refresh"""
    target._needs_consistency_check = True

@event.listens_for(Car, "expire")
def on_car_expire(target, attrs):
    """Flag car for consistency check after expire"""
    target._needs_consistency_check = True

# This is a descriptor that can intercept attribute access
class ConsistencyCheckingDescriptor:
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
            
        # Check if we need to validate the car's data
        needs_check = getattr(obj, '_needs_consistency_check', True)
        if needs_check:
            # Only do consistency check once
            obj._needs_consistency_check = False
            
            # Perform the actual consistency check
            has_sale = hasattr(obj, 'sale') and obj.sale is not None
            
            if has_sale and obj.date_sold is None:
                # Car has a sale but no date_sold, update it
                obj.date_sold = obj.sale.sale_date
                db.session.merge(obj)
                
            elif has_sale and obj.date_sold != obj.sale.sale_date:
                # date_sold doesn't match sale date, fix it
                obj.date_sold = obj.sale.sale_date
                db.session.merge(obj)
                
            elif obj.date_sold is not None and not has_sale:
                # Car is marked as sold but has no sale record, clear date_sold
                obj.date_sold = None
                db.session.merge(obj)
                
        # Return the result of the is_available property
        return obj.date_sold is None

# Replace the is_available property with our descriptor
Car.is_available = ConsistencyCheckingDescriptor()


class VehicleMake(db.Model):
    """Model for storing unique vehicle makes"""
    __tablename__ = 'vehicle_makes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<VehicleMake {self.name}>'
    
    @staticmethod
    def sanitize_name(name):
        """Sanitize make name: trim whitespace and capitalize first letter of each word"""
        if not name:
            return None
        # Remove any extra whitespace and capitalize each word
        return ' '.join(word.capitalize() for word in name.strip().split())
    
    @classmethod
    def get_or_create(cls, make_name):
        """Get existing make or create a new one if it doesn't exist"""
        sanitized_name = cls.sanitize_name(make_name)
        if not sanitized_name:
            return None
            
        # Check for existing make (case insensitive)
        existing = cls.query.filter(db.func.lower(cls.name) == db.func.lower(sanitized_name)).first()
        if existing:
            return existing
            
        # Create new make
        new_make = cls(name=sanitized_name)
        db.session.add(new_make)
        db.session.commit()
        return new_make


class VehicleModel(db.Model):
    """Model for storing unique vehicle models"""
    __tablename__ = 'vehicle_models'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    make_id = db.Column(db.Integer, db.ForeignKey('vehicle_makes.id'), nullable=False)
    
    # Add a unique constraint for name+make_id
    __table_args__ = (
        db.UniqueConstraint('name', 'make_id', name='unique_model_make'),
    )
    
    # Relationship with VehicleMake
    make = db.relationship('VehicleMake', backref=db.backref('models', lazy='dynamic'))

    def __repr__(self):
        return f'<VehicleModel {self.name}>'
    
    @staticmethod
    def sanitize_name(name):
        """Sanitize model name: trim whitespace and capitalize first letter of each word"""
        if not name:
            return None
        # Remove any extra whitespace and capitalize each word
        return ' '.join(word.capitalize() for word in name.strip().split())
    
    @classmethod
    def get_or_create(cls, model_name, make_id=None):
        """Get existing model or create a new one if it doesn't exist"""
        sanitized_name = cls.sanitize_name(model_name)
        if not sanitized_name:
            return None
            
        # Check for existing model (case insensitive)
        existing = cls.query.filter(
            db.func.lower(cls.name) == db.func.lower(sanitized_name),
            cls.make_id == make_id
        ).first()
        
        if existing:
            return existing
            
        # Create new model
        new_model = cls(name=sanitized_name, make_id=make_id)
        db.session.add(new_model)
        db.session.commit()
        return new_model


class VehicleYear(db.Model):
    """Model for storing vehicle years"""
    __tablename__ = 'vehicle_years'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return f'<VehicleYear {self.year}>'


class VehicleColor(db.Model):
    """Model for storing vehicle colors"""
    __tablename__ = 'vehicle_colors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<VehicleColor {self.name}>'
    
    @staticmethod
    def sanitize_name(name):
        """Sanitize color name: trim whitespace and capitalize first letter of each word"""
        if not name:
            return None
        # Remove any extra whitespace and capitalize each word
        return ' '.join(word.capitalize() for word in name.strip().split()) 