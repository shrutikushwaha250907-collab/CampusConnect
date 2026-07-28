from flask import Flask, render_template, request, redirect, session, flash
from models import db, User, Skill
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


# -------------------- Home --------------------

@app.route("/")
def home():
    return render_template("home.html")


# -------------------- Register --------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Username already exists!")
            return redirect("/register")

        new_user = User(
            fullname=fullname,
            email=email,
            username=username,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful!")
        return redirect("/login")

    return render_template("register.html")


# -------------------- Login --------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session["user"] = user.username

            return redirect("/dashboard")

        flash("Invalid Username or Password")

    return render_template("login.html")


# -------------------- Dashboard --------------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    user = User.query.filter_by(
        username=session["user"]
    ).first()

    return render_template(
        "dashboard.html",
        user=user
    )


# -------------------- Profile --------------------

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user" not in session:
        return redirect("/login")

    user = User.query.filter_by(
        username=session["user"]
    ).first()

    if request.method == "POST":

        user.branch = request.form["branch"]
        user.semester = request.form["semester"]
        user.skills = request.form["skills"]
        user.bio = request.form["bio"]
        user.linkedin = request.form["linkedin"]
        user.github = request.form["github"]

        db.session.commit()

        flash("Profile Updated Successfully!")

        return redirect("/profile")

    return render_template(
        "profile.html",
        user=user
    )


# -------------------- Skill Marketplace --------------------

@app.route("/skills")
def skills():

    if "user" not in session:
        return redirect("/login")

    all_skills = Skill.query.all()

    return render_template(
        "skills.html",
        skills=all_skills,
        username=session["user"]
    )


@app.route("/add-skill", methods=["GET", "POST"])
def add_skill():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        title = request.form["title"]
        level = request.form["level"]
        description = request.form["description"]

        new_skill = Skill(
            title=title,
            level=level,
            description=description,
            owner=session["user"]
        )

        db.session.add(new_skill)
        db.session.commit()

        flash("Skill Added Successfully!")

        return redirect("/skills")

    return render_template("add_skill.html")


@app.route("/delete-skill/<int:id>")
def delete_skill(id):

    if "user" not in session:
        return redirect("/login")

    skill = Skill.query.get_or_404(id)

    if skill.owner == session["user"]:

        db.session.delete(skill)
        db.session.commit()

        flash("Skill Deleted!")

    return redirect("/skills")



# -------------------- Logout --------------------

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)