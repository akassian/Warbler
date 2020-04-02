"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from models import db, User, Message

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


class MessageModelTestCase(TestCase):
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

    def test_message_model(self):
        """does making a Message instance work?
           do our column requirements work?"""

        message = Message(text="does this work?",
                          user_id="1"
                          )

        db.session.add(message)
        db.session.commit()

        # confirm message was added to DB
        self.assertIsInstance(message, Message)
        self.assertIsInstance(message.id, int)

        message2 = Message(text=None,
                           user_id="1"
                           )

        db.session.add(message2)

        # confirm that bad instance cannot be added to DB
        self.assertRaises(IntegrityError, db.session.commit)
