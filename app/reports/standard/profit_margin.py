from app.reports.base import Report
from app.models import Car, Sale, Dealer, Stand
from sqlalchemy import func, and_, extract, join, case
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import decimal

class ProfitMarginReport(Report):
    """
    Report showing profit margins across sales, including:
    - Overall profit margin
    - Margins by make/model
    - Margin trends over time
    - Top performing models
    - ROI (Return on Investment) analysis
    """
    template_path = "reports/profit-margin.html"
    parameter_rules = {
        "timeframe": {
            "type": "string",
            "required": False,
            "default": "last_30_days",
            "choices": ["last_30_days", "last_90_days", "year_to_date", "last_year", "all_time", "custom"]
        },
        "start_date": {
            "type": "date",
            "required": False,
            "default": None
        },
        "end_date": {
            "type": "date",
            "required": False,
            "default": None
        },
        "stand_id": {
            "type": "integer",
            "required": False,
            "default": None
        },
        "dealer_id": {
            "type": "integer",
            "required": False,
            "default": None
        }
    }

    def __init__(self, timeframe=None, start_date=None, end_date=None, stand_id=None, dealer_id=None):
        super().__init__()
        self.timeframe = timeframe or self.parameter_rules["timeframe"]["default"]
        self.start_date = start_date
        self.end_date = end_date
        self.stand_id = stand_id
        self.dealer_id = dealer_id
        
    def generate(self):
        # Apply date filter based on timeframe
        date_filter = self._get_date_filter()
        
        # Get all sales in the specified timeframe with applied filters
        sales_query = Sale.query.join(Car)
        
        if date_filter is not None:
            sales_query = sales_query.filter(date_filter)
            
        if self.stand_id:
            sales_query = sales_query.filter(Car.stand_id == self.stand_id)
            
        if self.dealer_id:
            sales_query = sales_query.filter(Sale.dealer_id == self.dealer_id)
            
        sales = sales_query.all()
        
        # Calculate summary metrics
        total_cars_sold = len(sales)
        total_revenue = sum(self._decimal(sale.sale_price) for sale in sales)
        total_cost = sum(self._decimal(sale.car.total_investment) for sale in sales)
        total_profit = total_revenue - total_cost
        
        average_revenue = total_revenue / total_cars_sold if total_cars_sold > 0 else decimal.Decimal('0.00')
        average_cost = total_cost / total_cars_sold if total_cars_sold > 0 else decimal.Decimal('0.00')
        average_profit = total_profit / total_cars_sold if total_cars_sold > 0 else decimal.Decimal('0.00')
        average_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else decimal.Decimal('0.00')
        average_roi = (total_profit / total_cost * 100) if total_cost > 0 else decimal.Decimal('0.00')
        
        # Get profit by make/model with individual cars
        profit_by_make_model = self._get_profit_by_make_model(sales)
        
        # Get profit by make (for backward compatibility)
        profit_by_make = self._get_profit_by_make(sales)
        
        # Get margin distribution
        margin_distribution = self._get_margin_distribution(sales)
        
        # Get margin trend over time
        margin_trend = self._get_margin_trend(self.timeframe, self.start_date, self.end_date, 
                                             self.stand_id, self.dealer_id)
        
        # Get top performing models
        top_models = self._get_top_models(sales)
        
        # Get high performing sales
        high_performing_sales = self._get_high_performing_sales(sales)
        
        # Get available dealers and stands for filtering
        dealers = Dealer.query.all()
        stands = Stand.query.all()
        
        return {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "timeframe": self.timeframe,
            "start_date": self.start_date.strftime("%Y-%m-%d") if self.start_date else None,
            "end_date": self.end_date.strftime("%Y-%m-%d") if self.end_date else None,
            "stand_id": self.stand_id,
            "dealer_id": self.dealer_id,
            "total_cars_sold": total_cars_sold,
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "average_revenue": average_revenue,
            "average_cost": average_cost,
            "average_profit": average_profit,
            "average_margin": average_margin,
            "average_roi": average_roi,
            "profit_by_make": profit_by_make,
            "profit_by_make_model": profit_by_make_model,
            "margin_distribution": margin_distribution,
            "margin_trend": margin_trend,
            "top_models": top_models,
            "high_performing_sales": high_performing_sales,
            "available_dealers": dealers,
            "available_stands": stands
        }
    
    def _decimal(self, value):
        """Convert a value to Decimal safely"""
        if isinstance(value, decimal.Decimal):
            return value
        return decimal.Decimal(str(value)) if value is not None else decimal.Decimal('0.00')
    
    def _get_date_filter(self):
        """Create date filter based on the selected timeframe"""
        today = date.today()
        
        # If custom date range is provided, use it
        if self.timeframe == "custom" and self.start_date and self.end_date:
            return and_(Sale.sale_date >= self.start_date, Sale.sale_date <= self.end_date)
        
        # Otherwise use preset timeframes
        if self.timeframe == "last_30_days":
            start_date = today - timedelta(days=30)
            return Sale.sale_date >= start_date
            
        elif self.timeframe == "last_90_days":
            start_date = today - timedelta(days=90)
            return Sale.sale_date >= start_date
            
        elif self.timeframe == "year_to_date":
            start_date = date(today.year, 1, 1)
            return Sale.sale_date >= start_date
            
        elif self.timeframe == "last_year":
            start_date = date(today.year - 1, 1, 1)
            end_date = date(today.year - 1, 12, 31)
            return and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
            
        elif self.timeframe == "all_time":
            return None
            
        return None
    
    def _get_profit_by_make(self, sales):
        """Calculate profit metrics grouped by make"""
        makes = {}
        
        for sale in sales:
            car = sale.car
            make = car.vehicle_make
            
            if make not in makes:
                makes[make] = {
                    "make": make,
                    "count": 0,
                    "total_revenue": decimal.Decimal('0.00'),
                    "total_cost": decimal.Decimal('0.00'),
                    "total_profit": decimal.Decimal('0.00')
                }
                
            makes[make]["count"] += 1
            makes[make]["total_revenue"] += self._decimal(sale.sale_price)
            makes[make]["total_cost"] += self._decimal(car.total_investment)
            
        # Calculate averages and margins
        for make in makes.values():
            make["total_profit"] = make["total_revenue"] - make["total_cost"]
            make["avg_revenue"] = make["total_revenue"] / make["count"]
            make["avg_cost"] = make["total_cost"] / make["count"]
            make["avg_profit"] = make["total_profit"] / make["count"]
            make["margin"] = (make["total_profit"] / make["total_revenue"] * 100) if make["total_revenue"] > 0 else 0
            make["roi"] = (make["total_profit"] / make["total_cost"] * 100) if make["total_cost"] > 0 else 0
            
        # Sort by profit margin descending
        return sorted(
            makes.values(),
            key=lambda x: x["margin"],
            reverse=True
        )
    
    def _get_profit_by_make_model(self, sales):
        """Calculate profit metrics grouped by make/model with individual car details"""
        make_models = {}
        
        for sale in sales:
            car = sale.car
            make = car.vehicle_make
            model = car.vehicle_model
            make_model_key = f"{make}_{model}"
            
            # Purchase, repair, and refuel costs for ROI calculation
            purchase_cost = self._decimal(car.purchase_price)
            repair_cost = self._decimal(car.total_repair_cost)
            refuel_cost = self._decimal(car.refuel_cost)
            total_investment = purchase_cost + repair_cost + refuel_cost
            
            sale_price = self._decimal(sale.sale_price)
            profit = sale_price - total_investment
            margin = (profit / sale_price * 100) if sale_price > 0 else 0
            roi = (profit / total_investment * 100) if total_investment > 0 else 0
            
            # Create car detail record
            car_detail = {
                "car_id": car.car_id,
                "car_name": car.full_name,
                "year": car.year,
                "vin": car.licence_number,
                "colour": car.colour,
                "purchase_price": purchase_cost,
                "repair_cost": repair_cost, 
                "refuel_cost": refuel_cost,
                "investment": total_investment,
                "sale_price": sale_price,
                "profit": profit,
                "margin": margin,
                "roi": roi,
                "sale_date": sale.sale_date,
                "dealer_name": sale.dealer.dealer_name if sale.dealer else "Unknown"
            }
            
            # Add to make/model group
            if make_model_key not in make_models:
                make_models[make_model_key] = {
                    "make": make,
                    "model": model,
                    "count": 0,
                    "total_revenue": decimal.Decimal('0.00'),
                    "total_cost": decimal.Decimal('0.00'),
                    "total_profit": decimal.Decimal('0.00'),
                    "cars": []
                }
                
            # Update group totals
            make_models[make_model_key]["count"] += 1
            make_models[make_model_key]["total_revenue"] += sale_price
            make_models[make_model_key]["total_cost"] += total_investment
            make_models[make_model_key]["total_profit"] += profit
            
            # Add car to group
            make_models[make_model_key]["cars"].append(car_detail)
            
        # Calculate averages and percentages
        for make_model in make_models.values():
            make_model["avg_revenue"] = make_model["total_revenue"] / make_model["count"]
            make_model["avg_cost"] = make_model["total_cost"] / make_model["count"]
            make_model["avg_profit"] = make_model["total_profit"] / make_model["count"]
            make_model["margin"] = (make_model["total_profit"] / make_model["total_revenue"] * 100) if make_model["total_revenue"] > 0 else 0
            make_model["roi"] = (make_model["total_profit"] / make_model["total_cost"] * 100) if make_model["total_cost"] > 0 else 0
            
            # Sort cars by profit descending
            make_model["cars"] = sorted(make_model["cars"], key=lambda x: x["profit"], reverse=True)
            
        # Sort make/models by total profit descending
        return sorted(
            make_models.values(),
            key=lambda x: x["total_profit"],
            reverse=True
        )
    
    def _get_margin_distribution(self, sales):
        """Group sales by profit margin ranges"""
        ranges = [
            {"range": "Less than 10%", "min": 0, "max": 10, "count": 0},
            {"range": "10-20%", "min": 10, "max": 20, "count": 0},
            {"range": "20-30%", "min": 20, "max": 30, "count": 0},
            {"range": "More than 30%", "min": 30, "max": float('inf'), "count": 0}
        ]
        
        for sale in sales:
            # Calculate margin for this sale
            revenue = self._decimal(sale.sale_price)
            cost = self._decimal(sale.car.total_investment)
            profit = revenue - cost
            
            if revenue > 0:
                margin = (profit / revenue * 100)
                
                # Add to appropriate range
                for range_data in ranges:
                    if range_data["min"] <= margin < range_data["max"]:
                        range_data["count"] += 1
                        break
            
        return ranges
    
    def _get_margin_trend(self, timeframe, start_date=None, end_date=None, stand_id=None, dealer_id=None):
        """Get profit margin trend over time based on timeframe and filters"""
        today = date.today()
        result = []
        
        # Build base query with filters
        base_query = Sale.query.join(Car)
        
        if stand_id:
            base_query = base_query.filter(Car.stand_id == stand_id)
            
        if dealer_id:
            base_query = base_query.filter(Sale.dealer_id == dealer_id)
        
        # Custom date range
        if timeframe == "custom" and start_date and end_date:
            # Monthly data for the specified range
            current_date = start_date.replace(day=1)
            end_month = end_date.replace(day=1)
            
            while current_date <= end_month:
                month_end = (current_date + relativedelta(months=1) - timedelta(days=1))
                if month_end > end_date:
                    month_end = end_date
                
                month_sales = base_query.filter(
                    and_(Sale.sale_date >= current_date, Sale.sale_date <= month_end)
                ).all()
                
                if month_sales:
                    month_revenue = sum(self._decimal(sale.sale_price) for sale in month_sales)
                    month_cost = sum(self._decimal(sale.car.total_investment) for sale in month_sales)
                    month_profit = month_revenue - month_cost
                    month_margin = (month_profit / month_revenue * 100) if month_revenue > 0 else 0
                    month_roi = (month_profit / month_cost * 100) if month_cost > 0 else 0
                else:
                    month_margin = 0
                    month_roi = 0
                    
                result.append({
                    "label": current_date.strftime("%b %Y"),
                    "margin": month_margin,
                    "roi": month_roi
                })
                
                # Move to the next month
                current_date = (current_date + relativedelta(months=1))
            
        elif timeframe == "last_30_days":
            # Daily data for the last 30 days
            for days_ago in range(29, -1, -1):
                day_date = today - timedelta(days=days_ago)
                day_sales = base_query.filter(func.date(Sale.sale_date) == day_date).all()
                
                if day_sales:
                    day_revenue = sum(self._decimal(sale.sale_price) for sale in day_sales)
                    day_cost = sum(self._decimal(sale.car.total_investment) for sale in day_sales)
                    day_profit = day_revenue - day_cost
                    day_margin = (day_profit / day_revenue * 100) if day_revenue > 0 else 0
                    day_roi = (day_profit / day_cost * 100) if day_cost > 0 else 0
                else:
                    day_margin = 0
                    day_roi = 0
                    
                result.append({
                    "label": day_date.strftime("%b %d"),
                    "margin": day_margin,
                    "roi": day_roi
                })
                
        elif timeframe == "last_90_days":
            # Weekly data for the last 90 days
            for week in range(12, -1, -1):
                week_end = today - timedelta(days=week*7)
                week_start = week_end - timedelta(days=6)
                
                week_sales = base_query.filter(
                    and_(Sale.sale_date >= week_start, Sale.sale_date <= week_end)
                ).all()
                
                if week_sales:
                    week_revenue = sum(self._decimal(sale.sale_price) for sale in week_sales)
                    week_cost = sum(self._decimal(sale.car.total_investment) for sale in week_sales)
                    week_profit = week_revenue - week_cost
                    week_margin = (week_profit / week_revenue * 100) if week_revenue > 0 else 0
                    week_roi = (week_profit / week_cost * 100) if week_cost > 0 else 0
                else:
                    week_margin = 0
                    week_roi = 0
                    
                result.append({
                    "label": f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}",
                    "margin": week_margin,
                    "roi": week_roi
                })
                
        elif timeframe in ["year_to_date", "last_year"]:
            # Monthly data for the year
            year = today.year
            if timeframe == "last_year":
                year = today.year - 1
                
            for month in range(1, 13):
                month_start = date(year, month, 1)
                # Handle December as a special case
                if month == 12:
                    month_end = date(year, month, 31)
                else:
                    month_end = date(year, month + 1, 1) - timedelta(days=1)
                    
                # Skip future months in year_to_date mode
                if timeframe == "year_to_date" and month_start > today:
                    continue
                    
                month_sales = base_query.filter(
                    and_(Sale.sale_date >= month_start, Sale.sale_date <= month_end)
                ).all()
                
                if month_sales:
                    month_revenue = sum(self._decimal(sale.sale_price) for sale in month_sales)
                    month_cost = sum(self._decimal(sale.car.total_investment) for sale in month_sales)
                    month_profit = month_revenue - month_cost
                    month_margin = (month_profit / month_revenue * 100) if month_revenue > 0 else 0
                    month_roi = (month_profit / month_cost * 100) if month_cost > 0 else 0
                else:
                    month_margin = 0
                    month_roi = 0
                    
                result.append({
                    "label": month_start.strftime("%b %Y"),
                    "margin": month_margin,
                    "roi": month_roi
                })
                
        elif timeframe == "all_time":
            # Yearly data for all time
            sales_years = db.session.query(
                extract('year', Sale.sale_date).label('year')
            ).distinct().order_by('year').all()
            
            for year_row in sales_years:
                year = int(year_row[0])
                year_start = date(year, 1, 1)
                year_end = date(year, 12, 31)
                
                year_sales = base_query.filter(
                    and_(Sale.sale_date >= year_start, Sale.sale_date <= year_end)
                ).all()
                
                if year_sales:
                    year_revenue = sum(self._decimal(sale.sale_price) for sale in year_sales)
                    year_cost = sum(self._decimal(sale.car.total_investment) for sale in year_sales)
                    year_profit = year_revenue - year_cost
                    year_margin = (year_profit / year_revenue * 100) if year_revenue > 0 else 0
                    year_roi = (year_profit / year_cost * 100) if year_cost > 0 else 0
                else:
                    year_margin = 0
                    year_roi = 0
                    
                result.append({
                    "label": str(year),
                    "margin": year_margin,
                    "roi": year_roi
                })
                
        return result
    
    def _get_top_models(self, sales):
        """Find top performing car models by profit margin"""
        models = {}
        
        for sale in sales:
            car = sale.car
            make = car.vehicle_make
            model = car.vehicle_model
            model_key = f"{make} {model}"
            
            if model_key not in models:
                models[model_key] = {
                    "model": model,
                    "make": make,
                    "count": 0,
                    "total_revenue": decimal.Decimal('0.00'),
                    "total_cost": decimal.Decimal('0.00'),
                    "total_profit": decimal.Decimal('0.00')
                }
                
            models[model_key]["count"] += 1
            models[model_key]["total_revenue"] += self._decimal(sale.sale_price)
            models[model_key]["total_cost"] += self._decimal(car.total_investment)
            
        # Calculate derived metrics
        for model in models.values():
            model["total_profit"] = model["total_revenue"] - model["total_cost"]
            model["avg_profit"] = model["total_profit"] / model["count"]
            model["margin"] = (model["total_profit"] / model["total_revenue"] * 100) if model["total_revenue"] > 0 else 0
            model["roi"] = (model["total_profit"] / model["total_cost"] * 100) if model["total_cost"] > 0 else 0
            
        # Only include models with at least 2 sales
        models_with_min_sales = [model for model in models.values() if model["count"] >= 2]
        
        # Sort by margin and return top 5
        return sorted(
            models_with_min_sales,
            key=lambda x: x["margin"],
            reverse=True
        )[:5]
    
    def _get_high_performing_sales(self, sales):
        """Get individual sales with highest profit margin"""
        sales_data = []
        
        for sale in sales:
            car = sale.car
            revenue = self._decimal(sale.sale_price)
            cost = self._decimal(car.total_investment)
            profit = revenue - cost
            margin = (profit / revenue * 100) if revenue > 0 else 0
            roi = (profit / cost * 100) if cost > 0 else 0
            
            sales_data.append({
                "car_id": car.car_id,
                "car_name": f"{car.year} {car.vehicle_make} {car.vehicle_model}",
                "sale_date": sale.sale_date,
                "dealer_name": sale.dealer.dealer_name if sale.dealer else "Unknown",
                "revenue": revenue,
                "cost": cost,
                "profit": profit,
                "margin": margin,
                "roi": roi
            })
            
        # Sort by margin and return top 5
        return sorted(
            sales_data,
            key=lambda x: x["margin"],
            reverse=True
        )[:5] 