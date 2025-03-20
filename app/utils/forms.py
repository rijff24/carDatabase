from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms import IntegerField, DateField, FloatField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional, ValidationError
from datetime import datetime

class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[DataRequired(), Length(1, 50)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

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
    licence_number = StringField('Licence Number', validators=[DataRequired(), Length(1, 20)])
    registration_number = StringField('Registration Number', validators=[DataRequired(), Length(1, 20)])
    purchase_price = FloatField('Purchase Price', validators=[DataRequired(), NumberRange(min=0)])
    source = StringField('Source', validators=[DataRequired(), Length(1, 50)])
    date_bought = DateField('Date Bought', validators=[DataRequired()], format='%Y-%m-%d')
    refuel_cost = FloatField('Refuel Cost', validators=[Optional(), NumberRange(min=0)])
    current_location = StringField('Current Location', validators=[DataRequired(), Length(1, 100)])
    repair_status = SelectField('Repair Status', validators=[DataRequired()],
                               choices=[('Purchased', 'Purchased (awaiting collection)'),
                                       ('Waiting for Repairs', 'Waiting for Repairs'),
                                       ('In Repair', 'In Repair'),
                                       ('On Display', 'On Display at Stand'),
                                       ('Waiting for Payment', 'Waiting for Payment/Paperwork'),
                                       ('Sold', 'Sold')])
    submit = SubmitField('Submit')

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
    repair_cost = FloatField('Repair Cost', validators=[DataRequired(), NumberRange(min=0)])
    additional_notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Submit')

class PartForm(FlaskForm):
    """Form for adding or editing a part"""
    part_name = StringField('Part Name', validators=[DataRequired(), Length(1, 100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    manufacturer = StringField('Manufacturer', validators=[Optional(), Length(max=100)])
    standard_price = FloatField('Standard Price', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Submit')

class RepairPartForm(FlaskForm):
    """Form for adding a part to a repair"""
    repair_id = HiddenField('Repair ID', validators=[DataRequired()])
    part_id = SelectField('Part', validators=[DataRequired()], coerce=int)
    purchase_price = FloatField('Purchase Price', validators=[DataRequired(), NumberRange(min=0)])
    purchase_date = DateField('Purchase Date', validators=[DataRequired()], format='%Y-%m-%d')
    vendor = StringField('Vendor', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField('Add Part')

class StandForm(FlaskForm):
    """Form for adding or editing a stand"""
    stand_name = StringField('Stand Name', validators=[DataRequired(), Length(1, 100)])
    location = StringField('Location', validators=[DataRequired(), Length(1, 150)])
    additional_info = TextAreaField('Additional Information', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Submit')

class DealerForm(FlaskForm):
    """Form for adding or editing a dealer"""
    dealer_name = StringField('Dealer Name', validators=[DataRequired(), Length(1, 100)])
    contact_info = StringField('Contact Information', validators=[DataRequired(), Length(1, 150)])
    submit = SubmitField('Submit')

class RepairProviderForm(FlaskForm):
    """Form for adding or editing a repair provider"""
    provider_name = StringField('Provider Name', validators=[DataRequired(), Length(1, 100)])
    service_type = StringField('Service Type', validators=[DataRequired(), Length(1, 50)])
    contact_info = StringField('Contact Information', validators=[DataRequired(), Length(1, 150)])
    location = StringField('Location', validators=[DataRequired(), Length(1, 100)])
    submit = SubmitField('Submit')

class CarSaleForm(FlaskForm):
    """Form for recording a car sale"""
    car_id = HiddenField('Car ID', validators=[DataRequired()])
    date_sold = DateField('Sale Date', validators=[DataRequired()], format='%Y-%m-%d')
    sale_price = FloatField('Sale Price', validators=[DataRequired(), NumberRange(min=0)])
    dealer_id = SelectField('Dealer', validators=[DataRequired()], coerce=int)
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