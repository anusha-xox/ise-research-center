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
from form_data import LoginForm

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



