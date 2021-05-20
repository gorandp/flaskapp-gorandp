import functools
from bson.objectid import ObjectId
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from .tools import char_limit


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        e = char_limit(username, 15, 'Username')
        e += char_limit(password, 50, 'Password')
        if e:
            error = e

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.database["users"].find_one({
            "username": username
        }) is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.database["users"].insert_one({
                "username": username,
                "password": generate_password_hash(password)
            })
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.database["users"].find_one({
            "username": username
        })

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        user['_id'] = str(user['_id'])
        if error is None:
            session.clear()
            session['user_id'] = user['_id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        user = get_db().database["users"].find_one({
            "_id": ObjectId(user_id)
        })
        user['_id'] = str(user['_id'])
        g.user = user


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
