from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required

dealers_bp = Blueprint('dealers', __name__)

@dealers_bp.route('/')
@login_required
def index():
    return render_template('dealers/index.html') 