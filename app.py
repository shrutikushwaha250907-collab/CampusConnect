from flask import Flask, render_template

app = Flask(__name__)

app.secret_key = "campusconnect"

# Home Page
@app.route("/")
def home():
    return render_template("home.html")

# Login Page
@app.route("/login")
def login():
    return render_template("login.html")

# Register Page
@app.route("/register")
def register():
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)