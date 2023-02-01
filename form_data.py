from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length
from flask_bootstrap import Bootstrap
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator

REG_CATEGORY = ["GM", "SC", "ST", "Physically Handicapped", "Other"]
GENDER = ["Male", "Female", "Non-Binary", "Other", "Prefer not to say"]
DURATION_TYPE = ["Full Time", "Part Time"]


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
    __bind_key__ = 'candidate'
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
    c_email = StringField('Email', validators=[DataRequired(), Email()])
    c_phone = db.Column(db.Integer, unique=True, nullable=False)
