from common import get_db
from dbhandle import DB
from models.todo import Todo
import time


class User:
    """Class representing todolist owners"""
    def __init__(self, name, password=None, id_=None, email=None, registration_date=None):
        self.id = id_
        self.name = name
        self.password = password
        self.email = email
        #  for new user registration date is set (current time), for existing user is taken from db
        self.registration_date = registration_date if registration_date else time.strftime("%Y-%m-%d %H:%M")

    @classmethod
    def get_users_list(cls):
        """ Retrieves all users from database and returns them as list.
        Returns:
            list(Userlist): list of all users
        """
        db = get_db()
        users = []
        query = """SELECT `name`, `password`, `id`, `email`, `registration_date` FROM `users`;"""
        users_from_db = DB.execute_select_query(db, query)
        for user in users_from_db:
            users.append(User(*user))
        return users

    @classmethod
    def get_by_id(cls, id_):
        """ Retrieves user with given id from database.
        Args:
            id_(int): user id
        Returns:
            Todo: User object with a given id
        """
        db = get_db()
        query = """SELECT `name`, `password`, `id`, `email`, `registration_date`
                   FROM `users`
                   WHERE `id` = ?;"""
        values = (id_, )
        user_from_db = DB.execute_select_query(db, query, values)
        return User(*user_from_db[0]) if user_from_db else None

    @classmethod
    def get_by_name(cls, name):
        """ Retrieves user with given name from database.
        Args:
            name(string): user name,
            db: dababase object
        Returns:
            User object with a given name
        """
        db = get_db()
        query = """SELECT `name`, `password`, `id`, `email`, `registration_date`
                   FROM `users`
                   WHERE `name` = ?;"""
        values = (name, )
        user_from_db = DB.execute_select_query(db, query, values)
        return User(*user_from_db[0])

    @classmethod
    def get_by_email(cls, email):
        """ Retrieves user with given name from database.
        Args:
            name(string): user name,
            db: dababase object
        Returns:
            User object with a given name
        """
        db = get_db()
        query = """SELECT `name`, `password`, `id`, `email`, `registration_date`
                   FROM `users`
                   WHERE `email` = ?;"""
        values = (email, )
        user_from_db = DB.execute_select_query(db, query, values)
        return User(*user_from_db[0])

    @classmethod
    def is_user_with_name_in_user_list(cls, name):
        """checks that is user with given name in database"""
        db = get_db()
        query = "SELECT * FROM users WHERE name=?"
        values = (name, )
        user_from_db = DB.execute_select_query(db, query, values)
        return bool(user_from_db)

    @classmethod
    def is_user_with_email_in_user_list(cls, email):
        """checks that is user with given email in database"""
        db = get_db()
        query = "SELECT * FROM users WHERE email=?"
        values = (email, )
        user_from_db = DB.execute_select_query(db, query, values)
        return bool(user_from_db)

    @property
    def active_todos_count(self):
        """connects with db and counts active todos for user"""
        db = get_db()
        query = """SELECT COUNT(`id`) FROM `todo_items`
                   WHERE `owner_id` = ? AND `is_archived` = 0;"""
        values = (self.id, )
        return DB.execute_select_query(db, query, values)[0][0]

    @property
    def active_todos_done_count(self):
        """connects with db and counts active todos with done status for user"""
        db = get_db()
        query = """SELECT COUNT(`id`) FROM `todo_items`
                   WHERE `owner_id` = ? AND `is_archived` = 0 AND `status` = 1;"""
        values = (self.id, )
        return DB.execute_select_query(db, query, values)[0][0]

    @property
    def active_todos_undone_count(self):
        """connects with db and counts active todos with undone status for user"""
        db = get_db()
        query = """SELECT COUNT(`id`) FROM `todo_items`
                   WHERE `owner_id` = ? AND `is_archived` = 0 AND `status` = 0;"""
        values = (self.id, )
        return DB.execute_select_query(db, query, values)[0][0]

    @property
    def archived_todos_count(self):
        """connects with db and counts archived todos for user"""
        db = get_db()
        query = """SELECT COUNT(`id`) FROM `todo_items`
                   WHERE `owner_id` = ? AND `is_archived` = 1;"""
        values = (self.id, )
        return DB.execute_select_query(db, query, values)[0][0]

    @property
    def is_admin(self):
        """checks that user has admin status """
        db = get_db()
        query = "SELECT users.id FROM users_permissions " \
                "JOIN users ON users.id=users_permissions.user_id " \
                "JOIN permission_types ON users_permissions.permission_id = permission_types.id " \
                "WHERE users.id = ? AND permission_types.name = ?"
        values = (self.id, 'admin')
        return bool(DB.execute_select_query(db, query, values))

    def save(self):
        """ Saves/updates user data in database """
        db = get_db()
        if self.id:  # user edit
            query = "UPDATE `users` SET `name` = ?, `password` = ?, `email` = ?, `registration_date` = ? " \
                    " WHERE id = ?;"
            values = (self.name, self.password, self.email, self.registration_date, self.id)
            DB.execute_update_query(db, query, values)
        else:  # new user
            query = "INSERT INTO `users` (`name`, `password`, `email`, `registration_date`) " \
                    "VALUES (?, ?, ?, ?); "
            values = (self.name, self.password, self.email, self.registration_date)
            DB.execute_insert_query(db, query, values)

    def delete(self):
        """ Removes user from the database """
        db = get_db()
        query = "DELETE FROM `users` WHERE `id` = ?"
        values = (self.id, )
        DB.execute_delete_query(db, query, values)
        Todo.delete_todos_by_user_id(self.id)

    def set_admin_status(self, is_admin):
        """toggle admin status for user - add new record or delete existed record
           in user permission table"""
        db = get_db()
        if self.is_admin != is_admin:
            if self.is_admin:
                query = "DELETE FROM users_permissions WHERE user_id = ?"
                values = (self.id, )
                DB.execute_delete_query(db, query, values)
            else:
                query = "INSERT INTO `users_permissions` (user_id, permission_id) VALUES (?, ?)"
                values = (self.id, 1)
                DB.execute_insert_query(db, query, values)

    def get_password(self):
        return self.password
