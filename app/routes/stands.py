from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required

stands_bp = Blueprint('stands', __name__)

@stands_bp.route('/')
@login_required
def index():
    return render_template('stands/index.html') 