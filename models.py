from hashlib import md5
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app import login

friends = db.Table('friends', db.Column('user_id', db.Integer, db.ForeignKey("user.id")),
                   db.Column('friend_id', db.Integer, db.ForeignKey("user.id")))


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', backref='author', lazy='select')

    def __repr__(self):
        return 'Author - {}'.format(self.last_name)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)

    def __repr__(self):
        return 'Book - {}'.format(self.name)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), nullable=True, unique=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(255), unique=True, nullable=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    token = db.Column(db.String(256), nullable=True, unique=True)
    friends_user = db.relationship('User', secondary=friends, primaryjoin=(friends.c.user_id == id),
                                   secondaryjoin=(friends.c.friend_id == id),
                                   backref=db.backref('friends', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def avatar(self, size):
        hash_sum = md5(self.username.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?s={}&d=retro'.format(hash_sum, size)

    def is_friends(self, user):
        return self.friends_user.filter(friends.c.friend_id == user.id).count() > 0

    def add_friend(self, user):
        if not self.is_friends(user):
            self.friends_user.append(user)

    def delete_friend(self, user):
        if self.is_friends(user):
            self.friends_user.remove(user)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
