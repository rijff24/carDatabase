from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from werkzeug.urls import url_parse
from datetime import datetime
from app.utils.forms import LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        # Log the user in and update last login timestamp
        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.now()
        db.session.commit()
        
        # Redirect to the next page or dashboard
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
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