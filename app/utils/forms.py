from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms import IntegerField, DateField, FloatField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional, ValidationError, Regexp
from datetime import datetime
from app.utils.validators import validate_username, validate_password

class LoginForm(FlaskForm):
    """Login form with enhanced validation"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(3, 32),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Username can only contain letters, numbers, and underscores')
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

    def validate_username(self, field):
        """Custom username validation"""
        if not validate_username(field.data):
            raise ValidationError('Username must be 3-32 characters long and contain only letters, numbers, and underscores')

class CarForm(FlaskForm):
    """Form for adding or editing a car"""
    vehicle_name = StringField('Vehicle Name', validators=[DataRequired(), Length(1, 100)])
    vehicle_make = StringField('Make', validators=[DataRequired(), Length(1, 50)])
    vehicle_model = StringField('Model', validators=[DataRequired(), Length(1, 50)])
    year = IntegerField('Year', validators=[
        DataRequired(), 
        NumberRange(min=1990, max=datetime.now().year, 
                   message=f'Year must be between 1990 and {datetime.now().year}')
    ])
    colour = StringField('Colour', validators=[DataRequired(), Length(1, 50)])
    dekra_condition = SelectField('Dekra Condition', validators=[DataRequired()], 
                                choices=[('Platinum', 'Platinum'), 
                                        ('Diamond', 'Diamond'),
                                        ('Gold', 'Gold'),
                                        ('Green', 'Green'),
                                        ('Other', 'Other')])
    licence_number = StringField('Licence Number', validators=[
        DataRequired(), 
        Length(1, 20),
        Regexp(r'^[A-Z0-9 ]{5,20}$', message='Licence number must be in South African format')
    ])
    registration_number = StringField('Registration Number', validators=[
        DataRequired(), 
        Length(1, 20),
        Regexp(r'^[A-Z0-9 ]{5,20}$', message='Registration number must be in South African format')
    ])
    purchase_price = FloatField('Purchase Price (R)', validators=[DataRequired(), NumberRange(min=0)])
    source = SelectField('Source (Dealer)', validators=[DataRequired()], coerce=int)
    date_bought = DateField('Date Bought', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.now().date())
    refuel_cost = FloatField('Refuel Cost (R)', validators=[Optional(), NumberRange(min=0)])
    current_location = StringField('Current Location', validators=[Optional(), Length(max=100)])
    repair_status = SelectField('Repair Status', validators=[DataRequired()],
                               choices=[('Purchased', 'Purchased (awaiting collection)'),
                                       ('Waiting for Repairs', 'Waiting for Repairs'),
                                       ('In Repair', 'In Repair'),
                                       ('On Display', 'On Display at Stand'),
                                       ('Waiting for Payment', 'Waiting for Payment/Paperwork'),
                                       ('Sold', 'Sold')])
    date_added_to_stand = DateField('Date Added to Stand (leave empty if not on stand yet)', validators=[Optional()], format='%Y-%m-%d')
    date_sold = DateField('Date Sold (leave empty if not sold yet)', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Submit')

    def validate_date_bought(self, field):
        """Ensure date_bought is not in the future"""
        if field.data > datetime.now().date():
            raise ValidationError('Purchase date cannot be in the future')

    def validate_date_added_to_stand(self, field):
        """Ensure date_added_to_stand is after date_bought"""
        if field.data and self.date_bought.data and field.data < self.date_bought.data:
            raise ValidationError('Date added to stand must be after purchase date')
    
    def validate_date_sold(self, field):
        """Ensure date_sold is after date_added_to_stand"""
        if field.data and hasattr(self, 'date_added_to_stand') and self.date_added_to_stand.data and field.data < self.date_added_to_stand.data:
            raise ValidationError('Sale date must be after date added to stand')

class RepairForm(FlaskForm):
    """Form for adding or editing a repair"""
    car_id = SelectField('Car', validators=[DataRequired()], coerce=int)
    repair_type = SelectField('Repair Type', validators=[DataRequired()],
                            choices=[('Upholstery', 'Upholstery'),
                                    ('Panel Beating', 'Panel Beating'),
                                    ('Tires/Suspension', 'Tires/Suspension'),
                                    ('Workshop Repairs', 'Workshop Repairs'),
                                    ('Car Wash', 'Car Wash'),
                                    ('Air Conditioning', 'Air Conditioning'),
                                    ('Brakes/Clutch', 'Brakes/Clutch'),
                                    ('Windscreen', 'Windscreen'),
                                    ('Covers', 'Covers'),
                                    ('Diagnostics', 'Diagnostics'),
                                    ('Other', 'Other')])
    provider_id = SelectField('Service Provider', validators=[DataRequired()], coerce=int)
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[Optional()], format='%Y-%m-%d')
    repair_cost = FloatField('Labor Cost', validators=[DataRequired(), NumberRange(min=0)])
    additional_notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Submit')

    def validate_start_date(self, field):
        """Ensure start_date is not in the future"""
        if field.data > datetime.now().date():
            raise ValidationError('Start date cannot be in the future')
    
    def validate_end_date(self, field):
        """Ensure end_date is after start_date if provided"""
        if field.data and self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('End date must be after start date')
        
        if field.data and field.data > datetime.now().date():
            raise ValidationError('End date cannot be in the future')

class PartForm(FlaskForm):
    """Form for adding or editing a part"""
    part_name = StringField('Part Name', validators=[
        DataRequired(), 
        Length(1, 100),
        Regexp(r'^[a-zA-Z0-9\-\.\& ]+$', message='Part name can only contain letters, numbers, spaces, hyphens, dots and ampersands')
    ])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    manufacturer = StringField('Manufacturer', validators=[
        Optional(), 
        Length(max=100),
        Regexp(r'^[a-zA-Z0-9\-\.\& ]+$', message='Manufacturer name can only contain letters, numbers, spaces, hyphens, dots and ampersands')
    ])
    standard_price = FloatField('Standard Price', validators=[
        Optional(), 
        NumberRange(min=0, message='Price cannot be negative')
    ])
    submit = SubmitField('Submit')

    def validate_standard_price(self, field):
        """Validate the price format"""
        if field.data is not None:
            # Check if it has more than 2 decimal places
            str_value = str(field.data)
            if '.' in str_value:
                decimals = len(str_value.split('.')[1])
                if decimals > 2:
                    raise ValidationError('Price cannot have more than 2 decimal places')

class RepairPartForm(FlaskForm):
    """Form for adding a part to a repair"""
    repair_id = HiddenField('Repair ID', validators=[DataRequired()])
    part_id = SelectField('Part', validators=[DataRequired()], coerce=int)
    purchase_price = FloatField('Purchase Price', validators=[DataRequired(), NumberRange(min=0)])
    purchase_date = DateField('Purchase Date', validators=[DataRequired()], format='%Y-%m-%d')
    vendor = StringField('Vendor', validators=[
        DataRequired(), 
        Length(1, 100),
        Regexp(r'^[a-zA-Z0-9\-\.\& ]+$', message='Vendor name can only contain letters, numbers, spaces, hyphens, dots and ampersands')
    ])
    submit = SubmitField('Add Part')

    def validate_purchase_date(self, field):
        """Ensure purchase_date is not in the future"""
        if field.data > datetime.now().date():
            raise ValidationError('Purchase date cannot be in the future')

class StandForm(FlaskForm):
    """Form for adding or editing a stand"""
    stand_name = StringField('Stand Name', validators=[
        DataRequired(), 
        Length(1, 100),
        Regexp(r'^[a-zA-Z0-9\-\.\& ]+$', message='Stand name can only contain letters, numbers, spaces, hyphens, dots and ampersands')
    ])
    location = StringField('Location', validators=[
        DataRequired(), 
        Length(1, 150),
        Regexp(r'^[a-zA-Z0-9\-\.\,\/ ]+$', message='Location format is invalid')
    ])
    capacity = IntegerField('Capacity', validators=[
        DataRequired(), 
        NumberRange(min=1, max=100, message='Capacity must be between 1 and 100 vehicles')
    ], default=10)
    additional_info = TextAreaField('Additional Information', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Submit')
    
    def validate_capacity(self, field):
        """Additional capacity validation"""
        # For edit operations, check if capacity is being reduced below current car count
        if hasattr(self, 'obj') and self.obj and hasattr(self.obj, 'current_car_count'):
            if field.data < self.obj.current_car_count:
                raise ValidationError(f'Capacity cannot be less than current number of cars ({self.obj.current_car_count})')

class DealerForm(FlaskForm):
    """Form for adding or editing a dealer"""
    dealer_name = StringField('Dealer Name', validators=[
        DataRequired(), 
        Length(1, 100),
        Regexp(r'^[a-zA-Z0-9\-\.\& ]+$', message='Dealer name can only contain letters, numbers, spaces, hyphens, dots and ampersands')
    ])
    contact_info = StringField('Contact Information', validators=[
        DataRequired(), 
        Length(1, 150),
        Regexp(r'^[a-zA-Z0-9\-\.\+\@\, ]+$', message='Contact information format is invalid')
    ])
    address = StringField('Address', validators=[
        Optional(), 
        Length(max=200),
        Regexp(r'^[a-zA-Z0-9\-\.\,\/ ]+$', message='Address format is invalid')
    ])
    submit = SubmitField('Submit')
    
    def validate_contact_info(self, field):
        """Validate that contact information contains at least a phone number or email"""
        if not any(char in field.data for char in ['@', '+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
            raise ValidationError('Contact information must include a phone number or email address')

class RepairProviderForm(FlaskForm):
    """Form for adding or editing a repair provider"""
    provider_name = StringField('Provider Name', validators=[
        DataRequired(), 
        Length(1, 100),
        Regexp(r'^[a-zA-Z0-9\-\.\& ]+$', message='Provider name can only contain letters, numbers, spaces, hyphens, dots and ampersands')
    ])
    service_type = StringField('Service Type', validators=[
        DataRequired(), 
        Length(1, 50),
        Regexp(r'^[a-zA-Z0-9\-\/ ]+$', message='Service type can only contain letters, numbers, spaces, hyphens and slashes')
    ])
    contact_info = StringField('Contact Information', validators=[
        DataRequired(), 
        Length(1, 150),
        Regexp(r'^[a-zA-Z0-9\-\.\+\@\, ]+$', message='Contact information format is invalid')
    ])
    location = StringField('Location', validators=[
        DataRequired(), 
        Length(1, 100),
        Regexp(r'^[a-zA-Z0-9\-\.\,\/ ]+$', message='Location format is invalid')
    ])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    rating = SelectField('Rating', validators=[Optional()], 
                        choices=[('', 'Not Rated'), ('1', '1 Star'), ('2', '2 Stars'), 
                                ('3', '3 Stars'), ('4', '4 Stars'), ('5', '5 Stars')],
                        coerce=lambda x: int(x) if x else None)
    submit = SubmitField('Submit')

    def validate_contact_info(self, field):
        """Validate that contact information contains at least a phone number or email"""
        if not any(char in field.data for char in ['@', '+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
            raise ValidationError('Contact information must include a phone number or email address')

class CarSaleForm(FlaskForm):
    """Form for recording a car sale"""
    car_id = HiddenField('Car ID', validators=[DataRequired()])
    date_sold = DateField('Sale Date', validators=[DataRequired()], format='%Y-%m-%d')
    sale_price = FloatField('Sale Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Record Sale')

class DateRangeForm(FlaskForm):
    """Form for filtering reports by date range"""
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    end_date = DateField('End Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Apply Filter')

    def validate_end_date(self, field):
        """Ensure end_date is after start_date"""
        if field.data < self.start_date.data:
            raise ValidationError('End date must be after start date') 