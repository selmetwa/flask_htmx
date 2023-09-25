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
  
  return render_template('streams/stream_details.html', stream=stream, tasks=tasksInStream)


@bp.route('/render_add_task_to_stream_view/<id>', methods=(['GET']))
def render_add_task_to_stream_view(id):
    return '''
    <form class="form" hx-post="/add_task_to_stream/{}" hx-target=".task-list" hx-swap="innerHTML" hx-on::after-request="this.reset()">
      <h2>Create New Task</h2>
      <label>Task Title</label>
      <input type="text" name="title" id="title" />
      <label for="priority">Choose a priority level from 1-5</label>
      <select name="priority" id="priority">
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="4">4</option>
        <option value="5">5</option>
      </select>
      <label for="description">Description</label>
      <textarea name="description" id="description">
      </textarea>
      <button type="submit">Submit</button>
    </form>
'''.format(id)

@bp.route('/add_task_to_stream/<id>', methods=(['POST']))
def add_task_to_stream(id):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority_level = request.form['priority']
        stream_id = id

        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tasks (title, description, priority_level, stream_id) VALUES (?, ?, ?, ?)',
                (title, description, priority_level, stream_id)
            )
            db.commit()

        tasks_in_stream = db.execute('SELECT * FROM tasks t WHERE stream_id = ?', (id,)).fetchall()

        html_string = '''
          <button hx-trigger="click" hx-target=".task-list" hx-get="/render_add_task_to_stream_view/{}" hx-swap="innerHTML">Add Task To Stream</button>
        '''.format(id)

        for row in tasks_in_stream:
            task = dict(row)
            html_block = '''
            <li class="task-card task_wrapper-{}">
              <p hx-trigger="click" hx-get="/load_task_details/{}" hx-target=".drawer_content" hx-swap="innerHTML" onclick="openDrawer()">
                {}
              </p>
              <div class="task-buttons">
                <div class="completed_wrapper-{}">
                <button hx-post="/mark_as_completed/{}" hx-trigger="click" hx-target=".completed_wrapper-{}" hx-swap="outerHTML">
                  Mark as complete
                </button>
                </div>
                <button hx-post="/delete_task/{}" hx-trigger="click" hx-confirm="Are you sure?" hx-target=".task_wrapper-{}" hx-swap="outerHTML">Delete</button>
              </div>
            </li>'''.format(task['id'], task['id'], task['title'], task['id'], task['id'], task['id'], task['id'], task['id'])
            html_string += html_block

    return html_string