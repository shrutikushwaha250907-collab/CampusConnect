from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ---------------- USER ----------------

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    username = db.Column(db.String(50), unique=True, nullable=False)

    password = db.Column(db.String(100), nullable=False)

    # NEW
    role = db.Column(db.String(20), default="student")

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


# ---------------- SKILLS ----------------

class Skill(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)

    level = db.Column(db.String(30), nullable=False)

    description = db.Column(db.Text)

    owner = db.Column(db.String(100))


# ---------------- NOTES ----------------

class Note(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)

    subject = db.Column(db.String(100), nullable=False)

    filename = db.Column(db.String(200), nullable=False)

    owner = db.Column(db.String(100), nullable=False)


# ---------------- EVENTS ----------------

class Event(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)

    date = db.Column(db.String(30), nullable=False)

    location = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text, nullable=False)

    organizer = db.Column(db.String(100), nullable=False)


# ---------------- ANNOUNCEMENTS ----------------

class Announcement(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)

    message = db.Column(db.Text, nullable=False)

    posted_by = db.Column(db.String(100), nullable=False)

    date = db.Column(db.String(30), nullable=False)


# ---------------- EVENT REGISTRATION ----------------

class EventRegistration(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(db.Integer, nullable=False)

    student = db.Column(db.String(100), nullable=False)