import os
import unittest
 
from api import app, db
from api.models import User, Entry
 
class BasicTests(unittest.TestCase):

    def setUp(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, 'test.db')
        self.username = 'test_user'
        self.password = self.confirm = 'test_password'
        self.app = app.test_client()
        db.create_all()


    def tearDown(self):
        db.drop_all()


    def register(self, email, password, confirm):
        return self.app.post(
            '/register',
            data=dict(email=email, password=password, confirm=confirm),
            follow_redirects=True
        )

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)
 
    def test_main_page(self):
        response = self.app.get('/get/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
 
    def stest_login_logout(self):
        response = self.register(self.username, self.password,
                                 self.confirm)
        self.assertEqual(response.status_code, 200)

        response = self.login(self.username, self.password)
        self.assertIn(b'You were logged in', response.data)

        response = logout()
        self.assertIn(b'You were logged out' ,response.data)

        response = login(self.username + 'x', self.password)
        self.assertIn(b'Invalid username' ,response.data)

        response = login(self, self.username, self.password + 'x')
        self.assertIn(b'Invalid password' ,response.data)

    def test_get_json(self):
        user = User(self.username, 'some@email.com', self.password)
        db.session.add(user)
        self.test_key = 'test_key'
        self.test_value = 'test_value'
        entry = Entry(self.test_key, self.test_value, 1)
        db.session.add(entry)
        db.session.commit()

        response = self.app.get('/get/some_value?username={}&api_key={}'.format(self.username, self.password))
        print(response.json_data)

if __name__ == "__main__":
    unittest.main()