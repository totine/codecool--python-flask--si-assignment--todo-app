import time
from dbhandle import DB
from common import get_db



class Todo:
    """ Class representing todo item."""

    def __init__(self, name, id_=None, status=0, create_date=None, priority=3, due_date=None, owner_id=None, is_archived=False):
        self.id = id_
        self.name = name
        self.status = status
        self.create_date = create_date if create_date else time.strftime("%Y-%m-%d %H:%M")
        self.priority = priority
        self.due_date = due_date
        self.is_archived = bool(is_archived)
        self.owner_id = owner_id
        self.last_modify_time_temp = None

    @property
    def last_modify_time(self):
        db = get_db()
        query = """SELECT MAX(`change_date`) FROM history WHERE `item_id`=?;"""
        values = (self.id, )
        modify_time = DB.execute_select_query(db, query, values)[0][0]
        return modify_time if modify_time else None

    def toggle(self):
        if self.status == 0:
            self.status = 1
        else:
            self.status = 0
        self.last_modify_time_temp = time.strftime("%Y-%m-%d %H:%M")

    def save(self):
        """ Saves/updates todo item in database """
        db = get_db()
        if self.id:
            query = "UPDATE `todo_items` SET `name` = ?, `status` = ?, " \
                    "`priority` = ?, `due_date` = ?, `is_archived` = ? WHERE id = ?;"
            values = (self.name, self.status, self.priority, self.due_date, int(self.is_archived), self.id)
            DB.execute_update_query(db, query, values)
        else:
            query = "INSERT INTO `todo_items` (`name`, `create_date`, `priority`, `due_date`, `owner_id`) " \
                    "VALUES (?, ?, ?, ?, ?); "
            values = (self.name, self.create_date, self.priority, self.due_date, self.owner_id)
            DB.execute_insert_query(db, query, values)

    def save_status_change(self):
        db = get_db()
        query = """INSERT INTO `history` (`item_id`, `change_date`, `status_after_change`)
                VALUES (?, ?, ?)"""
        values = (self.id, self.last_modify_time_temp, self.status)
        DB.execute_insert_query(db, query, values)

    def delete(self):
        db = get_db()
        """ Removes todo item from the database """
        query = "DELETE FROM `todo_items` WHERE `id` = ?"
        values = (self.id, )
        DB.execute_delete_query(db, query, values)

    @classmethod
    def get_all(cls, user_id, is_archived=False):
        """ Retrieves all Todos form database and returns them as list.
        Returns:
            list(Todo): list of all todos
        """
        db = get_db()
        todo_list = []
        query = "SELECT `name`, `id`, `status`, `create_date`, " \
                "`priority`, `due_date`, `owner_id`, `is_archived` " \
                "FROM `todo_items` " \
                "WHERE `is_archived` = ? AND `owner_id` = ?;"
        values = (int(is_archived), user_id)
        todo_items_from_db = DB.execute_select_query(db, query, values)
        for item in todo_items_from_db:
            todo_list.append(Todo(*item))
        return todo_list

    @classmethod
    def get_by_id(cls, id_):
        """ Retrieves todo item with given id from database.
        Args:
            id_(int): item id
        Returns:
            Todo: Todo object with a given id
        """
        db = get_db()
        query = "SELECT `name`, `id`, `status`, `create_date`, `priority`, `due_date`, `owner_id` " \
                "FROM `todo_items` " \
                "WHERE `todo_items`.`id` = ?;"
        values = (id_, )
        todo_item_from_db = DB.execute_select_query(db, query, values)
        return Todo(*todo_item_from_db[0]) if todo_item_from_db else None

    def get_name(self):
        return self.name



