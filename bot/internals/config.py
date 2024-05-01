"""
Contains the config for the project.
"""
# Standard Imports
from json import dump, load
from pathlib import Path
from os import environ

# Third Party Imports
from dotenv import load_dotenv as loadDotEnv
from pydantic import BaseModel

# Package Relative Imports
from .logging import createLogger, SuppressedLoggerAdapter


class Db(BaseModel):
    """
    Model used to store the database connection details.
    """
    ip: str
    port: int
    name: str
    user: str
    password: str


class Status(BaseModel):
    """
    Model used to store the status details.
    """
    status: str
    statusType: str

    def __str__(self) -> str:
        """
        Returns the status.

        Returns:
            str: The status.
        """
        return self.status


class Bot(BaseModel):
    """
    Model used to store the bot details.
    """
    token: str
    owonerId: str
    debug: bool
    status: Status


class Config:
    """
    The config class for the bot. This class is used to store the config values for the bot.
    """
    # Type Hints
    _configFilePath: Path
    _logger: SuppressedLoggerAdapter

    _db: Db
    _debug: bool

    def __init__(
            self,
            configJson: Path = Path("BotData/config.json"),
            envFile: Path = Path("BotData/.env")
    ) -> None:
        """
        Initialises the config class.

        Args:
            configJson (Path): The path to the config file.
            envFile (Path): The path to the environment file.

        Returns:
            None
        """
        self._configFilePath = configJson

        self._logger = createLogger("Config")
        self._logger.info("Initializing config")

        # Load the environment variables
        loadDotEnv(dotenv_path=envFile)

        # Load the environment variables
        self._db = Db(
            ip=environ.get("DB_IP"),
            port=int(environ.get("DB_PORT")),
            name=environ.get("DB_NAME"),
            user=environ.get("DB_USER"),
            password=environ.get("DB_PASSWORD")
        )
        self._debug = environ.get("BOT_DEBUG").lower() == "true"

    """
========================================================================================================================
        Properties
========================================================================================================================
    """

    @property
    def db(self) -> Db:
        """
        The database connection details.

        Returns:
            Db: The database connection details.
        """
        return self._db

    @property
    def bot(self) -> Bot:
        """
        The bot details.

        Returns:
            Bot: The bot details.
        """
        return Bot(
            token=environ.get("BOT_TOKEN_DEBUG" if self._debug else "BOT_TOKEN"),
            owonerId=environ.get("BOT_OWNER_ID"),
            debug=self._debug,
            status=Status(
                status=self._get("status"),
                statusType=self._get("statusType")
            )
        )

    """
========================================================================================================================
        Json Getters and Setters
========================================================================================================================
    """

    def _get(
            self,
            key: str
    ) -> str | int | bool | list[str | int]:
        """
        Gets a value from the config file.
        Args:
            key: The key of the value to get.

        Returns:
            The value of the key.
        """
        with open(self._configFilePath, 'r') as file:
            configData: dict[str, str | int | bool | list[str]] = load(file)

        try:
            self._logger.debug(f"Getting value for key '{key}'")
        except AttributeError:
            pass
        return configData[key]

    def _set(
            self,
            key: str,
            value: str | int | bool | list[str | int]
    ) -> None:
        """
        Writes a new value to the config file.
        Args:
            key(str): The key of the value to write.
            value: The value to write.
        """
        self._logger.debug(f"Writing new value for key '{key}': {value}")
        with open(self._configFilePath, 'r') as file:
            configData: dict[str, str | int | bool | list[str]] = load(file)

        configData[key] = value

        with open(self._configFilePath, 'w') as file:
            dump(configData, file, indent=4)
