from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

app = Flask(__name__)
app.secret_key = "dev"

db = SQLAlchemy()

""" 
This is the association table between users. It defines a many-to-many relationship
between one user and another user.
You will not need to interact with this table directly.
"""
friend = db.Table(
    'friends',
    db.Column('friend_id', db.Integer, primary_key=True),
    db.Column('f1_id', db.Integer, db.ForeignKey('users.user_id')),
    db.Column('f2_id', db.Integer, db.ForeignKey('users.user_id'))
)


class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    # Because the relationship joins the table to itself, you need to specify primary and secondary join
    # Note the use of `secondary` for the association table.
    following = db.relationship(
        'User',
        secondary=friend,
        primaryjoin=user_id == friend.c.f1_id,
        secondaryjoin=user_id == friend.c.f2_id,
        backref='followers'
    )

    def get_all_friends(self):
        """ Get all friends, those you are following AND those following you. """
        return self.following + self.followers

    def __repr__(self):
        return f"User id={self.user_id} name={self.name}"


def connect_to_db(flask_app, db_uri="postgresql:///test-m2m", echo=False):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")


if __name__ == "__main__":

    os.system('dropdb test-m2m')
    os.system('createdb test-m2m')

    # Call connect_to_db(app, echo=False) if your program output gets
    # too annoying; this will tell SQLAlchemy not to print out every
    # query it executes.

    connect_to_db(app)
    db.create_all()

    alice = User(name="Alice")
    bob = User(name="Bob")
    charlie = User(name="Charlie")
    diana = User(name="Diana")

    # Alice follows Bob and Charlie
    alice.following.append(bob)
    alice.following.append(charlie)

    # Charlie follows Diana
    charlie.following.append(diana)

    db.session.add(alice)
    db.session.add(charlie)
    db.session.commit()

    print(alice.following)  # Bob, Charlie
    print(diana.followers)  # Charlie
    print(charlie.get_all_friends())  # Alice, Diana


