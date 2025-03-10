import pytest

from hooks.utils.pyproject_file import PyprojectFile


@pytest.fixture
def path_to_pyproject_file(tmp_path_factory):
    """Example TOML file fixture."""
    filepath = tmp_path_factory.mktemp("data") / "pyproject.toml"
    contents = (
        '[build-system]',
        'requires = [ "poetry-core>=1.0.0",]',
        'build-backend = "poetry.core.masonry.api"',
        '',
        '[tool.poetry]',
        'name = "package-name"',
        'version = "1.0.0"',
        'description = "A Description"',
        'authors = [ "First Author","Second Author"]',
        'license = "MIT"',
        'repository = "https://github.com/stfc/pre-commit-hooks"',
        'keywords = [ "pre-commit", "hooks",]',
        '',
        '[tool.mypy]',
        'warn_return_any = true',
        'warn_unused_configs = true',
        'warn_redundant_casts = true',
        '',
        '[[tool.mypy.overrides]]',
        'module = [ "regex", "pylint", "pylint.reporters", "pylint.lint",  "requirements", "toml",]',
        'ignore_missing_imports = true',
        '',
        '[tool.isort]',
        'profile = "black"',
        'skip = [ "build_seq.py", "conf.py",]',
        'float_to_top = true',
        '',
        '[tool.poetry.scripts]',
        'check-missing-requirements = "hooks.check_missing_requirements:main"',
        'check-mypy-import-errors = "hooks.check_mypy_import_errors:main"',
        'check-pylint-import-errors = "hooks.check_pylint_import_errors:main"',
        '',
        '[tool.poetry.dependencies]',
        'python = ">=3.8, <4.0"',
        'regex = "^2022.1.18"',
        'requirements-parser = "^0.11.0"',
        'toml = "^0.10.2"',
        'mypy = "^1.1.1"',
        'mypy-extensions = "^1.0.0"',
        'ruff = "^0.2.1"',
        'pylint = "^3.1.0"',
        '',
        '[tool.poetry.group.dev]',
        'optional = true',
        '',
        '[tool.poetry.group.dev.dependencies]',
        'black = "^22.3.0"',
        'isort = "^5.10.1"',
        'pre-commit = "^2.15.0"',
        'tox = "^3.24.4"',
        'jupyterlab-code-formatter = "^1.4.10"',
        'Sphinx = "^4.2.0"',
        'sphinx-rtd-theme = "^1.0.0"',
        '',
        '[tool.ruff]',
        'line-length = 88',
        'src = ["hooks"]',
        '[tool.ruff.lint]',
        'select = [',
        '    "F",',
        '    "E",',
        '    "W",',
        '    "I001"',
        ']',
    )
    contents_string = "\n".join(contents)
    with open(filepath, 'a') as f:
        f.write(contents_string)

    return filepath


def test_package_name(path_to_pyproject_file):
    """Test whether the package name is correctly extracted."""
    pyproject_file = PyprojectFile(path_to_pyproject_file)
    package_name = pyproject_file.package_name
    assert package_name == "package-name"


def test_add_mypy_ignore(path_to_pyproject_file):
    """Test whether packages are correctly added to the ignore list."""
    pyproject_file = PyprojectFile(path_to_pyproject_file)
    pyproject_file.add_mypy_ignore(["numpy"])
    mypy_ignores = pyproject_file.contents["tool"]["mypy"]["overrides"][0]["module"]
    assert "numpy" in mypy_ignores

