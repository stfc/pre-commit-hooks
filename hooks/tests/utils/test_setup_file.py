import pytest
from pathlib import Path

from hooks.utils import setup_file

reason = (
    "This fails but setup.cfg files are not high priority for us to "
    "support so it is not high priority to support this."
)


@pytest.fixture
def path_to_setupfile(tmp_path_factory):
    filepath = tmp_path_factory.mktemp("data") / "setup.cfg"
    contents = (
        '[metadata]',
        'name = my_package',
        'version = 1.0.0',
        'author = Author Name',
        'author_email = author_name@institude.ac.uk',
        'description = My package description',
        'long_description = file: README.rst, CHANGELOG.rst, LICENSE.rst',
        'keywords = one, two',
        'license = BSD-3-Clause',
        'classifiers =',
        '    Programming Language :: Python :: 3',
        '',
        '[options]',
        'zip_safe = False',
        'include_package_data = True',
        'packages = find:',
        'python_requires = >=3.8',
        '',
        '[options.package_data]',
        '* = *.txt, *.rst',
        'hello = *.msg',
        '',
        '[options.entry_points]',
        'console_scripts =',
        '    executable-name = my_package.module:function',
        '',
        '[options.extras_require]',
        'pdf = ReportLab>=1.2; RXP',
        'rest = docutils>=0.3; pack ==1.1, ==1.3',
        '',
        '[options.packages.find]',
        'exclude =',
        '    examples*',
        '    tools*',
        '    docs*',
        '    my_package.tests*',
        '',
        '[flake8]',
        'max-line-length = 88',
        '',
        '[pylint]',
        'ignored-modules = [numpy, requests]',
    )
    contents_string = "\n".join(contents)
    with open(filepath, 'a') as f:
        f.write(contents_string)

    return filepath


def test_package_name(path_to_setupfile):
    setup = setup_file.SetupFile(path_to_setupfile)
    package_name = setup.package_name
    assert package_name == "my_package"


def test_get_config_section(path_to_setupfile):
    setup = setup_file.SetupFile(path_to_setupfile)
    section = setup._get_config_section("[flake8]")

    assert section == "[flake8]\nmax-line-length = 88\n\n"


@pytest.mark.xfail(reason=reason)
def test_add_pylint_ignore(path_to_setupfile):
    setup = setup_file.SetupFile(path_to_setupfile)
    setup.add_pylint_ignore("pandas")
    modified_section = setup._get_config_section("[pylint]")
    contents = Path(path_to_setupfile).read_text()

    # The final line contains the pylint ignores
    pylint_ignore_line = contents.split("\n")[-1]
    assert pylint_ignore_line == "ignored-modules = [numpy, requests, pandas]"
