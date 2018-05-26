from flask import jsonify, render_template, url_for, flash, redirect, request
from wtforms.validators import ValidationError

from api import app, db, bcrypt
from api.forms import RegistrationForm, LoginForm
from api.models import entry_schema, Entry, User
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/set/", methods=["GET", "POST"])
@login_required
def set_entry():
    if request.method == 'POST':
        json_data = request.get_json()
        if json_data and 'key' in request.json and 'value' in request.json:
            try:
                if request.is_xhr:
                    data = entry_schema.load(json_data)[0]
                else:
                    data = entry_schema.load(json_data)
            except ValidationError as err:
                return jsonify(err.messages), 422
            key, value, user_id = data['key'], data['value'], current_user.id
            entry = Entry.query.filter_by(key=key).first()
            if entry is None:
                entry = Entry(key=key, value=value, user_id=user_id)
                db.session.add(entry)
                db.session.commit()
                return jsonify({'value': 'The entry with key {} was succesfully created'.format(key)})
            return jsonify({'value': 'The entry {} already exist'.format(key)})
        else:
            return jsonify({'value': 'Data structure must be {"key": "your key", "value": "your value"}'}), 400
    elif request.method == 'GET':
        return render_template('set.html')

@app.route("/get/", methods=["GET"])
@app.route("/get/<key>", methods=["GET"])
@login_required
def get_entry(key=None):
    if key is None and not request.is_xhr:
        return render_template('get.html')

    entry = Entry.query.filter_by(key=key).first()
    if entry:
        return entry_schema.jsonify(entry)
    else:
        return jsonify({'value': 'No value with this key in db'})

### register views
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('set_entry'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('set_entry'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('set_entry'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@login_required
@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')