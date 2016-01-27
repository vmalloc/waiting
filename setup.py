import os
import platform
import itertools
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "waiting", "__version__.py")) as version_file:
    exec(version_file.read())

_INSTALL_REQUIREMENTS = ["pyforge"]
if platform.python_version() < '2.7':
    _INSTALL_REQUIREMENTS.append('unittest2')

setup(name="waiting",
      classifiers = [
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          ],
      description="Utility for waiting for stuff to happen",
      license="BSD",
      author="Rotem Yaari",
      author_email="vmalloc@gmail.com",
      version=__version__,
      packages=find_packages(exclude=["tests"]),
      install_requires=_INSTALL_REQUIREMENTS,
      scripts=[],
      namespace_packages=[]
      )
