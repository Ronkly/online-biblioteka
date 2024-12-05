from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, FileField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileRequired


class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author_name = StringField('Autor', validators=[DataRequired()])
    description = TextAreaField('Opis')
    year = IntegerField('Godina izdanja', validators=[DataRequired()])
    grade = FloatField('Razred', validators=[DataRequired()])
    file = FileField('Upload', validators=[FileRequired()])
    submit = SubmitField('Submit')
