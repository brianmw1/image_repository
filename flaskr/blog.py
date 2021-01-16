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

bp = Blueprint('blog', __name__)

#home page
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'select p.id, title, image, created, author_id, username'
        ' from post p join user u on p.author_id = u.id'
        ' order by created desc'
    ).fetchall()
    return render_template('blog/index.html', posts = posts)

def valid_file(filename):
    if filename.split('.')[-1].lower() in VALID_FILE_TYPES:
        return True
    else:
        return False

#used to prevent duplicates while saving to a folder
def make_unique(string):
    id = uuid1().__str__()[:10]
    return id + "-" + string


#create page
@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        error = None

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
                    'insert into post (title, image, author_id)'
                    ' values (?,?,?)',
                    (title, unique_filename, g.user['id'])
                )
            db.commit()
            return redirect(url_for('blog.index'))
    
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'select p.id, title, body, created, author_id, username'
        ' from post p join user u on p.author_id = u.id'
        ' where p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))\

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('delete from post where id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))