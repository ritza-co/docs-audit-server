from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, url


class CreateUrlForm(FlaskForm):
  url = URLField('url', validators=[DataRequired(), url(message='url not valid')], render_kw={"placeholder": "https://docs.example.com/getting-started"} )

