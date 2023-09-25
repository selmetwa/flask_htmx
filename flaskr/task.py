from flask import (
    Blueprint, flash, render_template, request, Markup, redirect, url_for
)

from flaskr.db import get_db

bp = Blueprint('task', __name__)

@bp.route('/load_more_tasks/<page>', methods=(['POST']))
def load_more_tasks(page):
   print(page)
   limit = 5
   offset = int(page) * limit
   db = get_db()

   sqliteRows = db.execute(
       'SELECT t.id, title, description, priority_level, is_completed, created FROM tasks t ORDER BY created DESC LIMIT ? OFFSET ?',
       (limit, offset,)
    ).fetchall()

   count = db.execute('SELECT COUNT(*) from tasks').fetchone()[0]
   tasks = []
   for row in sqliteRows:
    tasks.append(dict(row))

   html_string = ''''''
   
   for task in tasks:
      buttons_block = ''
      is_completed = task['is_completed']
      class_name = 'completed' if is_completed else 'incomplete'
      if is_completed:
        buttons_block += '''
          <div class="completed_wrapper-{}">
            <button hx-post="/mark_as_incomplete/{}" hx-trigger="click" hx-target=".task_wrapper-{}" hx-swap="outerHTML">
              Mark as incomplete
            </button> 
          </div>
        '''.format(task['id'], task['id'], task['id'])
      else:
        buttons_block += '''
          <div class="completed_wrapper-{}">
            <button hx-post="/mark_as_completed/{}" hx-trigger="click" hx-target=".task_wrapper-{}" hx-swap="outerHTML">
              Mark as complete
            </button> 
          </div>
        '''.format(task['id'], task['id'], task['id'])
      html_block = '''
      <li class="task-card task_wrapper-{} hx-trigger="click" hx-get="/load_task_details/{}" hx-target=".drawer_content" hx-swap="innerHTML">
        <p hx-trigger="click" hx-target=".task_details_wrapper" hx-swap="innerHTML" hx-post="/load_task_details/{}" class={} onclick="openDrawer()">
          {}
        </p>
        <div class="task-buttons">
          <div class="completed_wrapper-{}">
            {}
          </div>
          <button hx-post="/delete_task/{}" hx-trigger="click" hx-confirm="Are you sure?" hx-target=".task_wrapper-{}" hx-swap="outerHTML">Delete</button>
        </div>
      </li>'''.format(task['id'], task['id'], task['id'], class_name, task['title'], task['id'], buttons_block, task['id'], task['id'])
      html_string += html_block
   
   if count > offset + limit:
    html_string += '''
      <div class="paginated-tasks">
        <button hx-trigger="click" hx-post="/load_more_tasks/{}" hx-target=".paginated-tasks" hx-swap="outerHTML">
          Load More
        </button>
        <p>Showing {} of {}</p>
      </div>
      '''.format((int(page) + 1), offset + limit, count)
   else:
      html_string += '''
        <p>Showing {} of {}</p>
      '''.format(count, count)

   return html_string

@bp.route('/', methods=(['GET']))
def index():
    db = get_db()

    sqliteRows = db.execute(
       'SELECT t.id, title, description, priority_level, is_completed, created FROM tasks t ORDER BY created DESC LIMIT 5'
    ).fetchall()

    count = db.execute('SELECT COUNT(*) from tasks').fetchone()[0]
    tasks = []
    for row in sqliteRows:
        tasks.append(dict(row))

    current = len(tasks)
    return render_template('task/index.html', tasks=tasks, count=count, current=current)

@bp.route('/delete_task/<id>', methods=(['POST']))
def delete_task(id):
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (id,))
    db.commit()

    return ''

# Only handle rendering of the template
def toggle_task(id, is_completed):
   db = get_db()
   updatedRow = db.execute('SELECT * from tasks WHERE id = ?', (id,)).fetchone()
   db.commit()
   task = dict(updatedRow)

   button_content = ''
   class_name = 'completed' if is_completed else 'incomplete'

   if (is_completed):
      button_content = '''
        <div class="completed_wrapper-{}">
          <button hx-post="/mark_as_incomplete/{}" hx-trigger="click" hx-target=".task_wrapper-{}" hx-swap="outerHTML">Mark as incomplete</button>
        </div>
      '''.format(id, id, id)
   else:
      button_content = '''
        <div class="completed_wrapper-{}">
          <button hx-post="/mark_as_completed/{}" hx-trigger="click" hx-target=".task_wrapper-{}" hx-swap="outerHTML">Mark as complete</button>
        </div>
      '''.format(id, id, id)

   content = '''
    <li class="task-card task_wrapper-{}">
      <p hx-trigger="click" hx-target=".task_details_wrapper" hx-swap="innerHTML" hx-post="/load_task_details/{}" class={} onclick="openDrawer()">
        {}
      </p>
      <div class="task-buttons">
        {}
        <button hx-post="/delete_task/{}" hx-trigger="click" hx-confirm="Are you sure?" hx-target=".task_wrapper-{}" hx-swap="outerHTML">Delete</button>
      </div>
    </li>
  '''.format(id, id, class_name, task['title'], button_content, id, id)

   return content

@bp.route('/mark_as_incomplete/<id>', methods=(['POST']))
def mark_as_incomplete(id):
   db = get_db()
   db.execute('UPDATE tasks SET is_completed = 0 WHERE id = ?', (id,))
   db.commit()
   
   return toggle_task(id, False)


@bp.route('/mark_as_completed/<id>', methods=(['POST']))
def mark_as_completed(id):
   db = get_db()
   db.execute('UPDATE tasks SET is_completed = 1 WHERE id = ?', (id,))
   db.commit()

   return toggle_task(id, True)

# @bp.route('/load_task_details/<id>', methods=(['POST']))
# def load_task_details(id):
#   db = get_db()

#   sqliteRow = db.execute('SELECT * FROM tasks t WHERE id = ?', (id,)).fetchone()
#   div_content = '''
#     <div>
#       Task Name: {}
#       Task Description: {}
#       Task Priority: {}
#       Is Task Completed: {}
#     </div>
#   '''.format(sqliteRow['title'], sqliteRow['description'], sqliteRow['priority_level'], sqliteRow['is_completed'])

#   return Markup(div_content)

@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':

      title = request.form['title']
      description = request.form['description']
      priority = request.form['priority']
      stream_id = request.form['stream_id']
      error = None

      if error is not None:
        flash(error)
      else:
         db = get_db()

         db.execute(
            'INSERT INTO tasks (title, description, priority_level, stream_id)'
            ' VALUES (?, ?, ?, ?)',
            (title, description, priority, stream_id)
         )
         db.commit()

      response_content = '''
          <div class="success_alert">
            <h3>Task Created Successfully</h3>
            <a href="/">Back To Tasks</a>
          </div>
        '''.format(title, stream_id)

      return Markup(response_content)

    db = get_db()
    sqliteRow = db.execute('SELECT s.stream_id, title FROM stream s ORDER BY created DESC').fetchall()
    streams = []
    for row in sqliteRow:
        streams.append(dict(row))
      
    return render_template('task/create.html', streams=streams)


@bp.route('/load_task_details/<id>', methods=(['GET']))
def load_task_details(id):
  db = get_db()
  taskRow = db.execute('SELECT * FROM tasks where id = ?', (id,)).fetchone()
  task = dict(taskRow)

  title = task['title']
  description = task['description']
  priority_level = task['priority_level']
  is_completed = task['is_completed']

  html_content = '''
    <div class="task_details">
      <h3>Task Details</h3>
      <p>Task Name: {}</p>
      <p>Task Description: {}</p>
      <p>Task Priority: {}</p>
      <p>Is Task Completed: {}</p>
    </div>
   '''.format(title, description, priority_level, is_completed)
  
  return html_content