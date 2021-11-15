"""Some of our hooks need to read and/or modify contents of ``pyproject.toml``;
this module provides the utility to do so easily.
"""

import toml

from .config_file import ConfigFile


class PyprojectFile(ConfigFile):
    """Setup file object to include custom functionality within our hooks
    specific to a ``pyproject.toml`` file.
    """

    def __init__(self, path: str) -> None:
        super().__init__(path, "pyproject.toml")
        self.contents = toml.load(self.path)

    @property
    def package_name(self) -> str:
        return str(self.contents["tool"]["poetry"]["name"])

    def add_mypy_ignore(self, bad_imports):
        self.contents["tool"]["mypy"]["overrides"][0]["module"].extend(bad_imports)

    def add_pylint_ignore(self, bad_imports):
        if "ignored_modules" in self.contents["tool"]["pylint"]["messages_control"]:
            self.contents["tool"]["pylint"]["messages_control"][
                "ignored_modules"
            ].extend(bad_imports)
        else:
            self.contents["tool"]["pylint"]["messages_control"][
                "ignored_modules"
            ] = bad_imports

    def save_to_disk(self):
        self.path.write_text(toml.dumps(self.contents))
