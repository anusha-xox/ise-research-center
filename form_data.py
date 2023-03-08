from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, URL
from flask_bootstrap import Bootstrap
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError
from main import ProjectDetails, Guide, ckeditor
from flask_ckeditor import CKEditor, CKEditorField

REG_CATEGORY = ["GM", "SC", "ST", "Physically Handicapped", "Other"]
GENDER = ["Male", "Female", "Non-Binary", "Other", "Prefer not to say"]
DURATION_TYPE = ["Full Time", "Part Time"]
DESIGNATION = ["Assistant Professor", "Associate Professor", "Professor", "HOD"]
ASSO_RC = ["CSE", "ISE"]
PROJECT_STATUS = ["Completed", "Ongoing"]
PROJECT_TYPE = ["Research", "Consultancy"]
THESIS_PHASES = ["Comprehensive Viva", "Coursework Completion", "Degree Certification", "Open Seminar - 1",
                 "Open Seminar - 2", "Thesis Submission", "Vivavoce"]


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
    reg_date = DateField('Registration Date', format='%Y-%m-%d')
    thesis_title = StringField('Title of Thesis', validators=[DataRequired()])
    duration_type = SelectField('Duration Type', choices=DURATION_TYPE, validators=[DataRequired()])
    c_email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'readonly': True})
    c_phone = StringField('Phone No.', validators=[DataRequired()])
    c_drive_link = StringField("Drive Link for Thesis", validators=[DataRequired(), URL()])
    submit = SubmitField(label='Submit')

    def validate_reg_date(form, field):
        pass


class CandidateEditForm(FlaskForm):
    c_fname = StringField('First Name', validators=[DataRequired()])
    c_mname = StringField('Middle Name')
    c_lname = StringField('Last Name')
    c_gender = SelectField('Gender', choices=GENDER, validators=[DataRequired()])
    reg_category = SelectField('Department Name', choices=REG_CATEGORY, validators=[DataRequired()])
    thesis_title = StringField('Title of Thesis', validators=[DataRequired()])
    duration_type = SelectField('Duration Type', choices=DURATION_TYPE, validators=[DataRequired()])
    c_email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'readonly': True})
    c_phone = StringField('Phone No.', validators=[DataRequired()])
    c_drive_link = StringField("Drive Link for Thesis", validators=[DataRequired(), URL()])
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

class GuideEditForm(FlaskForm):
    g_fname = StringField('First Name', validators=[DataRequired()])
    g_mname = StringField('Middle Name')
    g_lname = StringField('Last Name')
    g_designation = SelectField('Designation', choices=DESIGNATION, validators=[DataRequired()])
    g_arcenter = SelectField('Associated Research Center', choices=ASSO_RC, validators=[DataRequired()])
    g_email = StringField('Email ID', validators=[DataRequired(), Email()], render_kw={'readonly': True})
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


class AssignGuide(FlaskForm):
    vtu_no = StringField('VTU Registration Number Of Candidate', validators=[DataRequired()])
    c_g_email = SelectField("Choose Guide")
    submit = SubmitField(label='Assign')

    def __init__(self, *args, **kwargs):
        super(AssignGuide, self).__init__(*args, **kwargs)
        self.c_g_email.choices = [c.g_email for c in Guide.query.all()]


class UpdatePhdStatus(FlaskForm):
    vtu_no = StringField('VTU Registration Number Of Candidate', validators=[DataRequired()],
                         render_kw={'readonly': True})
    full_name = StringField('Full Name', validators=[DataRequired()], render_kw={'readonly': True})
    thesis_phase = SelectField('Current Phase of Thesis', choices=THESIS_PHASES, validators=[DataRequired()])
    submit = SubmitField(label='Submit')


class MessageForm(FlaskForm):
    subject = StringField("Subject", validators=[DataRequired()])
    date = StringField(label='Date and Time', validators=[DataRequired()], render_kw={'readonly': True})
    body = CKEditorField("Message Content", validators=[DataRequired()])
    author_email = StringField(label='Email', validators=[DataRequired(), Email()], render_kw={'readonly': True})
    submit = SubmitField(label='Send Message To All')


class CandidateToProject(FlaskForm):
    vtu_no = StringField('VTU Registration Number Of Candidate', validators=[DataRequired()])
    c_p_id = SelectField("Choose Project")
    submit = SubmitField(label='Assign')

    def __init__(self, *args, **kwargs):
        super(CandidateToProject, self).__init__(*args, **kwargs)
        self.c_p_id.choices = [f"{c.p_id} ~ {c.title}" for c in ProjectDetails.query.all()]


class GuideToProject(FlaskForm):
    c_g_email = SelectField("Choose Guide")
    g_p_id = SelectField("Choose Project")
    submit = SubmitField(label='Assign')

    def __init__(self, *args, **kwargs):
        super(GuideToProject, self).__init__(*args, **kwargs)
        self.c_g_email.choices = [c.g_email for c in Guide.query.all()]
        self.g_p_id.choices = [f"{c.p_id} ~ {c.title}" for c in ProjectDetails.query.all()]
