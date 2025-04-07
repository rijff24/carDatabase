from app.reports.base import Report
from app.models import Sale, Dealer, Car, Stand
from sqlalchemy import func, extract, and_, event
from datetime import datetime, timedelta, date
import decimal
import calendar

class SalesPerformanceReport(Report):
    """
    Report showing sales performance metrics, including:
    - Total sales by period (month, quarter, year)
    - Sales by dealer
    - Sales by stand
    - Average sale prices and margins
    - Average time in stock
    - Sales trends over time
    """
    template_path = "reports/sales-performance.html"
    parameter_rules = {
        "period": {
            "type": "string",
            "required": False,
            "default": "monthly",
            "choices": ["monthly", "quarterly", "yearly"]
        },
        "year": {
            "type": "integer",
            "required": False,
            "default": datetime.now().year
        },
        "start_date": {
            "type": "date",
            "required": False
        },
        "end_date": {
            "type": "date",
            "required": False
        },
        "vehicle_make": {
            "type": "string",
            "required": False
        },
        "vehicle_model": {
            "type": "string",
            "required": False
        },
        "stand_ids": {
            "type": "list",
            "required": False
        }
    }

    def __init__(self, period=None, year=None, start_date=None, end_date=None, 
                 vehicle_make=None, vehicle_model=None, stand_ids=None):
        super().__init__()
        self.period = period or self.parameter_rules["period"]["default"]
        self.year = year or datetime.now().year
        self.start_date = start_date
        self.end_date = end_date
        self.vehicle_make = vehicle_make
        self.vehicle_model = vehicle_model
        self.stand_ids = stand_ids or []
        
    def _ensure_data_consistency(self):
        """Ensure data consistency between Car and Sale models before generating the report"""
        # Find cars with inconsistencies
        inconsistencies = 0
        from app import db
        
        # First check for duplicate sales for the same car
        try:
            from sqlalchemy import text
            with db.engine.connect() as conn:
                duplicates = conn.execute(
                    text("SELECT car_id, COUNT(*) as count FROM sales GROUP BY car_id HAVING count > 1")
                ).fetchall()
                
                for car_id, count in duplicates:
                    print(f"Found car ID {car_id} with {count} sale records. Cleaning up duplicates...")
                    # Keep only the most recent sale record
                    sales = Sale.query.filter_by(car_id=car_id).order_by(Sale.sale_date.desc()).all()
                    
                    # Delete all but the most recent sale
                    for i, sale in enumerate(sales):
                        if i > 0:  # Skip the first (most recent) one
                            db.session.delete(sale)
                            inconsistencies += 1
        except Exception as e:
            print(f"Error checking for duplicate sales: {e}")
        
        # Now check for Car/Sale inconsistencies one by one
        for car in Car.query.all():
            # Get all sales for this car (should be at most one after our cleanup)
            sales = Sale.query.filter_by(car_id=car.car_id).all()
            has_sale = len(sales) > 0
            
            if has_sale and car.date_sold is None:
                # Car has a sale record but date_sold is None
                car.date_sold = sales[0].sale_date  # Use the first sale (should be only one)
                inconsistencies += 1
                
            elif has_sale and car.date_sold != sales[0].sale_date:
                # Car's date_sold doesn't match sale date
                car.date_sold = sales[0].sale_date
                inconsistencies += 1
                
            elif car.date_sold is not None and not has_sale:
                # Car is marked as sold but has no sale record
                car.date_sold = None
                inconsistencies += 1
                
        # If any inconsistencies were found, commit the changes
        if inconsistencies > 0:
            db.session.commit()
            print(f"Fixed {inconsistencies} car/sale inconsistencies before generating the report.")
            
        return inconsistencies
        
    def generate(self):
        # First ensure data consistency
        self._ensure_data_consistency()
        
        # Generate period labels based on selected period
        periods, period_labels = self._get_period_definitions()
        
        # Get all sales with filtering
        sales_query = Sale.query.join(Car)
        
        # Apply date filtering
        if self.start_date and self.end_date:
            sales_query = sales_query.filter(Sale.sale_date.between(self.start_date, self.end_date))
        else:
            sales_query = sales_query.filter(extract('year', Sale.sale_date) == self.year)
        
        # Apply vehicle make/model filtering
        if self.vehicle_make:
            sales_query = sales_query.filter(Car.vehicle_make == self.vehicle_make)
        if self.vehicle_model:
            sales_query = sales_query.filter(Car.vehicle_model == self.vehicle_model)
            
        # Apply stand filtering
        if self.stand_ids:
            sales_query = sales_query.filter(Car.stand_id.in_(self.stand_ids))
            
        # Get the filtered sales
        sales = sales_query.all()
        
        # Calculate total metrics
        total_sales_count = len(sales)
        total_revenue = sum(self._decimal(sale.sale_price) for sale in sales)
        total_cost = sum(self._decimal(sale.car.total_investment) for sale in sales)
        total_profit = total_revenue - total_cost
        
        # Calculate profit margin
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else decimal.Decimal('0.00')
        average_margin = profit_margin  # They are the same for the overall summary
        
        # Calculate average time in stock
        avg_time_in_stock = self._calculate_avg_time_in_stock(sales)
        
        # Calculate sales by period
        sales_by_period = self._get_sales_by_period(periods)
        
        # Calculate sales by dealer
        sales_by_dealer = self._get_sales_by_dealer()
        
        # Calculate sales by stand
        sales_by_stand = self._get_sales_by_stand()
        
        # Get top performing dealers
        top_dealers = sales_by_dealer[:3] if len(sales_by_dealer) >= 3 else sales_by_dealer
        
        # Get top performing stands
        top_stands = sales_by_stand[:3] if len(sales_by_stand) >= 3 else sales_by_stand
        
        # Get sales count trend
        sales_count_trend = [period["count"] for period in sales_by_period]
        
        # Get revenue and profit trend
        revenue_profit_trend = {
            "revenue": [float(period["revenue"]) for period in sales_by_period],
            "profit": [float(period["profit"]) for period in sales_by_period]
        }
        
        # Add chart-specific data
        sales_counts = [period["count"] for period in sales_by_period]
        revenues = [float(period["revenue"]) for period in sales_by_period]
        profits = [float(period["profit"]) for period in sales_by_period]
        
        # Get year-over-year comparison
        previous_year_comparison = self._get_previous_year_comparison()
        
        # Get top 5 most sold car models
        top_models = self._get_top_models()
        
        # Get vehicle makes for filter options
        vehicle_makes = Car.query.with_entities(Car.vehicle_make).distinct().all()
        vehicle_makes = [make[0] for make in vehicle_makes]
        
        # Get vehicle models for filter options (if make is selected)
        vehicle_models = []
        if self.vehicle_make:
            model_query = Car.query.with_entities(Car.vehicle_model).filter(Car.vehicle_make == self.vehicle_make).distinct()
            vehicle_models = [model[0] for model in model_query.all()]
            
        # Get all stands for filter options
        stands = Stand.query.all()
        
        return {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "period": self.period,
            "period_name": self.period,
            "period_label": "Period",
            "year": self.year,
            "current_year": datetime.now().year,
            "month": 0,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "vehicle_make": self.vehicle_make,
            "vehicle_model": self.vehicle_model,
            "stand_ids": self.stand_ids,
            "total_sales_count": total_sales_count,
            "total_sales": total_sales_count,  # For template compatibility
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "average_margin": average_margin,
            "profit_margin": profit_margin,
            "avg_time_in_stock": avg_time_in_stock,
            "period_labels": period_labels,
            "sales_by_period": sales_by_period,
            "sales_by_dealer": sales_by_dealer,
            "sales_by_stand": sales_by_stand,
            "dealer_performance": sales_by_dealer,  # For template compatibility
            "top_dealers": top_dealers,
            "top_stands": top_stands,
            "sales_count_trend": sales_count_trend,
            "revenue_profit_trend": revenue_profit_trend,
            "previous_year_comparison": previous_year_comparison,
            "top_models": top_models,
            # Add chart data
            "sales_counts": sales_counts,
            "revenues": revenues,
            "profits": profits,
            # Add filter options
            "vehicle_makes": vehicle_makes,
            "vehicle_models": vehicle_models,
            "stands": stands
        }
    
    def _decimal(self, value):
        """Convert a value to Decimal safely"""
        if isinstance(value, decimal.Decimal):
            return value
        return decimal.Decimal(str(value)) if value is not None else decimal.Decimal('0.00')
    
    def _get_period_definitions(self):
        """Define periods based on selected periodicity"""
        period_labels = []
        periods = []
        
        if self.period == "monthly":
            # Define all 12 months
            for i in range(1, 13):
                month_name = calendar.month_name[i]
                periods.append({
                    "id": i,
                    "name": month_name,
                    "start_month": i,
                    "end_month": i
                })
                period_labels.append(month_name)
                
        elif self.period == "quarterly":
            # Define 4 quarters
            quarters = [
                {"id": 1, "name": "Q1", "start_month": 1, "end_month": 3},
                {"id": 2, "name": "Q2", "start_month": 4, "end_month": 6},
                {"id": 3, "name": "Q3", "start_month": 7, "end_month": 9},
                {"id": 4, "name": "Q4", "start_month": 10, "end_month": 12}
            ]
            periods = quarters
            period_labels = [q["name"] for q in quarters]
            
        elif self.period == "yearly":
            # Just one period - the whole year
            periods = [{"id": 1, "name": str(self.year), "start_month": 1, "end_month": 12}]
            period_labels = [str(self.year)]
            
        return periods, period_labels
    
    def _calculate_avg_time_in_stock(self, sales):
        """Calculate average time in stock for sold cars"""
        total_days = 0
        valid_sales = 0
        
        for sale in sales:
            if sale.car.date_added_to_stand and sale.car.date_sold:
                days_in_stock = (sale.car.date_sold - sale.car.date_added_to_stand).days
                if days_in_stock >= 0:  # Ensure valid data
                    total_days += days_in_stock
                    valid_sales += 1
                    
        if valid_sales > 0:
            return total_days / valid_sales
        return 0
    
    def _get_sales_by_period(self, periods):
        """Calculate sales metrics for each defined period"""
        result = []
        
        for period in periods:
            # Build filter for this period
            date_filter = extract('year', Sale.sale_date) == self.year
            
            if self.start_date and self.end_date:
                # Use custom date range if provided
                start_date = self.start_date
                end_date = self.end_date
                date_filter = Sale.sale_date.between(start_date, end_date)
            else:
                # Otherwise use period definition
                date_filter = and_(
                    extract('year', Sale.sale_date) == self.year,
                    extract('month', Sale.sale_date) >= period["start_month"],
                    extract('month', Sale.sale_date) <= period["end_month"]
                )
            
            # Start query with date filter
            period_query = Sale.query.join(Car).filter(date_filter)
            
            # Apply additional filters
            if self.vehicle_make:
                period_query = period_query.filter(Car.vehicle_make == self.vehicle_make)
            if self.vehicle_model:
                period_query = period_query.filter(Car.vehicle_model == self.vehicle_model)
            if self.stand_ids:
                period_query = period_query.filter(Car.stand_id.in_(self.stand_ids))
                
            # Get filtered sales
            period_sales = period_query.all()
            
            # Calculate metrics
            count = len(period_sales)
            revenue = sum(self._decimal(sale.sale_price) for sale in period_sales)
            cost = sum(self._decimal(sale.car.total_investment) if sale.car is not None else decimal.Decimal('0.00')
                      for sale in period_sales)
            profit = revenue - cost
            margin = (profit / revenue * 100) if revenue > 0 else decimal.Decimal('0.00')
            avg_price = revenue / count if count > 0 else decimal.Decimal('0.00')
            
            # Calculate period-over-period changes
            previous_period_id = period["id"] - 1
            previous_period_data = next((p for p in result if p["period_id"] == previous_period_id), None)
            
            sales_change = 0
            revenue_change = 0
            profit_change = 0
            
            if previous_period_data:
                prev_sales = previous_period_data["count"]
                prev_revenue = previous_period_data["revenue"]
                prev_profit = previous_period_data["profit"]
                
                sales_change = ((count - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
                revenue_change = ((revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
                profit_change = ((profit - prev_profit) / prev_profit * 100) if prev_profit > 0 else 0
            
            result.append({
                "period_id": period["id"],
                "period_name": period["name"],
                "label": period["name"],
                "count": count,
                "revenue": revenue,
                "cost": cost,
                "profit": profit,
                "margin": margin,
                "avg_price": avg_price,
                "trend": sales_change,
                "sales_change": sales_change,
                "revenue_change": revenue_change,
                "profit_change": profit_change
            })
            
        return result
    
    def _get_sales_by_dealer(self):
        """Calculate sales metrics grouped by dealer"""
        # Get all dealers with sales in the specified year
        dealer_sales = {}
        
        # Start query with date filter
        if self.start_date and self.end_date:
            date_filter = Sale.sale_date.between(self.start_date, self.end_date)
        else:
            date_filter = extract('year', Sale.sale_date) == self.year
            
        sales_query = Sale.query.join(Car).filter(date_filter)
        
        # Apply additional filters
        if self.vehicle_make:
            sales_query = sales_query.filter(Car.vehicle_make == self.vehicle_make)
        if self.vehicle_model:
            sales_query = sales_query.filter(Car.vehicle_model == self.vehicle_model)
        if self.stand_ids:
            sales_query = sales_query.filter(Car.stand_id.in_(self.stand_ids))
            
        # Get filtered sales
        sales = sales_query.all()
        
        # Group by dealer and calculate metrics
        for sale in sales:
            dealer_id = sale.dealer_id
            dealer = Dealer.query.get(dealer_id)
            
            if dealer_id not in dealer_sales:
                dealer_sales[dealer_id] = {
                    "dealer_id": dealer_id,
                    "dealer_name": dealer.dealer_name if dealer else "Unknown",
                    "sales_count": 0,
                    "total_revenue": decimal.Decimal('0.00'),
                    "total_cost": decimal.Decimal('0.00'),
                    "total_profit": decimal.Decimal('0.00')
                }
                
            dealer_sales[dealer_id]["sales_count"] += 1
            dealer_sales[dealer_id]["total_revenue"] += self._decimal(sale.sale_price)
            dealer_sales[dealer_id]["total_cost"] += self._decimal(sale.car.total_investment) if sale.car is not None else decimal.Decimal('0.00')
            
        # Calculate derived metrics
        total_sales = sum(dealer["sales_count"] for dealer in dealer_sales.values())
        
        for dealer in dealer_sales.values():
            dealer["total_profit"] = dealer["total_revenue"] - dealer["total_cost"]
            dealer["average_sale"] = dealer["total_revenue"] / dealer["sales_count"] if dealer["sales_count"] > 0 else decimal.Decimal('0.00')
            dealer["margin"] = (dealer["total_profit"] / dealer["total_revenue"] * 100) if dealer["total_revenue"] > 0 else decimal.Decimal('0.00')
            dealer["sales_percentage"] = (dealer["sales_count"] / total_sales * 100) if total_sales > 0 else decimal.Decimal('0.00')
            
        # Sort by sales count (descending)
        return sorted(dealer_sales.values(), key=lambda x: x["sales_count"], reverse=True)
    
    def _get_sales_by_stand(self):
        """Calculate sales metrics grouped by stand"""
        # Get all stands with sales in the specified period
        stand_sales = {}
        
        # Start query with date filter
        if self.start_date and self.end_date:
            date_filter = Sale.sale_date.between(self.start_date, self.end_date)
        else:
            date_filter = extract('year', Sale.sale_date) == self.year
            
        sales_query = Sale.query.join(Car).filter(date_filter)
        
        # Apply additional filters
        if self.vehicle_make:
            sales_query = sales_query.filter(Car.vehicle_make == self.vehicle_make)
        if self.vehicle_model:
            sales_query = sales_query.filter(Car.vehicle_model == self.vehicle_model)
        if self.stand_ids:
            sales_query = sales_query.filter(Car.stand_id.in_(self.stand_ids))
            
        # Get filtered sales
        sales = sales_query.all()
        
        # Group by stand and calculate metrics
        for sale in sales:
            car = sale.car
            if car is None:
                continue  # Skip sales without an associated car
                
            stand_id = car.stand_id
            
            if not stand_id:
                continue  # Skip if no stand associated
                
            stand = Stand.query.get(stand_id)
            
            if stand_id not in stand_sales:
                stand_sales[stand_id] = {
                    "stand_id": stand_id,
                    "stand_name": stand.stand_name if stand else "Unknown",
                    "location": stand.location if stand else "",
                    "sales_count": 0,
                    "total_revenue": decimal.Decimal('0.00'),
                    "total_cost": decimal.Decimal('0.00'),
                    "total_profit": decimal.Decimal('0.00'),
                    "total_days_in_stock": 0,
                    "cars_with_stock_data": 0
                }
                
            stand_sales[stand_id]["sales_count"] += 1
            stand_sales[stand_id]["total_revenue"] += self._decimal(sale.sale_price)
            stand_sales[stand_id]["total_cost"] += self._decimal(car.total_investment)
            
            # Calculate time in stock for this car
            if car.date_added_to_stand and car.date_sold:
                days_in_stock = (car.date_sold - car.date_added_to_stand).days
                if days_in_stock >= 0:  # Ensure valid data
                    stand_sales[stand_id]["total_days_in_stock"] += days_in_stock
                    stand_sales[stand_id]["cars_with_stock_data"] += 1
            
        # Calculate derived metrics
        total_sales = sum(stand["sales_count"] for stand in stand_sales.values())
        
        for stand in stand_sales.values():
            stand["total_profit"] = stand["total_revenue"] - stand["total_cost"]
            stand["average_sale"] = stand["total_revenue"] / stand["sales_count"] if stand["sales_count"] > 0 else decimal.Decimal('0.00')
            stand["margin"] = (stand["total_profit"] / stand["total_revenue"] * 100) if stand["total_revenue"] > 0 else decimal.Decimal('0.00')
            stand["sales_percentage"] = (stand["sales_count"] / total_sales * 100) if total_sales > 0 else decimal.Decimal('0.00')
            
            # Calculate average days in stock
            if stand["cars_with_stock_data"] > 0:
                stand["avg_days_in_stock"] = stand["total_days_in_stock"] / stand["cars_with_stock_data"]
            else:
                stand["avg_days_in_stock"] = 0
            
        # Sort by sales count (descending)
        return sorted(stand_sales.values(), key=lambda x: x["sales_count"], reverse=True)
    
    def _get_previous_year_comparison(self):
        """Compare current year with previous year"""
        current_year = self.year
        previous_year = current_year - 1
        
        # Get current year sales
        current_year_sales = Sale.query.filter(extract('year', Sale.sale_date) == current_year).all()
        current_sales = len(current_year_sales)
        current_revenue = sum(self._decimal(sale.sale_price) for sale in current_year_sales)
        current_cost = sum(self._decimal(sale.car.total_investment) if sale.car is not None else decimal.Decimal('0.00') 
                          for sale in current_year_sales)
        current_profit = current_revenue - current_cost
        
        # Get previous year sales
        previous_year_sales = Sale.query.filter(extract('year', Sale.sale_date) == previous_year).all()
        previous_sales = len(previous_year_sales)
        previous_revenue = sum(self._decimal(sale.sale_price) for sale in previous_year_sales)
        previous_cost = sum(self._decimal(sale.car.total_investment) if sale.car is not None else decimal.Decimal('0.00')
                           for sale in previous_year_sales)
        previous_profit = previous_revenue - previous_cost
        
        # Calculate percentage changes
        sales_change = ((current_sales - previous_sales) / previous_sales * 100) if previous_sales > 0 else 0
        revenue_change = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
        profit_change = ((current_profit - previous_profit) / previous_profit * 100) if previous_profit > 0 else 0
        
        return {
            "current_year": current_year,
            "previous_year": previous_year,
            "current_sales": current_sales,
            "previous_sales": previous_sales,
            "sales_change": sales_change,
            "current_revenue": current_revenue,
            "previous_revenue": previous_revenue,
            "revenue_change": revenue_change,
            "current_profit": current_profit,
            "previous_profit": previous_profit,
            "profit_change": profit_change
        }
    
    def _get_top_models(self):
        """Get top selling car models"""
        # Track sales by model
        model_sales = {}
        
        # Start query with date filter
        if self.start_date and self.end_date:
            date_filter = Sale.sale_date.between(self.start_date, self.end_date)
        else:
            date_filter = extract('year', Sale.sale_date) == self.year
            
        # Make sure we only include cars that have been sold (date_sold is not None)
        sales_query = Sale.query.join(Car).filter(date_filter).filter(Car.date_sold.isnot(None))
        
        # Apply additional filters
        if self.vehicle_make:
            sales_query = sales_query.filter(Car.vehicle_make == self.vehicle_make)
        if self.vehicle_model:
            sales_query = sales_query.filter(Car.vehicle_model == self.vehicle_model)
        if self.stand_ids:
            sales_query = sales_query.filter(Car.stand_id.in_(self.stand_ids))
            
        # Get filtered sales
        sales = sales_query.all()
        
        # Group by model
        for sale in sales:
            car = sale.car
            if car is None:
                continue  # Skip sales without an associated car
                
            model_key = f"{car.vehicle_make}_{car.vehicle_model}"
            
            if model_key not in model_sales:
                model_sales[model_key] = {
                    "make": car.vehicle_make,
                    "model": car.vehicle_model,
                    "count": 0,
                    "total_revenue": decimal.Decimal('0.00'),
                    "average_price": decimal.Decimal('0.00'),
                    "cars": []  # Keep track of car IDs for this model
                }
                
            model_sales[model_key]["count"] += 1
            model_sales[model_key]["total_revenue"] += self._decimal(sale.sale_price)
            model_sales[model_key]["cars"].append({
                "car_id": car.car_id,
                "full_name": car.full_name,
                "vin": car.licence_number
            })
            
        # Calculate average prices
        for model in model_sales.values():
            model["average_price"] = model["total_revenue"] / model["count"]
            
        # Sort by count (descending) and take top 5
        sorted_models = sorted(model_sales.values(), key=lambda x: x["count"], reverse=True)
        return sorted_models[:5] if len(sorted_models) > 5 else sorted_models 