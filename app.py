import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import Flask, render_template, request, redirect, session, flash

from models import (
    db,
    User,
    Skill,
    Note,
    Event,
    Announcement,
    EventRegistration,
    Question,
    Discussion
)

from config import Config


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


# -------------------- UPLOAD FOLDER --------------------

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -------------------- DATABASE SETUP --------------------

with app.app_context():

    os.makedirs(
        app.instance_path,
        exist_ok=True
    )

    db.create_all()

    admin = User.query.filter_by(
        username="admin"
    ).first()

    if not admin:

        admin = User(
            fullname="Administrator",
            email="admin@campusconnect.com",
            username="admin",
            password="admin123",
            role="admin"
        )

        db.session.add(admin)

        db.session.commit()

        print("Admin account created.")


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "home.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form["fullname"]

        email = request.form["email"]

        username = request.form["username"]

        password = request.form["password"]


        existing_user = User.query.filter_by(
            username=username
        ).first()


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


    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

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


    return render_template(
        "login.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    announcements = Announcement.query.order_by(
        Announcement.id.desc()
    ).all()


    return render_template(
        "dashboard.html",
        user=user,
        announcements=announcements
    )


# =========================================================
# PROFILE
# =========================================================

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


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin():

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    if user.role == "student":

        flash("Access Denied!")

        return redirect("/dashboard")


    total_students = User.query.filter_by(
        role="student"
    ).count()


    total_teachers = User.query.filter_by(
        role="teacher"
    ).count()


    total_events = Event.query.count()

    total_notes = Note.query.count()

    total_skills = Skill.query.count()

    total_announcements = Announcement.query.count()

    total_discussions = Discussion.query.count()


    return render_template(
        "admin_dashboard.html",

        user=user,

        total_students=total_students,

        total_teachers=total_teachers,

        total_events=total_events,

        total_notes=total_notes,

        total_skills=total_skills,

        total_announcements=total_announcements,

        total_discussions=total_discussions
    )


# =========================================================
# MANAGE USERS
# =========================================================

@app.route("/manage-users")
def manage_users():

    if "user" not in session:

        return redirect("/login")


    current_user = User.query.filter_by(
        username=session["user"]
    ).first()


    if current_user.role == "student":

        flash("Access Denied!")

        return redirect("/dashboard")


    users = User.query.order_by(
        User.fullname
    ).all()


    return render_template(
        "manage_users.html",
        users=users,
        current_user=current_user
    )


# =========================================================
# DELETE USER
# =========================================================

@app.route("/delete-user/<int:id>")
def delete_user(id):

    if "user" not in session:

        return redirect("/login")


    current_user = User.query.filter_by(
        username=session["user"]
    ).first()


    if current_user.role == "student":

        flash("Access Denied!")

        return redirect("/dashboard")


    user = User.query.get_or_404(id)


    # Cannot delete yourself

    if user.username == current_user.username:

        flash("You cannot delete your own account.")

        return redirect("/manage-users")


    # Teacher restrictions

    if current_user.role == "teacher":

        if user.role != "student":

            flash(
                "Teachers can only delete student accounts."
            )

            return redirect("/manage-users")


    db.session.delete(user)

    db.session.commit()


    flash("User Deleted Successfully!")


    return redirect("/manage-users")


# =========================================================
# SKILLS
# =========================================================

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


# =========================================================
# ADD SKILL
# =========================================================

@app.route("/add-skill", methods=["GET", "POST"])
def add_skill():

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    if user.role == "student":

        flash(
            "Only Teachers and Admin can add skills."
        )

        return redirect("/skills")


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


    return render_template(
        "add_skill.html"
    )


# =========================================================
# DELETE SKILL
# =========================================================

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


# =========================================================
# NOTES
# =========================================================

@app.route("/notes")
def notes():

    if "user" not in session:

        return redirect("/login")


    all_notes = Note.query.all()


    return render_template(
        "notes.html",
        notes=all_notes,
        username=session["user"]
    )


# =========================================================
# UPLOAD NOTE
# =========================================================

@app.route("/upload-note", methods=["GET", "POST"])
def upload_note():

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    if user.role == "student":

        flash(
            "Only Teachers and Admin can upload notes."
        )

        return redirect("/notes")


    if request.method == "POST":

        title = request.form["title"]

        subject = request.form["subject"]

        file = request.files["file"]


        filename = secure_filename(
            file.filename
        )


        upload_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )


        file.save(upload_path)


        note = Note(
            title=title,
            subject=subject,
            filename=filename,
            owner=session["user"]
        )


        db.session.add(note)

        db.session.commit()


        flash("Note Uploaded Successfully!")


        return redirect("/notes")


    return render_template(
        "upload_note.html"
    )


# =========================================================
# DOWNLOAD NOTE
# =========================================================

@app.route("/download/<filename>")
def download(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )


# =========================================================
# DELETE NOTE
# =========================================================

@app.route("/delete-note/<int:id>")
def delete_note(id):

    if "user" not in session:

        return redirect("/login")


    note = Note.query.get_or_404(id)


    if note.owner == session["user"]:

        path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            note.filename
        )


        if os.path.exists(path):

            os.remove(path)


        db.session.delete(note)

        db.session.commit()


        flash(
            "Note Deleted Successfully!"
        )


    return redirect("/notes")


# =========================================================
# EVENTS
# =========================================================

@app.route("/events")
def events():

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    all_events = Event.query.all()


    return render_template(
        "events.html",
        events=all_events,
        username=session["user"],
        user=user
    )


# =========================================================
# ADD EVENT
# =========================================================

@app.route("/add-event", methods=["GET", "POST"])
def add_event():

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    if user.role == "student":

        flash(
            "Only Teachers and Admin can add events."
        )

        return redirect("/events")


    if request.method == "POST":

        title = request.form["title"]

        date = request.form["date"]

        location = request.form["location"]

        description = request.form["description"]


        event = Event(
            title=title,
            date=date,
            location=location,
            description=description,
            organizer=session["user"]
        )


        db.session.add(event)

        db.session.commit()


        flash("Event Added Successfully!")


        return redirect("/events")


    return render_template(
        "add_event.html",
        user=user
    )


# =========================================================
# DELETE EVENT
# =========================================================

@app.route("/delete-event/<int:id>")
def delete_event(id):

    if "user" not in session:

        return redirect("/login")


    event = Event.query.get_or_404(id)


    if event.organizer == session["user"]:

        db.session.delete(event)

        db.session.commit()


        flash(
            "Event Deleted Successfully!"
        )


    return redirect("/events")


# =========================================================
# ADD TEACHER
# =========================================================

@app.route("/add-teacher", methods=["GET", "POST"])
def add_teacher():

    if "user" not in session:

        return redirect("/login")


    admin = User.query.filter_by(
        username=session["user"]
    ).first()


    if admin.role != "admin":

        flash("Access Denied!")

        return redirect("/dashboard")


    if request.method == "POST":

        fullname = request.form["fullname"]

        email = request.form["email"]

        username = request.form["username"]

        password = request.form["password"]


        existing = User.query.filter_by(
            username=username
        ).first()


        if existing:

            flash(
                "Username already exists!"
            )

            return redirect("/add-teacher")


        teacher = User(
            fullname=fullname,
            email=email,
            username=username,
            password=password,
            role="teacher"
        )


        db.session.add(teacher)

        db.session.commit()


        flash(
            "Teacher Added Successfully!"
        )


        return redirect("/add-teacher")


    teachers = User.query.filter_by(
        role="teacher"
    ).all()


    return render_template(
        "add_teacher.html",
        teachers=teachers
    )


# =========================================================
# ANNOUNCEMENTS
# =========================================================

@app.route("/announcements")
def announcements():

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    all_announcements = Announcement.query.order_by(
        Announcement.id.desc()
    ).all()


    return render_template(
        "announcements.html",
        announcements=all_announcements,
        user=user
    )


# =========================================================
# ADD ANNOUNCEMENT
# =========================================================

@app.route("/add-announcement", methods=["GET", "POST"])
def add_announcement():

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    if user.role == "student":

        flash(
            "Only Teachers and Admin can post announcements."
        )

        return redirect("/announcements")


    if request.method == "POST":

        title = request.form["title"]

        message = request.form["message"]


        announcement = Announcement(
            title=title,
            message=message,
            posted_by=user.fullname,
            date=datetime.now().strftime(
                "%d %B %Y"
            )
        )


        db.session.add(announcement)

        db.session.commit()


        flash(
            "Announcement Posted Successfully!"
        )


        return redirect("/announcements")


    return render_template(
        "add_announcement.html"
    )


# =========================================================
# DELETE ANNOUNCEMENT
# =========================================================

@app.route("/delete-announcement/<int:id>")
def delete_announcement(id):

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    announcement = Announcement.query.get_or_404(id)


    if (
        user.role == "admin"
        or announcement.posted_by == user.fullname
    ):

        db.session.delete(announcement)

        db.session.commit()


        flash(
            "Announcement Deleted Successfully!"
        )


    else:

        flash(
            "You cannot delete this announcement."
        )


    return redirect("/announcements")


# =========================================================
# EVENT REGISTRATION
# =========================================================

@app.route("/register-event/<int:event_id>")
def register_event(event_id):

    if "user" not in session:

        return redirect("/login")


    already_registered = EventRegistration.query.filter_by(
        event_id=event_id,
        student=session["user"]
    ).first()


    if already_registered:

        flash(
            "You have already registered for this event."
        )

        return redirect("/events")


    registration = EventRegistration(
        event_id=event_id,
        student=session["user"]
    )


    db.session.add(registration)

    db.session.commit()


    flash(
        "Event Registration Successful!"
    )


    return redirect("/events")


# =========================================================
# EVENT REGISTRATIONS
# =========================================================

@app.route("/event-registrations/<int:event_id>")
def event_registrations(event_id):

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    if user.role == "student":

        flash("Access Denied")

        return redirect("/events")


    event = Event.query.get_or_404(
        event_id
    )


    registrations = EventRegistration.query.filter_by(
        event_id=event_id
    ).all()


    return render_template(
        "event_registrations.html",
        event=event,
        registrations=registrations
    )


# =========================================================
# DISCUSSIONS
# =========================================================

@app.route("/discussions")
def discussions():

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    all_discussions = Discussion.query.order_by(
        Discussion.id.desc()
    ).all()


    return render_template(
        "discussions.html",
        discussions=all_discussions,
        user=user
    )


# =========================================================
# ADD DISCUSSION
# =========================================================

@app.route("/add-discussion", methods=["GET", "POST"])
def add_discussion():

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    if request.method == "POST":

        title = request.form["title"]

        question = request.form["question"]


        discussion = Discussion(
            title=title,
            question=question,
            asked_by=user.fullname
        )


        db.session.add(discussion)

        db.session.commit()


        flash(
            "Question Posted Successfully!"
        )


        return redirect("/discussions")


    return render_template(
        "add_discussion.html",
        user=user
    )


# =========================================================
# REPLY DISCUSSION
# =========================================================

@app.route(
    "/reply-discussion/<int:id>",
    methods=["GET", "POST"]
)
def reply_discussion(id):

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    if user.role == "student":

        flash(
            "Only Teachers/Admin can reply."
        )

        return redirect("/discussions")


    discussion = Discussion.query.get_or_404(
        id
    )


    if request.method == "POST":

        discussion.reply = request.form["reply"]

        discussion.replied_by = user.fullname


        db.session.commit()


        flash(
            "Reply Posted Successfully!"
        )


        return redirect("/discussions")


    return render_template(
        "reply_discussion.html",
        discussion=discussion,
        user=user
    )


# =========================================================
# DELETE DISCUSSION
# =========================================================

@app.route("/delete-discussion/<int:id>")
def delete_discussion(id):

    if "user" not in session:

        return redirect("/login")


    user = User.query.filter_by(
        username=session["user"]
    ).first()


    if user.role == "student":

        flash(
            "Permission Denied!"
        )

        return redirect("/discussions")


    discussion = Discussion.query.get_or_404(
        id
    )


    db.session.delete(discussion)

    db.session.commit()


    flash(
        "Discussion Deleted!"
    )


    return redirect("/discussions")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.pop(
        "user",
        None
    )


    return redirect("/")


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )