# Error Handling

This document details the error handling mechanisms implemented in the Car Repair and Sales Tracking Application.

## Error Types

The application handles the following categories of errors:

1. **User Input Errors** - Invalid or incomplete data submitted by users
2. **Authentication Errors** - Issues with user authentication and authorization
3. **Database Errors** - Problems with database operations
4. **Business Logic Errors** - Violations of business rules
5. **System Errors** - Issues with system resources or external services
6. **Unhandled Exceptions** - Unexpected errors

## Error Handling Architecture

The application implements a layered error handling approach:

```
┌─────────────────────────────────────────────┐
│ Global Exception Handler (app-wide catchall) │
└──────────────────────┬──────────────────────┘
                       │
     ┌─────────────────┼─────────────────┐
     │                 │                 │
┌────▼─────┐     ┌─────▼────┐     ┌─────▼────┐
│ Route    │     │ Form     │     │ API      │
│ Handlers │     │ Handlers │     │ Handlers │
└────┬─────┘     └─────┬────┘     └─────┬────┘
     │                 │                 │
┌────▼─────┐     ┌─────▼────┐     ┌─────▼────┐
│ Template │     │ Local    │     │ JSON     │
│ Rendering│     │ Handling │     │ Response │
└──────────┘     └──────────┘     └──────────┘
```

## Form Validation Errors

Form validation is handled by Flask-WTF forms:

```python
class VehicleForm(FlaskForm):
    vehicle_name = StringField('Vehicle Name', validators=[
        DataRequired(message="Vehicle name is required"),
        Length(min=3, max=100, message="Vehicle name must be 3-100 characters")
    ])
    purchase_price = DecimalField('Purchase Price', validators=[
        DataRequired(message="Purchase price is required"),
        NumberRange(min=0, message="Price cannot be negative")
    ])
    date_bought = DateField('Purchase Date', validators=[
        DataRequired(message="Purchase date is required"),
        ValidateDateNotInFuture()
    ])
    
    # Custom validator
    def validate_vehicle_name(form, field):
        if len(field.data.split()) < 2:
            raise ValidationError("Please provide make and model")
```

### Client-Side Validation

User input is validated on the client side using:

1. **HTML5 Validation**:
   ```html
   <input type="number" min="0" step="0.01" required>
   ```

2. **JavaScript Validation**:
   ```javascript
   $('#vehicleForm').validate({
       rules: {
           vehicle_name: {
               required: true,
               minlength: 3
           },
           purchase_price: {
               required: true,
               number: true,
               min: 0
           }
       },
       // Error messages and styling
   });
   ```

### Server-Side Validation

All inputs are validated server-side regardless of client validation:

```python
@inventory.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    form = VehicleForm()
    
    if form.validate_on_submit():
        try:
            car = Car(
                vehicle_name=form.vehicle_name.data,
                purchase_price=form.purchase_price.data,
                date_bought=form.date_bought.data,
                # Other fields
            )
            db.session.add(car)
            db.session.commit()
            flash('Vehicle added successfully', 'success')
            return redirect(url_for('inventory.view_car', car_id=car.car_id))
        except Exception as e:
            db.session.rollback()
            log_error('add_car', str(e))
            flash('An error occurred while adding the vehicle', 'danger')
    
    # If validation failed or GET request, render form with errors
    return render_template('inventory/add_car.html', form=form)
```

## Database Error Handling

Database errors are caught and handled at multiple levels:

```python
def safe_commit():
    """Safely commit database changes with error handling"""
    try:
        db.session.commit()
        return True, None
    except IntegrityError as e:
        db.session.rollback()
        log_error('database_integrity', str(e))
        return False, "Database integrity error. This may be due to duplicate data."
    except SQLAlchemyError as e:
        db.session.rollback()
        log_error('database', str(e))
        return False, "Database error. Please try again later."
    except Exception as e:
        db.session.rollback()
        log_error('database_unknown', str(e))
        return False, "An unexpected error occurred. Please try again later."
```

Usage example:

```python
@inventory.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    form = VehicleForm()
    
    if form.validate_on_submit():
        car = Car(
            vehicle_name=form.vehicle_name.data,
            purchase_price=form.purchase_price.data,
            date_bought=form.date_bought.data,
            # Other fields
        )
        db.session.add(car)
        
        success, error_message = safe_commit()
        if success:
            flash('Vehicle added successfully', 'success')
            return redirect(url_for('inventory.view_car', car_id=car.car_id))
        else:
            flash(error_message, 'danger')
    
    # If validation failed or GET request, render form with errors
    return render_template('inventory/add_car.html', form=form)
```

## Business Logic Error Handling

Business rule violations are handled with custom exceptions:

```python
class BusinessRuleError(Exception):
    """Exception raised for business rule violations"""
    pass

class ValidationError(Exception):
    """Exception raised for data validation errors"""
    pass
```

These exceptions are used throughout the application:

```python
def record_sale(car_id, sale_price, sale_date, dealer_id):
    """Record a sale with business rule enforcement"""
    car = Car.query.get_or_404(car_id)
    
    try:
        # Business rule: Car must be on display to be sold
        if car.repair_status != 'On Display':
            raise BusinessRuleError("Car must be on display before it can be sold")
        
        # Business rule: Car cannot be sold twice
        if car.date_sold:
            raise BusinessRuleError("This car has already been sold")
        
        # Record sale
        car.sale_price = sale_price
        car.date_sold = sale_date
        car.repair_status = 'Sold'
        
        # Create sale record
        sale = Sale(
            car_id=car_id,
            dealer_id=dealer_id,
            sale_price=sale_price,
            sale_date=sale_date
        )
        db.session.add(sale)
        
        success, error_message = safe_commit()
        if not success:
            raise BusinessRuleError(error_message)
        
        return sale
            
    except BusinessRuleError as e:
        log_error('business_rule', str(e), car_id=car_id)
        raise
    except Exception as e:
        log_error('record_sale_unknown', str(e), car_id=car_id)
        raise BusinessRuleError("An error occurred while recording the sale")
```

In the route handler:

```python
@sales.route('/record_sale/<int:car_id>', methods=['GET', 'POST'])
@login_required
def record_sale(car_id):
    form = SaleForm()
    
    if form.validate_on_submit():
        try:
            sale = record_sale(
                car_id,
                form.sale_price.data,
                form.sale_date.data,
                form.dealer_id.data
            )
            flash('Sale recorded successfully', 'success')
            return redirect(url_for('sales.view_sale', sale_id=sale.sale_id))
        except BusinessRuleError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash('An unexpected error occurred', 'danger')
    
    # Get car for form display
    car = Car.query.get_or_404(car_id)
    return render_template('sales/record_sale.html', form=form, car=car)
```

## HTTP Error Handling

Custom error pages are defined for common HTTP errors:

```python
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    log_error('server_error', str(e))
    return render_template('errors/500.html'), 500
```

## API Error Handling

For API endpoints, errors are returned as JSON responses:

```python
@api.errorhandler(404)
def api_not_found(e):
    return jsonify({
        'error': 'Resource not found',
        'status_code': 404
    }), 404

@api.errorhandler(400)
def api_bad_request(e):
    return jsonify({
        'error': str(e),
        'status_code': 400
    }), 400

@api.errorhandler(500)
def api_server_error(e):
    log_error('api_server_error', str(e))
    return jsonify({
        'error': 'Internal server error',
        'status_code': 500
    }), 500
```

API response format for errors:

```json
{
    "error": "Car must be on display before it can be sold",
    "status_code": 400,
    "resource": "car",
    "resource_id": 42,
    "timestamp": "2023-04-12T15:30:45Z"
}
```

## Global Exception Handler

A global exception handler catches any unhandled exceptions:

```python
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle any uncaught exception"""
    # Log the error and stacktrace
    app.logger.error('Unhandled exception: %s', str(e), exc_info=True)
    
    # Different handling for API vs HTML requests
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'An unexpected error occurred',
            'status_code': 500
        }), 500
    
    # For regular requests return the 500 page
    return render_template('errors/500.html'), 500
```

## Error Logging

All errors are logged for monitoring and debugging:

```python
def log_error(error_type, message, **context):
    """Log error with context"""
    error_data = {
        'type': error_type,
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        'request_path': request.path,
        'request_method': request.method,
        'user_id': current_user.user_id if current_user.is_authenticated else None,
        'ip_address': request.remote_addr
    }
    
    # Add any additional context
    error_data.update(context)
    
    # Log to application logger
    app.logger.error(
        "%s: %s (User: %s, Path: %s)",
        error_type,
        message,
        error_data['user_id'],
        error_data['request_path'],
        extra=error_data
    )
    
    # For severe errors, can also save to database
    if error_type in ['server_error', 'database', 'security']:
        error_log = ErrorLog(
            error_type=error_type,
            message=message,
            user_id=error_data['user_id'],
            request_path=error_data['request_path'],
            request_method=error_data['request_method'],
            context_data=json.dumps(context)
        )
        try:
            # Use a separate session to avoid conflicts with the current transaction
            with app.app_context():
                db2 = SQLAlchemy(app)
                db2.session.add(error_log)
                db2.session.commit()
        except:
            # Log to stderr if database logging fails
            app.logger.critical("Failed to log error to database", exc_info=True)
```

## Error Database Schema

Errors are stored in the database for analysis:

```python
class ErrorLog(db.Model):
    __tablename__ = 'error_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    error_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    request_path = db.Column(db.String(255))
    request_method = db.Column(db.String(10))
    context_data = db.Column(db.Text)  # JSON string of additional context
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='error_logs')
```

## Error Notification System

Critical errors trigger notifications to administrators:

```python
def notify_admin_of_error(error_type, message, context):
    """Send notification of critical error to administrators"""
    if error_type not in ['server_error', 'database', 'security']:
        return  # Only notify for critical errors
    
    # Prepare email content
    subject = f"[CRITICAL] {error_type} error in Car App"
    body = f"""
    A critical error occurred in the Car Repair and Sales Tracking Application:
    
    Error Type: {error_type}
    Message: {message}
    Timestamp: {datetime.utcnow().isoformat()}
    
    Context:
    {json.dumps(context, indent=2)}
    
    Please investigate immediately.
    """
    
    # Send email to all admins
    admin_users = User.query.filter_by(role='admin').all()
    for admin in admin_users:
        send_email(admin.email, subject, body)
    
    # Could also integrate with SMS or other notification systems
```

## User Feedback

Users receive appropriate feedback for different error types:

1. **Validation Errors** - Specific, helpful messages
2. **Business Rule Violations** - Clear explanation of the rule
3. **System Errors** - Generic message with error reference

Example of flash messages:

```python
# Validation error - specific
flash('Vehicle name must be 3-100 characters', 'warning')

# Business rule - clear explanation
flash('Car must be on display before it can be sold', 'warning')

# System error - generic with reference
error_id = log_error('database', str(e))
flash(f'An error occurred (Ref: {error_id}). The technical team has been notified.', 'danger')
```

## Error Templates

Custom error templates provide a consistent look and helpful information:

```html
<!-- errors/500.html -->
{% extends "base.html" %}

{% block title %}Server Error{% endblock %}

{% block content %}
<div class="error-container">
  <div class="error-code">500</div>
  <h1>Server Error</h1>
  
  <p>Something went wrong on our end. The error has been logged and we'll look into it.</p>
  
  {% if error_reference %}
  <p>Error Reference: {{ error_reference }}</p>
  {% endif %}
  
  <div class="error-actions">
    <a href="{{ url_for('main.dashboard') }}" class="btn btn-primary">
      <i class="fas fa-home"></i> Return to Dashboard
    </a>
    <a href="javascript:history.back()" class="btn btn-secondary">
      <i class="fas fa-arrow-left"></i> Go Back
    </a>
  </div>
</div>
{% endblock %}
```

## Error Recovery

The application implements strategies for recovering from errors:

1. **Transaction Rollback** - All database transactions are rolled back on error
2. **State Restoration** - Form data is preserved after an error
3. **Retry Mechanisms** - Critical operations can be retried with exponential backoff

Example of a retry mechanism:

```python
def retry_operation(operation, max_attempts=3, backoff_factor=2):
    """Retry an operation with exponential backoff"""
    attempt = 0
    last_exception = None
    
    while attempt < max_attempts:
        try:
            return operation()
        except (SQLAlchemyError, ConnectionError) as e:
            attempt += 1
            last_exception = e
            
            if attempt >= max_attempts:
                break
                
            # Calculate sleep time with exponential backoff
            sleep_time = backoff_factor ** attempt
            time.sleep(sleep_time)
    
    # If we get here, all attempts failed
    log_error('retry_failed', str(last_exception), attempts=max_attempts)
    raise last_exception
```

## Monitoring and Alerts

The application includes monitoring for error patterns:

1. **Error Rate Monitoring** - Alerts on sudden increases in error rates
2. **Error Clustering** - Identifies related errors
3. **Trend Analysis** - Tracks error rates over time

## Error Documentation

Each error type is documented for user reference:

```python
ERROR_DOCS = {
    'validation': {
        'title': 'Validation Error',
        'description': 'The submitted data did not meet the requirements',
        'user_action': 'Please check the form fields and try again'
    },
    'business_rule': {
        'title': 'Business Rule Violation',
        'description': 'The operation would violate a business rule',
        'user_action': 'Please review the specific rule mentioned in the error message'
    },
    'database': {
        'title': 'Database Error',
        'description': 'A problem occurred while accessing the database',
        'user_action': 'Please try again later or contact support if the problem persists'
    },
    # Additional error types...
}
```

This documentation is used in error messages and help pages. 