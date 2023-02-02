"""Some of our hooks need to read and/or modify contents of ``setup.cfg``;
this module provides the utility to do so easily.
"""

from typing import List, Set, Union

import regex as re

from .config_file import ConfigFile


class SetupFile(ConfigFile):
    """Setup file object to include custom functionality within our hooks
    specific to a ``setup.cfg`` file.
    """

    def __init__(self, path: str) -> None:
        super().__init__(path, "setup.cfg")
        self.contents = self.path.read_text()

    @property
    def lines(self) -> List[str]:
        """Returns the contents of this setup file, line by line."""
        return self.contents.split("\n")

    @property
    def package_name(self) -> str:
        """Returns the name of the package this setup file refers to.

        This is extracted from the ``name = <package_name`` line of the file."""
        return [
            line.split(" ")[2] for line in self.lines if line.split(" ")[0] == "name"
        ][0]

    def _get_config_section(self, section_name: str, pattern: str = None) -> str:
        """
        Finds a required configuration section by header

        Args:
            section_name: starting string of the section to retrieve
            pattern: regex pattern to split the file by

        Raises:
            Exception: if the requested section can't be found in the config file

        Returns:
            requested section of the config file, if found
        """
        pattern = pattern or r"(\[[^\n\]]+\]\n[^\[]*)"
        for section in re.split(pattern, self.contents):
            if section.startswith(section_name):
                return str(section)
        raise Exception(f"Section not found: {section_name}")

    def _modify_section_line(
        self,
        section_name: str,
        line_start: str,
        line_end: Union[str, List[str], Set[str]],
        mode: str = "append",
    ) -> None:
        """
        Modifies the contents of a line within a section. If the line doesn't
        exist, it'll be added to the end of the section and updated on disk.

        Args:
            section_name: config section to search within
            line_start: beginning of the line you'd like to modify
            line_end: string(s) to append
            mode (optional): append or replace an existing line, if found

        Raises:
            ValueError: if a `mode` value other than 'append' or 'replace' is
                provided

        Returns:
            str: new section containing the requested modifications
        """
        if mode.lower() not in ["append", "replace"]:
            raise ValueError(
                f"Error: mode supplied must be 'append' or 'replace', not {mode}"
            )
        if not isinstance(line_end, str):
            line_end = ", ".join(line_end)
        section = self._get_config_section(section_name)
        match = re.search(rf"({line_start}[^\n]+\n)", section)
        if match:
            if mode.lower() == "append":
                new_line = match.group(0).rstrip("\n") + ", " + line_end + "\n"
            else:
                new_line = line_start + line_end + "\n"
            new_section = section.replace(match.group(0), new_line)
        else:
            new_section = section.rstrip("\n") + "\n" + line_start + line_end + "\n\n"
        self.contents.replace(section, new_section)
        return

    def add_mypy_ignore(self, bad_imports):
        def _generate_mypy_ignores(bad_modules: Union[str, Set[str]]) -> str:
            """Prepares setup.cfg entries to tell mypy to ignore a specific module
            or modules.

            Args:
                bad_modules (Union[str, List[str]]): One or more bad modules,
                    extracted from mypy stdout

            Returns:
                str: new content to append to setup.cfg to silence the mypy errors
            """
            if isinstance(bad_modules, str):
                bad_modules = set([bad_modules])
            new_content = "\n".join(
                {
                    "\n".join([f"[mypy-{item}]", "ignore_missing_imports = True\n"])
                    for item in bad_modules
                }
            )
            return new_content

        # generate new config file contents by appending any required ignore
        # statements:
        new_config = "\n".join([self.contents, _generate_mypy_ignores(bad_imports)])
        self.contents = new_config

    def add_pylint_ignore(self, bad_imports):

        self._modify_section_line(
            section_name="[pylint]",
            line_start="ignored-modules = ",
            line_end=bad_imports,
            mode="append",
        )

    def save_to_disk(self) -> None:
        """Saves the (updated) contents of this config file back to disk."""
        self.path.write_text(self.contents)
