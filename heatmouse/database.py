"""
The database class used by Heat Mouse to access the SQL database.

Classes
-------
Database
    Creates connection access to the local SQL database.
"""

# %% --- Imports -----------------------------------------------------------------------
import os
import sqlite3

import pandas as pd

import heatmouse


# %% --- Classes -----------------------------------------------------------------------
# %% Database
class Database:
    """
    Creates connection access to the local SQL database.

    Properties
    ----------
    connection : sqlite3.Connection
        Get connection to local SQL database.
    cursor : sqlite3.Cursor
        Get cursor object from connection.

    Methods
    -------
    get_all_data
        Query all tables and return all table data using get_data.
    get_data
        Query specific table and return all table data.
    get_icon
        Query the icon table and return a table specific icon.
    store_all_data
        Sort through given data and store it in the appropriate table using store_data.
    store_data
        Store data in a table.
    store_icon
        Store icon in a table.

    Protected Methods
    -----------------
    _create_table
        Create a new table if it does not exist.
    _init_icons_table
        Create icons table if it does not exist.
    """

    # %% --- Dunder Methods ------------------------------------------------------------
    # %% __init__
    def __init__(self):
        self._connection = None
        self._cursor = None
        self._init_icons_table()

    # %% --- Properties ----------------------------------------------------------------
    # %% connection
    @property
    def connection(self) -> sqlite3.Connection:
        """Get connection to local SQL database."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                heatmouse.PARENT_DIR.joinpath("database\\heatmouse_database.db")
            )
        return self._connection

    # %% cursor
    @property
    def cursor(self) -> sqlite3.Cursor:
        """Get cursor object from connection."""
        if self._cursor is None:
            self._cursor = self.connection.cursor()
        return self._cursor

    # %% --- Methods -------------------------------------------------------------------
    # %% get_all_data
    def get_all_data(self) -> dict[str : tuple[list, list, list]]:
        """
        Query all tables and return all table data using get_data.

        Returns
        -------
        dict[str: tuple[list, list, list]]
            Table data stored as {Application: (X-Position, Y-Position, Button)}
        """
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

    # %% get_data
    def get_data(self, application: str) -> tuple[list, list, list]:
        """
        Query specific table and return all table data.

        Arguments
        ---------
        application : str
            Application name, used as table title.

        Returns
        -------
        tuple[list, list, list]
            Table data stored as (X-Position, Y-Position, Button).
        """
        table = pd.read_sql_query(f"SELECT * FROM '{application}';", self.connection)
        return (
            table["x_position"].to_list(),
            table["y_position"].to_list(),
            table["click"].to_list(),
        )

    # %% get_icon
    def get_icon(self, application: str) -> str:
        """
        Query the icon table and return a table specific icon.

        Arguments
        ---------
        application : str
            Application name, used as table title.
        """
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

    # %% store_all_data
    def store_all_data(self, all_data: dict[str : tuple[list, list, list]]):
        """
        Sort through given data and store it in the appropriate table using store_data.

        Arguments
        ---------
        all_data: dict[str : tuple[list, list, list]]
            Table data stored as {Application: (X-Position, Y-Position, Button)}.
        """
        for application, data in all_data.items():
            self.store_data(application, data)

    # %% store_data
    def store_data(self, application: str, data: tuple[list, list, list]):
        """
        Store data in a table.

        Arguments
        ---------
        data: tuple[list, list, list]
            Table data stored as (X-Position, Y-Position, Button).
        """
        self._create_table(application)
        for x_position, y_position, click in zip(data[0], data[1], data[2]):
            self.cursor.execute(
                f"""INSERT INTO '{application}' VALUES
                ({x_position}, {y_position}, '{click}');""",
            )
        self.connection.commit()

    # %% store_icon
    def store_icon(self, application: str, icon: str):
        """
        Store icon in a table.

        Arguments
        ---------
        application : str
            Application name, used as table title.
        icon : icon
            Icon path.
        """
        self.cursor.execute(f"INSERT INTO icons VALUES ('{application}', '{icon}');")
        self.connection.commit()

    # %% --- Protected Methods ---------------------------------------------------------
    # %% _create_table
    def _create_table(self, application: str):
        """
        Create a new table if it does not exist.

        Arguments
        ---------
        application : str
            Application name, used as table title.
        """
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
        """Create icons table if it does not exist."""
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS icons(application TEXT UNIQUE, icon TEXT);"
        )
        self.connection.commit()
