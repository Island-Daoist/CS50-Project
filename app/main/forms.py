from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import Users


class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About Me', validators=[Length(min=0, max=280)], render_kw={'autofocus': True})
    submit = SubmitField('Submit Changes')

    def __init__(self, original_username, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = Users.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class StatusForm(FlaskForm):
    status = StringField('Say Something...',
                         validators=[Length(min=1, max=120, message='Please enter something to say, but no more than 120 characters!')])
    submit = SubmitField('Share Your Thoughts')


class MessageForm(FlaskForm):
    message = TextAreaField('Type your message here...', validators=[DataRequired(), Length(min=1, max=140)], render_kw={'autofocus': True})
    submit = SubmitField('Send your Message')
