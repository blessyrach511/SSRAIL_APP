from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = "ssrailworks_secure_key_2026"

# ======================
# DATABASE CONFIG
# ======================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///railway.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ======================
# GOOGLE LOGIN
# ======================

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)

# ======================
# DATABASE TABLES
# ======================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(100), nullable=True)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    department = db.Column(db.String(100))
    status = db.Column(db.String(50))
    progress = db.Column(db.Integer)
    description = db.Column(db.Text)


# ======================
# HOME PAGE
# ======================

@app.route("/")
def home():
    return render_template("home.html")


# ======================
# REGISTER
# ======================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        password = request.form["password"]

        existing = User.query.filter_by(email=email).first()

        if existing:
            flash("Email already registered.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            fullname=fullname,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


# ======================
# LOGIN
# ======================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user"] = user.fullname
            session["email"] = user.email
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


# ======================
# GOOGLE LOGIN
# ======================

@app.route("/google-login")
def google_login():
    redirect_uri = url_for("authorize", _external=True)
    return google.authorize_redirect(redirect_uri)

# ======================
# FORGOT PASSWORD
# ======================

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]

        user = User.query.filter_by(email=email).first()

        if user:
            return redirect(url_for("reset_password", email=email))
        else:
            flash("Email not found.")
            return redirect(url_for("forgot_password"))

    return render_template("forgot_password.html")


# ======================
# RESET PASSWORD
# ======================

@app.route("/reset-password/<email>", methods=["GET", "POST"])
def reset_password(email):

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("Invalid reset request.")
        return redirect(url_for("login"))

    if request.method == "POST":

        new_password = request.form["password"]

        user.password = generate_password_hash(new_password)

        db.session.commit()

        flash("Password updated successfully. Please login.")
        return redirect(url_for("login"))

    return render_template("reset_password.html", email=email)

@app.route("/authorize")
def authorize():

    token = google.authorize_access_token()
    user_info = token["userinfo"]

    email = user_info["email"]
    fullname = user_info["name"]

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            fullname=fullname,
            email=email,
            password=None
        )
        db.session.add(user)
        db.session.commit()

    session["user"] = fullname
    session["email"] = email

    return redirect(url_for("dashboard"))


# ======================
# DASHBOARD
# ======================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    total = Project.query.count()
    completed = Project.query.filter_by(status="Completed").count()
    inprogress = Project.query.filter_by(status="In Progress").count()
    delayed = Project.query.filter_by(status="Delayed").count()

    return render_template(
        "dashboard.html",
        username=session["user"],
        email=session["email"],
        total=total,
        completed=completed,
        progress=inprogress,
        delayed=delayed
    )


# ======================
# PROJECTS PAGE
# ======================

@app.route("/projects")
def projects():

    if "user" not in session:
        return redirect(url_for("login"))

    all_projects = Project.query.order_by(Project.id.desc()).all()

    return render_template(
        "projects.html",
        projects=all_projects,
        username=session["user"]
    )


# ======================
# PROJECT DETAILS
# ======================

@app.route("/project/<int:id>")
def project_details(id):

    if "user" not in session:
        return redirect(url_for("login"))

    project = Project.query.get(id)

    if not project:
        flash("Project not found.")
        return redirect(url_for("projects"))

    return render_template(
        "project_details.html",
        project=project,
        username=session["user"]
    )


# ======================
# ADD PROJECT
# ======================

@app.route("/add-project", methods=["GET", "POST"])
def add_project():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        project = Project(
            name=request.form["name"],
            department=request.form["department"],
            status=request.form["status"],
            progress=int(request.form["progress"]),
            description=request.form["description"]
        )

        db.session.add(project)
        db.session.commit()

        flash("Project added successfully.")
        return redirect(url_for("projects"))

    return render_template("add_project.html")


# ======================
# EDIT PROJECT
# ======================

@app.route("/edit-project/<int:id>", methods=["GET", "POST"])
def edit_project(id):

    if "user" not in session:
        return redirect(url_for("login"))

    project = db.session.get(Project, id)

    if not project:
        flash("Project not found.")
        return redirect(url_for("projects"))

    if request.method == "POST":

        project.name = request.form["name"]
        project.department = request.form["department"]
        project.status = request.form["status"]
        project.progress = int(request.form["progress"])
        project.description = request.form["description"]

        db.session.commit()

        flash("Project updated successfully.")
        return redirect(url_for("projects"))

    return render_template(
        "edit_project.html",
        project=project
    )


# ======================
# DELETE PROJECT
# ======================

@app.route("/delete-project/<int:id>")
def delete_project(id):

    if "user" not in session:
        return redirect(url_for("login"))

    project = Project.query.get(id)

    if project:
        db.session.delete(project)
        db.session.commit()
        flash("Project deleted successfully.")

    return redirect(url_for("projects"))


# ======================
# LOGOUT
# ======================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ======================
# RUN APP
# ======================

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        # demo data if empty
        if Project.query.count() == 0:

            sample_projects = [

                Project(
                    name="Track Expansion Hyderabad",
                    department="Engineering",
                    status="In Progress",
                    progress=68,
                    description="Track expansion and modernization work in Hyderabad zone."
                ),

                Project(
                    name="Signal Automation Chennai",
                    department="Operations",
                    status="Completed",
                    progress=100,
                    description="Advanced signalling automation completed in Chennai."
                ),

                Project(
                    name="Bridge Inspection Vijayawada",
                    department="Safety",
                    status="Delayed",
                    progress=35,
                    description="Bridge structural audit and repairs under process."
                ),

                Project(
                    name="Coach Modernization Mumbai",
                    department="Mechanical",
                    status="Planning",
                    progress=10,
                    description="Modern coach interior and system upgrade planning."
                )

            ]

            db.session.add_all(sample_projects)
            db.session.commit()

    app.run(debug=True, port=5001, use_reloader=False)