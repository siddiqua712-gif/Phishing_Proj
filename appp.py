from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
import pickle
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)
migrate = Migrate(app, db)
from models.user import User
with app.app_context():
    db.create_all()
    

# Load ML model
model = pickle.load(open("static/models/svm_model.pkl", "rb"))
vectorizer = pickle.load(open("static/models/vect.pkl", "rb"))
lrmodel = pickle.load(open("static/models/model.pkl", "rb"))

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    subject = db.Column(db.Text)
    prediction = db.Column(db.String(50))
    probability = db.Column(db.Float)
    date = db.Column(db.DateTime, default=lambda:datetime.now(IST))

# --- Routes ---
@app.route("/admin")
def admin_dashboard():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    all_users = User.query.all()
    all_activities = Activity.query.all()
    return render_template("admin_dashboard.html", users=all_users, logs=all_activities)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user"] = username
            session["role"] = user.role

            # ADMIN LOGIN
            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))

            # NORMAL USER LOGIN
            else:
                return redirect(url_for("dashboard"))

        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # check if user exists
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return render_template("register.html", error="User already exists")

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            password=hashed_password,
            role="user"
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    prediction = None
    probability = None

    subject = ""
    sender = ""
    urls = ""
    body = ""

    if request.method == "POST":
        subject = request.form["subject"]
        sender = request.form["sender"]
        urls = request.form["urls"]
        body = request.form["body"]

        combined_text = subject + " " + sender + " " + urls + " " + body
        X = vectorizer.transform([combined_text])

        result = model.predict(X)[0]
        probability = lrmodel.predict_proba(X)[0][1]

        prediction = "Phishing Email 🚨" if result == 1 else "Safe Email ✅"

        # ✅ SAVE TO DATABASE
        activity = Activity(
            username=session["user"],
            subject=subject,
            prediction=prediction,
            probability=round(probability * 100, 2)
        )

        db.session.add(activity)
        db.session.commit()

    return render_template(
        "index.html",
        prediction=prediction,
        probability=round(probability*100,2) if probability else None,
        subject=subject,
        sender=sender,
        urls=urls,
        body=body
    )
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    logs = Activity.query.filter_by(username=session["user"]).all()
    return render_template("dashboard.html", logs=logs)

if __name__ == "__main__":
    app.run(debug=True)