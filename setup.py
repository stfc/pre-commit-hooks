"""
Setup script for hooks using PBR package.
(Use `setup.cfg` to update package details and PBR will pick them up
automatically)
"""

from setuptools import setup

setup(setup_requires=["pbr"], pbr=True)
