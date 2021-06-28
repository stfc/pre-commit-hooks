"""Check and prevent mypy import errors."""
import sys
import warnings
from typing import Set, Union

from mypy import api as mypy

from .utils import Hook, SetupFile


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
    """

    def run(self) -> int:
        """
        Fix mypy parameters in ``setup.cfg`` to prevent the CI pipeline giving
        import errors during linting jobs, as not all packages provide mypy
        support. To be run from within the top level repo directory.

        The function applies pylint to this repo, and greps the resultant output
        for any import error messages. The function will then append the bad
        package/module names to a ``[mypy-<module-name>]`` section of ``setup.cfg``
        to silence the error in future.

        This is a known bug with mypy and in this case, silencing the errors
        is the only fix to prevent CI job failure.

        Raises:
            Exception: if mypy fails to run
        """
        setup_file = SetupFile("setup.cfg")
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
            line.split("'")[1]
            for line in mypy_stdout.split("\n")
            if "found module but no type hints" in line
            or "Cannot find implementation or library stub for module named" in line
            or "No library stub file for module" in line
        }
        if not bad_imports:
            print("  No mypy import errors found")
            return 0

        print(
            "  import errors found!\n",
            f"  adding new exceptions to setup.cfg: {', '.join(bad_imports)}",
        )

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
        new_config = "\n".join(
            [setup_file.contents, _generate_mypy_ignores(bad_imports)]
        )

        # write file to disk:
        setup_file.write_text(new_config)

        return 1


def main():
    """Hook entry point"""
    return CheckMypyImportErrors().run()


if __name__ == "__main__":
    sys.exit(main())
