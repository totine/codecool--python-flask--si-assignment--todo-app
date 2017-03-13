from flask import flash, url_for, redirect, session, g
from functools import wraps
from dbhandle import DB
from config import BaseConfig


# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


def get_db():
    db = getattr(g, '_database', None)
    if not db:
        db = g._database = DB.connect(BaseConfig.DATABASE)
    return db
