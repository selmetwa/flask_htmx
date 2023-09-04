from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint('task', __name__)

@bp.route('/', methods=(['GET']))
def index():
    db = get_db()

    sqliteRows = db.execute(
       'SELECT t.id, title, description, priority_level, created FROM tasks t ORDER BY created DESC'
    ).fetchall()

    tasks = []
    for row in sqliteRows:
        tasks.append(dict(row))

    print("sqliteRows: ", sqliteRows)
    print("tasks: ", tasks)
    return render_template('task/index.html', tasks=tasks)

@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':

      title = request.form['title']
      description = request.form['description']
      priority = request.form['priority']
      error = None

      if error is not None:
        flash(error)
      else:
         db = get_db()
         print("title: ", title) 
         print("description: ", description)
         print("priority: ", priority)

         db.execute(
            'INSERT INTO tasks (title, description, priority_level, stream_id)'
            ' VALUES (?, ?, ?, ?)',
            (title, description, priority, None)
         )
         db.commit()

    return render_template('task/create.html')