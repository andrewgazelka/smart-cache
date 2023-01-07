"""Setup"""

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="smart_cache",
    version="1.0.2",
    description="Python caching library that is persistent and uses bytecode analysis to determine re-evaluation",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/andrewgazelka/smart-cache",
    author="Andrew Gazelka",
    author_email="andrew.gazelka@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["smart_cache"],
    include_package_data=True,
    install_requires=[],
)
