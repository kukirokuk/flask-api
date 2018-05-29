from api import db, ma, login_manager
from flask_login import UserMixin

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80))
    value = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, key, value, user_id):
        self.key = key
        self.value = value
        self.user_id = user_id

class EntrySchema(ma.Schema):
    class Meta:
        fields = ('key', 'value', 'user_id')

entry_schema = EntrySchema()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    entries = db.relationship('Entry', backref='author', lazy=True)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
    def __repr__(self):
        return "User('{}', '{}')".format(self.username, self.email)