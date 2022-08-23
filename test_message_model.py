"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Likes

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


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        userA = User.signup("testa", "email@gmail.com", "password", None)
        userA.id = 1

        db.session.commit()
        userA = User.query.get(1)
        self.userA = userA

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="random text about nothing",
            user_id="1"
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(self.userA.messages), 1)
        self.assertEqual(self.userA.messages[0].text, "random text about nothing")
    
    def test_like(self):
        m = Message(
            text="random text about nothing",
            user_id="1"
        )

        m2 = Message(
            text="random text about something",
            user_id="1"
        )

        userB = User.signup("testb", "email@gmail.com", "password", None)
        userB.id = 2
        db.session.add_all( [m, m2, userB])
        db.session.commit()

        userB.likes.append(m)
        db.session.commit()

        likes = Likes.query.filter(Likes.user_id == 2).all()
        self.assertEqual(len(likes), 1)
        self.assetEqual(likes[0].message_id, m.id)



    