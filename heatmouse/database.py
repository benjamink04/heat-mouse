# %% --- Imports -----------------------------------------------------------------------
import os
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
        self._init_icons_table()

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
            if application == "icons":
                continue
            data = self.get_data(application)
            table_data[application] = data
        return table_data

    def get_data(self, application):
        table = pd.read_sql_query(f"SELECT * FROM '{application}';", self.connection)
        return (
            table["x_position"].to_list(),
            table["y_position"].to_list(),
            table["click"].to_list(),
        )

    def store_all_data(self, all_data):
        for application, data in all_data.items():
            self.store_data(application, data)

    def store_data(self, application, data):
        self._create_table(application)
        for x_position, y_position, click in zip(data[0], data[1], data[2]):
            self.cursor.execute(
                f"""INSERT INTO '{application}' VALUES
                ({x_position}, {y_position}, '{click}');""",
            )
        self.connection.commit()

    def get_icon(self, application):
        self.cursor.execute(
            f"SELECT icon FROM icons WHERE application='{application}';"
        )
        icons = self.cursor.fetchall()
        if len(icons) == 0:
            return None
        icon = icons[0][0]
        if os.path.exists(icon):
            return icon
        self.cursor.execute(f"DELETE FROM icons WHERE application='{application}';")
        return None

    def store_icon(self, application, icon):
        self.cursor.execute(f"INSERT INTO icons VALUES ('{application}', '{icon}');")
        self.connection.commit()

    # %% --- Protected Methods ---------------------------------------------------------
    # %% _create_table
    def _create_table(self, application):
        try:
            self.cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS '{application}'
                (x_position INTEGER, y_position INTEGER, click TEXT);""",
            )
        except sqlite3.OperationalError:
            print(f'Table could not be created: "{application}"')
        self.connection.commit()

    # %% _init_icon_table
    def _init_icons_table(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS icons(application TEXT UNIQUE, icon TEXT);"
        )
        self.connection.commit()
