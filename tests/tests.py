#!/usr/bin/env python
import unittest
from datetime import timedelta, datetime
from app import create_app, db
from app.models import Users, Status, Blogs, Messages
from config import Config
from flask_login import current_user, login_user, logout_user, confirm_login
from flask import g


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


def register(app, username, email, password, confirm_password):
    return app.post('/auth/register', data=dict(
        username=username, email=email, password=password, password2=confirm_password
    ), follow_redirects=True)


def login(app, username, password):
    return app.post('/auth/login', data=dict(
        username=username, password=password
    ), follow_redirects=True)


def logout(app):
    return app.get('/auth/logout', follow_redirects=True)


class UsersModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_app = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_user(self):
        user = Users(username='Tylor', email='tylor_branch@hotmail.com')
        user.set_password('123')
        db.session.add(user)
        db.session.commit()
        self.assertIsInstance(user, Users)
        user1 = Users.query.filter_by(username='Tylor')
        self.assertIsNotNone(user1)

    def test_valid_register_user(self):
        response = register(self.test_app, username='Tylor', email='example@example.com',
                            password='123', confirm_password='123')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Location'], 'http://127.0.0.1:5000/auth/login')
        self.assertIn(b'Congratulations, you have been registered!', response.data)
        user = Users.query.filter_by(username='Tylor').first()
        self.assertIsNotNone(user)

    def test_invalid_user_registration_nonmatching_password(self):
        response = register(self.test_app, username='Tylor', email='example@example.com',
                            password='123', confirm_password='456')
        self.assertIn(b'Field must be equal to password.', response.data)

    def test_invalid_user_registration_user_exists(self):
        response = register(self.test_app, username='Tylor', email='example@example.com',
                            password='123', confirm_password='123')
        self.assertEqual(response.status_code, 200)
        response = register(self.test_app, username='Tylor', email='example@example.com',
                            password='123', confirm_password='123')
        self.assertIn(b'Please use a different username.', response.data)

    def test_password(self):
        user = Users(username='Tylor')
        user.set_password('123')
        self.assertTrue(user.check_password('123'))
        self.assertFalse(user.check_password('456'))

    @unittest.skip('Not implemented yet')
    def test_post_status(self):
        user = Users(username='Tylor')
        status = Status(body='Hello', author=user)
        status_list = Status.query.all()
        self.assertIsInstance(status, Status)
        self.assertEqual(status_list, [status])

    def test_avatar(self):
        u = Users(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        user1 = Users(username='Tylor')
        user2 = Users(username='Darcia')
        db.session.add_all([user1, user2])
        db.session.commit()
        self.assertEqual(user1.followed.all(), [])
        self.assertEqual(user2.followed.all(), [])

        user1.follow(user2)
        db.session.commit()
        self.assertEqual(user1.followed.all(), [user2])
        self.assertTrue(user1.is_following(user2))
        self.assertEqual(user1.followed.first().username, 'Darcia')
        self.assertEqual(user1.followed.count(), 1)
        self.assertEqual(user2.followers.count(), 1)
        self.assertEqual(user2.followers.first().username, 'Tylor')

        user1.unfollow(user2)
        db.session.commit()
        self.assertFalse(user1.is_following(user2))
        self.assertEqual(user1.followed.count(), 0)
        self.assertEqual(user2.followers.count(), 0)

    def test_shown_followed_posts(self):
        user1 = Users(username='Tylor')
        user2 = Users(username='Darcia')
        user3 = Users(username='Elijah')
        user4 = Users(username='Everett')
        db.session.add_all([user1, user2, user3, user4])

        now = datetime.utcnow()
        status1 = Status(body='Status from Tylor', author=user1, timestamp=now + timedelta(seconds=1))
        status2 = Status(body='Status from Darcia', author=user2, timestamp=now + timedelta(seconds=2))
        status3 = Status(body='Status from Elijah', author=user3, timestamp=now + timedelta(seconds=3))
        status4 = Status(body='Status from Everett', author=user4, timestamp=now + timedelta(seconds=4))
        db.session.add_all([status1, status2, status3, status4])
        db.session.commit()

        user1.follow(user2)
        user1.follow(user3)
        user2.follow(user1)
        user3.follow(user4)
        db.session.commit()

        result1 = user1.related_posts().all()
        result2 = user2.related_posts().all()
        result3 = user3.related_posts().all()
        result4 = user4.related_posts().all()
        self.asserEqual(result1, [status2, status3, status1])
        self.asserEqual(result2, [status1, status2])
        self.asserEqual(result3, [status4, status3])
        self.asserEqual(result4, [status4])

    @unittest.skip('Not implemented yet')
    def test_login(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_friend_request(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_accept_friend(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_update_profile(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_reset_password(self):
        pass


class BlogModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        user = Users(username='Tylor', email='example@example.com')
        user.set_password('123')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @unittest.skip('Not implemented yet')
    def test_post_blog(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_view_blog(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_update_blog(self):
        pass


class MessagesModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_app = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @unittest.skip('Not implemented yet')
    def test_send_message(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_received_messages(self):
        pass


class WebpageOkStatusCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_app = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_page(self):
        response = self.test_app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.test_app.get('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.test_app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


    @unittest.skip('Not implemented yet')
    def test_reset_password_request_page(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_reset_password_page(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_validate_user_page(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_profile_page(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_update_profile_page(self):
        pass

    def test_view_blogs_page(self):
        response = self.test_app.get('/blogs/blogs', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_view_single_blog_page(self):
        response = self.test_app.get('/blogs/blog/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    @unittest.skip('Not implemented yet')
    def test_view_own_blogs_page(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_create_blog_page(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_update_blog_page(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_error_404_page(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_error_500_page(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_pending_requests_page(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_send_message_page(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_view_message_page(self):
        pass

    @unittest.skip('Not implemented yet')
    def test_user_popup(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
