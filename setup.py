from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from pip.req import parse_requirements
from pip.download import PipSession

import os

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(
    'requirements/install.txt', session=PipSession()
)
reqs = [str(ir.req) for ir in install_reqs]

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

about = {}

with open(os.path.join(here, "pyramid_cli", "__about__.py")) as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=about['__version__'],
    description=about['__summary__'],
    long_description=long_description,
    url=about['__uri__'],
    author=about['__author__'],
    author_email=about['__email__'],
    license=about['__license__'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    zip_safe=True,
    install_requires=reqs,
    setup_requires=['setuptools-git'],
    entry_points={
        'console_scripts': [
            'pyramid_cli = pyramid_cli.cli:main'
        ],
        'montague.config_loader': [
            'yaml = pyramid_cli.config.yaml:YAMLConfigLoader'
        ],
    },
)
