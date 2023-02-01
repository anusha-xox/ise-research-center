from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL, Email
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from form_data import LoginForm, RegisterForm, CandidateForm

app = Flask(__name__)

## ADMIN ADDS PROFESSORS, INDUSTRIES, ETC.

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_BINDS'] = {'candidate': 'sqlite:///candidate.db',
                                  'admin': 'sqlite:///admin.db',
                                  'departments': 'sqlite:///departments.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


class Candidate(db.Model):
    __bind_key__ = 'candidate'
    vtu_no = db.Column(db.Integer, primary_key=True)
    c_fname = db.Column(db.String(1000), nullable=False)
    c_mname = db.Column(db.String(1000))
    c_lname = db.Column(db.String(1000))
    c_gender = db.Column(db.String(1000))
    reg_category = db.Column(db.String(1000))
    reg_day = db.Column(db.Integer, nullable=False)
    reg_month = db.Column(db.Integer, nullable=False)
    reg_year = db.Column(db.Integer, nullable=False)
    thesis_title = db.Column(db.String(1000), nullable=False)
    duration_type = db.Column(db.String(1000), nullable=False)
    c_email = db.Column(db.String(100), unique=True, nullable=False)
    c_phone = db.Column(db.Integer, unique=True, nullable=False)


db.create_all()


@app.route('/')
def home():
    return redirect(url_for('register'))


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        )
        db.session.add(new_user)
        db.session.commit()
        display_name = form.username.data
        return redirect(url_for('candidate_details', display_name=display_name))
    return render_template("enter.html", form=form, title_given="Register")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        if email == 'admin@email.com' and password == 'admin':
            return redirect(url_for('admin'))
        else:
            user = User.query.filter_by(email=email).first()
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('candidate_details', display_name=user.username))
    return render_template('enter.html', form=form, title_given="Login")


@app.route('/candidate-details', methods=['GET', 'POST'])
def candidate_details():
    display_name = request.args.get("display_name")
    form = CandidateForm()
    if form.validate_on_submit():
        new_candidate = Candidate(
            vtu_no=form.vtu_no.data,
            c_fname=form.c_fname.data,
            c_mname=form.c_mname.data,
            c_lname=form.c_lname.data,
            c_gender=form.c_gender.data,
            reg_category=form.reg_category.data,
            reg_day=form.reg_date.data,
            reg_month=form.reg_month.data,
            reg_year=form.reg_year.data,
            thesis_title=form.thesis_title.data,
            duration_type=form.duration_type.data,
            c_email=form.c_email.data,
            c_phone=form.c_phone.data
        )
        db.session.add(new_candidate)
        db.session.commit()
        return redirect(url_for('logout'))
    return render_template("add_details.html", form=form, display_name=display_name)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template("admin-home.html")


@app.route('/about')
def about():
    pass


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
