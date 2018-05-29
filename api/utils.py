import base64
from flask import request, jsonify, g, abort
from functools import wraps
from urllib.parse import urlparse, urljoin

from api import db, bcrypt
from api.models import entry_schema, Entry, User
from wtforms.validators import ValidationError

def set_entry_processing(user_id):
    """ Function that check income set data and give the json response """
    json_data = request.get_json()
    if json_data and request.json.get('key') and request.json.get('value'):
        try:
            data = entry_schema.load(json_data)[0]
        except ValidationError as err:
            return jsonify(err.messages), 422
        key, value = data['key'], data['value']
        db_entry = Entry.query.filter_by(key=key, user_id=user_id).first()
        income_entry = Entry(key=key, value=value, user_id=user_id)
        db.session.add(income_entry)
        db.session.commit()
        if db_entry is None:
            return jsonify({'value': 'The entry with key {} was succesfully created'.format(key)})
        return jsonify({'value': 'The entry {} already existed and was succesfully reassigned'.format(key)})
    else:
        if request.is_xhr:
            return jsonify({'value': 'Please enter kay and value'})
        return jsonify({'value': 'Data structure must be {"key": "your key", "value": "your value"}'})

def get_entry_processing(user_id, key=None):
    """ Function that check income get data and give the json response """
    entry = Entry.query.filter_by(key=key, user_id=user_id).first()
    if entry:
        return entry_schema.jsonify(entry)
    else:
        return jsonify({'value': 'No value with this key in db'})

def custom_auth(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        """ Auth decorator that checks user authentication through url args 'api_key' and
        'username' also as via  headers basic auth and add user authenticated user object 
        to the flask g context object
        """

        # first, try to login using the username and api_key (user password) as url args\
        if request.args.get('api_key') and request.args.get('username'):
            current_user = User.query.filter_by(username=request.args.get('username')).first()
            if current_user and bcrypt.check_password_hash(current_user.password, request.args.get('api_key')):
                g.user = current_user
                return func(*args, **kwargs)
            return jsonify({'value': 'Your username or api_token url params are invalid '})

        # next, try to login using Basic Auth
        elif request.headers.get('Authorization'):
            api_key = request.headers.get('Authorization').replace('Basic ', '', 1)
            try:
                api_key = base64.b64decode(api_key).decode('ascii').split(':')[-1]
            except TypeError:
                pass
            hashed_password = bcrypt.generate_password_hash(api_key).decode('utf-8')
            current_user = User.query.filter_by(password=hashed_password).first()
            if current_user:
                return func(current_user, *args, **kwargs)
            return jsonify({'value': 'Your basic authentication name or pass are invalid '})

        # last, proceed to the view if user is logined via login page
        return func(*args, **kwargs)
    return wrap

def _is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    """ Function that checks if redirect link is safe"""
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if _is_safe_url(target):
            return target
        return abort(400)
