from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField
from wtforms.validators import DataRequired


class AddBookForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    book_author = StringField('Автор', validators=[DataRequired()])
    genre = SelectField('Жанр', coerce=int)
    submit = SubmitField('Сохранить')
