# Business Logic

This document details the key calculations, business rules, and workflows implemented in the Car Repair and Sales Tracking Application.

## Key Calculations

### Car Profit Calculation

The profit from a car sale is calculated as the difference between the sale price and total investment:

```python
def profit(self):
    """Calculate profit from sale"""
    if not self.sale_price:
        return None
    return self.sale_price - (self.purchase_price + self.total_repair_cost + self.refuel_cost)
```

Where:
- `sale_price`: Final selling price of the car
- `purchase_price`: Original price paid to acquire the car
- `total_repair_cost`: Sum of all repair costs for the car
- `refuel_cost`: Cost of refueling the car

This calculation is implemented as a property on the `Car` model and is computed dynamically rather than stored in the database.

### Commission Calculation

The commission for a car sale is determined based on profit thresholds:

```python
def commission(self):
    """Calculate commission based on profit"""
    profit = self.profit
    if profit is None:
        return None
    return 10000 if profit > 30000 else 5000
```

Commission rules:
- If profit is greater than 30,000, commission is 10,000
- Otherwise, commission is 5,000

This calculation is also implemented as a property on the `Car` model.

### Profit Margin Calculation

The profit margin percentage for a sale is calculated as:

```python
def profit_margin(self):
    """Calculate profit margin as a percentage"""
    if not self.sale_price or float(self.sale_price) == 0:
        return 0
    return (self.profit / float(self.sale_price)) * 100
```

This gives the profit as a percentage of the selling price, which is a common business metric for evaluating sales performance.

### Return on Investment (ROI) Calculation

The return on investment is calculated as:

```python
def roi(self):
    """Calculate return on investment as a percentage"""
    if not self.profit or not self.total_investment or float(self.total_investment) == 0:
        return 0
    return (self.profit / float(self.total_investment)) * 100
```

This metric evaluates how efficiently the business is using its capital by showing the percentage return on the total investment made in the vehicle.

### Days in Reconditioning Calculation

The number of days a car spent in reconditioning is calculated as:

```python
def days_in_recon(self):
    """Calculate days in reconditioning"""
    if not self.date_added_to_stand or not self.date_bought:
        return None
    return (self.date_added_to_stand - self.date_bought).days
```

This calculation measures the time from vehicle purchase to when it's ready for display, which is an important operational efficiency metric.

### Days on Stand Calculation

The number of days a car spent on the display stand is calculated as:

```python
def days_on_stand(self):
    """Calculate days on stand"""
    if not self.date_sold or not self.date_added_to_stand:
        return None
    return (self.date_sold - self.date_added_to_stand).days
```

This calculation measures how long it takes to sell a vehicle once it's on display, which is a key metric for sales velocity.

### Total Repair Cost Calculation

The total cost of all repairs for a car is calculated by summing the costs of individual repairs:

```python
def total_repair_cost(self):
    """Calculate total repair costs for this car"""
    return sum(float(repair.repair_cost) for repair in self.repairs.all())
```

This aggregates all repair costs associated with a vehicle.

### Total Investment Calculation

The total investment in a car is calculated as:

```python
def total_investment(self):
    """Calculate total investment in the car"""
    repair_cost = self.total_repair_cost or 0
    refuel = float(self.refuel_cost) if self.refuel_cost else 0
    purchase = float(self.purchase_price) if self.purchase_price else 0
    return purchase + repair_cost + refuel
```

This represents the total amount invested in the vehicle before sale.

### Repair Duration Calculation

The duration of a repair is calculated as:

```python
def duration_days(self):
    if not self.end_date or not self.start_date:
        return None
    return (self.end_date - self.start_date).days
```

This measures how long a repair takes to complete, which is important for tracking repair efficiency.

### Parts Cost for Repair Calculation

The total cost of parts used in a repair is calculated by summing the costs of all parts:

```python
def parts_cost(self):
    return sum(rp.total_cost for rp in self.repair_parts)
```

This aggregates the costs of all parts used in a specific repair.

## Business Rules

### Vehicle Status Management

The application enforces specific rules around vehicle status transitions:

1. **Status Workflow**:
   - New vehicles start with status "Waiting for Repairs"
   - After repair completion, status changes to "Ready for Display"
   - When added to a stand, status changes to "On Display"
   - When sold, status changes to "Sold"

2. **Status Validation**:
   ```python
   VALID_STATUSES = ['Waiting for Repairs', 'In Repair', 'Ready for Display', 'On Display', 'Sold']
   
   if status not in VALID_STATUSES:
       raise ValidationError(f"Invalid status: {status}")
   ```

3. **Status Transition Rules**:
   ```python
   def change_status(self, new_status):
       # Only allow sale status to be set when sale_price and date_sold are set
       if new_status == 'Sold' and (not self.sale_price or not self.date_sold):
           raise ValidationError("Cannot mark as sold without sale price and date")
       
       # Cannot add to display without stand_id
       if new_status == 'On Display' and not self.stand_id:
           raise ValidationError("Cannot display without assigning to a stand")
       
       # Update status
       self.repair_status = new_status
   ```

### Stand Capacity Management

Stands have capacity limits that must be enforced:

```python
def add_car_to_stand(self, car):
    # Check if stand has capacity
    if not self.space_available:
        raise ValidationError(f"Stand {self.name} is at capacity ({self.capacity})")
    
    # Remove car from any existing stand
    if car.stand_id:
        car.stand.remove_car(car)
    
    # Update car
    car.stand_id = self.stand_id
    car.current_location = self.location
    car.date_added_to_stand = datetime.now().date()
    car.repair_status = 'On Display'
```

### Sale Recording Rules

When recording a sale, several validations are performed:

```python
def record_sale(self, sale_price, sale_date, dealer_id, **kwargs):
    # Cannot sell a car that's already sold
    if self.date_sold:
        raise ValidationError("Car has already been sold")
    
    # Cannot sell a car that's not on display
    if self.repair_status != 'On Display':
        raise ValidationError("Car must be on display before it can be sold")
    
    # Update car details
    self.sale_price = sale_price
    self.date_sold = sale_date
    self.repair_status = 'Sold'
    
    # Create sale record
    sale = Sale(
        car_id=self.car_id,
        dealer_id=dealer_id,
        sale_price=sale_price,
        sale_date=sale_date,
        **kwargs
    )
    
    return sale
```

### User Role-Based Permissions

The application implements role-based access control:

```python
def requires_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
                
            if role == 'admin' and not current_user.is_admin():
                abort(403)
                
            if role == 'manager' and not current_user.is_manager():
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

Access rules:
- Admin users can access all features
- Managers can access everything except user management
- Regular users have limited access based on their specific role
- Some features are only available to specific roles

### Aging Vehicle Thresholds

The application includes configurable thresholds for vehicle aging on stands:

```python
def is_aging(self):
    """Check if a car has been on stand too long without selling"""
    if not self.date_added_to_stand or self.date_sold:
        return False
        
    # Get the aging threshold from settings
    threshold_days = Setting.get_setting('stand_aging_threshold_days', 180)
    days_on_stand = (datetime.now().date() - self.date_added_to_stand).days
    
    return days_on_stand >= threshold_days
```

This logic is used to flag vehicles that may require price adjustments or other interventions to increase the chance of sale.

### Status Inactivity Rules

The application monitors vehicles with unchanged status for extended periods:

```python
def has_inactive_status(self):
    """Check if a car's status has remained unchanged for too long"""
    if self.date_sold:  # Sold cars are never inactive
        return False
        
    # Get the inactivity threshold from settings
    threshold_days = Setting.get_setting('status_inactivity_threshold_days', 30)
    
    # Check how long since the status was last changed
    last_status_change = self.last_status_changed or self.date_bought
    days_since_change = (datetime.now().date() - last_status_change).days
    
    return days_since_change >= threshold_days
```

This helps identify vehicles that may be stuck in a particular stage of processing.

### Depreciation Tracking

When enabled, the application can track vehicle depreciation over time:

```python
def calculate_current_value(self):
    """Calculate current value taking into account depreciation"""
    if self.date_sold:  # Sold cars use actual sale price
        return self.sale_price
        
    # Check if depreciation tracking is enabled
    depreciation_enabled = Setting.get_setting('enable_depreciation_tracking', False)
    if not depreciation_enabled:
        return self.total_investment
        
    # Calculate days since purchase
    days_owned = (datetime.now().date() - self.date_bought).days
    
    # Apply depreciation formula (example: 15% annual depreciation)
    annual_rate = 0.15
    daily_rate = annual_rate / 365
    depreciation_factor = (1 - daily_rate) ** days_owned
    
    return self.total_investment * depreciation_factor
```

This feature allows for more accurate inventory valuation, particularly for vehicles held for extended periods.

### Data Validation and Sanitization

The application implements input sanitization for vehicle data:

```python
# Example: Vehicle make sanitization
@staticmethod
def sanitize_name(name):
    """Sanitize make name: trim whitespace and capitalize first letter of each word"""
    if not name:
        return None
    # Remove any extra whitespace and capitalize each word
    return ' '.join(word.capitalize() for word in name.strip().split())
```

This ensures that vehicle makes, models, and colors are stored consistently in the database, enabling better search and reporting capabilities.

### Settings Management

The application provides a flexible settings system for adjusting business rules without code changes:

```python
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

Default settings include:
- `stand_aging_threshold_days`: Number of days after which a car on stand is considered aging (default: 180)
- `status_inactivity_threshold_days`: Number of days after which a car with unchanged status is considered inactive (default: 30)
- `enable_depreciation_tracking`: Toggle for depreciation calculation (default: false)
- `enable_status_warnings`: Toggle for showing status warning indicators (default: true)
- `enable_subform_dropdowns`: Toggle for using dropdown modals for subforms (default: true)
- `enable_dark_mode`: Toggle for UI dark theme (default: false)

### Car-Sale Consistency Checking

The application enforces consistency between car and sale records using event listeners:

```python
@event.listens_for(Car, 'load')
def check_car_sale_consistency(target, context):
    """Ensure car.date_sold is consistent with the associated sale record"""
    # This event is fired when a Car object is loaded from the database
    # We'll defer actual validation until the object is accessed
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
```

This ensures that car records and sale records remain synchronized even when modified separately.

### Bulk Import Validation

When importing data in bulk, the application applies validation rules to ensure data quality:

```python
# Example: Car import validation
def import_cars(file: FileStorage) -> Dict[str, Any]:
    """Import cars from a CSV or Excel file."""
    success_count = 0
    fail_count = 0
    errors = []
    
    # Validate required columns
    required_columns = ['VIN', 'Make', 'Model', 'Year', 'Colour', 'Purchase Price']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        return {"success": 0, "failed": 0, "errors": errors}
    
    # Process each row with validation
    for index, row in df.iterrows():
        row_errors = []
        
        # Check for required fields
        if pd.isna(row.get('VIN')) or not str(row.get('VIN')).strip():
            row_errors.append('VIN is required')
        
        # Skip row if validation errors
        if row_errors:
            fail_count += 1
            errors.append(f"Row {index+2}: {'; '.join(row_errors)}")
            continue
            
        # Process valid row
        # ...
    
    return {"success": success_count, "failed": fail_count, "errors": errors}
```

This ensures that imported data meets the same validation standards as data entered through the application's user interface.

## Business Workflows

### New Vehicle Acquisition Workflow

1. **Record Purchase**:
   - Create new Car record with purchase details
   - Initial status: "Waiting for Repairs"
   - Set dealer_id if purchased through a dealer

2. **Repair Planning**:
   - Create Repair records for needed repairs
   - Assign repair providers
   - Add required parts

3. **Repair Execution**:
   - Update repair status as work progresses
   - Record actual costs
   - Update car status to "In Repair"

4. **Preparation for Display**:
   - Complete all repairs
   - Update car status to "Ready for Display"
   - Calculate total reconditioning cost

5. **Display Assignment**:
   - Assign car to a display stand
   - Update car status to "On Display"
   - Record date_added_to_stand

### Sale Process Workflow

1. **Sale Negotiation**:
   - Car must be in "On Display" status
   - Calculate potential profit at different price points

2. **Sale Recording**:
   - Record sale price and date
   - Assign dealer who made the sale
   - Update car status to "Sold"
   - Create Sale record with transaction details

3. **Commission Calculation**:
   - Calculate profit
   - Determine commission based on profit
   - Record commission for dealer

4. **Reporting**:
   - Update inventory reports
   - Update sales performance reports
   - Update dealer performance metrics

## Business KPIs and Metrics

The application tracks and calculates several key business metrics:

1. **Average Days to Sell**: Average time from purchase to sale
   ```python
   def average_days_to_sell(start_date=None, end_date=None):
       query = Car.query.filter(Car.date_sold != None)
       if start_date:
           query = query.filter(Car.date_sold >= start_date)
       if end_date:
           query = query.filter(Car.date_sold <= end_date)
           
       cars = query.all()
       if not cars:
           return 0
           
       total_days = sum((car.date_sold - car.date_bought).days for car in cars)
       return total_days / len(cars)
   ```

2. **Average Profit Margin**: Average profit as a percentage of sale price
   ```python
   def average_profit_margin(start_date=None, end_date=None):
       query = Car.query.filter(Car.date_sold != None)
       if start_date:
           query = query.filter(Car.date_sold >= start_date)
       if end_date:
           query = query.filter(Car.date_sold <= end_date)
           
       cars = query.all()
       if not cars:
           return 0
           
       profit_margins = [car.profit_margin for car in cars if car.profit_margin is not None]
       if not profit_margins:
           return 0
           
       return sum(profit_margins) / len(profit_margins)
   ```

3. **Inventory Turnover Rate**: Rate at which inventory is sold and replaced
   ```python
   def inventory_turnover_rate(period_days=30):
       # Count cars sold in period
       end_date = datetime.now().date()
       start_date = end_date - timedelta(days=period_days)
       sold_count = Car.query.filter(
           Car.date_sold >= start_date,
           Car.date_sold <= end_date
       ).count()
       
       # Average inventory during period
       avg_inventory = Car.query.filter(
           or_(
               Car.date_sold == None,
               Car.date_sold >= start_date
           ),
           Car.date_bought <= end_date
       ).count() / 2
       
       if avg_inventory == 0:
           return 0
           
       # Annualized turnover rate
       return (sold_count / avg_inventory) * (365 / period_days)
   ```

4. **Repair Efficiency**: Average repair cost and duration
   ```python
   def repair_efficiency_metrics():
       repairs = Repair.query.filter(Repair.end_date != None).all()
       if not repairs:
           return {'avg_cost': 0, 'avg_duration': 0}
           
       total_cost = sum(repair.repair_cost for repair in repairs)
       total_duration = sum(repair.duration_days for repair in repairs 
                           if repair.duration_days is not None)
       
       return {
           'avg_cost': total_cost / len(repairs),
           'avg_duration': total_duration / len(repairs) if total_duration > 0 else 0
       }
   ```

## Business Validation Rules

The application implements numerous validation rules to ensure data integrity:

1. **Price Validation**:
   ```python
   def validate_price(price):
       if price is None:
           return None
       
       try:
           price = float(price)
       except (ValueError, TypeError):
           raise ValidationError("Price must be a valid number")
           
       if price < 0:
           raise ValidationError("Price cannot be negative")
           
       return price
   ```

2. **Date Validation**:
   ```python
   def validate_date_sequence(start_date, end_date):
       if end_date and start_date and end_date < start_date:
           raise ValidationError("End date cannot be earlier than start date")
   ```

3. **Required Field Validation**:
   ```python
   def validate_required_fields(data, required_fields):
       for field in required_fields:
           if field not in data or data[field] is None or data[field] == '':
               raise ValidationError(f"Field '{field}' is required")
   ```

4. **Status Transition Validation**:
   ```python
   def validate_status_transition(current_status, new_status):
       valid_transitions = {
           'Waiting for Repairs': ['In Repair', 'Ready for Display'],
           'In Repair': ['Ready for Display'],
           'Ready for Display': ['On Display'],
           'On Display': ['Sold'],
           'Sold': []
       }
       
       if new_status not in valid_transitions.get(current_status, []):
           raise ValidationError(f"Cannot transition from '{current_status}' to '{new_status}'")
   ```

These business rules and calculations ensure the application operates according to the specified business requirements and provides accurate financial and operational metrics.

## System Settings

The application includes a configurable settings system that affects various aspects of business logic and application behavior.

### Setting Storage and Retrieval

Settings are stored in the database using a flexible key-value storage model:

```python
# Getting a setting with a default fallback value
threshold_days = Setting.get_setting('stand_aging_threshold_days', 180)

# Setting a value with type and description
Setting.set_setting(
    'enable_depreciation_tracking',
    True,
    description='Track depreciation of vehicles over time',
    type='bool'
)
```

### Core Settings and Their Effects

| Setting Key | Type | Default | Description | Effect |
|-------------|------|---------|-------------|--------|
| `stand_aging_threshold_days` | int | 180 | Number of days after which a car on a stand is considered aging | Controls when vehicles are flagged as "aging" in inventory reports; affects inventory aging warnings |
| `status_inactivity_threshold_days` | int | 30 | Number of days after which a car with unchanged status is considered inactive | Determines when vehicles are flagged as "inactive" in status reports; affects operational efficiency metrics |
| `enable_depreciation_tracking` | bool | false | Track depreciation of vehicles over time | When enabled, activates depreciation calculations in financial reports and vehicle valuation |
| `enable_status_warnings` | bool | true | Show warnings for vehicles with stale status | Controls whether the system displays warnings for vehicles with inactive status |
| `enable_subform_dropdowns` | bool | true | Use dropdown modals for subforms | UI preference that affects how subforms are displayed in the interface |
| `enable_dark_mode` | bool | false | Switch to a dark theme for the interface | UI preference that toggles between light and dark interface themes |

### Application of Settings

Settings are applied throughout the application in various contexts:

```python
# Example: Using settings in business logic
def check_vehicle_aging(vehicle):
    """Flag vehicles that have been on stand too long"""
    threshold = Setting.get_setting('stand_aging_threshold_days', 180)
    
    if vehicle.days_on_stand and vehicle.days_on_stand > threshold:
        return True  # Vehicle is aging
    return False  # Vehicle is within normal timeframe
```

```python
# Example: Using settings in a route
@app.route('/inventory')
def inventory():
    show_warnings = Setting.get_setting('enable_status_warnings', True)
    return render_template('inventory.html', show_warnings=show_warnings)
```

### Setting Categories

Settings are organized into logical groups for management:

1. **Thresholds & Rules** - Numerical thresholds and business rule toggles
2. **General Configuration** - Interface and general application preferences
3. **User Management** - Settings related to user accounts and permissions

### Access Control for Settings

Settings management is restricted to administrators:

```python
@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
@requires_role('admin')
def index():
    # Settings management code
```

This ensures that only authorized users can modify system-wide configurations. 