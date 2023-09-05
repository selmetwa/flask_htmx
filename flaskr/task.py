from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Markup
)
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint('task', __name__)

@bp.route('/', methods=(['GET']))
def index():
    db = get_db()

    sqliteRows = db.execute(
       'SELECT t.id, title, description, priority_level, is_completed, created FROM tasks t ORDER BY created DESC'
    ).fetchall()

    tasks = []
    for row in sqliteRows:
        tasks.append(dict(row))

    return render_template('task/index.html', tasks=tasks)

@bp.route('/delete_task/<id>', methods=(['POST']))
def delete_task(id):
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (id,))
    db.commit()

    return ''

@bp.route('/mark_as_incomplete/<id>', methods=(['POST']))
def mark_as_incomplete(id):
   db = get_db()
   db.execute('UPDATE tasks SET is_completed = 0 WHERE id = ?', (id,))
   db.commit()
   
   content = '''
    <div class="completed_wrapper-{}">
      <button hx-post="/mark_as_completed/{}" hx-trigger="click" hx-target=".completed_wrapper-{}" hx-swap="innerHTML">
        Mark as complete
      </button>
    </div>
   '''.format(id, id, id)

   return Markup(content)

@bp.route('/mark_as_completed/<id>', methods=(['POST']))
def mark_as_completed(id):
   db = get_db()
   db.execute('UPDATE tasks SET is_completed = 1 WHERE id = ?', (id,))
   db.commit()

   content = '''
    <div class="completed_wrapper-{}">
      <button hx-post="/mark_as_incomplete/{}" hx-trigger="click" hx-target=".completed_wrapper-{}" hx-swap="innerHTML">
        Mark as incomplete
      </button>
    </div>
   '''.format(id, id, id)
   
   return Markup(content)

@bp.route('/load_task_details/<id>', methods=(['POST']))
def load_task_details(id):
  db = get_db()

  sqliteRow = db.execute('SELECT * FROM tasks t WHERE id = ?', (id,)).fetchone()
  div_content = '''
    <div>
      Task Name: {}
      Task Description: {}
      Task Priority: {}
      Is Task Completed: {}
    </div>
  '''.format(sqliteRow['title'], sqliteRow['description'], sqliteRow['priority_level'], sqliteRow['is_completed'])

  return Markup(div_content)

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

         db.execute(
            'INSERT INTO tasks (title, description, priority_level, stream_id)'
            ' VALUES (?, ?, ?, ?)',
            (title, description, priority, None)
         )
         db.commit()

      response_content = '''
          <div>
            <p>Task Created Successfully</p>
            <p>Task name: {}</p>
          </div>
        '''.format(title)

      return Markup(response_content)

    return render_template('task/create.html')