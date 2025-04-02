# Authentication & Security

This document details the authentication and security mechanisms implemented in the Car Repair and Sales Tracking Application.

## Authentication System

The application uses Flask-Login to manage user authentication with the following features:

### User Model

The authentication system is based on the `User` model:

```python
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Role checking methods
    def is_admin(self):
        return self.role == 'admin'
    
    def is_manager(self):
        return self.role == 'manager' or self.role == 'admin'
    
    # Password handling
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

### Authentication Flow

1. **Login Process**:
   ```python
   @auth.route('/login', methods=['GET', 'POST'])
   def login():
       if current_user.is_authenticated:
           return redirect(url_for('main.dashboard'))
       
       form = LoginForm()
       if form.validate_on_submit():
           user = User.query.filter_by(username=form.username.data).first()
           
           if user is None or not user.check_password(form.password.data):
               flash('Invalid username or password', 'danger')
               return redirect(url_for('auth.login'))
           
           if not user.is_active:
               flash('This account has been deactivated', 'warning')
               return redirect(url_for('auth.login'))
           
           login_user(user, remember=form.remember_me.data)
           user.last_login = datetime.utcnow()
           db.session.commit()
           
           next_page = request.args.get('next')
           if not next_page or url_parse(next_page).netloc != '':
               next_page = url_for('main.dashboard')
               
           return redirect(next_page)
       
       return render_template('auth/login.html', title='Sign In', form=form)
   ```

2. **Logout Process**:
   ```python
   @auth.route('/logout')
   def logout():
       logout_user()
       return redirect(url_for('auth.login'))
   ```

3. **Password Reset**:
   ```python
   @auth.route('/reset_password_request', methods=['GET', 'POST'])
   def reset_password_request():
       # Password reset implementation
       # Sends email with reset link containing secure token
       pass
   ```

### User Registration

User registration is controlled by administrators:

```python
@auth.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    # Only admins can create users
    if not current_user.is_admin():
        abort(403)
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.username} has been created', 'success')
        return redirect(url_for('auth.user_list'))
    
    return render_template('auth/register.html', title='Register User', form=form)
```

## Role-Based Access Control

The application implements a role-based access control system:

### User Roles

1. **Admin**:
   - Full access to all features and data
   - Can manage users and system settings
   - Can configure business rules

2. **Manager**:
   - Can view all reports and data
   - Can manage inventory, repairs, and sales
   - Cannot manage users or system settings

3. **Sales**:
   - Can view and record sales
   - Can view inventory
   - Limited report access

4. **Inventory**:
   - Can manage vehicle inventory
   - Can view and create repair records
   - Limited report access

5. **Finance**:
   - Can view financial data and reports
   - Read-only access to inventory and sales
   - Cannot create or modify records

### Role Enforcement

Role-based access is enforced using decorators:

```python
def requires_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
                
            if role == 'admin' and not current_user.is_admin():
                abort(403)
                
            if role == 'manager' and not current_user.is_manager():
                abort(403)
                
            # Additional role checks based on the requested resource
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

Example usage:

```python
@inventory.route('/add_car', methods=['GET', 'POST'])
@login_required
@requires_role('manager')
def add_car():
    # Only managers and admins can add new cars
    # Function implementation
    pass
```

## Security Measures

### Password Security

1. **Hashing**:
   - Passwords are hashed using Werkzeug's security functions
   - Uses PBKDF2 algorithm with SHA-256 hash

2. **Requirements**:
   - Minimum 8 characters
   - Must contain uppercase, lowercase, and numbers
   - Complexity validation

   ```python
   def validate_password(password):
       if len(password) < 8:
           return False, "Password must be at least 8 characters long"
       
       if not any(c.isupper() for c in password):
           return False, "Password must contain at least one uppercase letter"
       
       if not any(c.islower() for c in password):
           return False, "Password must contain at least one lowercase letter"
       
       if not any(c.isdigit() for c in password):
           return False, "Password must contain at least one number"
       
       return True, ""
   ```

### CSRF Protection

Cross-Site Request Forgery protection is implemented using Flask-WTF:

```python
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
csrf = CSRFProtect(app)
```

All forms include CSRF tokens:

```html
<form method="POST" action="{{ url_for('auth.login') }}">
    {{ form.hidden_tag() }}
    <!-- Form fields -->
</form>
```

### Session Security

1. **Session Configuration**:
   ```python
   app.config['SESSION_COOKIE_SECURE'] = True  # In production
   app.config['SESSION_COOKIE_HTTPONLY'] = True
   app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)
   ```

2. **Session Management**:
   - Session expiration after 12 hours
   - Secure cookies in production
   - HTTP-only cookies to prevent JavaScript access

### XSS Prevention

1. **Template Escaping**:
   - Jinja2 automatically escapes variables to prevent XSS
   
2. **Content Security Policy**:
   ```python
   @app.after_request
   def add_security_headers(response):
       response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://code.jquery.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data:;"
       return response
   ```

### SQL Injection Prevention

1. **ORM Usage**:
   - SQLAlchemy ORM used for database queries
   - Parameterized queries prevent SQL injection

2. **Input Validation**:
   - All form inputs are validated
   - Data type checking enforced

### Audit Logging

The application maintains comprehensive audit logs:

```python
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    action = db.Column(db.String(50), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='audit_logs')
```

Usage:

```python
def log_action(action, resource_type, resource_id, details=None):
    """Log user action to audit trail"""
    if current_user.is_authenticated:
        log = AuditLog(
            user_id=current_user.user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
```

## API Security

For any external API endpoints:

1. **Token Authentication**:
   ```python
   def token_required(f):
       @wraps(f)
       def decorated(*args, **kwargs):
           token = request.headers.get('Authorization')
           
           if not token:
               return jsonify({'message': 'Token is missing!'}), 401
           
           if not token.startswith('Bearer '):
               return jsonify({'message': 'Invalid token format!'}), 401
           
           token = token.split(' ')[1]
           
           try:
               data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
               current_user = User.query.filter_by(user_id=data['user_id']).first()
           except:
               return jsonify({'message': 'Token is invalid!'}), 401
           
           return f(current_user, *args, **kwargs)
       return decorated
   ```

2. **Rate Limiting**:
   ```python
   limiter = Limiter(
       app,
       key_func=get_remote_address,
       default_limits=["100 per day", "20 per hour"]
   )
   
   @api.route('/vehicles')
   @limiter.limit("5 per minute")
   @token_required
   def get_vehicles(current_user):
       # API implementation
       pass
   ```

## Environment-Specific Security

### Development Environment
- Debug mode enabled
- Less strict security headers
- Local database

### Testing Environment
- Debug mode disabled
- Full security measures
- Test database

### Production Environment
- Debug mode disabled
- Full security measures
- Secured database access
- HTTPS enforced
- Environment-specific settings in `.env` file

```python
# config.py
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
```

## Backup and Disaster Recovery

1. **Database Backups**:
   - Automated daily backups
   - Weekly full backups
   - 30-day retention

2. **Backup Encryption**:
   - Backups are encrypted using AES-256
   - Keys stored separately from backup data

3. **Restoration Procedure**:
   - Documented step-by-step process
   - Regular restoration drills
   - Validation of backup integrity 