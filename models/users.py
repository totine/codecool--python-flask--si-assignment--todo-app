from common import get_db
from dbhandle import DB


class User:
    def __init__(self, name, password=None, id_=None):
        self.id = id_
        self.name = name
        self.password = password

    @classmethod
    def get_users_list(cls):
        db = get_db()
        users = []
        query = """SELECT `name`, `password`, `id` FROM `users`;"""
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
        query = """SELECT `name`, `password`, `id`
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
        query = """SELECT `name`, `password`, `id`
                   FROM `users`
                   WHERE `name` = ?;"""
        values = (name, )
        user_from_db = DB.execute_select_query(db, query, values)
        return User(*user_from_db[0])

    @classmethod
    def is_user_with_name_in_user_list(cls, name):
        db = get_db()
        query = "SELECT * FROM users WHERE name=?"
        values = (name, )
        user_from_db = DB.execute_select_query(db, query, values)
        return bool(user_from_db)

    def save(self):
        """ Saves/updates user data in database """
        db = get_db()
        if self.id:
            query = "UPDATE `users` SET `name` = ?, `password` = ? WHERE id = ?;"
            values = (self.name, self.password, self.id)
            DB.execute_update_query(db, query, values)
        else:
            query = "INSERT INTO `users` (`name`, `password`) VALUES (?, ?); "
            values = (self.name, self.password)
            DB.execute_insert_query(db, query, values)

    def delete(self):
        """ Removes user from the database """
        db = get_db()
        query = "DELETE FROM `users` WHERE `id` = ?"
        values = (self.id, )
        DB.execute_delete_query(db, query, values)

    def get_password(self):
        return self.password

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name
