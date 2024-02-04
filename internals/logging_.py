"""
Contains the miscellaneous methods associated with the project but not part of the main logic of the system
"""
# Standard library imports
from asyncio import Queue
from datetime import datetime
from logging import (CRITICAL, DEBUG, ERROR, FileHandler, Formatter, Handler, INFO, Logger, LoggerAdapter,
                     StreamHandler, WARNING, getLogger)
from logging import LogRecord
from os import getcwd, mkdir, path
from pathlib import Path
from sqlite3 import Connection, Cursor, OperationalError, ProgrammingError, connect
from sys import stdout
from typing import Literal


def getEscapeCode(
        baseColour: str,
        bold: bool = False,
        underline: bool = False,
) -> str:
    """
    Gets the ANSI escape code for the given colour.

    Args:
        baseColour (str): The base colour to get the ANSI escape code for.
        bold (bool): Whether the text should be bold.
        underline (bool): Whether the text should be underlined.

    Returns:
        str: The ANSI escape code for the given colour.

    Raises:
        ValueError: If the given colour is not a valid colour.

    Reference:
        https://gist.github.com/JBlond/2fea43a3049b38287e5e9cefc87b2124
    """
    if baseColour.endswith("_H"):  # Specifies that the colour is of a high intensity. (Defined as 90-97)
        baseColour = baseColour[:-2]
        highIntensity: bool = True
    else:
        highIntensity = False

    match baseColour.upper():
        case "BLACK":
            colourCode = 30
        case "RED":
            colourCode = 31
        case "GREEN":
            colourCode = 32
        case "YELLOW":
            colourCode = 33
        case "BLUE":
            colourCode = 34
        case "PURPLE":
            colourCode = 35
        case "CYAN":
            colourCode = 36
        case "WHITE":
            colourCode = 37
        case _:
            raise ValueError(f"{baseColour} is not a valid colour.")

    if highIntensity:
        colourCode += 60

    if bold:
        formatter: str = "1;"
    elif underline:
        formatter = "4;"
    elif bold and underline:
        formatter = "1;4;"
    else:
        formatter = ""
    # Assemble the ANSI escape code
    return f"\033[{formatter}{colourCode}m"


class ColourCodedFormatter(Formatter):
    """
    A formatter that adds colour coding to the log messages.
    """
    # Type hints
    colourCoding: dict[str, str]

    def __init__(
            self,
            fmt: str | None = None,
            datefmt: str | None = None,
            style: Literal["%", "{", "$"] = "%",
            colourCoding: dict[str, str] = None
    ):
        super().__init__(fmt, datefmt, style)

        if colourCoding is None:
            colourCoding = {
                "DEBUG": getEscapeCode("CYAN"),
                "INFO": getEscapeCode("GREEN"),
                "WARNING": getEscapeCode("YELLOW"),
                "ERROR": getEscapeCode("RED"),
                "CRITICAL": getEscapeCode("RED_H"),
            }
        self.colourCoding = colourCoding

    def format(self, record: LogRecord) -> str:
        """
        Formats the log message.

        Args:
            record (LogRecord): The log record to format.

        Returns:
            str: The formatted log message.
        """
        try:
            record.levelname = f"{self.colourCoding[record.levelname]}{record.levelname}\033[0m"
        except KeyError:  # Handles the case where the level name is not in the colour coding dictionary
            pass
        return super().format(record)


# Custom LoggerAdapter that can be disabled
class SuppressedLoggerAdapter(LoggerAdapter):
    """
    A logger adapter that can be disabled.
    """
    # Type hints
    suppressed: bool

    def __init__(self, logger: Logger, extra: dict[str, str] | None = None):
        super().__init__(logger, extra)
        self.suppressed = False

    def suppress(self):
        """
        Suppresses the logger.
        """
        self.suppressed = True

    def unsuppress(self):
        """
        Unsuppresses the logger.
        """
        self.suppressed = False

    def log(self, level: int, msg: str, *args, **kwargs):
        """
        Logs the message to the logger.

        Args:
            level (int): The level of the log message.
            msg (str): The log message.
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.
        """
        if not self.suppressed:
            super().log(level, msg, *args, **kwargs)


# Custom handler for logging to a database
class DatabaseHandler(Handler):
    """
    A handler that logs to a database.
    """
    # Type hints
    database: Connection
    cursor: Cursor
    taskSet: set = set()

    def __init__(self, databasePath: str | Path):
        super().__init__()

        self.database: Connection = connect(databasePath, check_same_thread=False)
        self.cursor: Cursor = self.database.cursor()
        self.queue = Queue()

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Logs (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                TimeStamp DATETIME NOT NULL,
                LevelNumber INTEGER NOT NULL,
                LevelName TEXT NOT NULL,
                LoggerName TEXT NOT NULL,
                Message TEXT NOT NULL
            )
            """
        )
        self.database.commit()

    def emit(self, record: LogRecord):
        """
        Logs the record to the database.

        Args:
            record (LogRecord): The record to log to the database.
        """
        if record.levelno < WARNING:
            return

        # Remove anything that is not a capital letter from the level name
        record.levelname = "".join([char for char in record.levelname if char.isupper()])
        cursor = self.database.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO Logs (
                    TimeStamp,
                    LevelNumber,
                    LevelName,
                    LoggerName,
                    Message
                ) VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    record.created,
                    record.levelno,
                    record.levelname,
                    record.name,
                    record.msg
                )
            )
        except OperationalError:
            pass

        except ProgrammingError:
            pass

        try:
            self.database.commit()
        except OperationalError:
            pass
        except SystemError:
            pass


def createLogger(
        name: str,
        level: str = "DEBUG",
        formatString: str = "[%(asctime)s] [%(loggername)s] [%(levelname)s] %(message)s",
        handlers: list[Handler] = None,
        doColour: bool = True,
        colourCoding: dict[str, str] = None
) -> SuppressedLoggerAdapter:
    """
    Creates a logger with the specified name, logging path, level, and formatter.

    Args:
        name (str): The name of the logger.
        level (str): The level of the logger.
        formatString (str): The format string for the logger.
        handlers (list): Additional handlers for the logger.
        doColour (bool): Whether to use colour coding in the logger for logging outputs.
        colourCoding (dict): The colour coding for the logger. Defaults to the default colour coding defined in the
            function.

    Returns:
        logger (Logger): The logger object.

    """
    if not path.exists(Path(f"{getcwd()}/Logs/")):
        mkdir(Path(f"{getcwd()}/Logs/"))

    loggingDirectory: str = name
    logFileName: str = name + "_"

    # Check if the logging directory exists, if not, create it
    if not path.exists(Path(f"{getcwd()}/Logs/{loggingDirectory}")):
        mkdir(Path(f"{getcwd()}/Logs/{loggingDirectory}"))

    match level.lower():
        case "debug":
            level = DEBUG
        case "info":
            level = INFO
        case "warning":
            level = WARNING
        case "error":
            level = ERROR
        case "critical":
            level = CRITICAL
        case _:
            raise ValueError("Invalid level specified")

    logger: Logger = getLogger(name)  # Sets the logger's name
    logger.setLevel(level)  # Sets the logger's level

    if logger.hasHandlers():  # This checks if the logger has already been created and if it has, it replaces the
        # handlers with the new ones
        logger.handlers.clear()

    if handlers is None:
        handlers: list[Handler] = [FileHandler(
            Path(
                f"{getcwd()}/Logs/{loggingDirectory}/{logFileName}{datetime.now().strftime('%d.%m.%Y')}.log"
            ),
            encoding="utf-8"
        ), StreamHandler(stdout), DatabaseHandler(
            Path(
                f"{getcwd()}/BotData/Logs.db"
            )
        )]

    colourFormatter: ColourCodedFormatter = ColourCodedFormatter(formatString, colourCoding=colourCoding)
    formatter: Formatter = Formatter(formatString)

    for handler in handlers:
        if not doColour or isinstance(handler, FileHandler) or isinstance(handler, DatabaseHandler):
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            pass

        else:
            handler.setFormatter(colourFormatter)
            logger.addHandler(handler)

    # A logger adapter is used here to allow for the logger name to be included in the log messages. This is useful
    # when multiple loggers are used in the same project.
    return SuppressedLoggerAdapter(logger, {"loggername": name})
