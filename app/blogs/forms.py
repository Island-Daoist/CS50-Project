from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import Blogs


class CreateBlogForm(FlaskForm):
    title = StringField('Blog Title', validators=[DataRequired()], render_kw={'autofocus': True})
    synopsis = StringField('Write a quick synopsis', validators=[DataRequired(), Length(min=0, max=200)])
    body = TextAreaField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('Post Blog!')

    def validate_title(self, title):
        blog = Blogs.query.filter_by(title=title.data).first()
        if blog is not None:
            raise ValidationError('Please choose a different title.')


class UpdateBlogForm(FlaskForm):
    title = StringField('Blog Title', validators=[DataRequired()])
    synopsis = StringField('Write a quick synopsis', validators=[DataRequired(), Length(min=0, max=200)])
    body = TextAreaField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('Update Blog!')

    def __init__(self, original_title, *args, **kwargs):
        super(UpdateBlogForm, self).__init__(*args, **kwargs)
        self.original_title = original_title

    def validate_title(self, title):
        if title.data != self.original_title:
            blog = Blogs.query.filter_by(title=title.data).first()
            if blog is not None:
                raise ValidationError('Please choose a different title.')
