from flask import (
    Blueprint, flash, render_template, request, Markup
)

from flaskr.db import get_db

bp = Blueprint('stream', __name__)

@bp.route('/streams', methods=(['GET']))
def streams():
    db = get_db()

    sqliteRows = db.execute(
       'SELECT s.stream_id, title, description, priority_level, created FROM stream s ORDER BY created DESC'
    ).fetchall()

    streams = []
    for row in sqliteRows:
        streams.append(dict(row))

    return render_template('streams/streams.html', streams=streams)

@bp.route('/create_stream', methods=(['GET', 'POST']))
def create_stream():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority_level = request.form['priority']

        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO stream (title, description, priority_level) VALUES (?, ?, ?)',
                (title, description, priority_level)
            )
            db.commit()

    return render_template('streams/create_stream.html')

@bp.route('/stream_details/<id>', methods=(['GET']))
def stream_details(id):
  db = get_db()

  sqliteRowStream = db.execute('SELECT * FROM stream s WHERE stream_id = ?', (id,)).fetchone()
  sqliteRowsTasksInStream = db.execute('SELECT * FROM tasks t WHERE stream_id = ?', (id,)).fetchall()
  stream = dict(sqliteRowStream)
  tasksInStream = []
  for row in sqliteRowsTasksInStream:
    tasksInStream.append(dict(row))
  print(stream)
  print(tasksInStream)
  
  return render_template('streams/stream_details.html', stream=stream, tasks=tasksInStream)