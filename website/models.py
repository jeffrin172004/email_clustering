from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    firstName = db.Column(db.String(150))
    email_clusters = db.relationship('EmailCluster', backref='user', lazy=True)

class EmailCluster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.Text)
    email_ids = db.Column(db.Text)
    email_count = db.Column(db.Integer)
    start_date = db.Column(db.DateTime(timezone=True))
    date_processed = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))