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

bp = Blueprint('blog', __name__)\

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
        'select p.id, title, image, created, author_id, private, username'
        ' from post p join user u on p.author_id = u.id'
        ' order by created desc'
    ).fetchall()
    
    #check the queried posts' privacy level and render template based on that.
    temp = []
    for post in posts:
        #check if the post is private and the current post's id is not the same as current session's id, then remove it from posts to be rendered
        if post['private'] == 0:
            temp.append(post)
        elif g.user:
            if post['author_id'] == g.user['id'] and post['private'] == 1:
                temp.append(post)

    return render_template('blog/index.html', posts = temp)


#create page
@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']

        #is_private variable uses 0/1 integers since SQLite3 doesn't allow for boolean values anyways
        print(request.form['privacy'])
        if request.form['privacy'] == 'private':
            is_private = 1
        else:
            is_private = 0
        
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
                print(is_private)
                #rename the file to unique file
                unique_filename = make_unique(secure_filename(file.filename))

                #save the file to images folder
                file.save(os.path.join(IMAGE_FOLDER,unique_filename))

                #saving data to db
                db.execute(
                    'insert into post (title, image, author_id, private)'
                    ' values (?,?,?,?)',
                    (title, unique_filename, g.user['id'], is_private)
                )
            db.commit()
            return redirect(url_for('blog.index'))
    
    return render_template('blog/create.html')