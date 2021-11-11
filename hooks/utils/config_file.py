"""Base config file definition."""

import abc
from pathlib import Path


class ConfigFile(metaclass=abc.ABCMeta):
    def __init__(self, path: str, desired_filename: str) -> None:
        """Base configuration file class - to be extended by concrete implementations.

        Args:
            path: path to the config file on disk
            desired_filename: what we expect the file on disk to be called (so we can
            check if we've been given a duff file).
        """
        self.path = Path(path)
        if not self.path.is_file():
            raise FileNotFoundError(f"Not a valid path: {path}")
        if self.path.name != desired_filename:
            raise ValueError(f"not a {desired_filename} file: {path}")

    @property
    @abc.abstractmethod
    def package_name(self) -> str:
        """Returns the name of the package this setup file refers to."""

    @abc.abstractmethod
    def add_mypy_ignore(self, bad_imports):
        """Adds new content to silence mypy bad import errors."""

    @abc.abstractmethod
    def add_pylint_ignore(self, bad_imports):
        """Adds new content to silece pylint bad import errors."""

    @abc.abstractmethod
    def save_to_disk(self):
        """Saves (updated) contents back to disk."""
