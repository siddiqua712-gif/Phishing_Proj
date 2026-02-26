from flask import Flask, request, render_template
import pickle

app = Flask(__name__)

# Load saved model & vectorizer
@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    if request.method == "POST":
    subject = request.form["subject"]
    sender = request.form["sender"]
    urls = request.form["urls"]
    body = request.form["body"]

    combined_text = subject + " " + body + " " + sender + " " + urls

    X_new = vectorizer.transform([combined_text])
    pred = svm_model.predict(X_new)[0]

    prediction = "Phishing" if pred == 1 else "Safe"
    return render_template("index.html", prediction=prediction)