"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

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

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        userA = User.signup("testa", "email@gmail.com", "password", None)
        userB = User.signup("testb", "email@gmail.com", "password", None)
        userA.id = 1
        userB.id = 2

        db.session.commit()
        userA = User.query.get(1)
        userB = User.query.get(2)
        self.userA = userA
        self.userB = userB

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_user_following(self):
        self.userA.following.append(self.userB)
        db.session.commit()

        self.assertEqual(len(self.userB.following),0)
        self.assertEqual(len(self.userA.following),1)
        self.assertEqual(self.userA.following[0].id, self.userB.id)


    def test_user_followers(self):
        self.userA.following.append(self.userB)
        db.session.commit()

        self.assertEqual(len(self.userB.followers),1)
        self.assertEqual(len(self.userA.followers),0)
        self.assertEqual(self.userB.followers[0].id, self.userA.id)

    def test_user_is_following(self):
        self.userA.following.append(self.userB)
        db.session.commit()

        self.assertTrue(self.userA.is_following(self.userB))
        self.assertFalse(self.userB.is_following(self.userA))

    def test_user_create(self):
        user = User.signup("testUser", "valid@email.com", "superqualitypassword", None)
        user.id = 15120985
        db.session.commit()

        user = User.query.get(15120985)
        self.assertEqual(user.username, "testUser")
        self.assertEqual(user.email, "valid@email.com")
        self.assertNotEqual(user.password, "superqualitypassword")

    def test_user_create_badpassword(self):
        user = User.signup("testUser", "valid@email.com", "", None)
        user.id = 15120985
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_user_create_bademail(self):
        user = User.signup("testUser", None, "superqualitypassword", None)
        user.id = 15120985
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_user_create_badusername(self):
        user = User.signup(None, "valid@email.com", "", None)
        user.id = 15120985
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_auth(self):
        user = User.authenticate(self.userA.username, "password")
        self.assertEqual(user.id, self.userA.id)

    def test_auth_username(self):
        self.assertFalse(User.authenticate("userC", "password"))
    
    def test_auth_password(self):
        self.assertFalse(User.authenticate("userC", "password2"))
    