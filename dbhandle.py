import sqlite3


class DB:

    @classmethod
    def connect(cls, db_name):
        """Connect with database"""
        return sqlite3.connect(db_name)

    @classmethod
    def close(cls, db):
        db.close()

    @classmethod
    def execute_update_query(cls, db, query, args):
        """Execute query based on provided parameters"""
        cur = db.cursor()
        if type(args) is tuple:
            args = [args]
        cur.executemany(query, args)
        db.commit()

    @classmethod
    def execute_delete_query(cls, db, query, args):
        """Execute query based on provided parameters"""
        cur = db.cursor()
        cur.execute(query, args)
        db.commit()


    @classmethod
    def execute_insert_query(cls, db, query, args):
        """Execute insert query and return new record id"""
        cur = db.cursor()
        cur.execute(query, args)
        last_id = cur.lastrowid
        db.commit()
        return last_id

    @classmethod
    def execute_select_query(cls, db, query, args=None):
        cur = db.cursor()
        cur.execute(query, args) if args else cur.execute(query)
        return cur.fetchall()

