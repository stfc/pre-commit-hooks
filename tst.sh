#!/bin/bash

pre-commit try-repo ./ check-missing-requirements --all-files
pre-commit try-repo ./ check-mypy-import-errors --all-files
pre-commit try-repo ./ check-pylint-import-errors --all-files
