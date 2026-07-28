from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    username = db.Column(db.String(50), unique=True, nullable=False)

    password = db.Column(db.String(100), nullable=False)

    branch = db.Column(db.String(100), default="")

    semester = db.Column(db.String(20), default="")

    skills = db.Column(db.String(300), default="")

    bio = db.Column(db.Text, default="")

    linkedin = db.Column(db.String(200), default="")

    github = db.Column(db.String(200), default="")

    profile_image = db.Column(
        db.String(200),
        default="images/default-profile.png"
    )


class Skill(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)

    level = db.Column(db.String(30), nullable=False)

    description = db.Column(db.Text)

    owner = db.Column(db.String(100))