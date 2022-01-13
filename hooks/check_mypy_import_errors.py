"""Check and prevent mypy errors due to missing stubs."""
import sys
import warnings
from typing import Optional

from mypy import api as mypy

from .utils import Hook, PyprojectFile, SetupFile
from .utils.config_file import ConfigFile


def _warning(message, *args, **kwargs):
    """
    Custom warning to monkeypatch on to warnings module. see:
    https://docs.python.org/3/library/warnings.html#warnings.showwarning

    Args:
        message (str): Oh, come on. Really? The message to show if the warning is
                       raised
    """

    print(message)


warnings.showwarning = _warning


class CheckMypyImportErrors(Hook):  # pylint: disable=too-few-public-methods
    """Hook to check whether mypy will raise import errors using the current
    project configuration, and fix the config file if necessary.

    This is configured to only run when changes to your `requirements.txt` or
    `pyproject.toml` file are staged.
    """

    def run(self) -> int:
        """
        Fix mypy parameters in ``setup.cfg`` or ``pyproject.toml`` to prevent the
        CI pipeline giving import errors during linting jobs, as not all packages
        provide mypy support. To be run from within the top level repo directory.

        The function applies pylint to this repo, and greps the resultant output
        for any import error messages. The function will then append the bad
        package/module names to the relevant config file section to silence
        the error in future.

        This is a known bug with mypy and in this case, silencing the errors
        is the only fix to prevent CI job failure.

        Raises:
            Exception: if mypy fails to run
        """
        setup_file: Optional[ConfigFile] = None
        for filename in self.args.filenames:
            if "pyproject.toml" in filename:
                setup_file = PyprojectFile(filename)
                break
            elif "setup.cfg" in filename:
                setup_file = SetupFile("setup.cfg")

        if not setup_file:
            print("  No setup file found")
            return 0

        mypy_stdout, mypy_err, _ = mypy.run([setup_file.package_name])

        # raise any mypy running errors (i.e. not type hinting issues)
        if len(mypy_err) > 0:
            raise Exception(mypy_err)

        # collect bad imports (usual error messages:
        # "<location>: error: Skipping analysing 'pandas': found module but no type
        # hints or library stubs", or
        # "<location>: error: Cannot find implementation or library stub for module
        # named 'pyodbc'")
        bad_imports = {
            line.split(('"' if '"' in line else "'"))[1]
            for line in mypy_stdout.split("\n")
            if "found module but no type hints" in line
            or "Cannot find implementation or library stub for module named" in line
            or "No library stub file for module" in line
            or "Library stubs not installed for" in line
        }
        if not bad_imports:
            print("  No mypy import errors found")
            return 0

        print(
            "  import errors found!\n",
            f"  adding new exceptions to config file: {', '.join(bad_imports)}",
        )
        setup_file.add_mypy_ignore(bad_imports)
        setup_file.save_to_disk()
        return 1


def main():
    """Hook entry point"""
    return CheckMypyImportErrors().run()


if __name__ == "__main__":
    sys.exit(main())
