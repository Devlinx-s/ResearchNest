from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from models import Department

class UploadPaperForm(FlaskForm):
    file = FileField('PDF File', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'Only PDF files are allowed!')
    ])
    title = StringField('Title', validators=[Length(max=255)])
    authors = StringField('Authors', validators=[Length(max=500)])
    abstract = TextAreaField('Abstract')
    keywords = StringField('Keywords (comma-separated)', validators=[Length(max=500)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    publication_year = IntegerField('Publication Year', validators=[
        NumberRange(min=1900, max=2030, message="Year must be between 1900 and 2030")
    ])
    submit = SubmitField('Upload Paper')
    
    def __init__(self, *args, **kwargs):
        super(UploadPaperForm, self).__init__(*args, **kwargs)
        self.department_id.choices = [(d.id, d.name) for d in Department.query.all()]

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Length(max=255)])
    department_id = SelectField('Department', coerce=int)
    year_from = IntegerField('Year From', validators=[NumberRange(min=1900, max=2030)])
    year_to = IntegerField('Year To', validators=[NumberRange(min=1900, max=2030)])
    keywords = StringField('Keywords')
    submit = SubmitField('Search')
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        choices = [(0, 'All Departments')] + [(d.id, d.name) for d in Department.query.all()]
        self.department_id.choices = choices

class UserProfileForm(FlaskForm):
    department = StringField('Department', validators=[Length(max=100)])
    year = IntegerField('Year', validators=[NumberRange(min=1, max=6)])
    submit = SubmitField('Update Profile')
