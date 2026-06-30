from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class VoucherForm(FlaskForm):
    code = StringField('Code', validators=[
        DataRequired(message='Please enter the voucher code!'),
        Length(1, 50, message='Code must be between 1 and 50 characters!')
    ])
    min_spend = DecimalField('Minimum Spend', default=0.0, validators=[
        Optional(),
        NumberRange(min=0.0, message='Minimum spend must be 0 or greater!')
    ])
    usage_limit = IntegerField('Usage Limit', validators=[
        Optional(),
        NumberRange(min=1, message='Usage limit must be 1 or greater!')
    ])
    usage_count = IntegerField('Usage Count', default=0, validators=[
        Optional(),
        NumberRange(min=0, message='Usage count must be 0 or greater!')
    ])
    status = SelectField('Status', choices=[
        ('true', 'Active'),
        ('false', 'Inactive'),
    ])
    submit = SubmitField('Submit')
