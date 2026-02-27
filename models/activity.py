from extensions import db
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    subject = db.Column(db.Text)
    prediction = db.Column(db.String(50))
    probability = db.Column(db.Float)
    date = db.Column(db.DateTime, default=lambda: datetime.now(IST))