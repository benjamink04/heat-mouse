# %% --- Imports -----------------------------------------------------------------------
import pathlib
import sqlite3

import pandas as pd

# %% --- Constants ---------------------------------------------------------------------
# %% PARENT_DIR
PARENT_DIR = pathlib.Path(__file__).parent.parent.absolute()


# %% --- Classes -----------------------------------------------------------------------
# %% database
class Database:
    def __init__(self):
        self._connection = None
        self._cursor = None

    # %% --- Properties ----------------------------------------------------------------
    # %% connection
    @property
    def connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(
                PARENT_DIR.joinpath("database\\heatmouse_database.db")
            )
        return self._connection

    # %% cursor
    @property
    def cursor(self):
        if self._cursor is None:
            self._cursor = self.connection.cursor()
        return self._cursor

    # %% --- Methods -------------------------------------------------------------------
    def get_all_data(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        table_data = {}
        for application in tables:
            application = application[0]
            data = self.get_data(application)
            table_data[application] = data
        return table_data

    def get_data(self, application):
        table = pd.read_sql_query(
            f"SELECT * from {application.replace(' ', '_')};", self.connection
        )
        return (
            table["x_position"].to_list(),
            table["y_position"].to_list(),
            table["click"].to_list(),
        )

    def store_all_data(self, all_data):
        print(all_data)
        for application, data in all_data.items():
            self.store_data(application, data)

    def store_data(self, application, data):
        self._create_table(application)
        for x_position, y_position, click in zip(data[0], data[1], data[2]):
            self.cursor.execute(
                f"INSERT INTO {application.replace(' ', '_')} VALUES ({x_position}, {y_position}, '{click}');",
            )
        self.connection.commit()

    # %% --- Protected Methods ---------------------------------------------------------
    # %% _create_table
    def _create_table(self, application):
        self.cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {application.replace(' ', '_')} (x_position INTEGER, y_position INTEGER, click TEXT);",
        )
        self.connection.commit()
