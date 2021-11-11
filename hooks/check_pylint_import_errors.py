"""Check and prevent pylint import errors."""

import json
import sys

from pylint import epylint as lint

from .utils import Hook, SetupFile


class CheckPylintImportErrors(Hook):  # pylint: disable=too-few-public-methods
    """Hook to check whether pylint will raise import errors using the current
    project configuration, and fix the config file if necessary.
    """

    def run(self) -> int:
        """
        Fixes pylint parameters in ``setup.cfg`` to prevent the CI pipeline giving
        import errors during linting jobs, as not all packages provide pylint
        support. This function should be run from within the top level repo
        directory.

        The function applies pylint to this repo, and greps the resultant output
        for any import error (E0401) messages. The function will then append
        the bad package/module names to the ``[pylint]`` section of ``setup.cfg``
        to silence the error in future.

        This is a known bug with pylint and in this case, silencing the errors
        is the only fix to prevent CI job failure.

        Raises:
            Exception: if pylint fails to run
        """
        setup_file = SetupFile("setup.cfg")
        # set some pylint options to match the CI pipeline and use the output here:
        pylint_opts = " ".join(
            [
                setup_file.package_name,  # lint package files
                "--rcfile='setup.cfg'",  # use local config file
                " --output-format=json",  # return json dict for subsequent parsing
            ]
        )
        # run pylint:
        pylint_stdout, pylint_err = lint.py_run(pylint_opts, return_std=True)

        # raise any pylint running errors (i.e. not linting issues)
        if len(pylint_err.getvalue()) > 0:
            raise Exception(pylint_err.getvalue())

        # grab lint issues as json dict:
        pylint_output = json.loads(pylint_stdout.getvalue())

        # get any package/module names from pylint import-error messages:
        bad_imports = {
            msg["message"].split("'")[1]
            for msg in pylint_output
            if msg["message-id"] == "E0401"
        }
        if len(bad_imports) == 0:
            print("  No pylint import errors found")
            return 0

        print(
            "  Pylint import errors found!\n",
            f"  adding new exceptions to setup.cfg: {', '.join(bad_imports)}",
        )

        # add bad modules to the pylint ignore section:
        setup_file.add_pylint_ignore(bad_imports)
        setup_file.save_to_disk()
        return 1


def main():
    """Hook entry point"""
    return CheckPylintImportErrors().run()


if __name__ == "__main__":
    sys.exit(main())
