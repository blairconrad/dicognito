"""Defines Dicognito custom exceptions."""


class TagError(ValueError):
    """Error raised when a tag name does not properly define a DICOM tag."""

    def __init__(self, tag: str):
        """
        Create a new TagError.

        Parameters
        ----------
        tag : str
            The malformed DICOM tag name.
        """
        message = f"Bad tag name '{tag}'. Must be a well-known DICOM element name or a string in the form 'stuv,wxyz' where each character is a hexadecimal digit."
        super().__init__(message)
