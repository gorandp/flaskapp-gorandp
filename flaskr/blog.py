from bson.objectid import ObjectId
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from datetime import datetime

from flaskr.auth import login_required
from flaskr.db import get_db
from .tools import char_limit

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.database["posts"].find()
    posts = sorted(posts, key=lambda post: post["created"])
    for p in posts:
        p['_id'] = str(p['_id'])
        p['authorId'] = str(p['authorId'])
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is None:
            e = char_limit(title, 50, 'Title')
            e += char_limit(body, 500, 'Body')
            if e:
                error = e

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.database["posts"].insert_one({
                "title": title,
                "body": body,
                "authorId": ObjectId(g.user['_id']),
                "created": datetime.utcnow()
            })
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().database["posts"].find_one({"_id": ObjectId(id)})
    post['_id'] = str(post['_id'])
    post['authorId'] = str(post['authorId'])

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['authorId'] != g.user['_id']:
        abort(403)

    return post


@bp.route('/<id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is None:
            e = char_limit(title, 50, 'Title')
            e += char_limit(body, 500, 'Body')
            if e:
                error = e

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.database["posts"].find_one_and_update(
                {"_id": ObjectId(id)},
                {"$set": {
                    "title": title,
                    "body": body
                }}
            )
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.database["posts"].delete_one({"_id": ObjectId(id)})
    return redirect(url_for('blog.index'))
