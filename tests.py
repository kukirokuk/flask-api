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
        self.test_key_2 = 'test_key_2'
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
        self.assertEqual(json.loads(str(response.get_data(as_text=True))), {'value': 'Your username or api_token url params are invalid '})

        #wrong password
        response = self.app.get('/get/some_value?username=wrong_user&api_key={}'.format(self.password))
        self.assertEqual(json.loads(response.get_data(as_text=True)), {'value': 'Your username or api_token url params are invalid '})

        #no value
        response = self.app.get('/get/some_value?username={}&api_key={}'.format(self.username, self.password))
        self.assertEqual(json.loads(response.get_data(as_text=True)), {'value': 'No value with this key in db'})

        #get key with success
        response = self.app.get('/get/{}?username={}&api_key={}'.format(self.test_key, self.username, self.password))
        self.assertEqual(json.loads(response.get_data(as_text=True)),  {'key': self.test_key, 'user_id': user.id, 'value': self.test_value})

    def test_set_json_access_url_params(self):
        user = User(self.username, 'some@email.com', self.hashed_password)
        db.session.add(user)

        entry = Entry(self.test_key, self.test_value, 1)
        db.session.add(entry)
        db.session.commit()

        #wrong username
        response = self.app.post('/set/?username={}&api_key=wrong_pass'.format(self.username),
                                 data=json.dumps(dict(key=self.test_key, value=self.test_value)),
                                 content_type='application/json')
        self.assertEqual(json.loads(str(response.get_data(as_text=True))), {'value': 'Your username or api_token url params are invalid '})

        #wrong password
        response = self.app.post('/set/?username=wrong_user&api_key={}'.format(self.password),
                                 data=json.dumps(dict(key=self.test_key, value=self.test_value)),
                                 content_type='application/json')
        self.assertEqual(json.loads(response.get_data(as_text=True)), {'value': 'Your username or api_token url params are invalid '})

        #set key with success
        response = self.app.post('/set/?username={}&api_key={}'.format(self.username, self.password),
                                 data=json.dumps(dict(key=self.test_key_2, value=self.test_value)),
                                 content_type='application/json')
        self.assertEqual(json.loads(response.get_data(as_text=True)),  {'value': 'The entry with key {} was succesfully created'.format(self.test_key_2)})

        #reassign existing key
        response = self.app.post('/set/?username={}&api_key={}'.format(self.username, self.password),
                                 data=json.dumps(dict(key=self.test_key_2, value=self.test_value)),
                                 content_type='application/json')
        self.assertEqual(json.loads(response.get_data(as_text=True)),  {'value': 'The entry {} already existed and was succesfully reassigned'.format(self.test_key_2)})

        #success get key with user that created it
        response = self.app.get('/get/{}?username={}&api_key={}'.format(self.test_key_2, self.username, self.password))
        self.assertEqual(json.loads(response.get_data(as_text=True)),  {'key': self.test_key_2, 'user_id': user.id, 'value': self.test_value})

        user2 = User('new_user', 'some_new@email.com', self.hashed_password)
        db.session.add(user2)
        db.session.commit()

        #fail get key old key with new user
        response = self.app.get('/get/{}?username={}&api_key={}'.format(self.test_key_2, 'new_user', self.password))
        self.assertEqual(json.loads(response.get_data(as_text=True)), {'value': 'No value with this key in db'})

if __name__ == "__main__":
    unittest.main()