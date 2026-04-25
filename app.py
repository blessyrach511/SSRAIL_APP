from flask import Flask, render_template, request, redirect, url_for, flash, session
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = "ssrailworks_secure_key_2026"

# -----------------------------
# MongoDB Connection (Fixed SSL)
# -----------------------------
client = MongoClient(
    os.getenv("MONGO_URI"),
    tls=True,
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=5000
)

db = client.ssrail_db
projects = db.projects
users = db.users

# -----------------------------
# Google Login (optional)
# -----------------------------
oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

# -----------------------------
# Demo Session
# -----------------------------
def set_demo_user():
    session["user"] = "Demo User"
    session["email"] = "demo@ssrailworks.com"

# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("home.html")

# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():

    set_demo_user()

    total = projects.count_documents({})
    completed = projects.count_documents({"status": "Completed"})
    inprogress = projects.count_documents({"status": "In Progress"})
    delayed = projects.count_documents({"status": "Delayed"})

    return render_template(
        "dashboard.html",
        username=session["user"],
        email=session["email"],
        total=total,
        completed=completed,
        progress=inprogress,
        delayed=delayed
    )

# -----------------------------
# PROJECTS PAGE
# -----------------------------
@app.route("/projects")
def all_projects():

    set_demo_user()

    data = list(projects.find().sort("_id", -1))

    return render_template(
        "projects.html",
        projects=data,
        username=session["user"]
    )

# -----------------------------
# PROJECT DETAILS
# -----------------------------
@app.route("/project/<id>")
def project_details(id):

    project = projects.find_one({"_id": ObjectId(id)})

    if not project:
        flash("Project not found")
        return redirect("/projects")

    return render_template(
        "project_details.html",
        project=project,
        username="Demo User"
    )

# -----------------------------
# ADD PROJECT
# -----------------------------
@app.route("/add-project", methods=["GET", "POST"])
def add_project():

    if request.method == "POST":

        projects.insert_one({
            "name": request.form["name"],
            "department": request.form["department"],
            "status": request.form["status"],
            "progress": int(request.form["progress"]),
            "description": request.form["description"]
        })

        flash("Project Added Successfully")
        return redirect("/projects")

    return render_template("add_project.html")

# -----------------------------
# DELETE PROJECT
# -----------------------------
@app.route("/delete-project/<id>")
def delete_project(id):

    projects.delete_one({"_id": ObjectId(id)})
    flash("Deleted Successfully")

    return redirect("/projects")

# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)