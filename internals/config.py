"""
Contains the config for the project.
"""
# Standard Imports
from json import dump, load
from pathlib import Path

# Package Relative Imports
from .logging_ import createLogger, SuppressedLoggerAdapter
from .errors import InvalidStatusType


class Config:
    """
    The config class for the bot. This class is used to store the config values for the bot.
    """
    # Type Hints
    configFilePath: Path
    logger: SuppressedLoggerAdapter

    def __init__(self, configFile: Path = Path("BotData/config.json")) -> None:
        """
        Initialises the config class.

        Args:
            configFile (Path): The path to the config file from the current working directory.

        Returns:
            None
        """
        self.configfile = configFile

        self.logger = createLogger("Config")
        self.logger.info("Initializing config")

    @property
    def status(self) -> str:
        """
        Gets the status.

        Returns:
            str: The status.
        """
        return self.getValue("status")

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
        return self.getValue("statusType")

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
        match value.lower():
            case "playing":
                pass
            case "watching":
                pass
            case "listening":
                pass
            case "streaming":
                pass
            case _:
                raise InvalidStatusType(value)

        self.setValue("statusType", value)

    @property
    def filterEnabled(self) -> bool:
        """
        Gets whether the filter is enabled or not.

        Returns:
            bool: Whether the filter is enabled or not.
        """
        return self.getValue("filterEnabled")

    @filterEnabled.setter
    def filterEnabled(self, value: bool) -> None:
        """
        Sets the filterEnabled value in the config file.

        Args:
            value (bool): The value to set filterEnabled to

        Returns:
            None
        """
        self.logger.debug(f"Setting filterEnabled to {value}")
        self.setValue("filterEnabled", value)

    @property
    def owonerId(self) -> list[int]:
        """
        Gets the owner id.
        Returns:
            int: The owner id.
        """
        return self.getValue("owonerId")

    @property
    def gifClassifiers(self) -> list[str]:
        """
        Gets the gif classifiers.
        Returns:
            list: The gif classifiers.
        """
        return self.getValue("gifClassifiers")

    @property
    def loggingLevel(self) -> str:
        """
        Gets the logging level.
        Returns:
            str: The logging level.
        """
        return self.getValue("loggingLevel")

    def getValue(self, key) -> str | int | bool | list[str | int]:
        """
        Gets a value from the config file.
        Args:
            key: The key of the value to get.

        Returns:
            The value of the key.
        """
        with open(self.configfile, 'r') as file:
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
        with open(self.configfile, 'r') as file:
            configData: dict[str, str | int | bool | list[str]] = load(file)

        configData[key] = value

        with open(self.configfile, 'w') as file:
            dump(configData, file, indent=4)
