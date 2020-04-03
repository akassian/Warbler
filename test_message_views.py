"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test2.com",
                                    password="testuser2",
                                    image_url=None)

        # msg = Message(text="testmessage")
        # self.testuser.messages.append(msg)
        db.session.commit()
        # self.msgid = msg.id

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        # Add msg normally
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

        # Logged out, should not be able to add msg
        with self.client as c:
            c.get("/logout")
            resp = c.post("/messages/new", data={"text": "Hello"},
                          follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('Access unauthorized.', html)

        # Adding message to another user, should not be able to add msg
        with self.client as c:
            resp = c.post("/messages/new", data={"text":"Hello"},
                          follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('Access unauthorized.', html)

    def test_view_message(self):
        """
        Can we view a message?
        """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "testmessage"})

            msg_id = Message.query.filter_by(text="testmessage").first().id

            resp = c.get(f"/messages/{msg_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testmessage', html)

    def test_delete_message(self):
        """
        Can we delete a message?
        """

        # Delete msg normally
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "testmessage"})

            msg_id = Message.query.filter_by(text="testmessage").first().id

            c.post(f"/messages/{msg_id}/delete", follow_redirects=True)
            resp = c.get(f"/messages/{msg_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Message does not exist', html)

        # Logged out, should not be able to delete msg
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "testmessage"})

            msg_id = Message.query.filter_by(text="testmessage").first().id

            c.get("/logout")

            resp = c.post(f"/messages/{msg_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('Access unauthorized.', html)

            # Make sure msg is still there!
            resp = c.get(f"/messages/{msg_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn('testmessage', html)

        # Logged in as another user,
        # should not be able to delete another's msg
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "testmessage"})

            c.get("/logout")

            c.post("/login", data={"username": "testuser",
                                   "password": "testuser"},
                   follow_redirects=True)

            msg_id = Message.query.filter_by(text="testmessage").first().id

            resp = c.post(f"/messages/{msg_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')

            # Make sure msg is still there!
            resp = c.get(f"/messages/{msg_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn('testmessage', html)
