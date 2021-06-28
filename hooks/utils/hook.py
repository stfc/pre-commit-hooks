"""Abstract base functionality, to be extended by individual hooks."""

import argparse
from abc import ABC, abstractmethod
from typing import Optional, Sequence


class Hook(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class to be extended by individual hooks.

    Attributes:
        args: the arguments available to a hook - ``filenames`` is provided by
            default to access the names of files which pre-commit wants our hook
            to check."""

    def __init__(self, argv: Optional[Sequence[str]] = None) -> None:
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument(
            "filenames",
            nargs="*",
            help="Filenames to check.",
        )
        self.args = self._parser.parse_args(argv)

    def add_arg(self, *args, **kwargs):
        """Adds a new argument to the hook, which can then be accessed through
        the ``args`` field in your pre-commit configuration."""
        self._parser.add_argument(*args, **kwargs)

    @abstractmethod
    def run(self) -> int:
        """Hook application - this must return 0 if the hook passes, or 1 if it
        fails."""
