import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods = ('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        #username field is empty
        if not username:
            error = 'Username is required.'
        #password field is empty
        elif not password:
            error = 'Password is required.'
        #check if the user has already registered
        elif db.execute(
            'select id from user where username = ?', (username,)
        ).fetchone() is not None:
            error = 'User ' + username + ' is already registered'

        """if the requested user registration is valid,
            then insert the new user into the db,
            then redirect the user to the login page.
        """
        if error is None:
            db.execute(
                'insert into user (username, password) VALUES(?,?)',
                (username, generate_password_hash(password))
            )
            db.commit()
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
        user = db.execute(
            'select * from user where username = ?', (username,)
        ).fetchone()
        
        #user does not exist in db
        if user is None:
            error = 'Incorrect username.'
        #password entered does not match password in db
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        #no error is found store the user's id to the session then redirect to home page
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

"""
before each request, if the current session has a user id stored
then get their data from the data base and store it in g.user
which lasts for the request. If the current session does not
have a user id stored, then leave g.user as none.
"""
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user where id = ?', (user_id,)
        ).fetchone()

#logging out, simply remove user info from session
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#decorator used to check if a user is logged in
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view