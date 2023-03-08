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
from flask_ckeditor import CKEditor, CKEditorField
from form_data import *

app = Flask(__name__)

# ADMIN ADDS PROFESSORS
# one to many bw guide and candidate

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iseResearch.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['CKEDITOR_PKG_TYPE'] = 'full-all'
ckeditor = CKEditor(app)

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
    reg_date = db.Column(db.String(1000), nullable=False)
    thesis_title = db.Column(db.String(1000), nullable=False)
    duration_type = db.Column(db.String(1000), nullable=False)
    c_email = db.Column(db.String(100), unique=True, nullable=False)
    c_phone = db.Column(db.Integer, unique=True, nullable=False)
    thesis_phase = db.Column(db.String(1000))

    c_p_id = db.Column(db.Integer, unique=False, nullable=True)
    c_g_id = db.Column(db.Integer, unique=False, nullable=True)


class Guide(db.Model):
    g_id = db.Column(db.Integer, primary_key=True)
    g_fname = db.Column(db.String(1000), nullable=False)
    g_mname = db.Column(db.String(1000))
    g_lname = db.Column(db.String(1000))
    g_designation = db.Column(db.String(1000))
    g_arcenter = db.Column(db.String(1000))
    g_email = db.Column(db.String(1000))

    g_p_id = db.Column(db.Integer, unique=False, nullable=True)


class ProjectDetails(db.Model):
    p_id = db.Column(db.Integer, primary_key=True)
    grant = db.Column(db.String(1000), nullable=False)
    date_of_issue = db.Column(db.String(1000), nullable=False)
    date_of_completion = db.Column(db.String(1000), nullable=False)
    project_type = db.Column(db.String(1000), nullable=False)
    funded_by = db.Column(db.String(1000), nullable=False)
    status = db.Column(db.String(1000), nullable=False)
    title = db.Column(db.String(1000), nullable=False)


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author_email = db.Column(db.String(250), nullable=False)


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
            reg_date=form.reg_date.data,
            thesis_title=form.thesis_title.data,
            duration_type=form.duration_type.data,
            c_email=form.c_email.data,
            c_phone=form.c_phone.data,
            # c_guide=form.c_guide.data
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
    CANDIDATE_LINKS = [
        url_for("view_details_candidate", vtu_no=vtu_no),
        url_for("edit_candidate_profile", vtu_no=vtu_no),
        url_for("view_current_projects", vtu_no=vtu_no),
        url_for("view_messages", vtu_no=vtu_no)
    ]
    return render_template(
        "grid.html",
        title=f"{current_candidate.c_fname} {current_candidate.c_mname} {current_candidate.c_lname}",
        grid_options=CANDIDATE_OPTIONS,
        grid_links=CANDIDATE_LINKS,
        grid_no=len(CANDIDATE_OPTIONS)
    )

@app.route("/view-current-projects")
def view_current_projects():
    vtu_no = int(request.args.get("vtu_no"))
    current_candidate = Candidate.query.get(vtu_no)
    return render_template("view_current_projects.html", messages=messages,
                           table_heading=f"{current_candidate.c_fname} {current_candidate.c_mname} {current_candidate.c_lname}'s Messages from Guide")


@app.route("/view-messages")
def view_messages():
    vtu_no = int(request.args.get("vtu_no"))
    current_candidate = Candidate.query.get(vtu_no)
    current_guide = Guide.query.get(current_candidate.c_g_id)
    guide_email = current_guide.g_email
    messages = Messages.query.filter_by(author_email=guide_email).all()
    return render_template("view_messages.html", messages=messages,
                           table_heading=f"{current_candidate.c_fname} {current_candidate.c_mname} {current_candidate.c_lname}'s Messages from Guide")


@app.route("/view-details-candidate")
def view_details_candidate():
    vtu_no = int(request.args.get("vtu_no"))
    current_candidate = Candidate.query.get(vtu_no)
    return render_template("view_details_candidate.html", c=current_candidate,
                           table_heading=f"{current_candidate.c_fname} {current_candidate.c_mname} {current_candidate.c_lname}'s Entered Details")


@app.route("/edit-candidate-profile", methods=["GET", "POST"])
def edit_candidate_profile():
    vtu_no = int(request.args.get("vtu_no"))
    current_candidate = Candidate.query.get(vtu_no)
    if current_candidate:
        form = CandidateEditForm(
            c_fname=current_candidate.c_fname,
            c_mname=current_candidate.c_mname,
            c_lname=current_candidate.c_lname,
            c_gender=current_candidate.c_gender,
            reg_category=current_candidate.reg_category,
            thesis_title=current_candidate.thesis_title,
            duration_type=current_candidate.duration_type,
            c_email=current_candidate.c_email,
            c_phone=current_candidate.c_phone
        )
        if form.validate_on_submit():
            current_candidate.c_fname = form.c_fname.data
            current_candidate.c_mname = form.c_mname.data
            current_candidate.c_lname = form.c_lname.data
            current_candidate.c_gender = form.c_gender.data
            current_candidate.reg_category = form.reg_category.data
            current_candidate.thesis_title = form.thesis_title.data
            current_candidate.duration_type = form.duration_type.data
            current_candidate.c_email = form.c_email.data
            current_candidate.c_phone = form.c_phone.data
            db.session.commit()
            return redirect(url_for("candidate_dashboard", vtu_no=vtu_no))
        return render_template("add_details.html", form=form,
                               display_name=f"{current_candidate.c_fname} {current_candidate.c_mname} {current_candidate.c_lname}")


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    ADMIN_OPTIONS = [
        "Add Project",
        "Generate Guide Credentials",
        "View Project Details",
        "Assign Candidate to Project",
        "Assign Guide to Project",
        "Assign Student to Guide",
        "Export Report To Excel",
        "View All Candidates Registered",
        "View All Faculties"
    ]
    ADMIN_LINKS = [
        url_for("add_project"),
        url_for("add_guide"),
        url_for("view_project_details"),
        url_for("candidate_to_project"),
        url_for("guide_to_project"),
        url_for("assign_guide"),
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


@app.route("/admin/edit-project", methods=["GET", "POST"])
def edit_project():
    p_id = int(request.args.get("p_id"))
    current_project = ProjectDetails.query.get(p_id)
    if current_project:
        form = ProjectForm(
            grant=current_project.grant,
            # date_of_issue=datetime.datetime(current_project.date_of_issue),
            # date_of_completion=datetime.datetime(current_project.date_of_completion),
            project_type=current_project.project_type,
            funded_by=current_project.funded_by,
            status=current_project.status,
            title=current_project.title,
        )
        if form.validate_on_submit():
            current_project.grant = int(form.grant.data),
            # current_project.date_of_issue = form.date_of_issue.data,
            # current_project.date_of_completion = form.date_of_completion.data,
            current_project.project_type = form.project_type.data,
            current_project.funded_by = form.funded_by.data,
            current_project.status = form.status.data,
            current_project.title = form.title.data,
            db.session.commit()
            return redirect(url_for('admin'))
        return render_template("add_details.html", form=form, display_name="Admin. Edit Project Details below.")


@app.route("/admin/delete-project", methods=["GET", "POST"])
def delete_project():
    p_id = int(request.args.get("p_id"))
    for c in Candidate.query.filter_by(c_p_id=p_id).all():
        c.c_p_id = 0
    for g in Guide.query.filter_by(g_p_id=p_id).all():
        g.g_p_id = 0
    current_project = ProjectDetails.query.get(p_id)
    db.session.delete(current_project)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route("/admin/candidate-to-project", methods=["GET", "POST"])
def candidate_to_project():
    form = CandidateToProject()
    if form.validate_on_submit():
        current_candidate = Candidate.query.get(form.vtu_no.data)
        current_candidate.c_p_id = int(form.c_p_id.data.split(" ~ ")[0])
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template("add_details.html", form=form, display_name="Admin. Assign Candidate to Project.")


@app.route("/admin/guide-to-project", methods=["GET", "POST"])
def guide_to_project():
    form = GuideToProject()
    if form.validate_on_submit():
        current_guide = Guide.query.filter_by(g_email=form.c_g_email.data).first()
        current_guide.g_p_id = int(form.g_p_id.data.split(" ~ ")[0])
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template("add_details.html", form=form, display_name="Admin. Assign Guide to Project.")


@app.route("/admin/assign-guide", methods=["GET", "POST"])
def assign_guide():
    form = AssignGuide()
    if form.validate_on_submit():
        current_candidate = Candidate.query.get(form.vtu_no.data)
        current_guide = Guide.query.filter_by(g_email=form.c_g_email.data).first()
        current_candidate.c_g_id = current_guide.g_id
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template("add_details.html", form=form, display_name="Admin. Assign Candidate to Guide.")


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
        url_for("view_candidates_under", g_id=g_id),
        "",
        url_for("add_messages", email=current_guide.g_email)
    ]
    return render_template(
        "grid.html",
        title=f"{current_guide.g_fname} {current_guide.g_mname} {current_guide.g_lname}",
        grid_options=GUIDE_OPTIONS,
        grid_links=GUIDE_LINKS,
        grid_no=len(GUIDE_OPTIONS)
    )


@app.route("/update-thesis-status", methods=["GET", "POST"])
def update_thesis_status():
    vtu_no = int(request.args.get("vtu_no"))
    current_candidate = Candidate.query.get(vtu_no)
    current_guide = Guide.query.get(current_candidate.c_g_id)
    form = UpdatePhdStatus(
        vtu_no=vtu_no,
        full_name=f"{current_candidate.c_fname} {current_candidate.c_mname} {current_candidate.c_lname}"
    )
    if form.validate_on_submit():
        current_candidate.thesis_phase = form.thesis_phase.data
        db.session.commit()
        return redirect(url_for("guide_dashboard", g_id=current_guide.g_id))
    return render_template("add_details.html", form=form,
                           display_name=f"{current_guide.g_fname} {current_guide.g_mname} {current_guide.g_lname}")


@app.route("/add-messages", methods=["GET", "POST"])
def add_messages():
    author_email = request.args.get("email")
    current_guide = Guide.query.filter_by(g_email=author_email).first()
    form = MessageForm(
        author_email=author_email,
        date=datetime.datetime.now(),
    )
    if form.validate_on_submit():
        new_message = Messages(
            subject=form.subject.data,
            date=form.date.data,
            body=form.body.data,
            author_email=form.author_email.data
        )
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for("guide_dashboard", g_id=current_guide.g_id))
    return render_template("add_details.html", form=form,
                           display_name=f"{current_guide.g_fname} {current_guide.g_mname} {current_guide.g_lname}")


@app.route("/view-candidates-under")
def view_candidates_under():
    g_id = int(request.args.get("g_id"))
    current_guide = Guide.query.get(g_id)
    candidates = Candidate.query.filter_by(c_g_id=g_id).all()
    if candidates:
        return render_template("view_candidates_under.html", candidates=candidates,
                               table_heading=f"Candidates Under {current_guide.g_fname}")
    return redirect(url_for("guide_dashboard", g_id=current_guide.g_id))


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
