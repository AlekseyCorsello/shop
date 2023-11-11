from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import TextAreaField
from wtforms import SubmitField
from wtforms import EmailField
from wtforms import PasswordField
from wtforms import RadioField
from wtforms import IntegerField
from wtforms import FloatField

from wtforms.validators import InputRequired
from wtforms.validators import Email
from wtforms.validators import Length

class LoginForm(FlaskForm):
    email = EmailField('E-mail', validators=[InputRequired(), Email(), Length(max=50)])
    password = PasswordField('Пароль', validators=[InputRequired(), Length(min=5, max=30)])
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    first_name = StringField('Имя', validators=[InputRequired(), Length(max=20)])
    last_name = StringField('Фамилия', validators=[InputRequired(), Length(max=20)])
    password = PasswordField('Пароль', validators=[InputRequired(), Length(min=5, max=30)])
    email = EmailField('E-mail', validators=[InputRequired(), Email(), Length(max=50)])
    submit = SubmitField('Зарегистрироваться')

class FilterForm(FlaskForm):
    category = RadioField('Категория')
    price_from = FloatField('Цена от')
    price_up_to = FloatField('Цена до')
    submit = SubmitField('Найти')

class ProfileForm(FlaskForm):
    first_name = StringField('Имя', validators=[InputRequired(), Length(max=20)])
    last_name = StringField('Фамилия', validators=[InputRequired(), Length(max=20)])
    password = PasswordField('Пароль', validators=[InputRequired(), Length(min=5, max=30)])
    new_password = PasswordField('Новый пароль', validators=[InputRequired(), Length(min=5, max=30)])
    save = SubmitField('Сохранить')

class ProductForm(FlaskForm):
    name = StringField('Название', validators=[InputRequired(), Length(max=200)])
    photo = StringField('Картинка', validators=[InputRequired()])
    category = StringField('Категория', validators=[InputRequired(), Length(max=20)])
    price = FloatField('Цена', validators=[InputRequired()])
    description = TextAreaField('Описание', validators=[InputRequired()])
    save = SubmitField('Сохранить')