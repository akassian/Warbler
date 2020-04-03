"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from flask_bcrypt import Bcrypt

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

bcrypt = Bcrypt()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test2.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(u)
        db.session.add(u2)
        db.session.commit()

        self.u = User.query.filter_by(username='testuser').first()
        self.u2 = User.query.filter_by(username='testuser2').first()
        self.client = app.test_client()

    def tearDown(self):
        """ roll back database to original state """
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u.messages), 0)
        self.assertEqual(len(self.u.followers), 0)

    def test_following_checks(self):
        "does checking if someone follows us work?"

        self.u.following.append(self.u2)

        # is u following u2? using is_following
        self.assertTrue(self.u.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u))

        # is u2 followed by u? using is_followed_by
        self.assertFalse(self.u.is_followed_by(self.u2))
        self.assertTrue(self.u2.is_followed_by(self.u))

    def test_create_user_success(self):
        "does creating a user... create a user?"

        user = User.signup(username="Bob",
                           email="testbob@bob.com",
                           password="bobword",
                           image_url="bob.jpg"
                           )

        hashed_pw = bcrypt.check_password_hash(user.password, "bobword")
        self.assertTrue(hashed_pw)

    def test_create_user_fail(self):
        "does giving bad data fail user signup?"

        with self.assertRaises(ValueError):
            user = User.signup(username="",
                               email="",
                               password="",
                               image_url=""
                               )

    def test_authentication(self):
        " does authentication work as intended?"

        user = User.signup(username="Bob",
                           email="testbob@bob.com",
                           password="bobword",
                           image_url="bob.jpg"
                           )

        # correct login
        self.assertTrue(User.authenticate('Bob', 'bobword'))
        # incorrect logins, bad username, then bad pw
        self.assertFalse(User.authenticate('Bobb', 'bobword'))
        self.assertFalse(User.authenticate('Bob', 'bobbword'))
