# Database Structure

The Car Repair and Sales Tracking Application uses SQLite with SQLAlchemy ORM for data storage. This document details the database schema, including tables, fields, relationships, and constraints.

## Database Technology

- **Database Engine**: SQLite
- **ORM**: SQLAlchemy
- **Migration Tool**: Flask-Migrate (Alembic)

The application uses separate database files for different environments:
- `data-dev.sqlite`: Development database
- `data-test.sqlite`: Testing database
- `data.sqlite`: Production database (if not overridden by DATABASE_URL)

## Dashboard Queries

The dashboard utilizes several optimized queries to present key metrics and visualizations. These queries retrieve data from various tables and apply filtering, grouping, and calculations.

### Stand Statistics Query

The Stand Statistics card on the dashboard uses the following logic to retrieve and calculate stand statistics:

1. **Query for Stands with Unsold Cars**:
   ```python
   # Fetch all stands
   all_stands = Stand.query.order_by(Stand.stand_name).all()
   
   # For each stand, get unsold cars
   for stand in all_stands:
       cars_on_this_stand = Car.query.filter(
           Car.stand_id == stand.stand_id,
           Car.date_sold == None
       ).all()
   ```

2. **Calculate Statistics for Each Stand**:
   ```python
   # Calculate average age (days on stand)
   total_age = 0
   for car in cars_on_this_stand:
       if car.date_added_to_stand:
           days_on_stand = (current_date - car.date_added_to_stand).days
           total_age += days_on_stand
   
   avg_age = round(total_age / total_cars_on_stand if total_cars_on_stand > 0 else 0)
   ```

3. **Build Data Structure for Visualization**:
   ```python
   stands_with_stats.append({
       'stand_id': stand.stand_id,
       'stand_name': stand.stand_name,
       'total_cars': total_cars_on_stand,
       'avg_age': avg_age
   })
   ```

4. **Sort for Optimal Display**:
   ```python
   # Sort stands by those with highest average age first (potential issues)
   stands_with_stats.sort(key=lambda x: x['avg_age'], reverse=True)
   ```

This approach allows the dashboard to present stand occupancy and aging information in a visually intuitive way, highlighting potential inventory issues without requiring a separate database view or materialized data.

## Database Schema

### Cars Table

**Table Name**: `cars`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| car_id | Integer | Primary Key, Autoincrement | Unique identifier for each car |
| vehicle_name | String(100) | Not Null | Name/identifier for the vehicle |
| vehicle_make | String(50) | Not Null | Manufacturer of the vehicle |
| vehicle_model | String(50) | Not Null | Model of the vehicle |
| year | Integer | Not Null | Year of manufacture |
| colour | String(50) | Not Null | Color of the vehicle |
| dekra_condition | String(20) | Not Null | Condition rating based on Dekra standards |
| licence_number | String(20) | Not Null | Vehicle license number |
| registration_number | String(20) | Not Null | Vehicle registration number |
| purchase_price | Numeric(10,2) | Not Null | Price paid when purchasing the vehicle |
| recon_cost | Numeric(10,2) | Nullable | Cost of reconditioning |
| final_cost_price | Numeric(10,2) | Nullable | Final cost after reconditioning |
| source | String(50) | Not Null | Where the vehicle was acquired from |
| date_bought | Date | Not Null, Default=Current Date | Date when vehicle was purchased |
| date_added_to_stand | Date | Nullable | Date when vehicle was added to display stand |
| date_sold | Date | Nullable | Date when vehicle was sold |
| refuel_cost | Numeric(10,2) | Default=0.00 | Cost of refueling |
| current_location | String(100) | Not Null | Current location of the vehicle |
| repair_status | String(30) | Not Null | Current repair status (In Repair, On Display, etc.) |
| stand_id | Integer | Foreign Key (stands.stand_id), Nullable | ID of the stand where vehicle is displayed |
| dealer_id | Integer | Foreign Key (dealers.dealer_id), Nullable | ID of the dealer handling the vehicle |
| sale_price | Numeric(10,2) | Nullable | Price at which vehicle was sold |

**Indexes**:
- Primary Key: `car_id`
- Index on `vehicle_make`, `vehicle_model` for faster searching
- Index on `repair_status` for filtering
- Index on `date_bought`, `date_sold` for date-based queries

**Calculated Properties** (not stored in database, computed in model):
- `days_in_recon`: Days between purchase and display (date_added_to_stand - date_bought)
- `days_on_stand`: Days between display and sale (date_sold - date_added_to_stand)
- `total_repair_cost`: Sum of costs of all repairs for this car
- `profit`: Sale price minus costs (sale_price - (purchase_price + total_repair_cost + refuel_cost))
- `commission`: Commission based on profit
- `total_investment`: Total invested in the car (purchase_price + total_repair_cost + refuel_cost)
- `sold`: Boolean indicating if the car has been sold (date_sold is not None)
- `full_name`: Complete name of the car (year make model)
- `is_available`: Boolean indicating if the car is available for sale

**Model Definition** (simplified):
```python
class Car(db.Model):
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
```

### Sales Table

**Table Name**: `sales`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| sale_id | Integer | Primary Key | Unique identifier for each sale |
| car_id | Integer | Foreign Key (cars.car_id), Not Null | ID of the car sold |
| dealer_id | Integer | Foreign Key (dealers.dealer_id), Not Null | ID of the dealer making the sale |
| sale_price | Numeric(10,2) | Not Null | Price at which the car was sold |
| sale_date | Date | Not Null, Default=Current Date | Date of the sale |
| payment_method | String(50) | Nullable | Method of payment (Cash, Card, Finance, etc.) |
| customer_name | String(100) | Nullable | Name of the customer |
| customer_contact | String(100) | Nullable | Contact information of the customer |
| notes | Text | Nullable | Additional notes about the sale |
| created_at | DateTime | Default=Current Time | When the sale record was created |
| updated_at | DateTime | Default=Current Time, OnUpdate=Current Time | When the sale record was last updated |

**Indexes**:
- Primary Key: `sale_id`
- Foreign Key: `car_id` references `cars.car_id`
- Foreign Key: `dealer_id` references `dealers.dealer_id`
- Index on `sale_date` for date-based queries

**Calculated Properties**:
- `profit`: Profit from the sale (sale_price - car.total_cost)
- `profit_margin`: Profit as percentage ((profit / sale_price) * 100)

**Model Definition** (simplified):
```python
class Sale(db.Model):
    __tablename__ = 'sales'
    
    sale_id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.car_id'), nullable=False)
    dealer_id = db.Column(db.Integer, db.ForeignKey('dealers.dealer_id'), nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_date = db.Column(db.Date, nullable=False, default=datetime.now().date)
    payment_method = db.Column(db.String(50))
    customer_name = db.Column(db.String(100))
    customer_contact = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    car = db.relationship('Car', back_populates='sale')
    dealer = db.relationship('Dealer', back_populates='sales')
```

### Dealers Table

**Table Name**: `dealers`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| dealer_id | Integer | Primary Key | Unique identifier for each dealer |
| name | String(100) | Not Null | Name of the dealer |
| contact_name | String(100) | Nullable | Primary contact person |
| contact_phone | String(20) | Nullable | Phone number |
| contact_email | String(100) | Nullable | Email address |
| address | Text | Nullable | Physical address |
| commission_rate | Numeric(5,2) | Default=10.00 | Standard commission rate (%) |
| notes | Text | Nullable | Additional notes about the dealer |
| is_active | Boolean | Default=True | Whether dealer is active |
| created_at | DateTime | Default=Current Time | When dealer was added |
| updated_at | DateTime | Default=Current Time, OnUpdate=Current Time | When dealer record was last updated |

**Indexes**:
- Primary Key: `dealer_id`
- Index on `name` for searching
- Index on `is_active` for filtering

**Model Definition** (simplified):
```python
class Dealer(db.Model):
    __tablename__ = 'dealers'
    
    dealer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(100))
    address = db.Column(db.Text)
    commission_rate = db.Column(db.Numeric(5, 2), default=10.00)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    cars = db.relationship('Car', backref='dealer_ref', foreign_keys='Car.dealer_id')
    sales = db.relationship('Sale', back_populates='dealer')
```

### Stands Table

**Table Name**: `stands`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| stand_id | Integer | Primary Key | Unique identifier for each stand |
| name | String(100) | Not Null | Name of the stand |
| location | String(200) | Not Null | Location of the stand |
| capacity | Integer | Default=10 | Maximum number of cars that can be displayed |
| manager_name | String(100) | Nullable | Name of the stand manager |
| contact_phone | String(20) | Nullable | Contact phone for the stand |
| notes | Text | Nullable | Additional notes about the stand |
| is_active | Boolean | Default=True | Whether stand is active |
| created_at | DateTime | Default=Current Time | When stand was added |
| updated_at | DateTime | Default=Current Time, OnUpdate=Current Time | When stand record was last updated |

**Indexes**:
- Primary Key: `stand_id`
- Index on `name` for searching
- Index on `is_active` for filtering

**Calculated Properties**:
- `current_count`: Number of cars currently on the stand
- `space_available`: Boolean indicating if there is space available (current_count < capacity)

**Model Definition** (simplified):
```python
class Stand(db.Model):
    __tablename__ = 'stands'
    
    stand_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, default=10)
    manager_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    @property
    def current_count(self):
        return len([car for car in self.cars if car.date_sold is None])
        
    @property
    def space_available(self):
        return self.current_count < self.capacity
```

### Repairs Table

**Table Name**: `repairs`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| repair_id | Integer | Primary Key | Unique identifier for each repair |
| car_id | Integer | Foreign Key (cars.car_id), Not Null | ID of the car being repaired |
| provider_id | Integer | Foreign Key (repair_providers.provider_id), Nullable | ID of the repair provider |
| repair_type | String(50) | Not Null | Type of repair (Mechanical, Body, Electrical, etc.) |
| description | Text | Not Null | Description of the repair |
| start_date | Date | Not Null, Default=Current Date | When repair started |
| end_date | Date | Nullable | When repair was completed |
| repair_cost | Numeric(10,2) | Default=0.00 | Total cost of the repair |
| status | String(20) | Default='Pending' | Status of the repair (Pending, In Progress, Completed) |
| notes | Text | Nullable | Additional notes about the repair |
| created_at | DateTime | Default=Current Time | When repair record was created |
| updated_at | DateTime | Default=Current Time, OnUpdate=Current Time | When repair record was last updated |

**Indexes**:
- Primary Key: `repair_id`
- Foreign Key: `car_id` references `cars.car_id`
- Foreign Key: `provider_id` references `repair_providers.provider_id`
- Index on `status` for filtering
- Index on `start_date`, `end_date` for date-based queries

**Calculated Properties**:
- `duration_days`: Days taken for repair (end_date - start_date)
- `parts_cost`: Sum of costs of all parts used in this repair

**Model Definition** (simplified):
```python
class Repair(db.Model):
    __tablename__ = 'repairs'
    
    repair_id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.car_id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('repair_providers.provider_id'))
    repair_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=datetime.now().date)
    end_date = db.Column(db.Date)
    repair_cost = db.Column(db.Numeric(10, 2), default=0.00)
    status = db.Column(db.String(20), default='Pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    provider = db.relationship('RepairProvider')
    repair_parts = db.relationship('RepairPart', backref='repair', cascade='all, delete-orphan')
    
    @property
    def duration_days(self):
        if not self.end_date or not self.start_date:
            return None
        return (self.end_date - self.start_date).days
        
    @property
    def parts_cost(self):
        return sum(rp.total_cost for rp in self.repair_parts)
```

### Parts Table

**Table Name**: `parts`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| part_id | Integer | Primary Key | Unique identifier for each part |
| part_name | String(100) | Not Null | Name of the part |
| description | Text | Nullable | Description of the part |
| manufacturer | String(100) | Nullable | Manufacturer of the part |
| standard_price | Numeric(10,2) | Nullable | Standard price of the part |
| stock_quantity | Integer | Not Null, Default=0, ≥0 | Current inventory level |
| make | String(100) | Nullable | Vehicle make this part is for |
| model | String(100) | Nullable | Vehicle model this part is for |
| storage_location | String(100) | Nullable | Where the part is stored |

**Indexes**:
- Primary Key: `part_id`
- Index on `part_name` for searching
- Index on `manufacturer` for filtering
- Index on `make` and `model` for vehicle-specific parts lookup

**Constraints**:
- The `stock_quantity` must be greater than or equal to 0 (enforced by check constraint)

**Model Definition** (simplified):
```python
class Part(db.Model):
    __tablename__ = 'parts'
    
    part_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    part_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    manufacturer = db.Column(db.String(100), nullable=True)
    standard_price = db.Column(db.Numeric(10, 2), nullable=True)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    make = db.Column(db.String(100), nullable=True)
    model = db.Column(db.String(100), nullable=True)
    storage_location = db.Column(db.String(100), nullable=True)
    
    # Add check constraint to prevent negative stock values
    __table_args__ = (
        CheckConstraint('stock_quantity >= 0', name='check_stock_quantity_non_negative'),
    )
    
    # Relationships
    repairs = db.relationship('Repair', secondary='repair_parts', back_populates='parts')
    
    def is_duplicate(self, name, make=None, model=None):
        """Case-insensitive + spacing-insensitive check for duplication"""
        # Implementation details...
```

### RepairPart Association Table

**Table Name**: `repair_parts`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| repair_part_id | Integer | Primary Key | Unique identifier for each repair-part association |
| repair_id | Integer | Foreign Key (repairs.repair_id), Not Null | ID of the repair |
| part_id | Integer | Foreign Key (parts.part_id), Not Null | ID of the part used |
| quantity | Integer | Default=1 | Quantity of parts used |
| unit_cost | Numeric(10,2) | Not Null | Cost per unit at time of use |
| total_cost | Numeric(10,2) | Not Null | Total cost (quantity * unit_cost) |
| notes | Text | Nullable | Additional notes |

**Indexes**:
- Primary Key: `repair_part_id`
- Foreign Key: `repair_id` references `repairs.repair_id`
- Foreign Key: `part_id` references `parts.part_id`

**Model Definition** (simplified):
```python
class RepairPart(db.Model):
    __tablename__ = 'repair_parts'
    
    repair_part_id = db.Column(db.Integer, primary_key=True)
    repair_id = db.Column(db.Integer, db.ForeignKey('repairs.repair_id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.part_id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False)
    total_cost = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.Text)
    
    def __init__(self, repair_id, part_id, quantity, unit_cost, notes=None):
        self.repair_id = repair_id
        self.part_id = part_id
        self.quantity = quantity
        self.unit_cost = unit_cost
        self.total_cost = unit_cost * quantity
        self.notes = notes
```

### RepairProviders Table

**Table Name**: `repair_providers`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| provider_id | Integer | Primary Key | Unique identifier for each provider |
| name | String(100) | Not Null | Name of the repair provider |
| contact_name | String(100) | Nullable | Primary contact person |
| contact_phone | String(20) | Nullable | Phone number |
| contact_email | String(100) | Nullable | Email address |
| address | Text | Nullable | Physical address |
| specialization | String(100) | Nullable | Area of specialization |
| rate_per_hour | Numeric(10,2) | Nullable | Hourly rate charged |
| is_preferred | Boolean | Default=False | Whether this is a preferred provider |
| notes | Text | Nullable | Additional notes |
| is_active | Boolean | Default=True | Whether provider is active |
| created_at | DateTime | Default=Current Time | When provider was added |
| updated_at | DateTime | Default=Current Time, OnUpdate=Current Time | When provider record was last updated |

**Indexes**:
- Primary Key: `provider_id`
- Index on `name` for searching
- Index on `is_active` for filtering
- Index on `is_preferred` for filtering

**Model Definition** (simplified):
```python
class RepairProvider(db.Model):
    __tablename__ = 'repair_providers'
    
    provider_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(100))
    address = db.Column(db.Text)
    specialization = db.Column(db.String(100))
    rate_per_hour = db.Column(db.Numeric(10, 2))
    is_preferred = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    repairs = db.relationship('Repair', backref='provider_ref')
```

### Users Table

**Table Name**: `users`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| user_id | Integer | Primary Key | Unique identifier for each user |
| username | String(64) | Not Null, Unique | Username for login |
| email | String(120) | Not Null, Unique | Email address |
| password_hash | String(128) | Not Null | Hashed password |
| first_name | String(64) | Nullable | User's first name |
| last_name | String(64) | Nullable | User's last name |
| role | String(20) | Default='user' | User role (admin, manager, user) |
| is_active | Boolean | Default=True | Whether user account is active |
| last_login | DateTime | Nullable | Last login timestamp |
| created_at | DateTime | Default=Current Time | When user was created |
| updated_at | DateTime | Default=Current Time, OnUpdate=Current Time | When user record was last updated |

**Indexes**:
- Primary Key: `user_id`
- Unique Index on `username`
- Unique Index on `email`
- Index on `role` for authorization checks
- Index on `is_active` for filtering

**Model Definition** (simplified):
```python
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def get_id(self):
        return str(self.user_id)
        
    @property
    def is_admin(self):
        return self.role == 'admin'
        
    @property
    def is_manager(self):
        return self.role in ['admin', 'manager']
        
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
```

### Vehicle Makes Table

**Table Name**: `vehicle_makes`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Autoincrement | Unique identifier for each make |
| name | String(50) | Not Null, Unique | Name of the vehicle make (manufacturer) |

**Indexes**:
- Primary Key: `id`
- Unique Index on `name`

**Model Definition** (simplified):
```python
class VehicleMake(db.Model):
    __tablename__ = 'vehicle_makes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relationships
    models = db.relationship('VehicleModel', backref='make', lazy='dynamic')
    
    @staticmethod
    def sanitize_name(name):
        """Sanitize make name: trim whitespace and capitalize first letter of each word"""
        if not name:
            return None
        return ' '.join(word.capitalize() for word in name.strip().split())
    
    @classmethod
    def get_or_create(cls, make_name):
        """Get existing make or create a new one if it doesn't exist"""
        sanitized_name = cls.sanitize_name(make_name)
        if not sanitized_name:
            return None
            
        existing = cls.query.filter(db.func.lower(cls.name) == db.func.lower(sanitized_name)).first()
        if existing:
            return existing
            
        new_make = cls(name=sanitized_name)
        db.session.add(new_make)
        db.session.commit()
        return new_make
```

### Vehicle Models Table

**Table Name**: `vehicle_models`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Autoincrement | Unique identifier for each model |
| name | String(50) | Not Null | Name of the vehicle model |
| make_id | Integer | Foreign Key (vehicle_makes.id), Not Null | ID of the make this model belongs to |

**Indexes**:
- Primary Key: `id`
- Foreign Key: `make_id` references `vehicle_makes.id`
- Unique Constraint on `name` and `make_id` combination

**Model Definition** (simplified):
```python
class VehicleModel(db.Model):
    __tablename__ = 'vehicle_models'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    make_id = db.Column(db.Integer, db.ForeignKey('vehicle_makes.id'), nullable=False)
    
    # Add a unique constraint for name+make_id
    __table_args__ = (
        db.UniqueConstraint('name', 'make_id', name='unique_model_make'),
    )
    
    @staticmethod
    def sanitize_name(name):
        """Sanitize model name: trim whitespace and capitalize first letter of each word"""
        if not name:
            return None
        return ' '.join(word.capitalize() for word in name.strip().split())
    
    @classmethod
    def get_or_create(cls, model_name, make_id=None):
        """Get existing model or create a new one if it doesn't exist"""
        sanitized_name = cls.sanitize_name(model_name)
        if not sanitized_name:
            return None
            
        existing = cls.query.filter(
            db.func.lower(cls.name) == db.func.lower(sanitized_name),
            cls.make_id == make_id
        ).first()
        
        if existing:
            return existing
            
        new_model = cls(name=sanitized_name, make_id=make_id)
        db.session.add(new_model)
        db.session.commit()
        return new_model
```

### Vehicle Colors Table

**Table Name**: `vehicle_colors`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Autoincrement | Unique identifier for each color |
| name | String(50) | Not Null, Unique | Name of the vehicle color |

**Indexes**:
- Primary Key: `id`
- Unique Index on `name`

**Model Definition** (simplified):
```python
class VehicleColor(db.Model):
    __tablename__ = 'vehicle_colors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    @staticmethod
    def sanitize_name(name):
        """Sanitize color name: trim whitespace and capitalize first letter of each word"""
        if not name:
            return None
        return ' '.join(word.capitalize() for word in name.strip().split())
```

### Vehicle Years Table

**Table Name**: `vehicle_years`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Autoincrement | Unique identifier for each year entry |
| year | Integer | Not Null, Unique | Vehicle manufacturing year |

**Indexes**:
- Primary Key: `id`
- Unique Index on `year`

**Model Definition** (simplified):
```python
class VehicleYear(db.Model):
    __tablename__ = 'vehicle_years'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.Integer, unique=True, nullable=False)
```

### Settings Table

**Table Name**: `settings`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Autoincrement | Unique identifier for each setting |
| key | String(100) | Not Null, Unique | Unique key for the setting |
| value | String(255) | Not Null | Value of the setting |
| type | String(20) | Not Null, Default='str' | Data type (str, int, bool, float) |
| description | Text | Nullable | Description of the setting |
| created_at | DateTime | Default=Current Time | When the setting was created |
| updated_at | DateTime | Default=Current Time, OnUpdate=Current Time | When the setting was last updated |

**Indexes**:
- Primary Key: `id`
- Unique Index on `key`

**Model Definition** (simplified):
```python
class Setting(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(20), default='str')  # str, int, bool, float
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    @classmethod
    def get_setting(cls, key, default=None, as_type=None):
        """Get a setting value by key with optional default value"""
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            return default
        
        # Determine conversion type
        convert_type = as_type or setting.type
        
        # Convert value based on type
        try:
            if convert_type == 'int':
                return int(setting.value)
            elif convert_type == 'float':
                return float(setting.value)
            elif convert_type == 'bool':
                return setting.value.lower() in ('true', '1', 'yes', 'y', 'on')
            else:
                return setting.value
        except (ValueError, TypeError):
            # If conversion fails, return the default
            return default
```

## Table Relationships

### One-to-Many Relationships:
- **Car to Repairs**: A car can have multiple repairs
- **Car to Sales**: A car can have one sale (although technically still a one-to-many relationship in the schema)
- **Dealer to Sales**: A dealer can have multiple sales
- **Stand to Cars**: A stand can have multiple cars
- **Repair Provider to Repairs**: A repair provider can provide multiple repairs
- **User to Various Activity Records**: Users can create multiple records of various types
- **VehicleMake to VehicleModels**: A make can have multiple models

### One-to-One Relationships:
- **Car to Sale**: A car can have at most one sale record (enforced at the application level)

### Many-to-Many Relationships:
- **Repairs to Parts**: A repair can use multiple parts, and a part can be used in multiple repairs (through the RepairPart association table)

## Database Integrity

The database schema implements several mechanisms to maintain data integrity:

### Primary Key Constraints
Every table has a primary key field that uniquely identifies each record.

### Foreign Key Constraints
Foreign key constraints ensure that relationships between tables are valid and that related records exist.

### Not Null Constraints
Critical fields are marked as `NOT NULL` to ensure that essential data is always provided.

### Unique Constraints
Certain fields that must contain unique values are constrained with unique indexes.

### Default Values
Many fields have default values to ensure consistency when specific values are not provided.

### Cascading Deletes
Some relationships are configured with cascading deletes to automatically remove dependent records when a parent record is deleted. 

### Data Sanitization
The vehicle make, model, and color tables provide sanitization methods to ensure standardized data entry, capitalizing words and removing extra whitespace. 