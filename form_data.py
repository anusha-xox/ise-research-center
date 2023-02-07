from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length
from flask_bootstrap import Bootstrap
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError
from main import Guide

REG_CATEGORY = ["GM", "SC", "ST", "Physically Handicapped", "Other"]
GENDER = ["Male", "Female", "Non-Binary", "Other", "Prefer not to say"]
DURATION_TYPE = ["Full Time", "Part Time"]
DESIGNATION = ["Assistant Professor", "Associate Professor", "Professor", "HOD"]
ASSO_RC = ["CSE", "ISE"]
PROJECT_STATUS = ["Completed", "Ongoing"]
PROJECT_TYPE = ["Research", "Consultancy"]


class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Login')


class RegisterForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Register')


class CandidateForm(FlaskForm):
    vtu_no = StringField('VTU Registration Number', validators=[DataRequired()])
    c_fname = StringField('First Name', validators=[DataRequired()])
    c_mname = StringField('Middle Name')
    c_lname = StringField('Last Name')
    c_gender = SelectField('Gender', choices=GENDER, validators=[DataRequired()])
    reg_category = SelectField('Department Name', choices=REG_CATEGORY, validators=[DataRequired()])
    reg_date = StringField('Date of Registration', validators=[DataRequired()])
    reg_month = StringField('Month of Registration', validators=[DataRequired()])
    reg_year = StringField('Year of Registration', validators=[DataRequired()])
    thesis_title = StringField('Title of Thesis', validators=[DataRequired()])
    duration_type = SelectField('Duration Type', choices=DURATION_TYPE, validators=[DataRequired()])
    c_email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'readonly': True})
    c_phone = StringField('Phone No.', validators=[DataRequired()])
    c_guide = SelectField("Choose Guide")

    def __init__(self, *args, **kwargs):
        super(CandidateForm, self).__init__(*args, **kwargs)
        self.c_guide.choices = [c.g_email for c in Guide.query.all()]

    submit = SubmitField(label='Submit')


class GuideForm(FlaskForm):
    g_fname = StringField('First Name', validators=[DataRequired()])
    g_mname = StringField('Middle Name')
    g_lname = StringField('Last Name')
    g_designation = SelectField('Designation', choices=DESIGNATION, validators=[DataRequired()])
    g_arcenter = SelectField('Associated Research Center', choices=ASSO_RC, validators=[DataRequired()])
    g_email = StringField('Email ID', validators=[DataRequired(), Email()])
    g_password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


class ProjectForm(FlaskForm):
    grant = StringField('Grand Received', validators=[DataRequired()])
    date_of_issue = DateField('Date of Issue', format='%Y-%m-%d')
    date_of_completion = DateField('Date Of Completion', format='%Y-%m-%d')
    project_type = SelectField("Project Type", choices=PROJECT_TYPE, validators=[DataRequired()])
    funded_by = StringField("Funded By", validators=[DataRequired()])
    status = SelectField('Project Status', choices=PROJECT_STATUS, validators=[DataRequired()])
    title = StringField("Title Given", validators=[DataRequired()])
    submit = SubmitField(label='Submit')

    def validate_date_of_completion(form, field):
        if field.data is None:
            pass
        elif field.data < form.date_of_issue.data:
            raise ValidationError("End date must not be earlier than start date.")
