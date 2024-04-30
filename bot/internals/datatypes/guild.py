"""
Guild datatype
"""
# Standard Library Imports
from datetime import datetime

# Third Party Imports
from psycopg2.extensions import connection as Connection

# Local Imports
from ._base import Base


class Guild(Base):
    """
    Guild datatype.
    """
    # Type hints
    _name: str

    def __init__(
            self,
            connection: Connection,
            id: int,
            createdAt: datetime,
            name: str
    ) -> None:
        """
        Initializes the Guild object.

        Args:
            connection (Connection): The connection to use for database operations.
            id (int): The ID of the guild.
            createdAt (datetime): The time the guild was created.
            name (str): The _name of the guild.

        Returns:
            None
        """
        super().__init__("guilds", connection, id, createdAt)
        self._name = name

    """
========================================================================================================================
    Properties
========================================================================================================================
    """
    @property
    def name(self) -> str:
        """
        Returns the _name of the guild.

        Returns:
            str: The _name of the guild.
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """
        Sets the _name of the guild.

        Args:
            value (str): The _name of the guild.

        Returns:
            None
        """
        self._set("name", value)
