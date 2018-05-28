from flask import jsonify, render_template, url_for, flash, redirect, request, g
from flask_login import login_user, current_user, logout_user, login_required

from api import app, db, bcrypt
from api.forms import RegistrationForm, LoginForm
from api.models import entry_schema, Entry, User
from api.utils import (
    set_entry_processing,
    get_entry_processing,
    custom_auth,
    get_redirect_target
)


### API views

@app.route("/set/", methods=["GET", "POST"])
@custom_auth
def set_entry():
    # login auth 
    if current_user.is_authenticated:
        if request.method == 'POST':
            return set_entry_processing(current_user.id)
        elif request.method == 'GET':
            return render_template('set.html')
    # api_key or base auth
    if g.get('user'):
        return set_entry_processing(g.get('user').id)
    return redirect(url_for('login'))


@app.route("/get/", methods=["GET"])
@app.route("/get/<key>", methods=["GET"])
@custom_auth
def get_entry(key=None):
    #TODO take access to the current_user variable in custom_auth decorator to get rid of excess if statements
    # login auth
    if current_user.is_authenticated:
        if key is None and not request.is_xhr:
            return render_template('get.html')
        return get_entry_processing(current_user.id, key)

    # api_key or base auth
    if g.get('user'):
        return get_entry_processing(g.user.id, key)

    #redirect to login if no auth
    return redirect(url_for('login'))


### Register views

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
            next_page = get_redirect_target()
            return redirect(next_page or url_for('login'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')