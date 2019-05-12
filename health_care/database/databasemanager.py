import os
from os.path import exists
from urllib.parse import urlparse

from sqlalchemy import create_engine

from ..config import BotConfig
from ..database import BaseModel



class AbstractDatabaseManager(object):

    def __init__(self, url=None):
        self.db_url = url or BotConfig.database_url
        self.db_name = urlparse(self.db_url).path.lstrip('/')

    def __enter__(self):
        self.engine = create_engine(self.db_url)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.engine.dispose()

    def create_database_if_not_exists(self):
        if not self.database_exists():
            self.create_database()

    def database_exists(self):  # pragma: no cover
        raise NotImplementedError()

    def create_database(self):  # pragma: no cover
        raise NotImplementedError()

    def drop_database(self):  # pragma: no cover
        raise NotImplementedError()

    def setup_schema(self):
        BaseModel.metadata.create_all(self.engine)

    def drop_schema(self):
        BaseModel.metadata.drop_all(self.engine)


class PostgresManager(AbstractDatabaseManager):

    def __enter__(self):
        super().__enter__()
        self.connection.execute('commit')
        return self

    def database_exists(self):
        r = self.connection.execute(
            f'SELECT 1 FROM pg_database WHERE datname = \'{self.db_name}\''
        )
        try:
            ret = r.cursor.fetchall()
            return ret
        finally:
            r.cursor.close()

    def create_database(self):
        self.connection.execute(f'CREATE DATABASE {self.db_name}')
        self.connection.execute(f'COMMIT')

    def drop_database(self):
        self.connection.execute(f'DROP DATABASE IF EXISTS {self.db_name}')
        self.connection.execute(f'COMMIT')


class SqliteManager(AbstractDatabaseManager):

    def __init__(self, url):
        super().__init__()
        self.filename = self.db_url.replace('sqlite:///', '')

    def database_exists(self):
        return exists(self.filename)

    def create_database(self):
        print('Database is creating')
        self.setup_schema()

    def drop_database(self):
        print('Removing: %s' % self.filename)
        os.remove(self.filename)


class DatabaseManager(AbstractDatabaseManager):

    def __new__(cls, *args, url=None, **kwargs):
        url = url or BotConfig.database_url
        if url.startswith('sqlite'):
            manager_class = SqliteManager
        elif url.startswith('postgres'):
            manager_class = PostgresManager
        else:
            raise ValueError(f'Unsupported database url: {url}')

        return manager_class(*args, url=url, **kwargs)
