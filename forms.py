from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField, PasswordField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Length, Email, NumberRange, EqualTo
from models import Department, Subject, Unit, Topic, QuestionDocument


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Length(max=50)])
    department = StringField('Department', validators=[Length(max=100)])
    year = IntegerField('Year', validators=[NumberRange(min=1, max=6)])
    submit = SubmitField('Sign Up')


class UploadPaperForm(FlaskForm):
    file = FileField('PDF File', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'Only PDF files are allowed!')
    ], render_kw={'multiple': True})
    is_bulk_upload = SelectField('Upload Type', choices=[
        (False, 'Single Paper'),
        (True, 'Bulk Upload')
    ], default=False, coerce=bool)
    title = StringField('Title', validators=[Length(max=255)], 
                       render_kw={'placeholder': 'Will be extracted from PDF if left blank'})
    authors = StringField('Authors', validators=[Length(max=500)],
                         render_kw={'placeholder': 'Will be extracted from PDF if available'})
    abstract = TextAreaField('Abstract', 
                           render_kw={'placeholder': 'Will be extracted from PDF if available'})
    keywords = StringField('Keywords (comma-separated)', validators=[Length(max=500)],
                          render_kw={'placeholder': 'Will be extracted from abstract if left blank'})
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    publication_year = IntegerField('Publication Year', validators=[
        NumberRange(min=1900, max=2030, message="Year must be between 1900 and 2030")
    ], default=lambda: datetime.now().year)
    submit = SubmitField('Upload Paper(s)')
    
    def __init__(self, *args, **kwargs):
        super(UploadPaperForm, self).__init__(*args, **kwargs)
        self.department_id.choices = [(dept.id, dept.name) for dept in Department.query.all()]


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Length(max=255)])
    department_id = SelectField('Department', coerce=int)
    year_from = IntegerField('Year From', validators=[NumberRange(min=1900, max=2030)])
    year_to = IntegerField('Year To', validators=[NumberRange(min=1900, max=2030)])
    keywords = StringField('Keywords')
    submit = SubmitField('Search')
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        choices = [(0, 'All Departments')] + [(dept.id, dept.name) for dept in Department.query.all()]
        self.department_id.choices = choices


class UserProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Length(max=50)])
    department = StringField('Department', validators=[Length(max=100)])
    year = IntegerField('Year', validators=[NumberRange(min=1, max=6)])
    submit = SubmitField('Update Profile')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

class UploadQuestionDocumentForm(FlaskForm):
    file = FileField('PDF File', validators=[
        FileRequired(),
        FileAllowed(['pdf'], 'Only PDF files are allowed!')
    ])
    title = StringField('Document Title', validators=[DataRequired(), Length(max=255)])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    document_type = SelectField('Document Type', choices=[
        ('question_paper', 'Question Paper'),
        ('assignment', 'Assignment'),
        ('quiz', 'Quiz'),
        ('practice_test', 'Practice Test')
    ], validators=[DataRequired()])
    academic_year = StringField('Academic Year', validators=[Length(max=20)])
    semester = SelectField('Semester', choices=[
        ('', 'Select Semester'),
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('3', 'Semester 3'),
        ('4', 'Semester 4'),
        ('5', 'Semester 5'),
        ('6', 'Semester 6'),
        ('7', 'Semester 7'),
        ('8', 'Semester 8')
    ])
    submit = SubmitField('Upload Question Document')
    
    def __init__(self, *args, **kwargs):
        super(UploadQuestionDocumentForm, self).__init__(*args, **kwargs)
        from models import Subject
        self.subject_id.choices = [(0, 'Select Subject')] + [(subj.id, f"{subj.code} - {subj.name}") for subj in Subject.query.all()]

class GenerateQuestionPaperForm(FlaskForm):
    title = StringField('Paper Title', validators=[DataRequired(), Length(max=255)])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    unit_ids = SelectMultipleField('Units', coerce=int)
    topic_ids = SelectMultipleField('Topics (Optional)', coerce=int)
    total_marks = IntegerField('Total Marks', validators=[DataRequired(), NumberRange(min=10, max=200)], default=100)
    duration_minutes = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=30, max=300)], default=180)
    
    # Difficulty distribution
    easy_percentage = IntegerField('Easy Questions (%)', validators=[NumberRange(min=0, max=100)], default=30)
    medium_percentage = IntegerField('Medium Questions (%)', validators=[NumberRange(min=0, max=100)], default=50)
    hard_percentage = IntegerField('Hard Questions (%)', validators=[NumberRange(min=0, max=100)], default=20)
    
    submit = SubmitField('Generate Question Paper')
    
    def __init__(self, *args, **kwargs):
        super(GenerateQuestionPaperForm, self).__init__(*args, **kwargs)
        from models import Subject, Unit, Topic
        self.subject_id.choices = [(0, 'Select Subject')] + [(subj.id, f"{subj.code} - {subj.name}") for subj in Subject.query.all()]
        self.unit_ids.choices = [(unit.id, unit.name) for unit in Unit.query.all()]
        self.topic_ids.choices = [(topic.id, topic.name) for topic in Topic.query.all()]
    
    def validate(self, extra_validators=None):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        
        # Check that percentages add up to 100
        total_percentage = (self.easy_percentage.data or 0) + (self.medium_percentage.data or 0) + (self.hard_percentage.data or 0)
        if total_percentage != 100:
            self.easy_percentage.errors.append('Difficulty percentages must add up to 100%')
            return False
        
        return True

class SubjectManagementForm(FlaskForm):
    name = StringField('Subject Name', validators=[DataRequired(), Length(max=100)])
    code = StringField('Subject Code', validators=[DataRequired(), Length(max=20)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Subject')
    
    def __init__(self, *args, **kwargs):
        super(SubjectManagementForm, self).__init__(*args, **kwargs)
        from models import Department
        self.department_id.choices = [(dept.id, dept.name) for dept in Department.query.all()]

class UnitManagementForm(FlaskForm):
    name = StringField('Unit Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    order_index = IntegerField('Order', validators=[NumberRange(min=1)], default=1)
    submit = SubmitField('Add Unit')
    
    def __init__(self, *args, **kwargs):
        super(UnitManagementForm, self).__init__(*args, **kwargs)
        from models import Subject
        self.subject_id.choices = [(subj.id, f"{subj.code} - {subj.name}") for subj in Subject.query.all()]

class TopicManagementForm(FlaskForm):
    name = StringField('Topic Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    unit_id = SelectField('Unit', coerce=int, validators=[DataRequired()])
    difficulty_level = SelectField('Difficulty Level', choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ], default='medium')
    submit = SubmitField('Add Topic')
    
    def __init__(self, *args, **kwargs):
        super(TopicManagementForm, self).__init__(*args, **kwargs)
        from models import Unit
        self.unit_id.choices = [(unit.id, f"{unit.subject.code} - {unit.name}") for unit in Unit.query.all()]


class ManualQuestionForm(FlaskForm):
    """Form for manually adding questions to units and topics."""
    question_text = TextAreaField('Question Text', validators=[DataRequired()], 
                                render_kw={'rows': 4, 'placeholder': 'Enter the question text here...'})
    question_type = SelectField('Question Type', choices=[
        ('text', 'Text'),
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('problem_solving', 'Problem Solving')
    ], default='text')
    difficulty_level = SelectField('Difficulty Level', choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ], default='medium')
    marks = IntegerField('Marks', validators=[NumberRange(min=1, max=20)], default=1)
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    unit_id = SelectField('Unit', coerce=int, validators=[DataRequired()])
    topic_id = SelectField('Topic (Optional)', coerce=int)
    has_formula = BooleanField('Contains Formulas/Math')
    has_image = BooleanField('Has Image')
    image_path = StringField('Image Path (if any)', validators=[Length(max=255)])
    document_id = SelectField('Document (Optional)', coerce=int)
    page_number = IntegerField('Page Number (if from document)', validators=[NumberRange(min=1)])
    question_number = StringField('Question Number (if from document)', validators=[Length(max=10)])
    submit = SubmitField('Add Question')
    
    def __init__(self, *args, **kwargs):
        super(ManualQuestionForm, self).__init__(*args, **kwargs)
        # Set up dynamic choices
        self.subject_id.choices = [(0, 'Select Subject')] + [(subj.id, f"{subj.code} - {subj.name}") for subj in Subject.query.all()]
        self.unit_id.choices = [(0, 'Select Unit')] + [(unit.id, unit.name) for unit in Unit.query.all()]
        self.topic_id.choices = [(0, 'Select Topic (Optional)')] + [(topic.id, topic.name) for topic in Topic.query.all()]
        self.document_id.choices = [(0, 'None')] + [(doc.id, doc.title) for doc in QuestionDocument.query.all()]
    
    def validate(self, extra_validators=None):
        if not super().validate():
            return False
            
        # If has_image is True, image_path is required
        if self.has_image.data and not self.image_path.data:
            self.image_path.errors.append('Image path is required when "Has Image" is checked')
            return False
            
        return True