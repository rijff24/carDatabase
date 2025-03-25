from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from urllib.parse import urlparse
from datetime import datetime
from app.utils.forms import LoginForm
from app.utils.validators import validate_form, validate_params, validate_username, validate_password
from app.utils.errors import ValidationError, AuthenticationError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@validate_form(LoginForm)
@validate_params(
    next=(str, False, None)
)
def login():
    """Login route"""
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = request.validated_form
    if request.method == 'POST':
        # Additional validation for username and password format
        if not validate_username(form.username.data):
            raise ValidationError(
                "Invalid username format. Username must be 3-32 characters long and contain only letters, numbers, and underscores.",
                field="username"
            )
        
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            raise AuthenticationError("Invalid username or password")
        
        # Log the user in and update last login timestamp
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.now()
        db.session.commit()
        
        # Redirect to the next page or dashboard
        next_page = request.validated_params.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        
        flash('Logged in successfully', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index')) 