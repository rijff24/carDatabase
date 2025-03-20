from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required

providers_bp = Blueprint('providers', __name__)

@providers_bp.route('/')
@login_required
def index():
    return render_template('providers/index.html') 