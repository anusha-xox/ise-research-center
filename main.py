from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL, Email
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from form_data import *

app = Flask(__name__)

# ADMIN ADDS PROFESSORS
# one to many bw guide and candidate

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iseResearch.db'
# app.config['SQLALCHEMY_BINDS'] = {'candidate': 'sqlite:///candidate.db',
#                                   'admin': 'sqlite:///admin.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    # posts = db.relationship("Model_name", backref="add_col_to_post_model_kinda, col won't be visible in table",
    # lazy=True)


class Candidate(db.Model):
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
    c_guide = db.Column(db.String(1000))


class Guide(db.Model):
    g_id = db.Column(db.Integer, primary_key=True)
    g_fname = db.Column(db.String(1000), nullable=False)
    g_mname = db.Column(db.String(1000))
    g_lname = db.Column(db.String(1000))
    g_designation = db.Column(db.String(1000))
    g_arcenter = db.Column(db.String(1000))
    g_email = db.Column(db.String(1000))


class ProjectDetails(db.Model):
    p_id = db.Column(db.Integer, primary_key=True)
    grant = db.Column(db.String(1000), nullable=False)
    date_of_issue = db.Column(db.String(1000), nullable=False)
    date_of_completion = db.Column(db.String(1000), nullable=False)
    project_type = db.Column(db.String(1000), nullable=False)
    funded_by = db.Column(db.String(1000), nullable=False)
    status = db.Column(db.String(1000), nullable=False)
    title = db.Column(db.String(1000), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

    # content = db.Column(db.Text, nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey("table_name.column_name"), nullable=False)

    def __repr__(self):
        return f"Added"


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
        display_email = form.email.data
        return redirect(url_for('candidate_details', display_name=display_name, c_email=display_email))
    return render_template("enter.html", form=form, title_given="Register")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if email == 'admin@email.com' and password == 'admin':
            return redirect(url_for('admin'))
        elif not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            user = User.query.filter_by(email=email).first()
            if check_password_hash(user.password, password):
                login_user(user)
                for c in Candidate.query.all():
                    if user.email == c.c_email:
                        return redirect(url_for("candidate_dashboard", vtu_no=c.vtu_no))
                for g in Guide.query.all():
                    if user.email == g.g_email:
                        return redirect(url_for("guide_dashboard", g_id=g.g_id))
                return redirect(url_for('candidate_details', display_name=user.username, c_email=user.email))
    return render_template('enter.html', form=form, title_given="Login")


@app.route('/candidate-details', methods=['GET', 'POST'])
def candidate_details():
    display_email = request.args.get("c_email")
    display_name = request.args.get("display_name")
    form = CandidateForm(
        c_email=display_email
    )
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
            c_phone=form.c_phone.data,
            c_guide=form.c_guide.data
        )
        db.session.add(new_candidate)
        db.session.commit()
        return redirect(url_for('logout'))
    return render_template("add_details.html", form=form, display_name=display_name)


@app.route("/candidate-dashboard", methods=["GET", "POST"])
def candidate_dashboard():
    vtu_no = int(request.args.get("vtu_no"))
    current_candidate = Candidate.query.get(vtu_no)
    CANDIDATE_OPTIONS = [
        "View Details",
        "Edit Profile",
        "View Current Projects",
        "View Messages from Guide",
        "Upload Documents to Guide"
    ]
    CANDIDATE_LINKS = []
    return render_template(
        "grid.html",
        title=f"{current_candidate.c_fname} {current_candidate.c_mname} {current_candidate.c_lname}",
        grid_options=CANDIDATE_OPTIONS,
        grid_links=CANDIDATE_LINKS,
        grid_no=len(CANDIDATE_OPTIONS)
    )


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    ADMIN_OPTIONS = [
        "Add Project",
        "Generate Guide Credentials",
        "Edit Student Details",
        "Edit Project",
        "Edit Guide Details",
        "View Project Details",
        "Assign Student to Project",
        "Assign Professor to Project",
        "Assign Student to Guide"
        "Share Circular To All",
        "Alumni Report",
        "View All Candidates Registered",
        "View All Users",
        "View All Faculties"
    ]
    ADMIN_LINKS = [
        url_for("add_project"),
        url_for("add_guide"),
        "",
        "",
        "",
        url_for("view_project_details"),
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        ""
    ]
    return render_template(
        "grid.html",
        title="Admin",
        grid_options=ADMIN_OPTIONS,
        grid_links=ADMIN_LINKS,
        grid_no=len(ADMIN_OPTIONS)
    )


@app.route("/guide", methods=["GET", "POST"])
def guide_dashboard():
    g_id = int(request.args.get("g_id"))
    current_guide = Guide.query.get(g_id)
    GUIDE_OPTIONS = [
        "View Details",
        "Edit Profile",
        "View Candidates Under Me",
        "View My Projects",
        "Send Message to Candidates"
    ]
    GUIDE_LINKS = [
        "",
        "",
        url_for("view_candidates_under", g_email=current_guide.g_email)
    ]
    return render_template(
        "grid.html",
        title=f"{current_guide.g_fname} {current_guide.g_mname} {current_guide.g_lname}",
        grid_options=GUIDE_OPTIONS,
        grid_links=GUIDE_LINKS,
        grid_no=len(GUIDE_OPTIONS)
    )


@app.route("/view-candidates-under")
def view_candidates_under():
    g_email = request.args.get("g_email")
    current_guide = Guide.query.filter_by(g_email=g_email).first()
    candidates = Candidate.query.filter_by(c_guide=current_guide.g_email).all()
    return render_template("view_candidates_under.html", candidates=candidates,
                           table_heading=f"Candidates Under {current_guide.g_fname}")


@app.route("/admin/generate-guide-credentials", methods=["GET", "POST"])
def add_guide():
    form = GuideForm()
    if form.validate_on_submit():
        new_guide = Guide(
            g_fname=form.g_fname.data,
            g_mname=form.g_mname.data,
            g_lname=form.g_lname.data,
            g_designation=form.g_designation.data,
            g_arcenter=form.g_arcenter.data,
            g_email=form.g_email.data
        )
        new_user = User(
            username="Admin_Generated",
            email=form.g_email.data,
            password=generate_password_hash(form.g_password.data, method='pbkdf2:sha256', salt_length=8)
        )
        db.session.add(new_guide)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template("add_details.html", form=form, display_name="Admin. Generate New Guide below.")


@app.route("/admin/add-project", methods=["GET", "POST"])
def add_project():
    form = ProjectForm()
    if form.validate_on_submit():
        new_project = ProjectDetails(
            grant=form.grant.data,
            date_of_issue=form.date_of_issue.data,
            date_of_completion=form.date_of_completion.data,
            project_type=form.project_type.data,
            funded_by=form.funded_by.data,
            status=form.status.data,
            title=form.title.data,
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template("add_details.html", form=form, display_name="Admin. Enter Project Details below.")


@app.route("/view-project-details", methods=["GET", "POST"])
def view_project_details():
    all_projects = ProjectDetails.query.order_by("date_of_issue").all()
    return render_template("view_project_details.html", all_projects=all_projects, table_heading="All Projects")


@app.route('/about')
def about():
    pass


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
