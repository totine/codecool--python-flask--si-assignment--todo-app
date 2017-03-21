import time
from dbhandle import DB
from common import get_db


class Todo:
    """ Class representing todo item."""

    def __init__(self, name, id_=None, status=0, create_date=None, priority=0, due_date=None, owner_id=None,
                 is_archived=False, description=None):
        self.id = id_
        self.name = name
        self.status = status
        self.create_date = create_date if create_date else time.strftime("%Y-%m-%d %H:%M")
        self.priority = priority
        self.due_date = due_date
        self.is_archived = bool(is_archived)
        self.owner_id = owner_id
        self.description = description

    @classmethod
    def get_all(cls, user_id, is_archived=False):
        """ Retrieves all Todos form database and returns them as list.
        Returns:
            list(Todo): list of all todos
        """
        db = get_db()
        todo_list = []
        query = "SELECT `name`, `id`, `status`, `create_date`, " \
                "`priority`, `due_date`, `owner_id`, `is_archived`, `description` " \
                "FROM `todo_items` " \
                "WHERE `is_archived` = ? AND `owner_id` = ? ORDER BY create_date DESC;"
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
        query = "SELECT `name`, `id`, `status`, `create_date`, `priority`, `due_date`," \
                " `owner_id`, `is_archived`, `description` " \
                "FROM `todo_items` " \
                "WHERE `todo_items`.`id` = ?;"
        values = (id_, )
        todo_item_from_db = DB.execute_select_query(db, query, values)
        return Todo(*todo_item_from_db[0]) if todo_item_from_db else None

    @classmethod
    def delete_todos_by_user_id(cls, user_id):
        """ removes all todos belong to user with user_id"""
        db = get_db()
        query = "DELETE FROM `todo_items` WHERE `owner_id` = ?"
        values = (user_id, )
        DB.execute_delete_query(db, query, values)

    def toggle(self):
        if self.status == 0:
            self.status = 1
            self.update_history('status done')
        else:
            self.status = 0
            self.update_history('status undone')
        self.save()

    def save(self):
        """ Saves/updates todo item in database """
        db = get_db()
        if self.id:
            query = "UPDATE `todo_items` SET `name` = ?, `status` = ?, " \
                    "`priority` = ?, `due_date` = ?, `is_archived` = ?, `description` = ? " \
                    "WHERE id = ?;"
            values = (self.name, self.status, self.priority, self.due_date, int(self.is_archived),
                      self.description, self.id)
            DB.execute_update_query(db, query, values)
            self.update_history('update')
        else:
            query = """INSERT INTO
                    `todo_items` (`name`, `create_date`, `priority`, `due_date`,
                    `owner_id`, `description`)
                    VALUES (?, ?, ?, ?, ?, ?); """
            values = (self.name, self.create_date, self.priority, self.due_date, self.owner_id,
                      self.description)
            DB.execute_insert_query(db, query, values)
            self.update_history('create')

    def delete(self):
        """ Removes todo item from the database """
        db = get_db()
        query = "DELETE FROM `todo_items` WHERE `id` = ?"
        values = (self.id, )
        DB.execute_delete_query(db, query, values)
        self.update_history('remove')

    def update_history(self, event):
        """saves events with event time in database"""
        event_dict = {'create': 1, 'remove': 2, 'archive': 3, 'activate': 4, 'update': 5,
                      'status done': 6, 'status undone': 7}
        history_query = "INSERT INTO todo_history (item_id, change_date, event_id) VALUES (?, ?, ?)"
        values = (self.id, time.strftime("%Y-%m-%d %H:%M"), event_dict[event])
        DB.execute_insert_query(get_db(), history_query, values)
