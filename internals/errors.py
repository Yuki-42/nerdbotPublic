"""
Contains all error classes for the project.
"""


class InvalidStatusType(Exception):
    """
    Raised when a passed status type is not valid.
    """

    def __init__(self, value: str) -> None:
        """
        Initialises the exception.

        Args:
            value (str): The value of the status that caused the error.
        """
        super().__init__(f"Invalid status type '{value}'")
