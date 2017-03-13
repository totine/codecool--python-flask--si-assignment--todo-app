from todo import Todo
from users import User
from flask import Flask, render_template, request, session, redirect, g, url_for, flash
from common import login_required
import config
import datetime


app = Flask(__name__)

app.config.from_object(config.BaseConfig)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
@login_required
def td_list():
    """ Shows list of todo items stored in the database.
    """
    todo_list = Todo.get_all(session['user_id'])
    archive_list = Todo.get_all(session['user_id'], is_archived=True)
    return render_template('index.html', todo_list=todo_list, archive_list=archive_list)


@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_name = request.form['username']
        if User.is_user_with_name_in_user_list(user_name):
            user = User.get_by_name(user_name)
            if request.form['password'] != user.get_password():
                error = "Wrong password. Try again"
            else:
                session['logged_in'] = True
                session['user_id'] = user.get_id()
                session['user_name'] = user.get_name()
                flash("You are logged in!")
                return redirect(url_for('td_list'))
        else:
            error = "No user with such name. Try again"
    return render_template('login.html', error=error)


@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash("You are logged out!")
    return redirect(url_for('login'))


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
        item_due_date = request.form['due_date']
        if item_due_date:
            year, month, day = list(map(lambda x: int(x), item_due_date.split('-')))
            if datetime.date(year, month, day) < datetime.date.today():
                flash('Date should be current or future')
                temp_item = Todo(item_name, priority=item_priority)
                return render_template('add.html', action=url_for('add'),
                                       submit_title="Add", item=temp_item)
        new_todo = Todo(item_name, due_date=item_due_date, priority=item_priority,
                        owner_id=session['user_id'])
        new_todo.save()
        flash("New task was added!")
        return redirect('/')
    if request.method == 'GET':
        return render_template('add.html', action=url_for('add'), submit_title="Add")


@app.route("/index.html")
@login_required
def index():
    return redirect('/')


@app.route("/todo/<todo_id>/remove/")
@login_required
def remove(todo_id):
    """ Removes todo item with selected id from the database """
    item_to_remove = Todo.get_by_id(todo_id)
    if item_to_remove:
        item_to_remove.delete()
        flash('Item {} has been removed'.format(item_to_remove.get_name()))
        return redirect('/')
    flash('Item not found')
    return redirect('/')


@app.route("/todo/<todo_id>/edit", methods=['GET', 'POST'])
@login_required
def edit(todo_id):
    """ Edits todo item with selected id in the database
    If the method was GET it should show todo item form.
    If the method was POST it shold update todo item in database.
    """
    item_to_edit = Todo.get_by_id(todo_id)
    if request.method == 'POST':

        item_name = request.form['item_name']
        item_status = request.form['status']
        item_priority = request.form['priority']
        item_due_date = request.form['due_date']
        item_to_edit.name = item_name
        item_to_edit.status = item_status
        item_to_edit.priority = item_priority
        item_to_edit.due_date = item_due_date
        item_to_edit.save()
        return redirect(url_for('td_list'))
    if request.method == 'GET':
        return render_template('add.html', action=(url_for('edit', todo_id=todo_id)),
                               submit_title="Submit", item=item_to_edit, is_edit=True)


@app.route("/todo/<todo_id>/toggle")
@login_required
def toggle(todo_id):
    item_to_edit = Todo.get_by_id(todo_id)
    item_to_edit.toggle()
    item_to_edit.save()
    item_to_edit.save_status_change()
    return redirect(url_for('td_list'))


@app.route("/todo/<todo_id>/archive")
@login_required
def archive(todo_id):
    item_to_archive = Todo.get_by_id(todo_id)
    item_to_archive.is_archived = True
    item_to_archive.save()
    return redirect(url_for('td_list'))


@app.route("/todo/<todo_id>/activate")
@login_required
def activate(todo_id):
    pass


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form['user_name']
        if User.is_user_with_name_in_user_list(user_name, ):
            flash('Username {} is taken. Choose another one'.format(user_name))
            return render_template('user_form.html', action=url_for('signup'),
                                   submit_title="Sign up")
        password = request.form['password']
        confirmed_password = request.form['confirm_password']
        if password != confirmed_password:
            flash('Input password again')
            temp_user = User(user_name)
            return render_template('user_form.html', action=url_for('signup'),
                                   submit_title="Sign up", user=temp_user)
        new_user = User(user_name, password)
        new_user.save()
        new_user = User.get_by_name(new_user.name)
        session['logged_in'] = True
        session['user_id'] = new_user.get_id()
        session['user_name'] = new_user.name
        flash("Welcome {}. You've just signed up!".format(session['user_name']))
        return redirect(url_for('td_list'))
    return render_template('user_form.html', action=url_for('signup'), submit_title="Sign up")


@app.route("/user/new", methods=['GET', 'POST'])
@login_required
def add_user():
    pass


@app.route("/user/<user_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user_to_edit = User.get_by_id(user_id)
    if request.method == 'POST':
        new_user_name = request.form['user_name']
        if User.is_user_with_name_in_user_list(new_user_name, ):
            flash('Username {} is taken. Choose another one'.format(new_user_name))
            return render_template('user_form.html', action=url_for('edit_user', user_id=user_id),
                                   submit_title="Submit", user=user_to_edit)
        new_password = request.form['password']
        confirmed_password = request.form['confirm_password']
        if new_password != confirmed_password:
            flash('Input password again')
            return render_template('user_form.html', action=url_for('edit_user', user_id=user_id),
                                   submit_title="Submit", user=user_to_edit)
        user_to_edit.name = new_user_name
        if new_password:
            user_to_edit.password = new_password
        user_to_edit.save()
        flash("Changes were saved")
        return redirect(url_for('td_list'))
    return render_template('user_form.html', action=url_for('edit_user', user_id=user_id),
                           submit_title="Submit", user=user_to_edit)


@app.route("/user/<user_id>/remove")
@login_required
def remove_user(user_id):
    """ Removes user with selected id from the database """
    user_to_remove = User.get_by_id(user_id)
    if user_to_remove:
        user_to_remove.delete()
        return redirect('/')
    flash("No such user")
    redirect('/')


@app.route("/user/<user_id>")
@login_required
def show_user(user_id):
    pass


if __name__ == "__main__":

    app.run()
