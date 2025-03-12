"""Checks to see if the package requirements are all present in the current
python environment.
"""
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import requirements

from .utils import Hook


def _parse_package_name(name: Optional[str]) -> Optional[str]:
    """
    Force lower case and replace underscore with dash to compare environment
    packages (see https://www.python.org/dev/peps/pep-0426/#name)

    Args:
        name: Unformatted package name

    Returns:
        Formatted package name
    """
    return name.lower().replace("_", "-") if name else None


def _get_installed_packages() -> List[str]:
    """
    Get a formatted list of packages installed in the current environment as
    returned by ``pip freeze``

    Returns:
        List of formatted names of installed packages
    """
    package_names = [
        _parse_package_name(req.name)
        for req in requirements.parse(
            subprocess.check_output(
                [sys.executable, "-m", "pip", "list", "--format", "freeze"]
            ).decode()
        )
    ]

    return [name for name in package_names if name]


def _get_required_packages(filepath: str) -> List[str]:
    """
    Get a formatted list of packages from a pip requirements file.

    Note:
        This filters out ``None`` values, which may occur if the requirements
        file includes an install direct from a git repo without the package name
        in a ``#egg=`` ending.

    Args:
        Path to requirements txt file

    Returns:
        List of formatted names of installed packages
    """
    package_names = [
        _parse_package_name(req.name)
        for req in requirements.parse(Path(filepath).read_text())
        if req.name
    ]

    return [name for name in package_names if name]


class CheckMissingRequirements(Hook):  # pylint: disable=too-few-public-methods
    """Hook to check all requirements are installed within the current dev
    environment."""

    def run(self) -> int:
        """
        Checks to see if the package requirements are all present in the current
        environment.

        Note:
            this hook should be run before ``isort`` in order to prevent
            unwanted import sorting based on an incorrect environment spec.
        """
        # assemble dict containing lists of any unmet requirements against each file:
        missing_requirements = {
            filepath: list(
                set(_get_required_packages(filepath)) - set(_get_installed_packages())
            )
            for filepath in self.args.filenames
        }
        if all((not missing for missing in missing_requirements.values())):
            return 0

        # assemble output string of all unmet dependencies:
        output_str = "\n".join(
            [
                f"  - {file}: {errors}"
                for file, errors in missing_requirements.items()
                if errors
            ]
        )
        print(
            f"These requirements are missing from your current environment:"
            f"\n{output_str}\n"
            f"\nPlease install the above or rebuild your environment to prevent "
            f"CI issues"
        )
        return 1


def main():
    """Hook entry point"""
    return CheckMissingRequirements().run()


if __name__ == "__main__":
    sys.exit(main())
