import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "https_shim",
    version = "0.1.0",
    author = "FIS Infrastructure Team",
    author_email = "oa.it-infrastructure@austin.utexas.edu",
    description = ("Subclass of HTTPSConnection that allows specifying "
                   "the protocol suite for Python 2.6/2.7."),
    url = "https://github.com/UT-Austin-FIS/https_shim",
    packages = find_packages(),
    install_requires = [],
    extras_require = {
        'test_support': ["mock>=1.0.1", "nose>=1.3.0"],
    },
    long_description = read("README.md"),
    classifiers=["Development Status :: 4 - Beta"],
)
