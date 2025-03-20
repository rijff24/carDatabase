from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    return render_template('reports/index.html') 