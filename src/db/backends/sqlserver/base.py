from db.backends.base.base import BaseDatabaseWrapper
from db.utils.utils import cached_property
from db.utils import DatabaseErrorWrapper
from .client import DatabaseClient
import pyodbc

class CursorWrapper:
    def __init__(self,cursor):
        self.cursor = cursor

    def execute(self,query,args=None):
        try:
            if args is None:
                self.cursor.execute(query)
                return [list(c) for c in self.cursor.fetchall()]
            else:
                self.cursor.execute(query,args)
                return [list(c) for c in self.cursor.fetchall()]
        except pyodbc.OperationalError as e:
            print(e.args[0])

    def executemany(self,query,args=None):
        try:
            return self.cursor.executemany(query,args)
        except pyodbc.OperationalError as e:
            print(e.args[0])
    def __getattr__(self, attr):
        return getattr(self.cursor,attr)
    def __iter__(self):
        return iter(self.cursor)
    def __enter__(self):
        return self
    def close(self):
        if self.cursor:
            self.cursor.close()
    def __exit__(self, exc_type, exc_value, traceback):
        # Close instead of passing through to avoid backend-specific behavior
        # (#17671). Catch errors liberally because errors in cleanup code
        # aren't useful.
        try:
            self.close()
        except pyodbc.Error:
            pass


class DatabaseWrapper(BaseDatabaseWrapper):
    Database = pyodbc
    def __init__(self,settings_dict):
        self.client = DatabaseClient()
        self.settings_dict = settings_dict
        self.connection = None
        self.autocommit = False

    def get_connection_params(self):
        return self.client.database_setting(self.settings_dict)

    def connect(self):
        try:
            self.connection =  pyodbc.connect(self.get_connection_params())
        except pyodbc.OperationalError as e:
            print(e.args[0])

    def ensure_connection(self):
        if self.connection is None:
            with self.wrap_database_errors:
                self.connect()

    def create_cursor(self,name=None):
        cursor = self.connection.cursor()
        return CursorWrapper(cursor)

    def close(self):
        try:
            self._close()
        finally:
            self.connection = None
    def commit(self):
        self._commit()

    def cursor(self):
        return self._cursor()

    def rollback(self):
        self._rollback()

    def set_autocommit(self,autocommit=False):
        self._set_autocommit(autocommit)

    def get_autocommit(self):
        return self._get_autocommit()

    @cached_property
    def wrap_database_errors(self):
        return DatabaseErrorWrapper(self)

    def _close(self):
        if self.connection is not None:
            with self.wrap_database_errors:
                self.connection.close()

    def _commit(self):
        if self.connection is not None:
            with self.wrap_database_errors:
                self.connection.commit()
    def _cursor(self,name=None):
        if self.connection is not None:
            with self.wrap_database_errors:
                return self.create_cursor(name)

    def _rollback(self):
        if self.connection is not None:
            with self.wrap_database_errors:
                self.connection.rollback()

    def _set_autocommit(self,autocommit):
        if self.connection is not None:
            with self.wrap_database_errors:
                self.connection.autocommit = autocommit

    def _get_autocommit(self):
        if self.connection is not None:
            with self.wrap_database_errors:
                return self.connection.autocommit

    def __enter__(self):
        if self.connection is None:
            self.ensure_connection()

    def __exit__(self,exc_type, exc_value, traceback):
        self.close()