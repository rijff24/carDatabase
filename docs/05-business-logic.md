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
    return sum(repair.repair_cost for repair in self.repairs.all())
```

This aggregates all repair costs associated with a vehicle.

### Total Investment Calculation

The total investment in a car is calculated as:

```python
def total_investment(self):
    """Calculate total investment in the car"""
    return self.purchase_price + self.total_repair_cost + self.refuel_cost
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