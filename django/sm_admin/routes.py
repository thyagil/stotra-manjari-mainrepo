from flask import render_template, request, redirect, url_for
from app import create_app
from servcies.project_service import list_projects, create_project, load_project

app = create_app()

@app.route("/")
def home():
    projects = list_projects()
    return render_template("home.html", projects=projects)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        proj_id = request.form["id"]
        friendly_name = request.form["friendly_name"]
        proj_type = request.form["type"]
        format = request.form["format"]

        try:
            create_project(proj_id, friendly_name, proj_type, format)
            return redirect(url_for("home"))
        except FileExistsError as e:
            return f"<h2>{e}</h2>", 400

    return render_template("new_project.html")

@app.route("/project/<proj_id>")
def project_dashboard(proj_id):
    try:
        meta = load_project(proj_id)
    except FileNotFoundError:
        return f"<h2>❌ No project.plist found for {proj_id}</h2>", 404

    return render_template("project_dashboard.html", proj_id=proj_id, meta=meta)
