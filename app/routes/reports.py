from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required
from app import db
from app.reports import get_report
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    """Reports index page."""
    now = datetime.now()
    return render_template('reports/index.html', current_date=now.strftime('%Y-%m-%d'))

@reports_bp.route('/sales-performance')
@login_required
def sales_performance():
    """Sales Performance Report."""
    report_class = get_report('sales_performance')
    report = report_class()
    return report.get()

@reports_bp.route('/repair-analysis')
@login_required
def repair_analysis():
    """Repair Cost Analysis Report."""
    report_class = get_report('repair_analysis')
    report = report_class()
    return report.get()

@reports_bp.route('/inventory-aging')
@login_required
def inventory_aging():
    """Inventory Aging Report."""
    report_class = get_report('inventory_aging')
    report = report_class()
    return report.get()

@reports_bp.route('/profit-margin')
@login_required
def profit_margin():
    """Profit Margin Analysis Report."""
    report_class = get_report('profit_margin')
    report = report_class()
    return report.get()