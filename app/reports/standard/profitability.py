from app.reports.base import Report
from app.models import Car, Sale, Stand, Dealer
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import decimal

class ProfitabilityReport(Report):
    """
    Detailed report showing investment vs profit per car, including:
    - Purchase price
    - Recon cost
    - Refuel cost
    - Total investment
    - Sale price
    - Profit
    - ROI %
    
    With filters for make, model, stand, and date range, and expandable drill-down by model.
    Uses color bands for ROI brackets (high/medium/low)
    """
    template_path = "reports/profitability.html"
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
        },
        "vehicle_make": {
            "type": "string",
            "required": False,
            "default": None
        },
        "vehicle_model": {
            "type": "string",
            "required": False,
            "default": None
        }
    }

    def __init__(self, timeframe=None, start_date=None, end_date=None, stand_id=None, dealer_id=None, 
                 vehicle_make=None, vehicle_model=None):
        super().__init__()
        self.timeframe = timeframe or self.parameter_rules["timeframe"]["default"]
        self.start_date = start_date
        self.end_date = end_date
        self.stand_id = stand_id
        self.dealer_id = dealer_id
        self.vehicle_make = vehicle_make
        self.vehicle_model = vehicle_model
        
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
            
        if self.vehicle_make:
            sales_query = sales_query.filter(Car.vehicle_make == self.vehicle_make)
            
        if self.vehicle_model:
            sales_query = sales_query.filter(Car.vehicle_model == self.vehicle_model)
            
        sales = sales_query.all()
        
        # Calculate summary metrics
        total_cars_sold = len(sales)
        total_revenue = sum(self._decimal(sale.sale_price) for sale in sales)
        total_investment = sum(self._decimal(sale.car.total_investment) for sale in sales)
        total_profit = total_revenue - total_investment
        
        average_revenue = total_revenue / total_cars_sold if total_cars_sold > 0 else decimal.Decimal('0.00')
        average_investment = total_investment / total_cars_sold if total_cars_sold > 0 else decimal.Decimal('0.00')
        average_profit = total_profit / total_cars_sold if total_cars_sold > 0 else decimal.Decimal('0.00')
        average_roi = (total_profit / total_investment * 100) if total_investment > 0 else decimal.Decimal('0.00')
        
        # Get cars with detailed investment and profit data
        cars_data = self._get_cars_profitability_data(sales)
        
        # Get profitability by make/model with drilldown
        model_profitability = self._get_model_profitability(sales)
        
        # Get ROI distribution for color bands
        roi_distribution = self._get_roi_distribution(sales)
        
        # Get available filters (makes, models, dealers, stands)
        makes_models = self._get_available_makes_models()
        dealers = Dealer.query.all()
        stands = Stand.query.all()
        
        return {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "timeframe": self.timeframe,
            "start_date": self.start_date.strftime("%Y-%m-%d") if self.start_date else None,
            "end_date": self.end_date.strftime("%Y-%m-%d") if self.end_date else None,
            "stand_id": self.stand_id,
            "dealer_id": self.dealer_id,
            "vehicle_make": self.vehicle_make,
            "vehicle_model": self.vehicle_model,
            "total_cars_sold": total_cars_sold,
            "total_revenue": total_revenue,
            "total_investment": total_investment,
            "total_profit": total_profit,
            "average_revenue": average_revenue,
            "average_investment": average_investment,
            "average_profit": average_profit,
            "average_roi": average_roi,
            "cars_data": cars_data,
            "model_profitability": model_profitability,
            "roi_distribution": roi_distribution,
            "available_makes_models": makes_models,
            "available_dealers": dealers,
            "available_stands": stands,
            # ROI color band thresholds
            "roi_thresholds": {
                "high": 30.0,  # 30% and above is high ROI
                "medium": 15.0  # 15-30% is medium, below 15% is low
            }
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

    def _get_cars_profitability_data(self, sales):
        """Get detailed profitability data for each car"""
        cars_data = []
        
        for sale in sales:
            car = sale.car
            
            # Get all cost components
            purchase_price = self._decimal(car.purchase_price)
            repair_cost = self._decimal(car.total_repair_cost)
            refuel_cost = self._decimal(car.refuel_cost)
            total_investment = purchase_price + repair_cost + refuel_cost
            
            sale_price = self._decimal(sale.sale_price)
            profit = sale_price - total_investment
            roi = (profit / total_investment * 100) if total_investment > 0 else decimal.Decimal('0.00')
            
            # Determine ROI color band
            roi_band = self._get_roi_band(roi)
            
            cars_data.append({
                "car_id": car.car_id,
                "make": car.vehicle_make,
                "model": car.vehicle_model,
                "year": car.year,
                "color": car.colour,
                "vin": car.licence_number,
                "stand_name": car.stand.stand_name if car.stand else "Unknown",
                "purchase_price": purchase_price,
                "repair_cost": repair_cost,
                "refuel_cost": refuel_cost,
                "total_investment": total_investment,
                "sale_price": sale_price,
                "profit": profit,
                "roi": roi,
                "roi_band": roi_band,
                "sale_date": sale.sale_date.strftime("%Y-%m-%d") if sale.sale_date else "Unknown",
                "dealer_name": sale.dealer.dealer_name if sale.dealer else "Unknown"
            })
        
        # Sort by ROI (highest to lowest)
        return sorted(cars_data, key=lambda x: x["roi"], reverse=True)
    
    def _get_model_profitability(self, sales):
        """Calculate profitability metrics grouped by make/model with drilldown to individual cars"""
        make_models = {}
        
        for sale in sales:
            car = sale.car
            make = car.vehicle_make
            model = car.vehicle_model
            make_model_key = f"{make}_{model}"
            
            # Purchase, repair, and refuel costs
            purchase_price = self._decimal(car.purchase_price)
            repair_cost = self._decimal(car.total_repair_cost)
            refuel_cost = self._decimal(car.refuel_cost)
            total_investment = purchase_price + repair_cost + refuel_cost
            
            sale_price = self._decimal(sale.sale_price)
            profit = sale_price - total_investment
            roi = (profit / total_investment * 100) if total_investment > 0 else decimal.Decimal('0.00')
            
            # Create car detail record for drilldown
            car_detail = {
                "car_id": car.car_id,
                "year": car.year,
                "color": car.colour,
                "vin": car.licence_number,
                "stand_name": car.stand.stand_name if car.stand else "Unknown",
                "purchase_price": purchase_price,
                "repair_cost": repair_cost,
                "refuel_cost": refuel_cost,
                "total_investment": total_investment,
                "sale_price": sale_price,
                "profit": profit,
                "roi": roi,
                "roi_band": self._get_roi_band(roi),
                "sale_date": sale.sale_date.strftime("%Y-%m-%d") if sale.sale_date else "Unknown",
                "dealer_name": sale.dealer.dealer_name if sale.dealer else "Unknown"
            }
            
            # Add to make/model group
            if make_model_key not in make_models:
                make_models[make_model_key] = {
                    "make": make,
                    "model": model,
                    "count": 0,
                    "total_purchase": decimal.Decimal('0.00'),
                    "total_repair": decimal.Decimal('0.00'),
                    "total_refuel": decimal.Decimal('0.00'),
                    "total_investment": decimal.Decimal('0.00'),
                    "total_revenue": decimal.Decimal('0.00'),
                    "total_profit": decimal.Decimal('0.00'),
                    "cars": []
                }
            
            # Update make/model group with this car's data
            make_models[make_model_key]["count"] += 1
            make_models[make_model_key]["total_purchase"] += purchase_price
            make_models[make_model_key]["total_repair"] += repair_cost
            make_models[make_model_key]["total_refuel"] += refuel_cost
            make_models[make_model_key]["total_investment"] += total_investment
            make_models[make_model_key]["total_revenue"] += sale_price
            make_models[make_model_key]["total_profit"] += profit
            make_models[make_model_key]["cars"].append(car_detail)
        
        # Calculate averages and ROI for each make/model
        for make_model in make_models.values():
            count = make_model["count"]
            make_model["avg_purchase"] = make_model["total_purchase"] / count
            make_model["avg_repair"] = make_model["total_repair"] / count
            make_model["avg_refuel"] = make_model["total_refuel"] / count
            make_model["avg_investment"] = make_model["total_investment"] / count
            make_model["avg_revenue"] = make_model["total_revenue"] / count
            make_model["avg_profit"] = make_model["total_profit"] / count
            make_model["roi"] = (make_model["total_profit"] / make_model["total_investment"] * 100) if make_model["total_investment"] > 0 else decimal.Decimal('0.00')
            make_model["roi_band"] = self._get_roi_band(make_model["roi"])
        
        # Sort by ROI (highest to lowest)
        return sorted(make_models.values(), key=lambda x: x["roi"], reverse=True)
    
    def _get_roi_band(self, roi):
        """Determine ROI color band (high, medium, low)"""
        if roi >= 30.0:
            return "high"
        elif roi >= 15.0:
            return "medium"
        else:
            return "low"
    
    def _get_roi_distribution(self, sales):
        """Calculate ROI distribution for color bands"""
        distribution = {
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for sale in sales:
            car = sale.car
            
            # Calculate ROI
            total_investment = self._decimal(car.total_investment)
            sale_price = self._decimal(sale.sale_price)
            profit = sale_price - total_investment
            roi = (profit / total_investment * 100) if total_investment > 0 else decimal.Decimal('0.00')
            
            # Increment appropriate band counter
            roi_band = self._get_roi_band(roi)
            distribution[roi_band] += 1
        
        # Calculate percentages
        total = len(sales)
        if total > 0:
            # Use a list of the original keys to avoid modifying during iteration
            for band in list(distribution.keys()):
                distribution[band + "_percent"] = (distribution[band] / total) * 100
        else:
            # Use a list of the original keys to avoid modifying during iteration
            for band in list(distribution.keys()):
                distribution[band + "_percent"] = 0
        
        return distribution
    
    def _get_available_makes_models(self):
        """Get all available makes and models for filtering"""
        makes_query = Car.query.with_entities(Car.vehicle_make).distinct().order_by(Car.vehicle_make)
        makes = [make[0] for make in makes_query.all() if make[0]]
        
        # Get models for each make
        makes_models = {}
        for make in makes:
            models_query = Car.query.with_entities(Car.vehicle_model).filter(Car.vehicle_make == make).distinct().order_by(Car.vehicle_model)
            makes_models[make] = [model[0] for model in models_query.all() if model[0]]
        
        return {
            "makes": makes,
            "makes_models": makes_models
        } 