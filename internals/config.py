"""
Contains the config for the project.
"""
# Standard Imports
from json import dump, load
from pathlib import Path
from os import environ

# Third Party Imports
from dotenv import load_dotenv as loadDotEnv

# Package Relative Imports
from .logging import createLogger, SuppressedLoggerAdapter
from .errors import InvalidStatusType


class Config:
    """
    The config class for the bot. This class is used to store the config values for the bot.
    """
    # Type Hints
    _configFilePath: Path
    logger: SuppressedLoggerAdapter

    dbIp: str
    dbPort: str
    dbName: str
    dbUser: str
    dbPassword: str
    debug: bool = False
    owonerId: str

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

        self.logger = createLogger("Config")
        self.logger.info("Initializing config")

        # Load the environment variables
        loadDotEnv(dotenv_path=envFile)

        # Set the environment variables
        self.dbIp = environ.get("DB_IP")
        self.dbPort = environ.get("DB_PORT")
        self.dbName = environ.get("DB_NAME")
        self.dbUser = environ.get("DB_USER")
        self.dbPassword = environ.get("DB_PASS")
        self.debug = environ.get("DEBUG") == "True"
        self.owonerId = environ.get("OWNER_ID")

    """
========================================================================================================================
        Environment Variables
========================================================================================================================
    """
    @property
    def token(self) -> str:
        """
        Gets the bot token.

        Returns:
            str: The bot token.
        """
        if self.debug:
            return environ.get("DEBUG_TOKEN")
        return environ.get("TOKEN")

    """
========================================================================================================================
        Json Config File
========================================================================================================================
    """

    @property
    def status(self) -> str:
        """
        Gets the status.

        Returns:
            str: The status.
        """
        return self.getJson("status")

    @status.setter
    def status(self, value: str) -> None:
        """
        Sets the status field in the config file to the provided value.

        Args:
            value (str): The value to set the status to.

        Returns:
            None
        """
        self.logger.debug(f"Setting status to '{value}'")
        self.setValue("status", value)

    @property
    def statusType(self) -> str:
        """
        Gets the status type.

        Returns:
            str: The status type.
        """
        return self.getJson("statusType")

    @statusType.setter
    def statusType(self, value: str) -> None:
        """
        Sets the statusType.

        Args:
            value (str): The value to set the statusType to.

        Raises:
            InvalidStatusType: Raised when the statusType is invalid.

        Returns:
            None
        """
        self.logger.debug(f"Attempting to set statusType to {value}")
        if value not in ["playing", "watching", "listening", "streaming"]:
            self.logger.error(f"Invalid status type '{value}'")
            raise InvalidStatusType(value)

        self.setValue("statusType", value)

    @property
    def gifClassifiers(self) -> list[str]:
        """
        Gets the gif classifiers.

        Returns:
            list: The gif classifiers.
        """
        return self.getJson("gifClassifiers")

    def getJson(self, key) -> str | int | bool | list[str | int]:
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
            self.logger.debug(f"Getting value for key '{key}'")
        except AttributeError:
            pass
        return configData[key]

    def setValue(self, key: str, value: str | int | bool | list[str | int]):
        """
        Writes a new value to the config file.
        Args:
            key(str): The key of the value to write.
            value: The value to write.
        """
        self.logger.debug(f"Writing new value for key '{key}': {value}")
        with open(self._configFilePath, 'r') as file:
            configData: dict[str, str | int | bool | list[str]] = load(file)

        configData[key] = value

        with open(self._configFilePath, 'w') as file:
            dump(configData, file, indent=4)
