from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Users


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'autofocus': True})
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'autofocus': True})
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResetPasswordRequest(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'autofocus': True})
    submit = SubmitField('Request Password Reset')


class ResetPassword(FlaskForm):
    password_1 = PasswordField('Password', validators=[DataRequired()], render_kw={'autofocus': True})
    password_2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password_1')])
    submit = SubmitField('Change your Password')


class ValidateUser(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'autofocus': True})
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Validate')
