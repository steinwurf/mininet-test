import os
import io
import re
import sys

from setuptools import setup, find_packages

cwd = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(cwd, 'README.rst'), encoding='utf-8') as fd:
    long_description = fd.read()


def file_find_version(filepath):

    with io.open(filepath, encoding='utf-8') as fd:

        VERSION = None

        regex = re.compile(
            r"""
        (                # Group and match
            VERSION      #    Match 'VERSION'
            \s*          #    Match zero or more spaces
            =            #    Match and equal sign
            \s*          #    Match zero or more spaces
        )                # End group

        '
        (                # Group and match
            \d\.\d\.\d  #    Match digit.digit.digit e.g. 1.2.3
        )                # End of group
        '
        """, re.VERBOSE)

        for line in fd:

            match = regex.match(line)
            if not match:
                continue

            # The second parenthesized subgroup.
            VERSION = match.group(2)
            break

        else:
            sys.exit('No VERSION variable defined in {} - aborting!'.format(
                filepath))

    return VERSION


def find_version():

    wscript_VERSION = file_find_version(
        filepath=os.path.join(cwd, 'wscript'))

    return wscript_VERSION


VERSION = find_version()

setup(
    name='mininet-test',
    version=VERSION,
    description=('Mininet helper functionality'),
    long_description=long_description,
    url='https://github.com/steinwurf/',
    author='Steinwurf ApS',
    author_email='contact@steinwurf.com',
    license='BSD 3-clause "New" or "Revised" License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Topic :: System :: Emulators",
    ],
    keywords=('mininet-test'),
    packages=find_packages(where='src', exclude=['test']),
    package_dir={"": "src"}
)
