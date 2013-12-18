import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "SSLConnection",
    version = "0.0.1",
    author = "FIS Infrastructure Team",
    author_email = "oa.it-infrastructure@austin.utexas.edu",
    description = ("Subclass of HTTPSConnection that allows specifying "
                   "the protocol suite."),
    url = "https://github.com/ut-adamc/SSLConnection",
    packages = find_packages(),
    install_requires = [],
    extras_require = {
        'test_support': ["nose>=1.3.0"],
    },
    long_description = read("README.md"),
    classifiers=["Development Status :: 4 - Beta"],
)
