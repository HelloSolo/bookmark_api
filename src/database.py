import random
import string
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    bookmarks = db.relationship("Bookmark", backref="userbookmark")

    def __repr__(self) -> str:
        return f"User>>> {self.username}"


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    body = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(3), nullable=True)
    visits = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def generate_short_character(self):
        picked_char = "".join(random.choices(string.digits + string.ascii_letters, k=3))
        link = self.query.filter_by(short_url=picked_char).first()

        if link:
            return self.generate_short_character()
        else:
            return picked_char

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.short_url = self.generate_short_character()

    def __repr__(self) -> str:
        return f"bookmark>>>{self.url}"
