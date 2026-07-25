from flask import Flask, render_template, request, redirect, session, flash
from models import db, User
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

    return render_template(
        "dashboard.html",
        username=session["user"]
    )


# -------------------- Logout --------------------

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)