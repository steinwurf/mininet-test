#! /usr/bin/env python
# encoding: utf-8

from waflib.Build import BuildContext
import os
import sys
import shutil
import hashlib
import subprocess

from waflib.Configure import conf
from waflib import Logs

import waflib

top = '.'

VERSION = '1.0.0'


class UploadContext(BuildContext):
    cmd = 'upload'
    fun = 'upload'


def options(opt):

    opt.add_option(
        '--run_tests', default=False, action='store_true',
        help='Run all unit tests')

    opt.add_option(
        '--pytest_basetemp', default='pytest_temp',
        help='Set the basetemp folder where pytest executes the tests')


def configure(conf):

    # We look for mininet needed to run the unit tests
    conf.find_program('mn', mandatory=True)


def build(bld):

    # Create a virtualenv in the source folder and build universal wheel
    # Make sure the virtualenv Python module is in path
    with bld.create_virtualenv(cwd=bld.path.abspath()) as venv:
        venv.run(cmd='python -m pip install wheel')
        venv.run(cmd='python setup.py bdist_wheel --universal',
                 cwd=bld.path.abspath())

    # Delete the egg-info directory, do not understand why this is created
    # when we build a wheel. But, it is - perhaps in the future there will
    # be some way to disable its creation.
    egg_info = os.path.join('src', 'wurfapi.egg-info')

    if os.path.isdir(egg_info):
        waflib.extras.wurf.directory.remove_directory(path=egg_info)

    # Run the unit-tests
    if bld.options.run_tests:
        _pytest(bld=bld)


def _find_wheel(ctx):
    """ Find the .whl file in the dist folder. """

    wheel = ctx.path.ant_glob('dist/*-'+VERSION+'-*.whl')

    if not len(wheel) == 1:
        ctx.fatal('No wheel found (or version mismatch)')
    else:
        wheel = wheel[0]
        Logs.info('Wheel %s', wheel)
        return wheel


def upload(bld):
    """ Upload the built wheel to PyPI (the Python Package Index) """

    with bld.create_virtualenv(cwd=bld.path.abspath()) as venv:
        venv.pip_install(packages=['twine'])

        wheel = _find_wheel(ctx=bld)

        venv.run('python -m twine upload {}'.format(wheel))


def _pytest(bld):

    # We need to be able to import mininet, which is a system package
    venv = bld.create_virtualenv(
        cwd=bld.path.abspath(), system_site_packages=True)

    venv.run(cmd='python -m pip install pytest')
    venv.run(cmd='python -m pip install pytest-testdirectory')

    # Install the mininet-test plugin in the virtualenv
    wheel = _find_wheel(ctx=bld)

    venv.run(cmd='python -m pip install {}'.format(wheel))

    # We override the pytest temp folder with the basetemp option,
    # so the test folders will be available at the specified location
    # on all platforms. The default location is the "pytest" local folder.
    basetemp = os.path.abspath(os.path.expanduser(
        bld.options.pytest_basetemp))

    # We need to manually remove the previously created basetemp folder,
    # because pytest uses os.listdir in the removal process, and that fails
    # if there are any broken symlinks in that folder.
    if os.path.exists(basetemp):
        waflib.extras.wurf.directory.remove_directory(path=basetemp)

    testdir = bld.path.find_node('test')

    # Make the basetemp directory
    os.makedirs(basetemp)

    # Main test command
    command = 'python -B -m pytest {} --basetemp {}'.format(
        testdir.abspath(), os.path.join(basetemp, 'unit_tests'))

    venv.run(command)
