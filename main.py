from models.todo import Todo
from models.todolist import TodoList
from models.users import User
from flask import Flask, render_template, request, session, redirect, g, url_for, flash
from common import login_required, admin_only
import config
import datetime


app = Flask(__name__)
app.config.from_object(config.BaseConfig)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/", methods=['GET', 'POST'])
@login_required
def td_list():
    """ Shows list of todo items stored in the database.
    """

    user = User.get_by_id(session['user_id'])
    new_todolist = TodoList(user)
    sort_types = {'name': new_todolist.sort_by_name,
                  'priority': new_todolist.sort_by_priority,
                  'due date': new_todolist.sort_by_due_date,
                  'create date': new_todolist.sort_by_create_date,
                  'status': new_todolist.sort_by_status}
    if request.method == 'GET':
        session['sort_type'] = 'create date'
        session['sort_direct'] = 'asc'
        sort_types[session['sort_type']](is_desc=True if session['sort_direct'] == 'desc' else False)
    if request.method == "POST" and new_todolist:
        sort_type = request.form['sort']
        if session['sort_type'] == sort_type:
            session['sort_direct'] = 'asc' if session['sort_direct'] == 'desc' else 'desc'
        else:
            session['sort_direct'] = 'asc'
        sort_types[sort_type](is_desc=session['sort_direct'] == 'desc')

        session['sort_type'] = sort_type
    todo_list = new_todolist.active_todos
    archive_list = new_todolist.archived_todos
    return render_template('index.html', todo_list=todo_list, archive_list=archive_list)


@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_name = request.form['username']
        if User.is_user_with_name_in_user_list(user_name) \
                or User.is_user_with_email_in_user_list(user_name):
            user = User.get_by_name(user_name) if User.is_user_with_name_in_user_list(user_name) \
                else User.get_by_email(user_name)
            if request.form['password'] != user.get_password():
                error = "Wrong password. Try again"
            else:
                session['logged_in'] = True
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['is_admin'] = True if user.is_admin else None
                session['sort_type'] = 'create date'
                session['sort_direct'] = 'desc'
                flash("You are logged in!")
                return redirect(url_for('td_list')) if not user.is_admin else redirect(url_for('admin_panel'))
        else:
            error = "No user with such name. Try again"
    return render_template('login.html', error=error)


@app.route("/logout")
def logout():
    session_out()
    flash("You are logged out!")
    return redirect(url_for('login'))


def session_out():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('is_admin', None)
    session.pop('user_name', None)
    session.pop('sort_type', None)


@app.route("/todo/new", methods=['GET', 'POST'])
@login_required
def add():
    """ Creates new todo item
    If the method was GET it should show new item form.
    If the method was POST it shold create and save new todo item.
    """
    if request.method == 'POST':
        item_name = request.form['item_name']
        item_priority = request.form['priority']
        item_due_date = request.form['due_date'] if request.form['due_date'] else None
        item_description = request.form['description'] if request.form['description'] else None
        if item_due_date:
            year, month, day = list(map(lambda x: int(x), item_due_date.split('-')))
            if datetime.date(year, month, day) < datetime.date.today():
                flash('Date should be current or future')
                temp_item = Todo(item_name, priority=item_priority, description=item_description)
                return render_template('todo_form.html', action=url_for('add'),
                                       submit_title="Add", item=temp_item)
        new_todo = Todo(item_name, due_date=item_due_date, priority=item_priority,
                        owner_id=session['user_id'], description=item_description)
        new_todo.save()
        flash("New task was added!")
        return redirect('/')
    if request.method == 'GET':
        return render_template('todo_form.html', action=url_for('add'), submit_title="Add", is_edit=False)


@app.route("/todo/<int:item_id>")
@login_required
def show_todo(item_id):
    item_to_show = Todo.get_by_id(item_id)
    if not item_to_show:
        flash("No such todo item")
        return redirect('/')
    if item_to_show.owner_id == session['user_id'] or session['is_admin']:
        return render_template('show_todo.html', item=item_to_show)
    else:
        flash('Access denied')
        return redirect('/')


@app.route("/index.html")
@login_required
def index():
    return redirect('/')


@app.route("/todo/<int:todo_id>/remove/")
@login_required
def remove(todo_id):
    """ Removes todo item with selected id from the database """

    item_to_remove = Todo.get_by_id(todo_id)
    if not item_to_remove:
        flash("No such todo item")
        return redirect('/')
    if item_to_remove:
        item_to_remove.delete()
        flash('Item {} has been removed'.format(item_to_remove.name.encode('utf-8')))
        return redirect('/')
    flash('Item not found')
    return redirect('/')


@app.route("/todo/<int:todo_id>/edit", methods=['GET', 'POST'])
@login_required
def edit(todo_id):
    """ Edits todo item with selected id in the database
    If the method was GET it should show todo item form.
    If the method was POST it should update todo item in database.
    """
    item_to_edit = Todo.get_by_id(todo_id)
    if not item_to_edit:
        flash("No such todo item")
        return redirect('/')
    if request.method == 'POST':
        item_name = request.form['item_name']
        if not item_to_edit.is_archived:
            item_status = request.form['status']
            if item_status and int(item_status) != item_to_edit.status:
                item_to_edit.toggle()
        item_priority = request.form['priority']
        item_due_date = request.form['due_date'] if request.form['due_date'] else None
        item_description = request.form['description'] if request.form['description'] else None
        item_to_edit.name = item_name
        item_to_edit.priority = item_priority
        item_to_edit.due_date = item_due_date
        item_to_edit.description = item_description
        item_to_edit.save()
        flash("Item {} edited".format(item_to_edit.name.encode('utf-8')))
        return redirect(url_for('td_list'))
    if request.method == 'GET':
        return render_template('todo_form.html', action=(url_for('edit', todo_id=todo_id)),
                               submit_title="Submit", item=item_to_edit, is_edit=True)


@app.route("/todo/<int:todo_id>/toggle")
@login_required
def toggle(todo_id):
    item_to_edit = Todo.get_by_id(todo_id)
    if not item_to_edit:
        flash("No such todo item")
        return redirect('/')
    item_to_edit.toggle()
    item_to_edit.save()
    return redirect(url_for('td_list'))


@app.route("/todo/<int:todo_id>/archive")
@login_required
def archive(todo_id):
    item_to_archive = Todo.get_by_id(todo_id)
    if not item_to_archive:
        flash("No such todo item")
        return redirect('/')
    item_to_archive.is_archived = True
    item_to_archive.save()
    item_to_archive.update_history('archive')
    flash('Item {} moved to archive'.format(item_to_archive.name.encode('utf-8')))
    return redirect(url_for('td_list'))


@app.route("/todo/<todo_id>/activate")
@login_required
def activate(todo_id):
    item_to_activate = Todo.get_by_id(todo_id)
    if not item_to_activate:
        flash("No such todo item")
        return redirect('/')
    item_to_activate.is_archived = False
    item_to_activate.status = 0
    item_to_activate.save()
    item_to_activate.update_history('activate')
    flash('Item {} is active again'.format(item_to_activate.name.encode('utf-8')))
    return redirect(url_for('td_list'))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form['user_name']
        email = request.form['email']
        if User.is_user_with_name_in_user_list(user_name):
            flash('Username {} is taken. Choose another one'.format(user_name.encode('utf-8')))
            temp_user = User(name=None, email=email)
            return render_template('user_form.html', action=url_for('signup'),
                                   submit_title="Sign up", user=temp_user)
        if User.is_user_with_email_in_user_list(email):
            temp_user = User(user_name)
            flash('Email {} is taken. Choose another one'.format(email.encode('utf-8')))
            return render_template('user_form.html', action=url_for('signup'),
                                   submit_title="Signup", user=temp_user)
        password = request.form['password']
        confirmed_password = request.form['confirm_password']
        if password != confirmed_password:
            flash('Input password again')
            temp_user = User(user_name, email)
            return render_template('user_form.html', action=url_for('signup'),
                                   submit_title="Signup", user=temp_user)
        new_user = User(user_name, password, email=email)
        new_user.save()
        new_user = User.get_by_name(new_user.name)
        session['logged_in'] = True
        session['user_id'] = new_user.id
        session['user_name'] = new_user.name.encode('utf-8')
        flash("Welcome {}. You've just signed up!".format(str(session['user_name'])))
        return redirect(url_for('td_list'))
    return render_template('user_form.html', action=url_for('signup'), submit_title="Signup")


@app.route("/users")
@admin_only
@login_required
def users_list():
    users = User.get_users_list()
    if not users:
        flash("There are no users.")
        return redirect('/')
    return render_template('includes/users_list.html', users=users)


@app.route("/users/new", methods=['GET', 'POST'])
@admin_only
@login_required
def add_user():
    if request.method == 'POST':
        user_name = request.form['user_name']
        email = request.form['email']
        if User.is_user_with_name_in_user_list(user_name):
            flash('Username {} is taken. Choose another one'.format(user_name.encode('utf-8')))
            return render_template('user_form.html', action=url_for('add_user'),
                                   submit_title="Add")
        if User.is_user_with_email_in_user_list(email):
            flash('Email {} is taken. Choose another one'.format(email))
            return render_template('user_form.html', action=url_for('add_user'),
                                   submit_title="Add")
        password = request.form['password']
        confirmed_password = request.form['confirm_password']
        if password != confirmed_password:
            flash('Input password again')
            temp_user = User(user_name, email=email)
            return render_template('user_form.html', action=url_for('add_user'),
                                   submit_title="Add", user=temp_user)
        new_user = User(user_name, password, email=email)
        new_user.save()
        if 'is_admin' in session:
            new_user = User.get_by_email(email)
            new_user.set_admin_status(bool(request.form.get('admin')))
        flash("User {} added to user list".format(new_user.name.encode('utf-8')))
        return redirect(url_for('admin_panel'))
    return render_template('user_form.html', action=url_for('add_user'), submit_title="Add")


@app.route("/users/<int:user_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if session['user_id'] == user_id or session['is_admin']:
        user_to_edit = User.get_by_id(user_id)
        if not user_to_edit:
            flash("No such user")
            return redirect('/')
        if request.method == 'POST':
            new_user_name = request.form['user_name']
            if new_user_name != user_to_edit.name and User.is_user_with_name_in_user_list(new_user_name, ):
                flash('Username {} is taken. Choose another one'.format(new_user_name.encode('utf-8')))
                return render_template('user_form.html', action=url_for('edit_user', user_id=user_id),
                                       submit_title="Submit", user=user_to_edit)
            new_email = request.form['email']
            if new_email != user_to_edit.email and User.is_user_with_email_in_user_list(new_email):
                flash('Email {} is taken. Choose another one'.format(new_email.encode('utf-8')))
                return render_template('user_form.html', action=url_for('edit_user'),
                                       submit_title="Submit")
            new_password = request.form['password']
            confirmed_password = request.form['confirm_password']
            if new_password != confirmed_password:
                flash('Input password again')
                return render_template('user_form.html', action=url_for('edit_user', user_id=user_id),
                                       submit_title="Submit", user=user_to_edit)
            user_to_edit.name = new_user_name
            user_to_edit.email = new_email
            if new_password:
                user_to_edit.password = new_password
            user_to_edit.save()
            if 'is_admin' in session:
                user_to_edit.set_admin_status(bool(request.form.get('admin')))
            flash("Changes were saved")
            return redirect(url_for('admin_panel'))
        return render_template('user_form.html', action=url_for('edit_user', user_id=user_id),
                               submit_title="Submit", user=user_to_edit, is_edit=True)
    else:
        flash('Access denied')
        return redirect('/')


@app.route("/users/<int:user_id>/remove")
@login_required
def remove_user(user_id):
    """ Removes user with selected id from the database """
    if session['user_id'] == user_id or session['is_admin']:
        user_to_remove = User.get_by_id(user_id)
        if user_to_remove:
            return redirect(url_for('remove_user_confirm', user_id=user_to_remove.id))
        flash("No such user")
        redirect('/')
    else:
        flash('Access denied')
        return redirect('/')


@app.route("/users/<int:user_id>/remove/confirm", methods=['GET', 'POST'])
@login_required
def remove_user_confirm(user_id):
    """  """
    if session['user_id'] == user_id or session['is_admin']:
        if request.method == 'POST':
            password = request.form['password']
            confirmed_password = request.form['confirm_password']
            if password != confirmed_password:
                flash("Passwords don't match. Try again.")
                return render_template('remove_confirm.html', user_id=user_id)
            user_to_remove = User.get_by_id(user_id)
            if 'is_admin' in session and session['is_admin'] == True:
                admin = User.get_by_id(session['user_id'])
                if password == admin.get_password():
                    user_to_remove.delete()
                    flash("User {} has been removed".format(user_to_remove.name.encode('utf-8')))
                    return redirect(url_for('admin_panel'))
                else:
                    flash("Wrong password. Try again")
                    return render_template('remove_confirm.html', user_id=user_id)
            else:
                if user_to_remove.get_password() == password:
                    user_to_remove.delete()
                    session_out()
                    flash("Your account has been deleted")
                    return redirect(url_for('login'))
                else:
                    flash("Wrong password. Try again")
                    return render_template('remove_confirm.html', user_id=user_id)
        return render_template('remove_confirm.html', user_id=user_id)
    else:
        flash('Access denied')
        return redirect('/')


@app.route("/users/<int:user_id>")
@login_required
def show_user(user_id):
    user_to_show = User.get_by_id(user_id)
    if not user_to_show:
        flash("No such user")
        return redirect('/')
    if session['user_id'] == user_id or session['is_admin']:
        return render_template('show_user.html', user=user_to_show)
    else:
        flash('Access denied')
        return redirect('/')


@app.route("/admin")
@login_required
@admin_only
def admin_panel():
    users = User.get_users_list()
    if not users:
        flash("No users")
        return redirect('/')
    return render_template('admin_panel.html', users=users)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run()

