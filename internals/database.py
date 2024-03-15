"""
The database module for the bot. This module is used to store the database values for the bot.
"""
# Standard Library Imports
from datetime import datetime
from pathlib import Path

# External imports
from sqlite3 import connect, Connection, Cursor
from discord import Member, User

# Internal imports
from .config import Config
from .logging_ import createLogger, SuppressedLoggerAdapter


class Database:
    """
    The database class for the bot. This class is used to store the database values for the bot.
    """
    # Type Hints
    config: Config
    logger: SuppressedLoggerAdapter
    connection: Connection

    def __init__(self, config, databaseLocation: Path = Path("BotData/database.db")):
        self.config = config
        self.logger = createLogger("Database", config.loggingLevel)
        self.logger.info("Initializing database")

        self.connection = connect(databaseLocation, check_same_thread=False)

        self.logger.info("Main database initialized")

    """
    # Properties
************************************************************************************************************************
    """

    @property
    def users(self) -> list[tuple[int, str, bool, int, int, bool, datetime]]:
        """
        Gets the users from the database.

        Returns:
            list: The users.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()

    @property
    def bannedGifs(self) -> list[str]:
        """
        Gets the banned gifs from the database.

        Returns:
            list: The banned gifs.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT url FROM banned_gifs")
        return [x[0] for x in cursor.fetchall()]

    @property
    def whitelistedGifs(self):
        """
        Gets the whitelisted gifs from the database.

        Returns:
            list: The whitelisted gifs.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT url FROM whitelist")
        return [x[0] for x in cursor.fetchall()]

    @property
    def filteredUsers(self):
        """
        Gets the users from the database that have opted in to filtering.

        Returns:
            list: The filtered users.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM users where apply_filter=1")
        return [x[0] for x in cursor.fetchall()]

    @property
    def reactions(self):
        """
        Gets the reactions from the database.

        Returns:
            list: The reactions.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT reaction FROM reactions")
        return [x[0] for x in cursor.fetchall()]

    """
    # Database Checks
************************************************************************************************************************
    """

    def checkUserExists(self, uid: int):
        """
        Checks if a user exists in the database.

        Args:
            uid (int): The user id.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM users WHERE id=?", (uid,))
        return cursor.fetchone() is not None

    def checkGifBanned(self, gifUrl):
        """
        Checks if a gif is banned.

        Args:
            gifUrl (str): The gif url.

        Returns:
            bool: Whether the gif is banned.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM banned_gifs WHERE url=?", (gifUrl,))
        return cursor.fetchone() is not None

    def checkMessageBannedGifs(self, message: str) -> bool:
        """
        Checks a message for banned gifs.

        Args:
            message (str): The message to check.

        Returns:
            bool: Whether the message contains a banned gif.
        """
        cursor: Cursor = self.connection.cursor()
        bannedGifs = cursor.execute("SELECT url FROM banned_gifs").fetchall()
        self.logger.info("Checking message for banned gifs.")

        for gif in bannedGifs:
            if gif[0] in message:
                self.logger.info("Message contains banned gif.")
                return True

        self.logger.info("Message does not contain banned gif.")
        return False

    def checkUserAdmin(self, user: Member | User):
        """
        Checks if a user is an admin.

        Args:
            user (int): The user id.

        Returns:
            bool: Whether the user is an admin.
        """
        # Check if the user is an administrator in the server TODO: Test this and move it out of database.py
        if user.top_role.permissions.administrator or user.id in self.config.owonerId:
            return True

    """
    # Database Modification
************************************************************************************************************************
    """

    def incrementMessagesSent(self, uid: int):
        """
        Increments the number of messages sent by a user.

        Args:
            uid (int): The user id.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET messages_sent=messages_sent+1 WHERE id=?", (uid,))
        self.connection.commit()

    """
    # Set Methods
************************************************************************************************************************
    """

    def setMessagesSent(self, uid: int, value: int):
        """
        Sets the number of messages sent by a user.

        Args:
            uid (int): The user id.
            value (int): The value to set messages_sent to.
        """
        self.logger.debug(f"Setting messages sent for user {uid}({self.getUserName(uid)}) to {value}")
        cursor: Cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET messages_sent=? WHERE id=?", (value, uid))
        self.connection.commit()

    def setUsername(self, uid: int, username: str):
        """
        Sets the username of a user.

        Args:
            uid (int): The user id.
            username (str): The username.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET username=? WHERE id=?", (username, uid))
        self.connection.commit()

    """
    ## Adding
************************************************************************************************************************
    """

    def addBannedGif(self, bannedBy: int, gifUrl: str, reason: str = None):
        """
        Adds a banned gif to the database.

        Args:
            bannedBy (int): The user who banned the gif.
            gifUrl (str): The gif url.
            reason (str): The reason for the ban.

        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("INSERT INTO banned_gifs (banned_by, url, reason) VALUES (?, ?, ?)",
                       (bannedBy, gifUrl, reason))
        self.connection.commit()

    def addUser(self, userId: int, username: str):
        """
        Adds a user to the database.

        Args:
            userId (int): The user id.
            username (str): The username.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("INSERT INTO users (id, username) VALUES (?, ?)",
                       (userId, username))
        self.connection.commit()

    def addWhitelistedGif(self, addedBy: int, gifUrl: str):
        """
        Adds a whitelisted gif to the database.

        Args:
            addedBy (int): The ID of the user who added the gif to the whitelist.
            gifUrl (str): The gif url.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("INSERT INTO whitelist (url, added_by) VALUES (?, ?)", (gifUrl, addedBy))
        self.connection.commit()

    def addReaction(self, reaction: str, addedBy: int, appliesTo: int):
        """
        Adds a reaction to the database.

        Args:
            reaction (str): The reaction itself
            addedBy (int): The user who added the reaction.
            appliesTo (int): The user for the reaction to apply to
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("INSERT INTO reactions (reaction, added_by, applies_to) VALUES (?, ?, ?)",
                       (reaction, addedBy, appliesTo))
        self.connection.commit()

    """
    ## Removing
************************************************************************************************************************
    """

    def removeBannedGif(self, gifUrl: str) -> None:
        """
        Removes a banned gif from the database.

        Args:
            gifUrl (str): The gif url.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("DELETE FROM banned_gifs WHERE url=?", (gifUrl,))
        self.connection.commit()

    def removeWhitelistedGif(self, gifUrl: str):
        """
        Removes a whitelisted gif from the database.

        Args:
            gifUrl (str): The gif url.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("DELETE FROM whitelist WHERE url=?", (gifUrl,))
        self.connection.commit()

    def removeReaction(self, reaction: str, appliesTo: int):
        """
        Removes a reaction from the database.

        Args:
            reaction (str): The reaction escape code
            appliesTo (int): The user id.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("DELETE FROM reactions WHERE reaction=? AND applies_to=?", (reaction, appliesTo))
        self.connection.commit()

    """
    # Get Methods
************************************************************************************************************************
    """

    def getUserReactions(self, user: int) -> list:
        """
        Gets the reactions for a user.

        Args:
            user: The ID of the user.

        Returns:
            list: The reaction escape codes
        """

        self.logger.info(f"Getting reactions for user {user}")
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT reaction FROM reactions WHERE applies_to=?", (user,))
        reactions = cursor.fetchall()
        self.logger.debug(f"Reactions for user {user}: {reactions}")
        return reactions

    def getUserName(self, uid: int) -> str:
        """
        Gets the username of a user.

        Args:
            uid (int): The user id.

        Returns:
            str: The username.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT username FROM users WHERE id=?", (uid,))
        return cursor.fetchone()[0]

    def getMessagesSent(self, uid: int) -> int:
        """
        Gets the number of messages sent by a user.

        Args:
            uid (int): The user id.

        Returns:
            int: The number of messages sent.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT messages_sent FROM users WHERE id=?", (uid,))
        return cursor.fetchone()[0]

    def getMessagesSentRank(self, uid: int) -> int:
        """
        Gets the rank of a user based on the number of messages sent.

        Args:
            uid (int): The user id.

        Returns:
            int: The number of messages sent.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE messages_sent > "
                       "(SELECT messages_sent FROM users WHERE id=?)", (uid,))
        return cursor.fetchone()[0] + 1

    def getMessagesDeleted(self, uid: int) -> int:
        """  # TODO: Make all of these server specific (so that it only counts for users that are in the current server)
        Gets the number of messages deleted by a user.

        Args:
            uid (int): The user id.

        Returns:
            int: The number of messages deleted.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT messages_deleted FROM users WHERE id=?", (uid,))
        return cursor.fetchone()[0]

    def getTopMessagesSent(self, limit: int) -> list:
        """
        Gets the top users based on the number of messages sent.

        Args:
            limit (int): The number of users to get.

        Returns:
            list: The top users.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT id, username, messages_sent FROM users ORDER BY messages_sent DESC LIMIT ?",
                       (limit,))
        return cursor.fetchall()

    def getTopMessagesDeleted(self, limit: int) -> list:
        """
        Gets the top users based on the number of messages deleted.

        Args:
            limit (int): The number of users to get.

        Returns:
            list: The top users.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT id, username, messages_deleted FROM users ORDER BY messages_deleted DESC LIMIT ?",
                       (limit,))

        return cursor.fetchall()

    def getMessagesDeletedRank(self, uid: int) -> int:
        """
        Gets the rank of a user based on the number of messages deleted.

        Args:
            uid (int): The user id.

        Returns:
            int: The number of messages deleted.
        """
        cursor: Cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE messages_deleted > "
                       "(SELECT messages_deleted FROM users WHERE id=?)", (uid,))
        return cursor.fetchone()[0] + 1
