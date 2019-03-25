from .query import Query
from db.utils import Q
from db.backends import DatabaseWrapper


class BaseManager:
    pass


class Manager(BaseManager):
    def __init__(self, model, Query=Query):
        self.model = model
        self.query = Query(self.model)
        self.database = DatabaseWrapper(self.model.database)

    def filter(self, *args, **kwargs):
        q_project = Q(*args, **kwargs)
        self.query.add_q(q_project)
        sql = self.query.as_sql()
        return self.execute(sql)

    def all(self):
        sql = self.query.all()
        return self.execute(sql)

    def decription(self):
        sql = self.query.as_decription()
        return self.execute(sql)

    def execute(self, sql):
        with self.database:
            cursor = self.database.create_cursor()
            with cursor:
                result = cursor.execute(sql)
        return result




