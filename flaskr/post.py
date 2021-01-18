from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from flaskr.auth import login_required
from flaskr.db import get_db

from uuid import uuid1
import os

VALID_FILE_TYPES={'jpg', 'png', 'jpeg'}
IMAGE_FOLDER = './flaskr/static/images'

bp = Blueprint('post', __name__)\

#helper functions ----------------------------------------------

#check if filename is a valid image file
def valid_file(filename):
    if filename.split('.')[-1].lower() in VALID_FILE_TYPES:
        return True
    else:
        return False

#used to prevent duplicates while saving to a folder
def make_unique(string):
    id = uuid1().__str__()[:10]
    return id + "-" + string

#-----------------------------------------------------------------

#home page
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'select p.id, title, filepath, created, user_id, private, username, price'
        ' from posts p join users u on p.user_id = u.id'
        ' order by created desc'
    ).fetchall()
    
    #check the queried posts' privacy level and render template based on that.
    temp = []
    for post in posts:
        #check if the post is private and the current post's id is not the same as current session's id, then remove it from posts to be rendered
        if post['private'] == 0:
            temp.append(post)
        elif g.user:
            if post['user_id'] == g.user['id']:
                temp.append(post)

    return render_template('post/index.html', posts = temp)


#create page
@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        price = None
        error = None

        #is_private variable uses 0/1 integers since SQLite3 doesn't allow for boolean values anyway
        if request.form['privacy'] == 'private':
            is_private = 1
        else:
            is_private = 0

            if not request.form['price']:
                error = 'Price is required'
            else:
                price = int(request.form['price'])
                if price < 0:
                    error = 'Price greater than 0 is required'
            
        if not title:
            error = 'Title is required.'
        
        if 'files' not in request.files:
            error = 'No file part'
        else:
            files = request.files.getlist("files")
        
        for file in files:
            if not file.filename:
                error = 'A file has no file name'

            if not valid_file(file.filename):
                error = 'A File\'s type is invalid'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            for file in files:
                #rename the file to unique file
                unique_filename = make_unique(secure_filename(file.filename))

                #save the file to images folder
                file.save(os.path.join(IMAGE_FOLDER,unique_filename))

                #saving data to db
                db.execute(
                    'insert into posts (title, filepath, user_id, private, price)'
                    ' values (?,?,?,?,?)',
                    (title, unique_filename, g.user['id'], is_private, price)
                )
            db.commit()
            return redirect(url_for('post.index'))
    
    return render_template('post/create.html')

@bp.route('/buy/<int:id>')
@login_required
def buy(id):
    db = get_db()
    error = None
    post = db.execute(
        'select id, user_id, price'
        ' from posts where id = ?',
        (id,)
    ).fetchone()
    buyer = db.execute('select id, balance from users where id = ?', (g.user['id'],)).fetchone()
    seller = db.execute('select id, balance from users where id = ?', (post['user_id'],)).fetchone()

    if buyer['balance'] - post['price'] < 0:
        error = 'User does not have sufficient funds.'

    if error:
        flash(error)
    else:
        #update buyer balance
        db.execute('update users set balance = ? where id = ?', (buyer['balance'] - post['price'], buyer['id']))
        #update seller balance
        db.execute('update users set balance = ? where id = ?', (seller['balance'] + post['price'], seller['id']))

        db.commit()
        
    return redirect(url_for('post.index'))
