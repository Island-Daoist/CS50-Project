"""
Module contains all of the SQL-Alchemy classes that create tables and functionality connected to those classes.

Functionality predominately stems from the Users class, with ForeignKey connections to other classes.

Classes Exported by Module:
---------------------------

    Users:
        Contains the base data for any user profile, along with functionality to follow and friend users.
        Also contains functions to update certain data points associated with the user in the SQL Database.

    Blogs:
        Used to create and manage the SQL table for Blog objects.

    Status:
        Used to create and manage the SQL table for Blog objects.

    Messages:
        Used to create and manage the SQL table for Blog objects.
"""
from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import jwt
from app import db, login


# Secondary Table created to accommodate a many-to-many relationship amongst users in the Users table
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)


# Secondary Table created to accommodate a many-to-many relationship amongst users in the Users table
# Table for active friends
friends = db.Table(
    'friends',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('users.id'))
)

# Secondary Table created to accommodate a many-to-many relationship amongst users in the Users table
# Table containing friend requests sent to users
pending_requests = db.Table(
    'pending_requests',
    db.Column('sender_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('respondent_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('timestamp', db.DateTime, index=True, default=datetime.utcnow)
)


class Users(db.Model, UserMixin):
    """
    Implement here.
    """
    # Base Information of Required for Users
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(280))

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self):
        return f'<User {self.username}>'

    # Password functionality group
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_password_reset_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_password_reset_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return Users.query.get(id)

    # Create connections to blog and status models
    blogs = db.relationship('Blogs', backref='author', lazy='dynamic')
    status = db.relationship('Status', backref='author', lazy='dynamic')

    # Create connections and functionality to messages model
    messages_sent = db.relationship('Messages', foreign_keys='Messages.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Messages', foreign_keys='Messages.recipient_id',
                                        backref='recipient', lazy='dynamic')
    # Variable updated by application when messages page accessed by user
    message_last_read_time = db.Column(db.DateTime)

    def new_messages(self):
        last_read_time = self.message_last_read_time or datetime(1900, 1, 1)
        return Messages.query.filter_by(recipient=self).filter(
            Messages.timestamp > last_read_time).count()

    # Functionality Group for Following other Users
    followed = db.relationship(
        'Users', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Status.query.join(
            followers, (followers.c.followed_id == Status.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Status.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Status.timestamp.desc())

    # Functionality Group for friend relations between Users
    user_friends = db.relationship(
        'Users', secondary=friends,
        primaryjoin=(friends.c.user_id == id),
        secondaryjoin=(friends.c.friend_id == id),
        backref=db.backref('friends', lazy='dynamic'), lazy='dynamic')

    pending_friend_requests = db.relationship(
        'Users', secondary=pending_requests,
        primaryjoin=(pending_requests.c.sender_id == id),
        secondaryjoin=(pending_requests.c.respondent_id == id),
        backref=db.backref('friend_requests', lazy='dynamic'), lazy='dynamic')

    def add_friend(self, user):
        if not self.is_friend(user):
            self.user_friends.append(user)
            user.user_friends.append(self)

    def unfriend(self, user):
        if self.is_friend(user):
            self.user_friends.remove(user)
            user.user_friends.remove(self)

    def is_friend(self, user):
        return self.user_friends.filter(friends.c.friend_id == user.id).count() > 0

    def add_friend_request(self, user):
        if self.verify_request(user):
            self.pending_friend_requests.append(user)

    def friends_posts(self):
        return Status.query.join(
            friends, (friends.c.friend_id == Status.user_id)).filter(
            friends.c.user_id == self.id).order_by(Status.timestamp.desc())

    def verify_request(self, user):
        if self.is_friend(user) or self.id == user.id:
            return False
        elif user in self.pending_friend_requests or self in user.pending_friend_requests:
            return False
        else:
            return True

    # Function group for status return data
    def related_posts(self):
        shown_posts_friends = Status.query.join(
            friends, (friends.c.friend_id == Status.user_id)).filter(
            friends.c.user_id == self.id)
        shown_posts_followed = Status.query.join(
            followers, (followers.c.followed_id == Status.user_id)).filter(
            followers.c.follower_id == self.id)
        own_posts = Status.query.filter_by(user_id=self.id)
        return own_posts.union(shown_posts_followed, shown_posts_friends).order_by(Status.timestamp.desc())


@login.user_loader
def load_user(id):
    return Users.query.get(int(id))


class Blogs(db.Model):
    """
    Implement here.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    synopsis = db.Column(db.Text)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Post {self.body}>'


class Status(db.Model):
    """
    Implement here.
    """
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Status {self.body}>'


class Messages(db.Model):
    """
    Implement here.
    """
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.body}>'
