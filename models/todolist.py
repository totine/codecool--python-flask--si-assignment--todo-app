from models.todo import Todo


class TodoList:
    """Class representing list of todo items for user (owner)"""
    def __init__(self, owner):
        self.owner = owner
        self.active_todos = Todo.get_all(self.owner.id, is_archived=False)
        self.archived_todos = Todo.get_all(self.owner.id, is_archived=True)

    def sort_by_name(self, is_desc=False):
        """sorts active and archived todos by name. If is_desc is True sorting is descending"""
        self.active_todos.sort(key=(lambda x: x.name), reverse=is_desc)
        self.archived_todos.sort(key=(lambda x: x.name), reverse=is_desc)

    def sort_by_due_date(self, is_desc=False):
        """sorts active and archived todos by due date. If is_desc is True sorting is descending"""
        self.active_todos.sort(key=(lambda x: x.due_date), reverse=is_desc)
        self.archived_todos.sort(key=(lambda x: x.due_date), reverse=is_desc)

    def sort_by_create_date(self, is_desc=False):
        """sorts active and archived todos creation time. If is_desc is True sorting is descending"""
        self.active_todos.sort(key=(lambda x: x.create_date), reverse=is_desc)
        self.archived_todos.sort(key=(lambda x: x.create_date), reverse=is_desc)

    def sort_by_priority(self, is_desc=False):
        """sorts active and archived todos by priority. If is_desc is True sorting is descending"""
        self.active_todos.sort(key=(lambda x: x.priority), reverse=is_desc)
        self.archived_todos.sort(key=(lambda x: x.priority), reverse=is_desc)

    def sort_by_status(self, is_desc=False):
        """sorts active and archived todos by status. If is_desc is True sorting is descending"""
        self.active_todos.sort(key=(lambda x: x.status), reverse=is_desc)
        self.archived_todos.sort(key=(lambda x: x.status), reverse=is_desc)
