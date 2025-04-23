from app.reports.base import Report
from app.models import Car, Repair, Setting, Stand
from datetime import datetime
from sqlalchemy import func, and_
import decimal
from dateutil.relativedelta import relativedelta

class InventoryAgingReport(Report):
    """
    Report showing the aging of inventory in stock, including:
    - Number of days in inventory
    - Vehicles requiring attention based on age
    - Distribution by different age ranges
    """
    template_path = "reports/inventory-aging.html"
    parameter_rules = {
        "status": {
            "type": "string",
            "required": False,
            "default": "all",
            "choices": ["all", "reconditioning", "ready", "stand"]
        },
        "stand_id": {
            "type": "integer",
            "required": False,
            "default": None
        },
        "make": {
            "type": "string",
            "required": False,
            "default": None
        },
        "model": {
            "type": "string",
            "required": False,
            "default": None
        },
        "min_age": {
            "type": "integer",
            "required": False,
            "default": 0
        },
        "max_age": {
            "type": "integer",
            "required": False,
            "default": None
        }
    }

    def __init__(self, status=None, stand_id=None, make=None, model=None, min_age=0, max_age=None):
        super().__init__()
        self.status = status or self.parameter_rules["status"]["default"]
        self.stand_id = stand_id
        self.make = make
        self.model = model
        self.min_age = min_age
        self.max_age = max_age
        
        # Get thresholds from settings
        self.stand_aging_threshold_days = Setting.get_setting('stand_aging_threshold_days', 45, 'int')
        self.status_inactivity_threshold_days = Setting.get_setting('status_inactivity_threshold_days', 30, 'int')
        self.enable_status_warnings = Setting.get_setting('enable_status_warnings', True, 'bool')
        self.enable_depreciation_tracking = Setting.get_setting('enable_depreciation_tracking', False, 'bool')
        
    def generate(self):
        # Query database for cars instead of using sample data
        from app.models import Car, Stand
        
        # Get actual stands from the database
        stands = Stand.query.order_by(Stand.stand_name).all()
        stands_data = [{"stand_id": stand.stand_id, "stand_name": stand.stand_name} for stand in stands]
        
        # Base query - exclude cars that have been sold
        car_query = Car.query.filter(Car.date_sold == None)
        
        # Apply filters from report parameters
        if self.status != "all":
            if self.status == "reconditioning":
                car_query = car_query.filter((Car.repair_status == "In Reconditioning") | (Car.repair_status == "Waiting for Repairs"))
            elif self.status == "stand":
                car_query = car_query.filter(Car.stand_id != None)
        
        if self.stand_id:
            car_query = car_query.filter(Car.stand_id == self.stand_id)
            
        if self.make:
            car_query = car_query.filter(Car.vehicle_make.ilike(f"%{self.make}%"))
            
        if self.model:
            car_query = car_query.filter(Car.vehicle_model.ilike(f"%{self.model}%"))
        
        # Execute query and get the cars
        db_cars = car_query.all()
        
        # Get all cars for status counts, vehicle makes and models (excluding sold cars)
        all_cars = Car.query.filter(Car.date_sold == None).all()
        
        # Convert to dictionary objects with required attributes
        cars = []
        for car_obj in db_cars:
            # Calculate days in inventory
            days_in_inventory = (datetime.now().date() - car_obj.date_bought).days
            
            # Skip if outside age range
            if self.min_age is not None and days_in_inventory < self.min_age:
                continue
            if self.max_age is not None and days_in_inventory > self.max_age:
                continue
            
            # Create car dictionary
            car = {
                "car_id": car_obj.car_id,
                "vin": car_obj.registration_number,
                "year": car_obj.year,
                "make": car_obj.vehicle_make,
                "model": car_obj.vehicle_model,
                "trim": car_obj.colour,
                "status": "reconditioning" if car_obj.repair_status == "In Reconditioning" or car_obj.repair_status == "Waiting for Repairs" else 
                          "stand" if car_obj.stand_id else "other",
                "date_bought": car_obj.date_bought,
                "purchase_price": car_obj.purchase_price,
                "date_sold": None,  # We're already filtering sold cars
                "vehicle_name": f"{car_obj.year} {car_obj.vehicle_make} {car_obj.vehicle_model}",
                "date_added_to_stand": car_obj.date_added_to_stand,
                "purchase_date": car_obj.date_bought,
                "recon_cost": car_obj.recon_cost or 0,
                "status_last_changed": datetime.now().date() - relativedelta(days=10),  # Placeholder, should be tracked in real app
                "book_value": car_obj.purchase_price,  # Placeholder, should be actual book value
                "stand_id": car_obj.stand_id,
                "current_location": car_obj.current_location,
                "days_in_inventory": days_in_inventory
            }
            
            # Calculate days in reconditioning and on stand
            if car["date_added_to_stand"]:
                car["days_in_recon"] = (car["date_added_to_stand"] - car["date_bought"]).days
                car["days_on_stand"] = (datetime.now().date() - car["date_added_to_stand"]).days
            else:
                car["days_in_recon"] = car["days_in_inventory"]
                car["days_on_stand"] = 0
                
            # Calculate how long since status changed (using placeholder)
            car["days_since_status_change"] = 10  # Placeholder
            car["is_status_inactive"] = self.enable_status_warnings and car["days_since_status_change"] > self.status_inactivity_threshold_days
            
            # Calculate stand warning levels
            if car["status"] == "stand":
                warning_threshold = self.stand_aging_threshold_days
                car["stand_warning_level"] = "none"
                if car["days_on_stand"] > warning_threshold:
                    car["stand_warning_level"] = "danger"  # Red
                elif car["days_on_stand"] > warning_threshold * 0.5:
                    car["stand_warning_level"] = "warning"  # Yellow
            else:
                car["stand_warning_level"] = "none"
                
            # Calculate total investment
            car["total_investment"] = car["purchase_price"] + car["recon_cost"]
            
            # Calculate depreciation (value lost)
            if self.enable_depreciation_tracking:
                car["value_lost"] = car["total_investment"] - car["book_value"]
            else:
                car["value_lost"] = decimal.Decimal("0.00")
                
            cars.append(car)
        
        # Prepare aging buckets
        aging_buckets = self._prepare_aging_buckets(cars)
        
        # Status counts
        status_counts = {
            "reconditioning": len([car for car in all_cars if car.repair_status == "In Reconditioning" or car.repair_status == "Waiting for Repairs"]),
            "stand": len([car for car in all_cars if car.stand_id is not None and car.repair_status != "Waiting for Repairs" and car.repair_status != "In Reconditioning"])
        }
        
        # Create a list of vehicle makes and models for filtering
        vehicle_makes = sorted(list(set(car.vehicle_make for car in all_cars)))
        vehicle_models = sorted(list(set(car.vehicle_model for car in all_cars)))
        
        # Group models by make for dynamic filtering
        models_by_make = {}
        for car in all_cars:
            if car.vehicle_make not in models_by_make:
                models_by_make[car.vehicle_make] = []
            if car.vehicle_model not in models_by_make[car.vehicle_make]:
                models_by_make[car.vehicle_make].append(car.vehicle_model)
        
        # Sort model lists
        for make in models_by_make:
            models_by_make[make].sort()
        
        # Calculate summary metrics
        total_inventory = len(cars)
        
        # Handle empty results
        if total_inventory == 0:
            return {
                "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": self.status,
                "stand_id": self.stand_id,
                "make": self.make,
                "model": self.model,
                "min_age": self.min_age,
                "max_age": self.max_age,
                "cars": [],
                "total_inventory": 0,
                "aged_vehicle_count": 0,
                "aged_vehicle_percentage": 0,
                "total_investment": str(decimal.Decimal('0.00')),
                "avg_investment_per_vehicle": str(decimal.Decimal('0.00')),
                "avg_days_in_inventory": 0,
                "aging_buckets": aging_buckets,
                "status_counts": status_counts,
                "stand_aging_threshold_days": self.stand_aging_threshold_days,
                "status_inactivity_threshold_days": self.status_inactivity_threshold_days,
                "enable_status_warnings": self.enable_status_warnings,
                "enable_depreciation_tracking": self.enable_depreciation_tracking,
                "stands": stands_data,
                "vehicle_makes": vehicle_makes,
                "vehicle_models": vehicle_models,
                "models_by_make": models_by_make
            }
        
        aged_vehicle_count = len([car for car in cars if car["days_in_inventory"] > self.stand_aging_threshold_days])
        aged_vehicle_percentage = (aged_vehicle_count / total_inventory * 100) if total_inventory > 0 else 0
        total_investment = sum(car["total_investment"] for car in cars)
        avg_investment_per_vehicle = total_investment / total_inventory if total_inventory > 0 else 0
        avg_days_in_inventory = sum(car["days_in_inventory"] for car in cars) / total_inventory if total_inventory > 0 else 0
        
        # Calculate value loss if depreciation tracking is enabled
        total_value_lost = decimal.Decimal('0.00')
        if self.enable_depreciation_tracking:
            total_value_lost = sum(car["value_lost"] for car in cars)
        
        # Convert cars for serialization
        serializable_cars = []
        for car in cars:
            car_copy = dict(car)
            car_copy["purchase_price"] = str(car["purchase_price"].quantize(decimal.Decimal('0.01')))
            car_copy["total_investment"] = str(car["total_investment"].quantize(decimal.Decimal('0.01')))
            car_copy["value_lost"] = str(car["value_lost"].quantize(decimal.Decimal('0.01')))
            car_copy["date_bought"] = car["date_bought"].isoformat()
            if car["date_added_to_stand"]:
                car_copy["date_added_to_stand"] = car["date_added_to_stand"].isoformat()
            if car["date_sold"]:
                car_copy["date_sold"] = car["date_sold"].isoformat()
            serializable_cars.append(car_copy)
            
        # Sort cars by days in inventory
        serializable_cars.sort(key=lambda c: c["days_in_inventory"], reverse=True)
        
        return {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": self.status,
            "stand_id": self.stand_id,
            "make": self.make,
            "model": self.model,
            "min_age": self.min_age,
            "max_age": self.max_age,
            "cars": serializable_cars,
            "total_inventory": total_inventory,
            "aged_vehicle_count": aged_vehicle_count,
            "aged_vehicle_percentage": aged_vehicle_percentage,
            "total_investment": str(total_investment.quantize(decimal.Decimal('0.01'))),
            "avg_investment_per_vehicle": str(avg_investment_per_vehicle.quantize(decimal.Decimal('0.01'))),
            "avg_days_in_inventory": avg_days_in_inventory,
            "aging_buckets": aging_buckets,
            "status_counts": status_counts,
            "stand_aging_threshold_days": self.stand_aging_threshold_days,
            "status_inactivity_threshold_days": self.status_inactivity_threshold_days,
            "enable_status_warnings": self.enable_status_warnings,
            "enable_depreciation_tracking": self.enable_depreciation_tracking,
            "total_value_lost": str(total_value_lost.quantize(decimal.Decimal('0.01'))),
            "stands": stands_data,
            "vehicle_makes": vehicle_makes,
            "vehicle_models": vehicle_models,
            "models_by_make": models_by_make
        }
        
    def _calculate_total_investment(self, car):
        """Calculate the total investment in a vehicle including purchase and repairs"""
        # Start with purchase price
        total = decimal.Decimal(str(car["purchase_price"])) if car["purchase_price"] else decimal.Decimal('0.00')
        
        # Add repair costs
        repair_costs = decimal.Decimal(str(car["recon_cost"])) if car["recon_cost"] else decimal.Decimal('0.00')
            
        total += repair_costs
        
        return total
        
    def _prepare_aging_buckets(self, cars):
        """
        Group cars into aging buckets based on the image example:
        0-60 days, 61-180 days, 181-195 days, 196-270 days, 91+ days
        """
        buckets = [
            {"label": "0-60 days", "min_days": 0, "max_days": 60, "count": 0, "investment": decimal.Decimal('0.00'), "alert": False, "warning_threshold": False},
            {"label": "61-180 days", "min_days": 61, "max_days": 180, "count": 0, "investment": decimal.Decimal('0.00'), "alert": False, "warning_threshold": False},
            {"label": "181-195 days", "min_days": 181, "max_days": 195, "count": 0, "investment": decimal.Decimal('0.00'), "alert": False, "warning_threshold": True},
            {"label": "196-270 days", "min_days": 196, "max_days": 270, "count": 0, "investment": decimal.Decimal('0.00'), "alert": False, "warning_threshold": True},
            {"label": "91+ days", "min_days": 271, "max_days": float('inf'), "count": 0, "investment": decimal.Decimal('0.00'), "alert": False, "warning_threshold": True}
        ]
        
        for car in cars:
            days = car["days_in_inventory"]
            matched = False
            
            for bucket in buckets:
                if bucket["min_days"] <= days <= bucket["max_days"]:
                    bucket["count"] += 1
                    bucket["investment"] += car["total_investment"]
                    matched = True
                    # Set alert to true if this is a warning threshold bucket and it has cars
                    if bucket["warning_threshold"]:
                        bucket["alert"] = True
                    break
            
            # If no bucket matched, put it in the 91+ days bucket for backward compatibility
            if not matched and days >= 91:
                buckets[4]["count"] += 1
                buckets[4]["investment"] += car["total_investment"]
                buckets[4]["alert"] = True
                    
        # Calculate percentages and averages
        total_count = len(cars)
        for bucket in buckets:
            bucket["percentage"] = (bucket["count"] / total_count * 100) if total_count > 0 else 0
            bucket["avg_investment"] = bucket["investment"] / bucket["count"] if bucket["count"] > 0 else decimal.Decimal('0.00')
            # Convert Decimal to string for JSON serialization
            bucket["investment"] = str(bucket["investment"])
            bucket["avg_investment"] = str(bucket["avg_investment"])
            
        return buckets 