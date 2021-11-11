"""Some of our hooks need to read and/or modify contents of ``pyproject.toml``;
this module provides the utility to do so easily.
"""

from pyproject_parser import PyProject

from .config_file import ConfigFile


class PyprojectFile(ConfigFile):
    """Setup file object to include custom functionality within our hooks
    specific to a ``setup.cfg`` file.
    """

    def __init__(self, path: str) -> None:
        super().__init__(path, "pyproject.toml")
        self.contents = PyProject.load(self.path)

    @property
    def package_name(self) -> str:
        return self.contents.tool["poetry"]["name"]

    def add_mypy_ignore(self, bad_imports):
        self.contents.tool["mypy"]["overrides"][0]["module"].append(bad_imports)

    def add_pylint_ignore(self, bad_imports):
        return NotImplementedError

    def save_to_disk(self):
        self.contents.dump(self.path)
