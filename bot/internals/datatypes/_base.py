"""
Base class for all data types.
"""

# Standard Library Imports
from typing import Any
from datetime import datetime

# Third Party Imports
from psycopg2.extensions import connection as Connection
from psycopg2.extras import RealDictRow, RealDictCursor
from psycopg2.sql import SQL, Identifier


class Base:
    """
    Base class for all data types.
    """
    # Type hints
    id: int
    createdAt: datetime

    _connection: Connection
    _tableName: str

    def __init__(
            self,
            tableName: str,
            connection: Connection,
            id: int,
            createdAt: datetime
    ) -> None:
        """
        Initializes the Base object.

        Args:
            tableName (str): The _name of the table in the database.
            connection (Connection): The connection to use for database operations.
            id (int): The ID of the data type.
            createdAt (datetime): The time the data type was created.

        Returns:
            None
        """
        self._tableName = tableName
        self._connection = connection
        self.id = id
        self.createdAt = createdAt  # String conversion is handled by postgres

    def __int__(self) -> int:
        """
        Returns the ID of the data type.

        Returns:
            int: The ID of the data type.
        """
        return self.id

    def dict(self) -> dict:
        """
        Returns the data type as a dictionary.

        Returns:
            dict: The data type as a dictionary.
        """
        return self.__dict__

    """
================================================================================================================================================================
        Database Operations
================================================================================================================================================================
    """

    def _set(
            self,
            column: str,
            value: Any
    ) -> None:
        """
        Sets a column in the database.

        Args:
            column (str): The column to set.
            value: The value to set the column to.

        Returns:
            None
        """
        with self._connection.cursor() as cursor:
            cursor.execute(
                SQL("UPDATE {tableName} SET {column} = %s WHERE id = %s").format(
                    tableName=Identifier(self._tableName),
                    column=Identifier(column),
                ),
                (value, self.id)
            )

    def _getAssoc(
            self,
            target: str,
            columns: tuple[str] = ("*",)
    ) -> list[RealDictRow]:
        """
        Gets related data from the database.

        Performs a join on the relation table to get the related data from the target table based on the ID of the data type.

        Args:
            target (str): The _name of the target table.
            columns (list[str]): The columns to get.
        """
        with self._connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                SQL("""
                SELECT {columns}
                FROM {target} 
                JOIN {relationTable} 
                ON {target}.id = {relationTable}.{target}_id 
                WHERE {relationTable}.{_tableName}_id = %s
                """).format(
                    columns=SQL(", ").join(map(Identifier, columns)),
                    target=Identifier(target),
                    relationTable=Identifier(f"{self._tableName}_{target}"),
                    _tableName=Identifier(self._tableName)
                ),
                (self.id,)
            )
            return cursor.fetchall()

    def _deleteAssoc(
            self,
            target: str
    ) -> None:
        """
        Deletes related data from the database.

        Args:
            target (str): The _name of the target table.

        Returns:
            None
        """
        with self._connection.cursor() as cursor:
            cursor.execute(
                SQL("DELETE FROM {relationTable} WHERE {_tableName}_id = %s").format(
                    relationTable=Identifier(f"{self._tableName}_{target}"),
                    _tableName=Identifier(self._tableName)
                ),
                (self.id,)
            )

    def _addAssoc(
            self,
            target: str,
            targetId: int
    ) -> None:
        """
        Adds related data to the database.

        Args:
            target (str): The _name of the target table.
            targetId (int): The ID of the target data type.

        Returns:
            None
        """
        with self._connection.cursor() as cursor:
            cursor.execute(
                SQL("INSERT INTO {relationTable} ({_tableName}_id, {target}_id) VALUES (%s, %s)").format(
                    relationTable=Identifier(f"{self._tableName}_{target}"),
                    _tableName=Identifier(self._tableName),
                    target=Identifier(target)
                ),
                (self.id, targetId)
            )

