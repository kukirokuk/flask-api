import os
import unittest
import json

from api import app, db, bcrypt
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
        self.test_key = 'test_key'
        self.test_value = 'test_value'
        self.hashed_password = bcrypt.generate_password_hash(self.password).decode('utf-8')
        self.app = app.test_client()
        db.create_all()


    def tearDown(self):
        db.drop_all()


    def test_get_json_access_url_params(self):
        user = User(self.username, 'some@email.com', self.hashed_password)
        db.session.add(user)

        entry = Entry(self.test_key, self.test_value, 1)
        db.session.add(entry)
        db.session.commit()

        #wrong username
        response = self.app.get('/get/some_value?username={}&api_key=wrong_pass'.format(self.username))
        self.assertEqual(json.loads(response.get_data()), {'value': 'Your username or api_token url params are invalid '})
        #wrong password
        response = self.app.get('/get/some_value?username=wrong_user&api_key={}'.format(self.password))
        self.assertEqual(json.loads(response.get_data()), {'value': 'Your username or api_token url params are invalid '})
        #no value
        response = self.app.get('/get/some_value?username={}&api_key={}'.format(self.username, self.password))
        self.assertEqual(json.loads(response.get_data()), {'value': 'No value with this key in db'})
        #get key with success
        response = self.app.get('/get/{}?username={}&api_key={}'.format(self.test_key, self.username, self.password))
        self.assertEqual(json.loads(response.get_data()),  {'key': self.test_key, 'user_id': user.id, 'value': self.test_value})
        
if __name__ == "__main__":
    unittest.main()