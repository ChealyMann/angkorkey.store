from flask_wtf.file import FileAllowed, FileField, MultipleFileField
from wtforms import SelectField, FloatField, BooleanField
from wtforms.fields.simple import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf import FlaskForm

from models import Category, Brand


def get_categories():
    return Category.query.all()


def get_brands():
    return Brand.query.filter_by(status="true").all()


class ProductForm(FlaskForm):
    name = StringField(
        "product_name",
        validators=[
            DataRequired(message="Please enter Product Name"),
            Length(min=1, max=50)
        ]
    )

    image = FileField(
        "image",
        validators=[
            FileAllowed(["jpg", "png", "jpeg", "webp"], "jpg, png, jpeg, webp only")
        ]
    )

    category = QuerySelectField(
        "category",
        query_factory=get_categories,
        get_label="name",
        allow_blank=False
    )

    brand = QuerySelectField(
        "brand",
        query_factory=get_brands,
        get_label="name",
        allow_blank=True,
        blank_text="No Brand"
    )

    desc = TextAreaField("desc")

    price = FloatField(
        "price",
        validators=[DataRequired(), NumberRange(min=0)]
    )

    old_price = FloatField(
        "old_price",
        validators=[Optional(), NumberRange(min=0)]
    )

    cost = FloatField(
        "cost",
        validators=[Optional(), NumberRange(min=0)],
        default=None
    )

    status = SelectField(
        "status",
        choices=[
            ("true", "Active"),
            ("false", "Inactive"),
        ],
        default="true"
    )

    best_selling = BooleanField("Best Selling", default=False)

    submit = SubmitField("Submit")


class ProductFormEdit(FlaskForm):
    name = StringField(
        "product_name",
        validators=[
            DataRequired(message="Please enter Product Name"),
            Length(min=1, max=50)
        ]
    )

    image = FileField(
        "image",
        validators=[
            FileAllowed(["jpg", "png", "jpeg", "webp"], "jpg, png, jpeg, webp only")
        ]
    )

    category = QuerySelectField(
        "category",
        query_factory=get_categories,
        get_label="name",
        allow_blank=False
    )

    brand = QuerySelectField(
        "brand",
        query_factory=get_brands,
        get_label="name",
        allow_blank=True,
        blank_text="No Brand"
    )

    desc = TextAreaField("desc")

    price = FloatField(
        "price",
        validators=[DataRequired(), NumberRange(min=0)]
    )

    old_price = FloatField(
        "old_price",
        validators=[Optional(), NumberRange(min=0)]
    )

    cost = FloatField(
        "cost",
        validators=[Optional(), NumberRange(min=0)],
        default=None
    )

    status = SelectField(
        "status",
        choices=[
            ("true", "Active"),
            ("false", "Inactive"),
        ],
        default="true"
    )

    best_selling = BooleanField("Best Selling", default=False)

    submit = SubmitField("Submit")


class ProductImageAdd(FlaskForm):
    images = MultipleFileField(
        "images",
        validators=[
            FileAllowed(["jpg", "png", "jpeg", "webp"], "jpg, png, jpeg, webp only")
        ]
    )

    submit = SubmitField("Submit")