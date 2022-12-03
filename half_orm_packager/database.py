"""Provides the Database class
"""

import os
import subprocess
import sys

from psycopg2 import OperationalError
from half_orm.model import Model
from half_orm.model_errors import UnknownRelation
from half_orm_packager import utils
from half_orm_packager.db_conn import DbConn


class Database:
    """Reads and writes the halfORM connection file
    """

    def __init__(self, name: str = None):
        self.__model = None
        self.__name = name
        self.__last_release = None
        self.__connection_params: DbConn = DbConn(name)
        if name:
            self.__model = Model(name)
            self.__init(name)

    def __call__(self, name):
        return self.__class__(name)

    def __init(self, name, get_release=True):
        self.__name = name
        self.__connection_params = DbConn(name)
        if get_release:
            self.__last_release = next(
                self.__model.get_relation_class('half_orm_meta.view.hop_last_release')().select())

    @property
    def last_release_s(self):
        "Returns the string representation of the last release X.Y.Z"
        return '{major}.{minor}.{patch}'.format(**self.__last_release)

    @property
    def last_release(self):
        "Returns the last release"
        return self.__last_release

    @property
    def model(self):
        "The model (halfORM) of the database"
        return self.__model

    @property
    def status(self):
        "The status (str) of the database"
        res = ['[Database]']
        res.append(f'- production: {self.__connection_params.production}')
        res.append(f'- last release: {self.last_release_s}')
        return '\n'.join(res)

    @property
    def production(self):
        "Returns wether the database is tagged in production or not."
        return self.__connection_params.production

    def init(self, name):
        """Called when creating a new repo.
        Tries to read the connection parameters and then connect to
        the database.
        """
        try:
            self.__init(name, get_release=False)
        except FileNotFoundError:
            self.__connection_params.set_params(name)
        return self.__init_db()

    def __init_db(self):
        """Tries to connect to the database. If unsuccessful, creates the
        database end initializes it with half_orm_meta.
        """
        try:
            self.__model = Model(self.__name)
        except OperationalError:
            sys.stderr.write(f"The database '{self.__name}' does not exist.\n")
            create = input('Do you want to create it (Y/n): ') or "y"
            if create.upper() == 'Y':
                self.execute_pg_command('createdb')
            else:
                sys.stderr.write(
                    f'Aborting! Please remove {self.__name} directory.\n')
                sys.exit(1)
        self.__model = Model(self.__name)
        try:
            self.__model.get_relation_class('half_orm_meta.hop_release')
        except UnknownRelation:
            hop_init_sql_file = os.path.join(
                utils.HOP_PATH, 'patches', 'sql', 'half_orm_meta.sql')
            self.execute_pg_command(
                'psql', '-f', hop_init_sql_file, stdout=subprocess.DEVNULL)
            self.__model.reconnect(reload=True)
            self.__last_release = self.__model.get_relation_class('half_orm_meta.hop_release')(
                major=0, minor=0, patch=0, changelog='Initial release'
            ).insert()[0]
        return self(self.__name)

    @property
    def execute_pg_command(self):
        "Helper: execute a postgresql command"
        return self.__connection_params.execute_pg_command
