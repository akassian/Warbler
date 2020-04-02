"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from flask_bcrypt import Bcrypt
from flask import g, session

from models import db, User, Message, Follows, Likes

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

db.drop_all()
db.create_all()

bcrypt = Bcrypt()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTests(TestCase):
    """ Test routes related to user functions """

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        pw_hash = bcrypt.generate_password_hash('HASHED_PASSWORD').decode('utf-8')

        u = User(
            email="test@test.com",
            username="testuser",
            password=pw_hash
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

    def test_signup(self):
        """Does signup work?"""

        with app.test_client() as client:  # GET test
            resp = client.get('/signup')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            # self.assertEqual(resp.location, 'http://localhost:5000/signup')
            self.assertIn('<h2 class="join-message">Join Warbler today.</h2>', html)

        with app.test_client() as client:  # POST test
            resp = client.post('/signup', data={
                'username': 'boblover',
                'email': 'headlover@boblover.com',
                'password': 'lovesbob123'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            # self.assertEqual(resp.location, '/')
            self.assertIn('<p>@boblover</p>', html)

    def test_login(self):
        """does logging in and out work?"""

        with app.test_client() as client:  # GET test
            resp = client.get('/login')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)

        with app.test_client() as client:  # POST test
            resp = client.post('/login', data={
                'username': 'testuser',
                'password': 'HASHED_PASSWORD'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('<p>@testuser</p>', html)
        
    def test_logout(self):
        "does logging out work?"

        with app.test_client() as client:  # as logged in user
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = '1'  # "logging in"

            resp = client.get('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('<div class="alert alert-message">Logged out!</div>', html)

        with app.test_client() as client:  # as logged out user
            resp = client.get('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('<div class="alert alert-message">Logged out!</div>', html)

    def test_users(self):
        """does the list of users load correctly?"""

        with app.test_client() as client:  # GET test
            resp = client.get('/users')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('<p>@testuser</p>', html)
            self.assertIn('<p>@testuser2</p>', html)

    def test_user_page(self):
        """does a user page load correctly?"""

        with app.test_client() as client:  # GET test
            resp = client.get('/users/1')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('<h4 id="sidebar-username">@testuser</h4>', html)
            self.assertIn('<ul class="user-stats nav nav-pills">', html)

    def test_user_following(self):
        """does the list of users you follow load correctly?"""

        logged_in_user = User.query.get_or_404(1)
        followed_user = User.query.get_or_404(2)
        logged_in_user.following.append(followed_user)
        db.session.commit()

        with app.test_client() as client:  # LOGGED IN test
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = '1'  # "logging in as user 1"
            resp = client.get('/users/1/following')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('<p>@testuser2</p>', html)

        with app.test_client() as client:  # LOGGED OUT test
            resp = client.get('/users/1/following', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)

    def test_user_followers(self):
        """does the list of users following you load correctly?"""

        logged_in_user = User.query.get_or_404(2)
        followed_user = User.query.get_or_404(1)
        logged_in_user.following.append(followed_user)
        db.session.commit()

        with app.test_client() as client:  # LOGGED IN test
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = '1'  # "logging in as user 1"
            resp = client.get('/users/1/followers')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('<p>@testuser2</p>', html)

        with app.test_client() as client:  # LOGGED OUT test
            resp = client.get('/users/1/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)

    def test_user_followers(self):
        """does the list of users following you load correctly?"""

        user2 = User.query.get_or_404(2)

        msg = Message(text='TESTTTTT')  # make a mesage to like
        user2.messages.append(msg)
        db.session.commit()

        like = Likes(user_id='1', message_id='1')  # like the new message
        db.session.add(like)
        db.session.commit()

        with app.test_client() as client:  # LOGGED IN test
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = '1'  # "logging in as user 1"
            resp = client.get('/users/1/likes')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('<p>TESTTTTT</p>', html)

        with app.test_client() as client:  # LOGGED OUT test
            resp = client.get('/users/1/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status, '200 OK')
            self.assertIn('<div class="alert alert-danger">Access unauthorized.</div>', html)

        # start with response codes, then HTML

        # /signup (GET, POST) DONE
        # /login (GET, POST) DONE 
        # /logout DONE

        # /users DONE
        # /users/<user_id> DONE
        # /users/<user_id>/following DONE
        # /users/<user_id>/followers DONE
        # /users/<user_id>/likes

        # ~~~ DO IN TEST_MESSAGES_VIEWS.PY ~~~
        # /users/follow/<follow_id> (POST)
        # /users/stop-following/<follow_id> (POST)
        # /users/profile (GET, POST)
        # /users/delete (POST)


        