from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import SelectField
from wtforms.fields.simple import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class BrandForm(FlaskForm):
    name = StringField(
        "brand_name",
        validators=[
            DataRequired(message="Please enter brand name"),
            Length(min=1, max=64)
        ]
    )

    desc = TextAreaField(
        "desc",
        validators=[
            Optional(),
            Length(max=255)
        ]
    )

    image = FileField(
        "image",
        validators=[
            FileAllowed(["jpg", "png", "jpeg", "webp"], "jpg, png, jpeg, webp only")
        ]
    )

    status = SelectField(
        "status",
        choices=[
            ("true", "Active"),
            ("false", "Inactive"),
        ],
        default="true"
    )

    submit = SubmitField("Submit")


class BrandFormEdit(BrandForm):
    pass